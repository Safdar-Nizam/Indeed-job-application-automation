import os
import time
import random
import logging
from datetime import datetime
from urllib.parse import quote_plus, urlparse

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    WebDriverException,
    NoSuchWindowException,
    InvalidSessionIdException,
)

import re

from config import (
    search_queries, title_keywords, title_blacklist, company_blacklist, resume_path,
    human_delay, typing_delay,
    page_load_delay, between_jobs_delay, form_field_delay,
    after_submit_delay, scroll_delay,
    add_firstname, add_lastname, add_phone, add_email,
    add_address, add_city, add_state, add_postal, add_country,
    add_linkedin, add_github, add_portfolio,
    add_university, add_education, add_degree, add_graduation_year,
    add_workauthorized, add_citizen, add_sponsorship, add_relocate,
    add_commute, add_commute2, add_criminal, add_DBS, add_valid_cert,
    add_available, add_shift, add_interview_dates, add_salary,
    add_gender, add_veteran, add_disability,
    experience_map, add_default_experience, default_unknown_multi,
    add_company, add_pronouns, add_race,
)

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────
log_filename = f"applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# STATS & GLOBALS
# ──────────────────────────────────────────────
stats = {
    "applied": 0, "skipped_title": 0, "skipped_external": 0,
    "skipped_no_btn": 0, "skipped_already": 0, "left_open": 0, "errors": 0,
}
INDEED_DOMAINS = {"indeed.com", "indeedapply.com", "indeed.force.com"}
main_window_handle = None
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNAL_FILE = os.path.join(SCRIPT_DIR, "GO.txt")


# ══════════════════════════════════════════════
# HUMAN-MIMICKING HELPERS
# ══════════════════════════════════════════════

def wait(low_high: tuple):
    time.sleep(random.uniform(*low_high))

def human_type(element, text: str):
    try:
        element.click()
        time.sleep(0.05)
    except Exception:
        pass
    element.send_keys(Keys.CONTROL, "a")
    time.sleep(0.03)
    element.send_keys(Keys.DELETE)
    time.sleep(0.05)
    for ch in text:
        element.send_keys(ch)
        time.sleep(typing_delay())

def human_scroll(driver, pixels=None):
    px = pixels or random.randint(150, 400)
    try:
        driver.execute_script(f"window.scrollBy(0, {px});")
    except Exception:
        pass
    wait(scroll_delay)

def random_mouse_jiggle(driver):
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        ActionChains(driver).move_to_element_with_offset(
            body, random.randint(80, 500), random.randint(80, 350)
        ).perform()
    except Exception:
        pass

def safe_click(driver, element, retries=3):
    for _ in range(retries):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            time.sleep(0.2)
            element.click()
            return True
        except ElementClickInterceptedException:
            time.sleep(0.4)
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                pass
        except (StaleElementReferenceException, WebDriverException):
            return False
    return False

def close_popups(driver):
    popup_selectors = [
        "[aria-label='close']", "[aria-label='Close']",
        "[data-gnav-element-name='CloseButton']",
        "#onetrust-accept-btn-handler",
        ".icl-CloseButton", "[aria-label='Dismiss']",
        "button.css-yi9ndv",
    ]
    for sel in popup_selectors:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, sel)
            if btn.is_displayed():
                btn.click()
                time.sleep(0.3)
        except Exception:
            pass

def ensure_main_window(driver):
    global main_window_handle
    try:
        current_handles = driver.window_handles
        if main_window_handle and main_window_handle in current_handles:
            driver.switch_to.window(main_window_handle)
            return True
        if current_handles:
            driver.switch_to.window(current_handles[0])
            main_window_handle = current_handles[0]
            return True
    except InvalidSessionIdException:
        raise
    except Exception:
        pass
    return False

