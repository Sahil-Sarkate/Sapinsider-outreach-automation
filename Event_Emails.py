"""
=============================================================
  SAPinsider Las Vegas 2026 — Email Outreach Automation
  Author: Sahil Sarkate
  Tools: Hunter.io (contact finder) + Outlook SMTP (sender)
=============================================================

HOW TO RUN:
  1. Fill in your credentials in the CONFIG section below
  2. Install dependencies:  pip install requests
  3. Run: python sapinsider_email_automation.py

The script will:
  - Search Hunter.io for SAP/recruiting contacts at each company
  - Send your personalized email to each found contact
  - Log everything to sapinsider_tracker.csv
  - Send max 5 emails/day (safe limit to avoid spam filters)
  - Skip companies already contacted on previous runs
=============================================================
"""

import smtplib
import requests
import csv
import os
import time
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =============================================================
#  CONFIG — FILL THESE IN BEFORE RUNNING
# =============================================================
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")   # reads from .env
OUTLOOK_EMAIL  = os.getenv("GMAIL_EMAIL")        # reads from .env
OUTLOOK_PASSWORD = os.getenv("GMAIL_PASSWORD")   # reads from .env

EMAILS_PER_DAY   = 7      # Max emails to send per run (keep at 5 to avoid spam)
DELAY_BETWEEN    = 60     # Seconds between each email (60 = 1 minute gap)
LOG_FILE         = "sapinsider_tracker.csv"

# Job titles to search for at each company (in priority order)
TARGET_TITLES = [
    "SAP Practice Manager",
    "SAP Alliance Manager",
    "University Relations",
    "Campus Recruiter",
    "Talent Acquisition",
    "Recruiter",
    "SAP Consultant",
    "Events Manager",
    "Marketing Manager",
]

# =============================================================
#  COMPANY LIST — All 77 SAPinsider Sponsors
# =============================================================

