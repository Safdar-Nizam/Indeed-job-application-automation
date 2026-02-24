import random

# ──────────────────────────────────────────────
# SEARCH QUERIES — (search_term, location, max_pages)
# ──────────────────────────────────────────────
search_queries = [
    ("software engineer", "New York, NY", 3),
    ("data scientist", "Remote", 3),
    ("python developer", "California", 3),
    ("machine learning engineer", "Remote", 3),
    ("cloud engineer", "United States", 3),
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
    # Add companies you want to skip, e.g.:
    # "scam company inc",
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
resume_path = r"C:\path\to\your\Resume.pdf"

# ──────────────────────────────────────────────
# PERSONAL
# ──────────────────────────────────────────────
add_firstname = "John"
add_lastname = "Doe"
add_phone = "5551234567"
add_email = "john.doe@email.com"
add_address = "123 Main Street"
add_city = "New York"
add_state = "NY"
add_postal = "10001"
add_country = "US"

add_linkedin = "https://www.linkedin.com/in/johndoe/"
add_github = ""
add_portfolio = ""

add_university = "Your University"
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
add_salary = "120000"

add_gender = "Male"
add_veteran = "No"
add_disability = "No"

add_company = "Your Current Company"
add_pronouns = "He/Him"
add_race = "Your Race"

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