def is_indeed_domain(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower()
        return any(d in host for d in INDEED_DOMAINS)
    except Exception:
        return False

def wait_for_page_ready(driver, timeout=8):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception:
        pass
    time.sleep(0.3)


# ══════════════════════════════════════════════
# TITLE FILTERING
# ══════════════════════════════════════════════

def title_matches(job_title: str) -> bool:
    t = job_title.lower()
    for bl in title_blacklist:
        if bl in t:
            return False
    for kw in title_keywords:
        if len(kw) <= 3:
            if re.search(r'\b' + re.escape(kw) + r'\b', t):
                return True
        else:
            if kw in t:
                return True
    return False


# ══════════════════════════════════════════════
# RESUME UPLOAD
# ══════════════════════════════════════════════

def try_upload_resume(driver):
    """Find any file input and upload the resume."""
    if not resume_path or not os.path.exists(resume_path):
        return
    try:
        file_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
        for fi in file_inputs:
            try:
                fi.send_keys(resume_path)
                log.info("        Resume uploaded.")
                time.sleep(1.0)
                return
            except Exception:
                continue
    except Exception:
        pass


# ══════════════════════════════════════════════
# FORM-FILLING LOGIC
# ══════════════════════════════════════════════

KEYWORD_TO_ANSWER = {
    # Order matters — more specific patterns first
    "first and last":  f"{add_firstname} {add_lastname}",
    "full name":       f"{add_firstname} {add_lastname}",
    "preferred name":  add_firstname,
    "first name":      add_firstname,
    "last name":       add_lastname,
    "cell phone":      add_phone,
    "phone":           add_phone,
    "mobile":          add_phone,
    "email":           add_email,
    "e-mail":          add_email,
    "address":         add_address,
    "street":          add_address,
    "city":            add_city,
    "state":           add_state,
    "province":        add_state,
    "postal":          add_postal,
    "zip":             add_postal,
    "zip code":        add_postal,
    "country":         add_country,
    "linkedin":        add_linkedin,
    "github":          add_github,
    "portfolio":       add_portfolio,
    "website":         add_portfolio,
    "university":      add_university,
    "college":         add_university,
    "school name":     add_university,
    "degree":          add_degree,
    "graduation":      add_graduation_year,
    "salary":          add_salary,
    "compensation":    add_salary,
    "desired pay":     add_salary,
    "pay rate":        add_salary,
    "expected pay":    add_salary,
    "interview":       add_interview_dates,
    "start date":      "Immediately",
    "earliest start":  "Immediately",
    "when can you":    "Immediately",
    "current company": add_company,
    "current employer":add_company,
    "company name":    add_company,
    "employer name":   add_company,
    "organization":    add_company,
    "pronoun":         add_pronouns,
}

CLICK_KEYWORD_TO_ANSWER = {
    "authorization":       add_workauthorized,
    "authorized":          add_workauthorized,
    "authorisation":       add_workauthorized,
    "authorised":          add_workauthorized,
    "right to work":       add_workauthorized,
    "legally authorized":  add_workauthorized,
    "work authorization":  add_workauthorized,
    "eligible to work":    add_workauthorized,
    "eligible":            "Yes",
    "legally eligible":    "Yes",
    "sponsorship":         add_sponsorship,
    "sponsor":             add_sponsorship,
    "visa":                add_sponsorship,
    "require sponsorship": add_sponsorship,
    "education":           add_education,
    "highest level":       add_education,
    "level of education":  add_education,
    "commute":             add_commute,
    "relocate":            add_relocate,
    "relocation":          add_relocate,
    "willing to relocate": add_relocate,
    "travel":              add_commute,
    "on-site":             "Yes",
    "onsite":              "Yes",
    "in-person":           "Yes",
    "hybrid":              "Yes",
    "remote":              "Yes",
    "shift":               add_shift,
    "veteran":             add_veteran,
    "military":            add_veteran,
    "disability":          add_disability,
    "criminal":            add_criminal,
    "background check":    "Yes",
    "felony":              add_criminal,
    "conviction":          add_criminal,
    "dbs":                 add_DBS,
    "valid":               add_valid_cert,
    "certification":       "Yes",
    "certified":           "Yes",
    "license":             "Yes",
    "gender":              add_gender,
    "sex":                 add_gender,
    "citizen":             add_citizen,
    "citizenship":         add_citizen,
    "available":           add_available,
    "drug test":           "Yes",
    "drug screen":         "Yes",
    "agree":               "Yes",
    "consent":             "Yes",
    "acknowledge":         "Yes",
    "18 years":            "Yes",
    "age":                 "Yes",
    "do you have":         "Yes",
    "are you able":        "Yes",
    "can you":             "Yes",
    "will you":            "Yes",
    "have you":            "Yes",
    "experience with":     "Yes",
    "familiar with":       "Yes",
    "proficient":          "Yes",
    "comfortable":         "Yes",
    "authorized to":       "Yes",
    "able to":             "Yes",
    "willing to":          "Yes",
    "race":                add_race,
    "ethnicity":           add_race,
    "ethnic":              add_race,
}


def get_experience_answer(question_text: str) -> str:
    q = question_text.lower()
    for keyword, years in experience_map.items():
        if keyword in q:
            return years
    return add_default_experience


def fill_text_field(question_element, answer: str) -> bool:
    if not answer:
        return False
    input_selectors = [
        '[id^="input-q"]',
        'input[type="text"]',
        'input[type="number"]',
        'input[type="tel"]',
        'input[type="email"]',
        "textarea",
        "input:not([type='hidden']):not([type='radio']):not([type='checkbox']):not([type='file']):not([type='submit'])",
    ]
    for sel in input_selectors:
        try:
            fields = question_element.find_elements(By.CSS_SELECTOR, sel)
            for field in fields:
                if field.is_displayed() and field.is_enabled():
                    current_val = (field.get_attribute("value") or "").strip()
                    if current_val:
                        return True
                    wait(form_field_delay)
                    human_type(field, answer)
                    return True
        except (NoSuchElementException, StaleElementReferenceException):
            continue
    return False


def click_option(question_element, answer: str) -> bool:
    if not answer:
        return False
    # Try exact text match first
    try:
        options = question_element.find_elements(
            By.XPATH, f'.//*[contains(text(), "{answer}")]'
        )
        for opt in options:
            if opt.is_displayed():
                wait(form_field_delay)
                try:
                    opt.click()
                except ElementClickInterceptedException:
                    try:
                        question_element.find_element(
                            By.XPATH, f'.//label[contains(text(), "{answer}")]'
                        ).click()
                    except Exception:
                        pass
                return True
    except Exception:
        pass

    # Try radio/checkbox labels
    try:
        labels = question_element.find_elements(By.TAG_NAME, "label")
        for label in labels:
            if answer.lower() in label.text.lower():
                wait(form_field_delay)
                label.click()
                return True
    except Exception:
        pass

    # Try select/dropdown
    try:
        selects = question_element.find_elements(By.TAG_NAME, "select")
        for select_el in selects:
            if select_el.is_displayed():
                sel = Select(select_el)
                for option in sel.options:
                    if answer.lower() in option.text.lower():
                        wait(form_field_delay)
                        sel.select_by_visible_text(option.text)
                        return True
    except Exception:
        pass

    return False


def smart_select_dropdown(question_element, question_text: str) -> bool:
    """Intelligently pick a dropdown option when no direct match found."""
    try:
        selects = question_element.find_elements(By.TAG_NAME, "select")
        for select_el in selects:
            if not select_el.is_displayed():
                continue
            sel = Select(select_el)
            opts = [o for o in sel.options if o.get_attribute("value")]

            if len(opts) <= 1:
                continue

            q = question_text.lower()
            # Prefer "Yes" options
            for o in opts:
                if o.text.strip().lower() == "yes":
                    sel.select_by_visible_text(o.text)
                    return True
            # Education question
            if "education" in q or "degree" in q:
                for o in opts:
                    if "master" in o.text.lower():
                        sel.select_by_visible_text(o.text)
                        return True
            # State/province selection
            if any(w in q for w in ("state", "province", "region")):
                for o in opts:
                    ot = o.text.strip().lower()
                    if "florida" in ot or ot == "fl":
                        sel.select_by_visible_text(o.text)
                        return True
            # Country selection
            if "country" in q:
                for o in opts:
                    ot = o.text.strip().lower()
                    if ot in ("united states", "us", "usa", "united states of america"):
                        sel.select_by_visible_text(o.text)
                        return True
            # Race/ethnicity
            if any(w in q for w in ("race", "ethnicity", "ethnic")):
                for o in opts:
                    if add_race.lower() in o.text.lower():
                        sel.select_by_visible_text(o.text)
                        return True
            # Gender
            if any(w in q for w in ("gender", "sex")):
                for o in opts:
                    if add_gender.lower() in o.text.lower():
                        sel.select_by_visible_text(o.text)
                        return True
            # Pronouns
            if "pronoun" in q:
                for o in opts:
                    if add_pronouns.lower() in o.text.lower():
                        sel.select_by_visible_text(o.text)
                        return True
            # Veteran
            if "veteran" in q or "military" in q:
                for o in opts:
                    if add_veteran.lower() in o.text.lower():
                        sel.select_by_visible_text(o.text)
                        return True
            # Experience years
            if "experience" in q or "years" in q:
                for o in opts:
                    txt = o.text.strip()
                    if txt in ("4", "5", "3-5", "3+", "4+", "5+"):
                        sel.select_by_visible_text(o.text)
                        return True
                # Pick the middle-to-high option
                if len(opts) > 2:
                    pick = opts[len(opts) * 2 // 3]
                    sel.select_by_visible_text(pick.text)
                    return True

            # Default: pick second option (skip placeholder "Select...")
            if len(opts) >= 2:
                pick = opts[1] if opts[0].text.strip().lower() in ("", "select", "select...", "choose", "--") else opts[0]
                sel.select_by_visible_text(pick.text)
                return True
    except Exception:
        pass
    return False


def identify_field_answer(element) -> str:
    """Try to identify what answer a field needs based on its HTML attributes."""
    combined = ""
    for attr in ("name", "id", "placeholder", "aria-label", "autocomplete", "data-testid"):
        try:
            val = element.get_attribute(attr) or ""
            combined += " " + val.lower()
        except Exception:
            pass
    try:
        label_id = element.get_attribute("aria-labelledby")
        if label_id:
            label_el = element.parent.find_element(By.ID, label_id)
            combined += " " + label_el.text.lower()
    except Exception:
        pass

    field_map = [
        (["firstname", "first_name", "first-name", "fname", "given-name", "givenname"], add_firstname),
        (["lastname", "last_name", "last-name", "lname", "surname", "family-name", "familyname"], add_lastname),
        (["fullname", "full_name", "full-name", "your-name"], f"{add_firstname} {add_lastname}"),
        (["phone", "mobile", "cell", "tel"], add_phone),
        (["email", "e-mail"], add_email),
        (["street", "address1", "address_line", "address-line", "address"], add_address),
        (["city", "municipality", "town"], add_city),
        (["state", "province", "region"], add_state),
        (["postal", "zip", "postcode"], add_postal),
        (["country"], add_country),
        (["linkedin"], add_linkedin),
        (["salary", "compensation", "pay"], add_salary),
        (["company", "employer", "organization"], add_company),
        (["university", "school", "college"], add_university),
    ]
    for keywords, answer in field_map:
        for kw in keywords:
            if kw in combined and answer:
                return answer
    return ""


def get_appropriate_date(question_text: str) -> str:
    """Return an appropriate date based on the question context."""
    q = question_text.lower()
    if any(w in q for w in ("leave", "left", "end date", "last day", "departure", "resigned", "when did you")):
        return "01/01/2025"
    elif any(w in q for w in ("start", "begin", "available", "join")):
        return "03/01/2026"
    return "01/01/2025"


def handle_date_field(question_element, question_text: str) -> bool:
    """Detect and fill date fields with appropriate dates."""
    # Check for actual date inputs
    try:
        date_inputs = question_element.find_elements(By.CSS_SELECTOR, 'input[type="date"]')
        for inp in date_inputs:
            if inp.is_displayed() and inp.is_enabled():
                val = (inp.get_attribute("value") or "").strip()
                if not val:
                    date_val = get_appropriate_date(question_text)
                    human_type(inp, date_val)
                    return True
    except Exception:
        pass

    # Check for text inputs expecting dates
    date_keywords = ["date", "when did you", "mm/dd", "mm-dd", "yyyy",
                     "leave date", "end date", "start date", "when did"]
    is_date_q = any(kw in question_text for kw in date_keywords)
    if not is_date_q:
        return False

    try:
        inputs = question_element.find_elements(By.CSS_SELECTOR,
            'input[type="text"], input:not([type]), input[type="date"]')
        for inp in inputs:
            if inp.is_displayed() and inp.is_enabled():
                val = (inp.get_attribute("value") or "").strip()
                if not val:
                    placeholder = (inp.get_attribute("placeholder") or "").lower()
                    if "mm" in placeholder or "date" in placeholder or is_date_q:
                        date_val = get_appropriate_date(question_text)
                        wait(form_field_delay)
                        human_type(inp, date_val)
                        return True
    except Exception:
        pass
    return False


def force_fill_blanks(driver):
    """Last resort: find any empty required field and fill intelligently."""
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR,
            "input[required]:not([type='hidden']):not([type='radio']):not([type='checkbox']):not([type='file'])"
        )
        for inp in inputs:
            try:
                if inp.is_displayed() and inp.is_enabled():
                    val = (inp.get_attribute("value") or "").strip()
                    if not val:
                        inp_type = (inp.get_attribute("type") or "text").lower()
                        if inp_type == "date":
                            human_type(inp, "01/01/2025")
                            continue
                        smart_answer = identify_field_answer(inp)
                        if smart_answer:
                            human_type(inp, smart_answer)
                        elif inp_type == "tel":
                            human_type(inp, add_phone)
                        elif inp_type == "number":
                            human_type(inp, add_default_experience)
                        elif inp_type == "email":
                            human_type(inp, add_email)
                        else:
                            human_type(inp, add_default_experience)
            except Exception:
                continue
    except Exception:
        pass

    # Also handle required textareas
    try:
        textareas = driver.find_elements(By.CSS_SELECTOR, "textarea[required]")
        for ta in textareas:
            try:
                if ta.is_displayed() and ta.is_enabled():
                    val = (ta.get_attribute("value") or "").strip()
                    if not val:
                        human_type(ta, "Yes")
            except Exception:
                continue
    except Exception:
        pass

    # Handle any unfilled selects
    try:
        selects = driver.find_elements(By.CSS_SELECTOR, "select[required]")
        for select_el in selects:
            try:
                if select_el.is_displayed():
                    sel = Select(select_el)
                    current = sel.first_selected_option.get_attribute("value")
                    if not current or current == "":
                        opts = [o for o in sel.options if o.get_attribute("value")]
                        if opts:
                            sel.select_by_visible_text(opts[0].text)
            except Exception:
                continue
    except Exception:
        pass

    # Handle unchecked required radios
    try:
        fieldsets = driver.find_elements(By.TAG_NAME, "fieldset")
        for fs in fieldsets:
            radios = fs.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            if radios and not any(r.is_selected() for r in radios):
                for r in radios:
                    try:
                        label = r.find_element(By.XPATH, "./ancestor::label | ./following-sibling::label | ../label")
                        if "yes" in label.text.lower():
                            label.click()
                            break
                    except Exception:
                        continue
                else:
                    try:
                        radios[0].find_element(By.XPATH, "./ancestor::label | ../label").click()
                    except Exception:
                        pass
    except Exception:
        pass

    # Also handle non-required but visible empty radios in question containers
    try:
        containers = driver.find_elements(By.CSS_SELECTOR, '.ia-Questions-item, [data-testid="question-container"]')
        for cont in containers:
            radios = cont.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            if radios and not any(r.is_selected() for r in radios):
                for r in radios:
                    try:
                        label = r.find_element(By.XPATH, "./ancestor::label | ./following-sibling::label | ../label")
                        if "yes" in label.text.lower():
                            label.click()
                            break
                    except Exception:
                        continue
                else:
                    try:
                        radios[0].find_element(By.XPATH, "./ancestor::label | ../label").click()
                    except Exception:
                        pass
    except Exception:
        pass


def answer_question(question_element):
    try:
        spans = question_element.find_elements(
            By.CSS_SELECTOR, "label, span, legend, h3, h4, p, div[role='group'] > span"
        )
        question_text = " ".join(s.text for s in spans if s.text.strip()).lower().strip()
    except Exception:
        question_text = ""

    if not question_text or len(question_text) < 2:
        return

    # 1. Try text field matches first (name, city, phone, etc.)
    for keyword, answer in KEYWORD_TO_ANSWER.items():
        if keyword in question_text and answer:
            if fill_text_field(question_element, answer):
                return

    # 2. Try date field detection
    if handle_date_field(question_element, question_text):
        return

    # 3. Click/radio/checkbox matches
    for keyword, answer in CLICK_KEYWORD_TO_ANSWER.items():
        if keyword in question_text and answer:
            if click_option(question_element, answer):
                return

    # 4. Experience / years questions
    if any(w in question_text for w in ("experience", "years", "how many", "how long")):
        exp = get_experience_answer(question_text)
        if fill_text_field(question_element, exp):
            return
        if click_option(question_element, exp):
            return
        if smart_select_dropdown(question_element, question_text):
            return

    # 5. Try smart dropdown as fallback
    if smart_select_dropdown(question_element, question_text):
        return

    # 6. Final fallbacks — only use "4" as absolute last resort
    has_radio_or_checkbox = False
    try:
        rc = question_element.find_elements(
            By.CSS_SELECTOR, 'input[type="radio"], input[type="checkbox"]'
        )
        has_radio_or_checkbox = len(rc) > 0
    except Exception:
        pass

    if has_radio_or_checkbox:
        if click_option(question_element, "Yes"):
            return
        if default_unknown_multi:
            click_option(question_element, default_unknown_multi)
    else:
        # Last resort: try to identify field from HTML attributes before defaulting
        try:
            inputs = question_element.find_elements(By.CSS_SELECTOR,
                "input:not([type='hidden']):not([type='radio']):not([type='checkbox']):not([type='file']), textarea")
            for inp in inputs:
                if inp.is_displayed() and inp.is_enabled():
                    val = (inp.get_attribute("value") or "").strip()
                    if not val:
                        smart_answer = identify_field_answer(inp)
                        if smart_answer:
                            human_type(inp, smart_answer)
                            return
        except Exception:
            pass
        fill_text_field(question_element, add_default_experience)


# ══════════════════════════════════════════════
# APPLICATION FLOW
# ══════════════════════════════════════════════

def find_and_click_button(driver) -> str:
    """Returns: 'submitted', 'continued', or 'none'."""
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        submit_btn = None
        continue_btn = None

        NEVER_CLICK = {"save and close", "save & close", "save and exit", "cancel", "discard"}
        for btn in buttons:
            try:
                if not btn.is_displayed():
                    continue
            except StaleElementReferenceException:
                continue
            txt = btn.text.strip().lower()
            if txt in NEVER_CLICK:
                continue
            if txt in ("submit your application", "submit application", "submit", "apply", "apply now"):
                submit_btn = btn
            elif txt in ("continue", "next", "continue to next step", "continue applying"):
                continue_btn = btn

        if continue_btn:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", continue_btn)
                time.sleep(0.5)
            except Exception:
                pass
            safe_click(driver, continue_btn)
            return "continued"
        if submit_btn:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
                time.sleep(0.5)
            except Exception:
                pass
            safe_click(driver, submit_btn)
            return "submitted"
    except Exception:
        pass

    btn_selectors = [
        'button[data-testid="submit-button"]',
        'button[aria-label="Submit your application"]',
        'button[aria-label="Continue"]',
        'button[type="submit"]',
        'button.ia-continueButton',
    ]
    for sel in btn_selectors:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, sel)
            if btn.is_displayed():
                txt = btn.text.strip().lower()
                safe_click(driver, btn)
                return "submitted" if "submit" in txt else "continued"
        except Exception:
            continue

    return "none"