COMPANIES = [
    # company_name, domain, tier
    ("KPMG",                     "kpmg.com",                "Double Platinum"),
    ("Onapsis",                  "onapsis.com",             "Double Platinum"),
    ("SAP",                      "sap.com",                 "Double Platinum"),
    ("Serrala",                  "serrala.com",             "Double Platinum"),
    ("YASH Technologies",        "yash.com",                "Double Platinum"),
    ("Avantra",                  "avantra.com",             "Platinum"),
    ("Boomi",                    "boomi.com",               "Platinum"),
    ("Insight Software",         "insightsoftware.com",     "Platinum"),
    ("Lemongrass",               "lemongrassconsulting.com","Platinum"),
    ("Pathlock",                 "pathlock.com",            "Platinum"),
    ("Protiviti",                "protiviti.com",           "Platinum"),
    ("PwC",                      "pwc.com",                 "Platinum"),
    ("Red Hat",                  "redhat.com",              "Platinum"),
    ("SUSE",                     "suse.com",                "Platinum"),
    ("Thomson Reuters",          "thomsonreuters.com",      "Platinum"),
    ("Tricentis",                "tricentis.com",           "Platinum"),
    ("CCH Tagetik",              "cchtagetik.com",          "Platinum"),
    ("xSuite",                   "xsuite.com",              "Platinum"),
    ("Accenture",                "accenture.com",           "Gold"),
    ("Basis Technologies",       "basistechnologies.com",   "Gold"),
    ("Delego",                   "delego.com",              "Gold"),
    ("EPI-USE Labs",             "epiuselabs.com",          "Gold"),
    ("IBM",                      "ibm.com",                 "Gold"),
    ("LRS Output Management",    "lrs.com",                 "Gold"),
    ("MYGO Consulting",          "mygoconsulting.com",      "Gold"),
    ("Neptune Software",         "neptune-software.com",    "Gold"),
    ("Redwood Software",         "redwood.com",             "Gold"),
    ("Saviynt",                  "saviynt.com",             "Gold"),
    ("Security Bridge",          "securitybridge.com",      "Gold"),
    ("Sovos",                    "sovos.com",               "Gold"),
    ("Vertex",                   "vertexinc.com",           "Gold"),
    ("VisionSoft",               "visionsoft.com",          "Gold"),
    ("Zscaler",                  "zscaler.com",             "Gold"),
    ("AiFA Labs",                "aifalabs.com",            "Silver"),
    ("Allevo",                   "allevo.ro",               "Silver"),
    ("Apiphani",                 "apiphani.com",            "Silver"),
    ("Arch",                     "archconsulting.com",      "Silver"),
    ("CBS",                      "cbs.de",                  "Silver"),
    ("Crave Infotech",           "craveinfotech.com",       "Silver"),
    ("Customer Advisory Group",  "customeradvisorygroup.com","Silver"),
    ("Dataglobal",               "dataglobal.com",          "Silver"),
    ("Delta IT",                 "delta-it.de",             "Silver"),
    ("Fastpath",                 "gofastpath.com",          "Silver"),
    ("Fujitsu",                  "fujitsu.com",             "Silver"),
    ("HGS Teklink",              "hgsteklink.com",          "Silver"),
    ("Horvath",                  "horvath-partners.com",    "Silver"),
    ("ITing",                    "iting.com",               "Silver"),
    ("Kyriba",                   "kyriba.com",              "Silver"),
    ("Libelle",                  "libelle.com",             "Silver"),
    ("McKinsol NeuVays",         "mckinsol.com",            "Silver"),
    ("Nagarro",                  "nagarro.com",             "Silver"),
    ("NextLabs",                 "nextlabs.com",            "Silver"),
    ("Nuvo",                     "getnuvo.com",             "Silver"),
    ("PBS Software Americas",    "pbssoftware.com",         "Silver"),
    ("Protera",                  "protera.com",             "Silver"),
    ("QSandS",                   "qsands.com",              "Silver"),
    ("Reply Syskoplan",          "reply.com",               "Silver"),
    ("Resulting IT",             "resultingit.com",         "Silver"),
    ("RFgen",                    "rfgen.com",               "Silver"),
    ("Roiable",                  "roiable.com",             "Silver"),
    ("SimpleFI",                 "simplefi.io",             "Silver"),
    ("SimpleMDG",                "simplemdg.com",           "Silver"),
    ("TCS",                      "tcs.com",                 "Silver"),
    ("Titan Consulting",         "titanconsulting.net",     "Silver"),
    ("The Silicon Partners",     "thesiliconpartners.com",  "Silver"),
    ("Trintech",                 "trintech.com",            "Silver"),
    ("TruQua",                   "truqua.com",              "Silver"),
    ("Turnkey Consulting",       "turnkeyconsulting.com",   "Silver"),
    ("Voquz Labs",               "voquz.com",               "Silver"),
    ("Whatfix",                  "whatfix.com",             "Silver"),
    ("Worksoft",                 "worksoft.com",            "Silver"),
    ("Worldpay",                 "worldpay.com",            "Silver"),
    ("Zoho",                     "zoho.com",                "Silver"),
    ("HPE",                      "hpe.com",                 "Pavilion"),
    ("Nova Intelligence",        "nova-intelligence.com",   "Pavilion"),
    ("Syniti",                   "syniti.com",              "Pavilion"),
]

# =============================================================
#  EMAIL TEMPLATES — Personalized per company tier
# =============================================================

def get_email(company_name, tier, first_name="there"):
    subject = f"Request for Conference Ticket Sponsorship – SAPinsider Las Vegas 2026"

    # Greeting
    greeting = f"Dear {first_name},"

    # Tier-specific opener
    openers = {
        "Double Platinum": f"I noticed {company_name} is a Double Platinum sponsor at SAPinsider Las Vegas 2026 — that's a significant investment in the SAP community, which is exactly why I'm reaching out.",
        "Platinum":        f"I noticed {company_name} is a Platinum sponsor at SAPinsider Las Vegas 2026 and wanted to reach out directly.",
        "Gold":            f"I came across {company_name}'s sponsorship of SAPinsider Las Vegas 2026 and wanted to connect.",
        "Silver":          f"I saw {company_name} is sponsoring SAPinsider Las Vegas 2026 and wanted to reach out.",
        "Pavilion":        f"I saw {company_name} will be at SAPinsider Las Vegas 2026 and wanted to connect before the event.",
    }
    opener = openers.get(tier, openers["Silver"])

    body = f"""{greeting}

My name is Sahil Sarkate. I am a graduate student at Illinois Institute of Technology pursuing my Master's in Information Technology Management (GPA: 3.55), graduating May 2026, with 2+ years of hands-on SAP S/4HANA experience in procurement configuration, MM-FI integration, master data governance, and LSMW data migration.

{opener}

I am writing to request a sponsored ticket to SAPinsider Las Vegas 2026 (March 16-19, Bellagio). The conference's sessions on SAP S/4HANA transformation, ERP modernization, and enterprise data management are directly aligned with my professional development, and attending would give me the opportunity to connect with {company_name}'s team in person.

As a full-time student, the registration fee is beyond my current budget. In return for your sponsorship, I would be happy to:
- Visit your booth and engage with your team throughout the event
- Promote {company_name}'s presence and insights on LinkedIn to my network
- Share key takeaways from your sessions with my peer community

I would also love to learn more about career opportunities and what a path at {company_name} looks like for someone with my background.

Thank you sincerely for your time and consideration. I hope to have the opportunity to connect at the event.

Warm regards,
Sahil Sarkate
Illinois Institute of Technology | M.S. Information Technology Management (May 2026)
SAP S/4HANA Consultant | 2+ Years Experience
(312) 358-9304 | ssarkate@hawk.illinoistech.edu
linkedin.com/in/sahil-sarkate"""

    return subject, body


