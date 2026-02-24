import random

# ──────────────────────────────────────────────
# SEARCH QUERIES — (search_term, location, max_pages)
# ──────────────────────────────────────────────
search_queries = [
    ("machine learning engineer", "Florida", 3),
    ("AI engineer", "Florida", 3),
    ("software engineer AI", "Florida", 3),
    ("data scientist", "Florida", 3),
    ("python developer", "Florida", 3),
    ("data engineer", "Florida", 3),
    ("software engineer", "Boca Raton, FL", 3),
    ("software engineer", "Miami, FL", 3),
    ("cloud engineer", "Florida", 3),
    ("ServiceNow developer", "Florida", 3),
    ("integration engineer", "Florida", 3),
    ("automation engineer", "Florida", 3),
    ("system administrator", "Florida", 3),
    ("machine learning engineer", "Remote", 3),
    ("AI engineer", "Remote", 3),
    ("software engineer", "Remote", 3),
    ("python developer", "Remote", 3),
    ("data scientist", "Remote", 3),
    ("data engineer", "Remote", 3),
    ("cloud engineer", "Remote", 3),
    ("ServiceNow developer", "Remote", 3),
    ("integration engineer", "Remote", 3),
    ("automation engineer", "Remote", 3),
    ("system administrator", "Remote", 3),
    ("machine learning engineer", "United States", 3),
    ("artificial intelligence engineer", "United States", 3),
    ("cloud engineer", "United States", 3),
    ("ServiceNow developer", "United States", 3),
    ("system administrator", "United States", 3),
    ("data scientist", "United States", 3),
    ("data engineer", "United States", 3),
]

# Jobs to SKIP even if title keywords match
title_blacklist = [
    "nurse", "dentist", "dental", "therapist", "physician", "pharmacist",
    "veterinary", "surgeon", "hr ", "human resources", "recruiter", "recruiting",
    "sales rep", "account executive", "business development", "marketing director",
    "teacher", "teaching", "instructor", "professor", "tutor", "bookkeep",
    "accounting", "accountant", "mechanic", "electrician", "plumber", "hvac",
    "roof", "construction", "driver", "warehouse", "forklift", "custodian",
    "security guard", "dispatcher", "call center", "administrative", "receptionist",
    "real estate", "chef", "cook", "restaurant", "bartender", "barista",
]

company_blacklist = [
    "adnet systems", "adnet",
]

title_keywords = [
    "ai", "artificial intelligence", "ml", "machine learning", "deep learning",
    "nlp", "natural language", "computer vision", "data scientist", "llm",
    "generative ai", "gen ai", "mlops", "ml ops",
    "software engineer", "software developer", "full stack", "fullstack", "full-stack",
    "backend engineer", "frontend engineer", "python developer", "python engineer",
    "java developer", "java engineer", "cloud engineer", "devops", "devops engineer",
    "platform engineer", "infrastructure engineer", "site reliability", "sre",
    "data engineer", "data platform", "solutions architect", "systems engineer",
    "application developer", "applications engineer", "automation engineer",
    "qa engineer", "sdet", "cloud", "aws", "azure", "gcp",
    "servicenow", "service now", "integration engineer", "integration specialist",
    "system admin", "systems admin", "sysadmin", "system administrator",
    "systems administrator", "network engineer", "security engineer", "cybersecurity",
]

# ──────────────────────────────────────────────
# TIMING
# ──────────────────────────────────────────────
def human_delay(low=0.6, high=1.8):
    return random.uniform(low, high)

def typing_delay():
    return random.uniform(0.02, 0.07)

page_load_delay = (1.2, 2.5)
between_jobs_delay = (0.8, 2.0)
form_field_delay = (0.3, 0.8)
after_submit_delay = (5.0, 7.0)
scroll_delay = (0.2, 0.5)

# ──────────────────────────────────────────────
# RESUME
# ──────────────────────────────────────────────
resume_path = r"C:\Users\sfdrn\OneDrive\Desktop\Safdar_Nizam.pdf"

# ──────────────────────────────────────────────
# PERSONAL
# ──────────────────────────────────────────────
add_firstname = "Safdar"
add_lastname = "Nizam"
add_phone = "5615524957"
add_email = "safdarnizam28@gmail.com"
add_address = "581 Lavers Cir"
add_city = "Delray Beach"
add_state = "FL"
add_postal = "33444"
add_country = "US"

add_linkedin = "https://www.linkedin.com/in/safdarnizam/"
add_github = ""
add_portfolio = ""

add_university = "Florida Atlantic University"
add_education = "Master"
add_degree = "Master of Computer Science"
add_graduation_year = "2025"

add_workauthorized = "Yes"
add_citizen = "Yes"
add_sponsorship = "No"
add_relocate = "Yes"
add_commute = "Yes"
add_commute2 = "Yes"
add_criminal = "No"
add_DBS = "Yes"
add_valid_cert = "Yes"

add_available = "Yes"
add_shift = "Day shift"
add_interview_dates = "Available immediately"
add_salary = "113000"

add_gender = "Male"
add_veteran = "No"
add_disability = "No"

add_company = "Help Us Grow"
add_pronouns = "He/Him"
add_race = "Asian"

# ──────────────────────────────────────────────
# EXPERIENCE
# ──────────────────────────────────────────────
experience_map = {
    "python": "5", "java": "4", "javascript": "4", "sql": "4", "aws": "4",
    "machine learning": "4", "deep learning": "4", "ai": "4", "data": "4",
    "software": "4", "engineering": "4", "programming": "5", "docker": "4",
}
add_default_experience = "4"
default_unknown_multi = "Yes"