def already_applied(driver) -> bool:
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        indicators = [
            "you've applied", "you have already applied",
            "already been submitted", "application has been submitted",
            "you already applied", "application was sent",
            "your application has been submitted",
        ]
        return any(ind in body_text for ind in indicators)
    except Exception:
        return False


def verify_submission(driver) -> bool:
    for _ in range(5):
        time.sleep(random.uniform(1.5, 2.5))
        try:
            body = driver.find_element(By.TAG_NAME, "body").text.lower()
            if any(s in body for s in ["application has been submitted", "you've applied", "application submitted", "successfully applied"]):
                return True
        except Exception:
            pass
    return False


def process_application(driver) -> bool:
    """Walk through the application form. Returns True if submitted."""
    last_page_source = ""
    stuck_count = 0

    for page_num in range(25):
        wait_for_page_ready(driver)
        time.sleep(human_delay(0.3, 0.8))
        random_mouse_jiggle(driver)

        if already_applied(driver):
            log.info("        Already applied -- skipping.")
            stats["skipped_already"] += 1
            return False

        # Try uploading resume on every page (only works if file input exists)
        try_upload_resume(driver)

        # Find and answer questions (with re-scan for dynamically appearing questions)
        question_selectors = [
            ".ia-Questions-item",
            ".ia-BasePage-component",
            '[data-testid="question-container"]',
            "fieldset",
            ".ia-Questions",
        ]
        for _scan in range(3):  # Re-scan up to 3 times for dynamic questions
            questions_found = []
            for sel in question_selectors:
                try:
                    found = driver.find_elements(By.CSS_SELECTOR, sel)
                    if found:
                        questions_found = found
                        break
                except Exception:
                    continue

            for q in questions_found:
                try:
                    answer_question(q)
                except Exception:
                    pass

            # Brief pause to let any new dynamic questions appear
            time.sleep(0.5)

        # Force fill any remaining empty required fields
        force_fill_blanks(driver)

        # Detect "Review your application" page — needs extra wait + full scroll
        is_review_page = False
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            review_indicators = [
                "review your application", "review and submit",
                "please review", "preparing", "review your",
                "application review", "review & submit",
            ]
            if any(ind in body_text for ind in review_indicators):
                is_review_page = True
        except Exception:
            pass

        if is_review_page:
            log.info("        >> Review page detected — waiting for full load...")
            time.sleep(random.uniform(5.0, 8.0))
            for _ in range(10):
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(random.uniform(0.4, 0.8))
            time.sleep(random.uniform(2.0, 4.0))
        else:
            human_scroll(driver, random.randint(80, 200))
            time.sleep(human_delay(0.2, 0.5))

        # Anti-stuck: detect if page hasn't changed
        try:
            current_source = driver.page_source[:2000]
        except Exception:
            current_source = ""

        result = find_and_click_button(driver)

        if result == "submitted":
            log.info("        >> Submit clicked. Waiting for confirmation...")
            time.sleep(random.uniform(5.0, 8.0))
            if already_applied(driver) or verify_submission(driver):
                log.info("        >> APPLICATION CONFIRMED!")
            else:
                log.info("        >> Submitted (page didn't confirm explicitly)")
            stats["applied"] += 1
            return True
        elif result == "continued":
            wait(page_load_delay)
            stuck_count = 0
            last_page_source = current_source
            continue
        else:
            if current_source and current_source == last_page_source:
                stuck_count += 1
            else:
                stuck_count = 0
            last_page_source = current_source
            max_stuck = 15 if is_review_page else 5
            if stuck_count >= max_stuck:
                log.warning("        Stuck. Giving up on this job.")
                return False
            if is_review_page:
                log.info(f"        >> Review page: scrolling down again (attempt {stuck_count+1})...")
                for _ in range(6):
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(0.4)
                time.sleep(2.0)
            force_fill_blanks(driver)
            time.sleep(1.0)
            result2 = find_and_click_button(driver)
            if result2 == "submitted":
                time.sleep(random.uniform(5.0, 8.0))
                if already_applied(driver) or verify_submission(driver):
                    log.info("        >> APPLICATION CONFIRMED!")
                stats["applied"] += 1
                return True
            elif result2 == "continued":
                wait(page_load_delay)
                stuck_count = 0
                continue

    log.warning("        Maxed out questionnaire pages.")
    return False