# =============================================================
#  HUNTER.IO — Find contacts by company domain
# =============================================================

def find_contact(domain, company_name):
    """
    Search Hunter.io for a contact at the given domain.
    Returns (first_name, last_name, email) or None if not found.
    """
    print(f"  🔍 Searching Hunter.io for contacts at {domain}...")

    # Try domain search first (finds all emails at the domain)
    url = "https://api.hunter.io/v2/domain-search"
    params = {
        "domain":  domain,
        "api_key": HUNTER_API_KEY,
        "limit":   10,
        "type":    "personal",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if response.status_code != 200:
            print(f"  ⚠️  Hunter API error: {data.get('errors', 'Unknown error')}")
            return None

        emails = data.get("data", {}).get("emails", [])
        if not emails:
            print(f"  ⚠️  No emails found for {domain}")
            return None

        # Priority scoring: prefer SAP/recruiting/events roles
        priority_keywords = [
            "sap", "recruiter", "recruiting", "talent", "university",
            "alliance", "partner", "events", "marketing", "hr",
            "practice", "consulting", "manager", "director"
        ]

        best = None
        best_score = -1

        for contact in emails:
            if not contact.get("value"):
                continue
            pos = (contact.get("position") or "").lower()
            score = sum(1 for kw in priority_keywords if kw in pos)
            if score > best_score:
                best_score = score
                best = contact

        # Fall back to first contact if no keyword match
        if not best and emails:
            best = emails[0]

        if best:
            fname = best.get("first_name") or "there"
            lname = best.get("last_name") or ""
            email = best.get("value")
            pos   = best.get("position") or "N/A"
            print(f"  ✅ Found: {fname} {lname} | {pos} | {email}")
            return fname, lname, email

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Network error for {domain}: {e}")

    return None


def find_contact_by_email_finder(domain, company_name):
    """
    Fallback: use Hunter.io email finder with a generic name search.
    """
    print(f"  🔍 Trying email finder fallback for {domain}...")
    url = "https://api.hunter.io/v2/email-finder"
    params = {
        "domain":     domain,
        "first_name": "hr",
        "last_name":  "recruiter",
        "api_key":    HUNTER_API_KEY,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        email = data.get("data", {}).get("email")
        if email:
            print(f"  ✅ Found via finder: {email}")
            return "there", "", email
    except:
        pass
    return None


# =============================================================
#  EMAIL SENDER — Outlook SMTP
# =============================================================

def send_email(to_email, subject, body, from_name="Sahil Sarkate"):
    """Send email via Outlook SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{OUTLOOK_EMAIL}>"
    msg["To"]      = to_email

    # Plain text version
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
            server.sendmail(OUTLOOK_EMAIL, to_email, msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError:
        print("  ❌ Authentication failed! Check your email/app password.")
        return False
    except smtplib.SMTPException as e:
        print(f"  ❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


# =============================================================
#  TRACKER — CSV log of all contacts and statuses
# =============================================================

def load_tracker():
    """Load existing tracker CSV to know who was already contacted."""
    contacted = set()
    if not os.path.exists(LOG_FILE):
        return contacted
    with open(LOG_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("status") in ("sent", "no_email_found"):
                contacted.add(row["company"])
    return contacted


def log_result(company, tier, contact_name, contact_email, status, notes=""):
    """Append a result row to the tracker CSV."""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["timestamp", "company", "tier", "contact_name",
                      "contact_email", "status", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "company":       company,
            "tier":          tier,
            "contact_name":  contact_name,
            "contact_email": contact_email,
            "status":        status,
            "notes":         notes,
        })


# =============================================================
#  MAIN — Run the automation
# =============================================================

def check_config():
    """Validate config before running."""
    errors = []
    if OUTLOOK_EMAIL == "YOUR_EMAIL@outlook.com":
        errors.append("❌ OUTLOOK_EMAIL not set in CONFIG section")
    if OUTLOOK_PASSWORD == "YOUR_APP_PASSWORD_HERE":
        errors.append("❌ OUTLOOK_PASSWORD not set in CONFIG section")
    if not HUNTER_API_KEY:
        errors.append("❌ HUNTER_API_KEY not set")
    if errors:
        print("\n" + "="*60)
        print("SETUP REQUIRED — Please fill in your credentials:")
        for e in errors:
            print(e)
        print("\nOpen this script and fill in the CONFIG section at the top.")
        print("="*60 + "\n")
        return False
    return True


def check_hunter_credits():
    """Check remaining Hunter.io search credits."""
    try:
        url = f"https://api.hunter.io/v2/account?api_key={HUNTER_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        searches = data["data"]["requests"]["searches"]
        used      = searches["used"]
        available = searches["available"]
        print(f"  Hunter.io Credits — Used: {used} | Available: {available}")
        return available
    except Exception as e:
        print(f"  ⚠️  Could not check Hunter.io credits: {e}")
        return 999  # assume available


def run():
    print("\n" + "="*60)
    print("  SAPinsider Las Vegas 2026 — Email Automation")
    print("  By Sahil Sarkate")
    print("="*60)

    # Check config
    if not check_config():
        return

    # Check Hunter credits
    print("\n📊 Checking Hunter.io account...")
    credits = check_hunter_credits()
    if credits < 5:
        print(f"\n⚠️  Only {credits} Hunter.io searches remaining!")
        print("   Visit hunter.io to upgrade or wait for monthly reset.")
        return

    # Load tracker
    already_contacted = load_tracker()
    print(f"\n📋 Already contacted: {len(already_contacted)} companies")
    print(f"📋 Remaining: {len(COMPANIES) - len(already_contacted)} companies")
    print(f"📋 Sending today: max {EMAILS_PER_DAY} emails\n")

    # Filter out already contacted
    pending = [(name, domain, tier) for name, domain, tier in COMPANIES
               if name not in already_contacted]

    if not pending:
        print("✅ All companies have been contacted! Check sapinsider_tracker.csv for results.")
        return

    sent_count = 0

    for company_name, domain, tier in pending:
        if sent_count >= EMAILS_PER_DAY:
            remaining = len(pending) - sent_count
            print(f"\n⏸️  Daily limit of {EMAILS_PER_DAY} reached.")
            print(f"   Run again tomorrow to contact the remaining {remaining} companies.")
            break

        print(f"\n{'='*50}")
        print(f"[{sent_count+1}/{EMAILS_PER_DAY}] {company_name} ({tier})")
        print(f"  Domain: {domain}")

        # Find contact via Hunter.io
        result = find_contact(domain, company_name)

        # Try fallback if primary search fails
        if not result:
            result = find_contact_by_email_finder(domain, company_name)

        if not result:
            print(f"  ⚠️  No contact found for {company_name} — logging and skipping.")
            log_result(company_name, tier, "N/A", "N/A", "no_email_found",
                       "Hunter.io returned no results")
            continue

        first_name, last_name, contact_email = result
        full_name = f"{first_name} {last_name}".strip()

        # Build personalized email
        subject, body = get_email(company_name, tier, first_name)

        # Send email
        print(f"  📧 Sending to: {full_name} <{contact_email}>...")
        success = send_email(contact_email, subject, body)

        if success:
            print(f"  ✅ Email sent successfully!")
            log_result(company_name, tier, full_name, contact_email, "sent")
            sent_count += 1
        else:
            print(f"  ❌ Failed to send — check credentials.")
            log_result(company_name, tier, full_name, contact_email, "failed",
                       "SMTP send failed")
            break  # Stop if auth fails to avoid lockout

        # Rate limit delay
        if sent_count < EMAILS_PER_DAY and sent_count < len(pending):
            print(f"  ⏳ Waiting {DELAY_BETWEEN} seconds before next email...")
            time.sleep(DELAY_BETWEEN)

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ SESSION COMPLETE")
    print(f"   Emails sent this session: {sent_count}")
    print(f"   Log file: {LOG_FILE}")
    print(f"   Run again tomorrow to continue with remaining companies.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()