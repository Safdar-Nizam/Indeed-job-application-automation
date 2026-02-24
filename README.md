<p align="center">
  <img src="assets/banner.png" alt="Indeed Job Application Automation" width="800"/>
</p>

<h1 align="center">🤖 Indeed Job Application Automation</h1>

<p align="center">
  <b>An intelligent bot that automatically searches for jobs on Indeed and submits applications on your behalf — hands-free.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/selenium-4.x-green?logo=selenium&logoColor=white" alt="Selenium"/>
  <img src="https://img.shields.io/badge/chrome-undetected-orange?logo=googlechrome&logoColor=white" alt="Chrome"/>
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey?logo=windows&logoColor=white" alt="Platform"/>
  <img src="https://img.shields.io/badge/license-MIT-purple" alt="License"/>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Logs & Monitoring](#-logs--monitoring)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#-disclaimer)

---

## 🔍 Overview

Applying to jobs is exhausting. You spend hours clicking the same buttons, filling out the same forms, and uploading the same resume — over and over again.

**This bot automates the entire Indeed "Easy Apply" workflow.** You configure it once with your personal details, target job titles, and preferred locations, then let it run. It will:

1. Open Chrome and wait for you to log in to Indeed
2. Apply to **every job** on your Indeed homepage (no filtering)
3. Search for jobs using your configured queries
4. Filter results by title keywords and company blacklists
5. Click "Apply Now", fill out every form field intelligently, upload your resume, and submit

All while mimicking human behavior to avoid detection.

---

## ✨ Features

### 🎯 Smart Job Targeting
- **Homepage sweep** — applies to ALL recommended jobs on your Indeed homepage before starting searches
- **Multi-query search** — runs multiple search queries across different locations
- **Title filtering** — only applies to jobs matching your target keywords (during search phase)
- **Blacklists** — skip specific job titles or companies you want to avoid
- **Date sorting** — prioritizes the newest job postings

### 🧠 Intelligent Form Filling
- **Context-aware answers** — recognizes questions about name, phone, city, email, address, salary, company, pronouns, race, etc. and fills them with YOUR configured data
- **Smart dropdown selection** — correctly picks your state (not just the first option), country, education level, gender, veteran status, and more
- **Experience matching** — maps technology keywords to your years of experience (e.g., "Python" → "5 years")
- **Date field detection** — identifies date inputs and fills them with proper `MM/DD/YYYY` format instead of garbage values
- **Radio/checkbox intelligence** — answers Yes/No questions based on keyword matching (work authorization, sponsorship, criminal background, etc.)
- **Dynamic question handling** — re-scans the page up to 3 times to catch follow-up questions that appear after previous selections
- **Last-resort field identification** — even when a question container isn't recognized, examines HTML attributes (`name`, `id`, `placeholder`, `aria-label`) to identify what the field is asking for

### 🤖 Human-Mimicking Behavior
- **Randomized delays** — every click, scroll, and keystroke has randomized timing
- **Character-by-character typing** — types into fields one character at a time at human speed
- **Mouse jiggling** — randomly moves the mouse to simulate human presence
- **Smooth scrolling** — scrolls pages in natural increments
- **Undetected Chrome** — uses `undetected-chromedriver` to bypass bot detection

### 🔄 Robust Application Flow
- **Multi-page form navigation** — handles Continue/Next buttons across unlimited form pages
- **Resume upload** — automatically uploads your PDF resume on every page that has a file input
- **Review page patience** — waits 5-8 seconds on review/confirmation pages instead of rushing
- **Submission verification** — checks for confirmation messages after submitting
- **Already-applied detection** — skips jobs you've already applied to
- **External redirect handling** — leaves external application tabs open for you to fill manually
- **Anti-stuck protection** — detects when stuck on a page and moves on gracefully
- **Session recovery** — handles window/tab management and recovers from navigation errors

### 📊 Detailed Logging
- Every action is logged to both the console and a timestamped log file
- End-of-run statistics: applications submitted, skipped counts, errors, external tabs left open

---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    STARTUP SEQUENCE                         │
│  1. Launch Chrome (undetected)                              │
│  2. Wait 40 seconds for you to log in to Indeed             │
│  3. Find the Indeed tab                                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 HOMEPAGE PHASE                              │
│  • Scrape all recommended job cards                         │
│  • Apply to EVERY job (no title filtering)                  │
│  • Scroll down to load more → repeat up to 8 rounds        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 SEARCH PHASE (per query)                    │
│  For each (search_term, location, max_pages):               │
│  • Build Indeed search URL with filters                     │
│  • For each page of results:                                │
│    ├─ Get all job cards                                     │
│    ├─ Filter by title_keywords and blacklists               │
│    ├─ Click matching jobs → Apply Now                       │
│    └─ Fill forms → Submit                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              APPLICATION FLOW (per job)                     │
│  For each form page (up to 25):                             │
│  1. Upload resume (if file input exists)                    │
│  2. Find all question containers                            │
│  3. Answer each question:                                   │
│     • Text fields → match keywords to your config           │
│     • Date fields → fill MM/DD/YYYY                         │
│     • Radio/checkbox → match keywords to Yes/No answers     │
│     • Dropdowns → smart selection (state, country, etc.)    │
│     • Experience → map technology to years                  │
│  4. Re-scan for dynamic questions (3 passes)                │
│  5. Force-fill any remaining blanks                         │
│  6. Click Continue/Next or Submit                           │
│  7. Verify submission                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

The project consists of three files:

| File | Purpose |
|------|---------|
| **`config.py`** | All your personal data, search queries, job filters, timing settings, and experience mappings. **This is the only file you need to edit.** |
| **`apply.py`** | The main automation engine — browser control, form filling, question answering, search & pagination, application flow. |
| **`launcher.py`** | A tiny wrapper that launches `apply.py` in a detached subprocess (optional convenience script). |

### Key Components in `apply.py`

| Component | What It Does |
|-----------|-------------|
| `KEYWORD_TO_ANSWER` | Maps question keywords → your text answers (name, city, phone, salary, etc.) |
| `CLICK_KEYWORD_TO_ANSWER` | Maps question keywords → click-based answers (Yes/No for authorization, sponsorship, etc.) |
| `answer_question()` | The brain — reads a question, tries text match → date detection → click match → experience match → dropdown → last resort |
| `identify_field_answer()` | Examines HTML attributes to figure out what a mystery field wants |
| `smart_select_dropdown()` | Intelligently picks dropdown options for state, country, education, experience, race, gender, etc. |
| `handle_date_field()` | Detects date inputs and fills with contextually appropriate dates |
| `force_fill_blanks()` | Last-resort sweep for any remaining empty required fields |
| `process_application()` | Walks through multi-page forms, handles review pages, detects stuck states |
| `process_homepage_jobs()` | Scrolls through and applies to homepage recommended jobs |
| `run_search()` | Executes search queries and processes result pages |

---

## 📦 Prerequisites

- **Python 3.9+** — [Download here](https://www.python.org/downloads/)
- **Google Chrome** — Latest version, [download here](https://www.google.com/chrome/)
- **An Indeed account** — You must be logged in before the bot starts
- **Windows OS** — Tested on Windows 10/11 (may work on macOS/Linux with minor adjustments)
- **Your resume** — A PDF file saved locally

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Safdar-Nizam/Indeed-job-application-automation.git
cd Indeed-job-application-automation
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install undetected-chromedriver selenium
```

That's it! Only two packages are needed:

| Package | Purpose |
|---------|---------|
| `undetected-chromedriver` | Launches Chrome in a way that bypasses bot detection |
| `selenium` | Controls the browser — clicking, typing, navigating |

---

## 🔧 Configuration

Open **`config.py`** in any text editor. This is where you personalize everything.

### Search Queries

Define what jobs to search for. Each entry is a tuple of `(search_term, location, max_pages)`:

```python
search_queries = [
    ("software engineer", "New York, NY", 3),
    ("data scientist", "Remote", 5),
    ("python developer", "California", 2),
]
```

- **`search_term`** — The job title or keywords to search
- **`location`** — City, state, "Remote", or country
- **`max_pages`** — How many pages of results to process (each page ≈ 15 jobs)

### Title Keywords & Blacklists

```python
# Only apply to jobs containing these keywords (during search phase)
title_keywords = [
    "software engineer", "data scientist", "python developer",
    "machine learning", "ai", "cloud engineer",
]

# NEVER apply to jobs with these words in the title
title_blacklist = [
    "nurse", "dentist", "sales rep", "teacher",
]

# NEVER apply to these companies
company_blacklist = [
    "scam company inc",
]
```

### Personal Information

Fill in your details. The bot uses these to answer form questions:

```python
# Basic Info
add_firstname = "John"
add_lastname = "Doe"
add_phone = "5551234567"
add_email = "john.doe@email.com"

# Address
add_address = "123 Main Street"
add_city = "New York"
add_state = "NY"
add_postal = "10001"
add_country = "US"

# Links
add_linkedin = "https://www.linkedin.com/in/johndoe/"
add_github = "https://github.com/johndoe"
add_portfolio = "https://johndoe.dev"

# Education
add_university = "MIT"
add_education = "Master"          # Used for dropdown selection
add_degree = "Master of Computer Science"
add_graduation_year = "2024"

# Work Authorization
add_workauthorized = "Yes"
add_citizen = "Yes"
add_sponsorship = "No"            # Do you require sponsorship?
add_relocate = "Yes"
add_commute = "Yes"
add_criminal = "No"

# Availability
add_available = "Yes"
add_shift = "Day shift"
add_interview_dates = "Available immediately"
add_salary = "120000"             # Base salary expectation

# Demographics (for voluntary EEO questions)
add_gender = "Male"
add_veteran = "No"
add_disability = "No"
add_company = "Current Corp"      # Your current/most recent employer
add_pronouns = "He/Him"
add_race = "Asian"
```

### Resume Path

Point to your resume PDF:

```python
resume_path = r"C:\Users\YourName\Desktop\Resume.pdf"
```

> **Tip:** Use a raw string (`r"..."`) on Windows to avoid issues with backslashes.

### Experience Mapping

Map technologies to your years of experience. When the bot sees "How many years of Python experience?", it looks up the answer here:

```python
experience_map = {
    "python": "5",
    "java": "4",
    "javascript": "3",
    "aws": "4",
    "machine learning": "4",
    "docker": "3",
}
add_default_experience = "4"  # Fallback for unknown technologies
```

### Timing Settings

Adjust how fast the bot operates. Slower = more human-like but takes longer:

```python
page_load_delay = (1.2, 2.5)      # Wait after page loads
between_jobs_delay = (0.8, 2.0)    # Wait between processing jobs
form_field_delay = (0.3, 0.8)      # Wait before filling each field
after_submit_delay = (5.0, 7.0)    # Wait after submitting
scroll_delay = (0.2, 0.5)          # Wait after scrolling
```

---

## ▶️ Usage

### Step 1: Start the Bot

```bash
cd Indeed-job-application-automation
python apply.py
```

Or use the launcher (runs in background):

```bash
python launcher.py
```

### Step 2: Log In to Indeed

When Chrome opens, you have **40 seconds** to:

1. Navigate to [indeed.com](https://www.indeed.com)
2. Log in with your Indeed account
3. Make sure you're on the Indeed homepage

The countdown is displayed in the console:

```
  INDEED AUTO-APPLIER -- Chrome is open
  You have 40 seconds to go to indeed.com and log in.
  Script takes over automatically after that.

  Starting in 40 seconds...
  Starting in 35 seconds...
  ...
  TIME'S UP -- taking over now!
```

### Step 3: Sit Back and Watch

The bot will now:

1. **Process homepage jobs** — apply to every recommended job
2. **Run search queries** — for each query in your config, search and apply to matching jobs
3. **Leave external applications open** — if a job redirects to an external site, the tab stays open for you

### Step 4: Review Results

When finished, the bot prints a summary:

```
ALL DONE
  Applications submitted:      47
  Skipped (wrong title):       123
  Skipped (no Indeed Apply):   18
  Skipped (already applied):   5
  Left open for you (external): 12
  Errors:                       3
```

The browser stays open so you can fill in any external application tabs.

---

## 📝 Logs & Monitoring

Every run creates a timestamped log file in the project directory:

```
applications_20260224_093454.log
```

The log contains detailed info about every action:

```
2026-02-24 09:34:56  INFO      PROCESSING HOMEPAGE RECOMMENDED JOBS
2026-02-24 09:35:02  INFO        Found 15 job cards on homepage (scroll round 1)
2026-02-24 09:35:05  INFO      [1/15] [HOME] MATCH: "Software Engineer"
2026-02-24 09:35:12  INFO              Resume uploaded.
2026-02-24 09:35:45  INFO              >> Submit clicked. Waiting for confirmation...
2026-02-24 09:35:52  INFO              >> APPLICATION CONFIRMED!
2026-02-24 09:35:52  INFO              Applied to: "Software Engineer"
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Chrome doesn't open** | Make sure Chrome is installed and up to date. Try `pip install --upgrade undetected-chromedriver`. |
| **"No Indeed tab found"** | You need to navigate to indeed.com and log in within 40 seconds. |
| **Bot puts "4" everywhere** | Make sure your `config.py` personal info is filled in correctly. The bot matches question keywords to your config values. |
| **Wrong state selected** | Update `add_state` in `config.py` to your state abbreviation (e.g., "FL", "NY", "CA"). |
| **Bot gets stuck on review page** | This is handled automatically — it waits up to 15 cycles. If it happens consistently, increase `max_stuck` in `process_application()`. |
| **Bot skips jobs I want** | Add more keywords to `title_keywords` in `config.py`. Note: homepage jobs are NOT filtered. |
| **External site applications** | Jobs that don't use "Indeed Apply" are left open in separate tabs for you to fill manually. |
| **"Browser session died"** | Chrome crashed or was closed. Restart the script. |
| **CAPTCHA appears** | Solve it manually. The bot waits if the page doesn't change. |

---

## ⚠️ Disclaimer

> **This tool is for educational and personal use only.**
>
> - Automated job applications may violate Indeed's Terms of Service. Use at your own risk.
> - The authors are not responsible for any consequences of using this tool, including but not limited to account suspension.
> - Always review applications before submitting them to real employers when possible.
> - Be respectful of employers' time — only apply to jobs you're genuinely interested in and qualified for.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>Built with ☕ and frustration from manually applying to 500+ jobs.</b>
</p>