# ══════════════════════════════════════════════
# SEARCH & PAGINATION
# ══════════════════════════════════════════════

def build_search_url(query: str, location: str, start: int = 0) -> str:
    url = f"https://www.indeed.com/jobs?q={quote_plus(query)}&l={quote_plus(location)}"
    url += "&sort=date"
    url += "&fromage=14"
    url += "&sc=0kf%3Aattr(DSQF7)%3B"
    if start > 0:
        url += f"&start={start}"
    return url


def get_job_cards(driver) -> list:
    selectors = [
        'div.job_seen_beacon',
        ".mosaic-provider-jobcards .tapItem",
        'a[data-jk]',
        'div[data-testid="slider_item"]',
        ".resultContent",
    ]
    for sel in selectors:
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, sel)
            if cards:
                return cards
        except Exception:
            continue
    return []


def get_job_title_from_card(card) -> str:
    title_selectors = [
        'h2.jobTitle span[title]',
        'h2.jobTitle span',
        'h2.jobTitle a span',
        '.jcs-JobTitle span',
        'a.jcs-JobTitle span',
        'h2 span',
    ]
    for sel in title_selectors:
        try:
            el = card.find_element(By.CSS_SELECTOR, sel)
            t = el.get_attribute("title") or el.text
            if t and t.strip():
                return t.strip()
        except Exception:
            continue
    try:
        return card.text.split("\n")[0].strip()
    except Exception:
        return ""


def get_company_from_card(card) -> str:
    company_selectors = [
        'span[data-testid="company-name"]',
        'span.companyName',
        'span.css-63koeb',
        'a[data-tn-element="companyName"]',
        '.company_location .companyName',
    ]
    for sel in company_selectors:
        try:
            el = card.find_element(By.CSS_SELECTOR, sel)
            t = el.text
            if t and t.strip():
                return t.strip()
        except Exception:
            continue
    try:
        lines = card.text.split("\n")
        if len(lines) >= 2:
            return lines[1].strip()
    except Exception:
        pass
    return ""


def company_is_blacklisted(company_name: str) -> bool:
    c = company_name.lower()
    for bl in company_blacklist:
        if bl in c:
            return True
    return False


def get_job_title_from_panel(driver) -> str:
    selectors = [
        'h2.jobsearch-JobInfoHeader-title',
        '.jobsearch-JobInfoHeader-title',
        'h1[data-testid="jobsearch-JobInfoHeader-title"]',
        'h2.jobTitle',
    ]
    for sel in selectors:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            t = el.text.strip()
            if t:
                return t
        except Exception:
            continue
    return ""


def get_apply_button(driver):
    selectors = [
        'button.ia-IndeedApplyButton',
        ".ia-IndeedApplyButton",
        'button[id="indeedApplyButton"]',
        'button[data-testid="indeedApplyButton"]',
        'button.indeed-apply-button',
    ]
    for sel in selectors:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, sel)
            if btn.is_displayed() and "apply" in btn.text.lower():
                return btn
        except NoSuchElementException:
            continue
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if btn.is_displayed() and btn.text.strip().lower() == "apply now":
                return btn
    except Exception:
        pass
    return None


def check_for_external_redirect(driver, pre_click_handles: set) -> str:
    time.sleep(1.5)
    try:
        current_handles = set(driver.window_handles)
    except Exception:
        return "gone"
    new_handles = current_handles - pre_click_handles

    if new_handles:
        new_handle = new_handles.pop()
        driver.switch_to.window(new_handle)
        time.sleep(0.8)
        try:
            new_url = driver.current_url
        except Exception:
            return "gone"
        if is_indeed_domain(new_url):
            return "indeed_apply"
        else:
            return "external_tab"

    try:
        current_url = driver.current_url
        if not is_indeed_domain(current_url):
            return "external_tab"
    except Exception:
        return "gone"

    return "same_page"


def process_job_card(driver, card, idx, total_on_page, label="", skip_title_filter=False):
    """Process a single job card: check title/company, click apply, fill form.
       Returns True if an application was attempted, False if skipped."""
    global main_window_handle

    job_title = get_job_title_from_card(card)
    company_name = get_company_from_card(card)

    if not skip_title_filter and job_title and not title_matches(job_title):
        log.info(f"  [{idx+1}/{total_on_page}]{label} SKIP (title): \"{job_title}\" @ {company_name}")
        stats["skipped_title"] += 1
        return False

    if company_name and company_is_blacklisted(company_name):
        log.info(f"  [{idx+1}/{total_on_page}]{label} SKIP (company): \"{job_title}\" @ {company_name}")
        stats["skipped_title"] += 1
        return False

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
        time.sleep(human_delay(0.3, 0.7))
        ActionChains(driver).move_to_element(card).pause(
            random.uniform(0.15, 0.4)
        ).click().perform()
        wait(between_jobs_delay)
    except Exception:
        return False

    if not job_title:
        job_title = get_job_title_from_panel(driver)
        if not skip_title_filter and job_title and not title_matches(job_title):
            log.info(f"  [{idx+1}/{total_on_page}]{label} SKIP: \"{job_title}\"")
            stats["skipped_title"] += 1
            return False

    if not job_title:
        job_title = "(title unknown)"

    log.info(f"  [{idx+1}/{total_on_page}]{label} MATCH: \"{job_title}\"")

    apply_btn = get_apply_button(driver)
    if not apply_btn:
        log.info(f"        No Indeed Apply button. Skipping.")
        stats["skipped_no_btn"] += 1
        return False

    pre_click_handles = set(driver.window_handles)
    safe_click(driver, apply_btn)

    redirect_type = check_for_external_redirect(driver, pre_click_handles)

    if redirect_type == "external_tab":
        ext_url = ""
        try:
            ext_url = driver.current_url
        except Exception:
            pass
        log.info(f"        EXTERNAL -- tab left open for you: {ext_url}")
        stats["left_open"] += 1
        ensure_main_window(driver)
        wait(between_jobs_delay)
        return False

    if redirect_type == "gone":
        log.warning(f"        Window gone. Moving on.")
        stats["errors"] += 1
        ensure_main_window(driver)
        return False

    wait_for_page_ready(driver)
    time.sleep(human_delay(0.3, 0.6))

    try:
        success = process_application(driver)
        if success:
            log.info(f"        Applied to: \"{job_title}\"")
            log.info("        Waiting 7 seconds to confirm submission...")
            time.sleep(7)
        else:
            log.info(f"        Could not complete: \"{job_title}\"")
    except Exception as e:
        log.error(f"        Error: {e}")
        stats["errors"] += 1

    try:
        current_handles = driver.window_handles
        if len(current_handles) > 1 and driver.current_window_handle != main_window_handle:
            driver.close()
    except Exception:
        pass
    ensure_main_window(driver)
    wait(between_jobs_delay)
    return True


def process_homepage_jobs(driver):
    """Process recommended jobs on the Indeed homepage before searching."""
    global main_window_handle

    log.info("")
    log.info("=" * 60)
    log.info("PROCESSING HOMEPAGE RECOMMENDED JOBS")
    log.info("=" * 60)

    homepage_selectors = [
        'div.job_seen_beacon',
        ".mosaic-provider-jobcards .tapItem",
        'a[data-jk]',
        'div[data-testid="slider_item"]',
        ".resultContent",
        'div.jobsearch-ResultsList div.cardOutline',
        'div[data-testid="job-card"]',
        'div.css-zu9cdh',
    ]

    scroll_rounds = 0
    max_scroll_rounds = 8
    processed_count = 0

    while scroll_rounds < max_scroll_rounds:
        cards = []
        for sel in homepage_selectors:
            try:
                found = driver.find_elements(By.CSS_SELECTOR, sel)
                if found:
                    cards = found
                    break
            except Exception:
                continue

        total_on_page = len(cards)
        if total_on_page == 0 and scroll_rounds == 0:
            log.info("    No recommended jobs found on homepage. Moving to search.")
            return

        log.info(f"    Found {total_on_page} job cards on homepage (scroll round {scroll_rounds + 1})")

        for idx in range(processed_count, total_on_page):
            try:
                ensure_main_window(driver)
            except InvalidSessionIdException:
                raise
            except Exception:
                break

            try:
                cards = []
                for sel in homepage_selectors:
                    try:
                        found = driver.find_elements(By.CSS_SELECTOR, sel)
                        if found:
                            cards = found
                            break
                    except Exception:
                        continue
                if idx >= len(cards):
                    break
                card = cards[idx]
            except Exception:
                continue

            process_job_card(driver, card, idx, total_on_page, label=" [HOME]", skip_title_filter=True)

        processed_count = total_on_page

        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(random.uniform(0.5, 1.0))
        time.sleep(random.uniform(1.0, 2.0))

        new_cards = []
        for sel in homepage_selectors:
            try:
                found = driver.find_elements(By.CSS_SELECTOR, sel)
                if found:
                    new_cards = found
                    break
            except Exception:
                continue

        if len(new_cards) <= total_on_page:
            log.info("    No more jobs loading on homepage. Done with homepage.")
            break

        scroll_rounds += 1

    log.info(f"    Homepage processing complete.")
    log.info("")


def run_search(driver, query: str, location: str, max_pages: int):
    global main_window_handle

    log.info("")
    log.info("=" * 60)
    log.info(f'SEARCHING: "{query}" in "{location}" -- {max_pages} pages')
    log.info("=" * 60)

    for page in range(max_pages):
        start = page * 10
        url = build_search_url(query, location, start)

        ensure_main_window(driver)
        try:
            driver.get(url)
        except InvalidSessionIdException:
            raise
        except Exception as e:
            log.error(f"Failed to load search page: {e}")
            continue
        wait_for_page_ready(driver)
        wait(page_load_delay)
        close_popups(driver)
        human_scroll(driver)
        random_mouse_jiggle(driver)

        log.info("")
        log.info(f"--- Page {page + 1}/{max_pages} for \"{query}\" in \"{location}\" ---")

        job_cards = get_job_cards(driver)
        total_on_page = len(job_cards)
        log.info(f"    {total_on_page} job cards found.")

        if not job_cards:
            log.warning("    No jobs on this page. Moving on.")
            break

        for idx in range(total_on_page):
            try:
                ensure_main_window(driver)
            except InvalidSessionIdException:
                raise
            except Exception:
                break

            try:
                job_cards = get_job_cards(driver)
                if idx >= len(job_cards):
                    break
                card = job_cards[idx]
            except Exception:
                continue

            process_job_card(driver, card, idx, total_on_page)

        log.info(f"--- Done with page {page + 1}/{max_pages} ---")

    log.info(f'Search complete: "{query}" in "{location}"')


# ══════════════════════════════════════════════
# SIGNAL FILE WAIT (no stdin needed)
# ══════════════════════════════════════════════

def find_indeed_tab(driver) -> bool:
    for handle in driver.window_handles:
        try:
            driver.switch_to.window(handle)
            if "indeed.com" in driver.current_url.lower():
                return True
        except Exception:
            continue
    return False


def main():
    global main_window_handle

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    log.info("Launching Chrome...")
    driver = uc.Chrome(options=options, use_subprocess=True)

    log.info("")
    log.info("=" * 60)
    log.info("  INDEED AUTO-APPLIER -- Chrome is open")
    log.info("=" * 60)
    log.info("  You have 40 seconds to go to indeed.com and log in.")
    log.info("  Script takes over automatically after that.")
    log.info("=" * 60)
    log.info("")

    for i in range(40, 0, -5):
        log.info(f"  Starting in {i} seconds...")
        time.sleep(5)

    log.info("  TIME'S UP -- taking over now!")
    log.info("")

    if not find_indeed_tab(driver):
        log.warning("No Indeed tab found. Waiting 15 more seconds...")
        for _ in range(5):
            time.sleep(3)
            if find_indeed_tab(driver):
                break
        if not find_indeed_tab(driver):
            log.error("No Indeed tab found. Exiting.")
            return

    main_window_handle = driver.current_window_handle
    log.info(f"Found Indeed: {driver.current_url}")

    close_popups(driver)

    # First: apply to recommended jobs on the homepage
    try:
        process_homepage_jobs(driver)
    except InvalidSessionIdException:
        log.error("Browser session died during homepage processing.")
        return
    except Exception as e:
        log.error(f"Error processing homepage jobs: {e}")

    # Then: run the search queries
    log.info(f"Searches: {len(search_queries)}")
    for i, (q, l, p) in enumerate(search_queries, 1):
        log.info(f"  {i}. \"{q}\" in \"{l}\" ({p} pages)")
    log.info("")

    for query, location, max_pages in search_queries:
        try:
            run_search(driver, query, location, max_pages)
# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

        except InvalidSessionIdException:
            log.error("Browser session died. Cannot continue.")
            break
        except Exception as e:
            log.error(f"Search error for '{query}' in '{location}': {e}")
            stats["errors"] += 1
            try:
                ensure_main_window(driver)
            except Exception:
                pass
            continue

    log.info("")
    log.info("=" * 60)
    log.info("ALL DONE")
    log.info(f"  Applications submitted:      {stats['applied']}")
    log.info(f"  Skipped (wrong title):       {stats['skipped_title']}")
    log.info(f"  Skipped (no Indeed Apply):    {stats['skipped_no_btn']}")
    log.info(f"  Skipped (already applied):    {stats['skipped_already']}")
    log.info(f"  Left open for you (external): {stats['left_open']}")
    log.info(f"  Errors:                       {stats['errors']}")
    log.info("=" * 60)

    try:
        open_tabs = len(driver.window_handles) - 1
        if open_tabs > 0:
            log.info(f"  {open_tabs} external tab(s) open for you to fill in.")
    except Exception:
        pass

    log.info(f"Log saved to: {log_filename}")
    log.info("Browser stays open. Close it manually when done.")


if __name__ == "__main__":
    main()
