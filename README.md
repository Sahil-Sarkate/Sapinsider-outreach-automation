## 🎯 Project Objective

SAPinsider Las Vegas 2026 is one of the most significant SAP conferences
of the year (March 16-19, Bellagio, Las Vegas). As a full-time graduate
student, the registration fee was not feasible.

Instead of giving up, I built this end-to-end outreach automation system
to connect directly with conference sponsors and request a sponsored ticket
while simultaneously demonstrating the kind of technical and domain skills
I bring as an SAP consultant and developer.

---

## 🔧 What This Project Does

- Searches **Hunter.io API** to find SAP Practice Managers, Recruiters,
  and Alliance Managers at each sponsoring company
- Sends **fully personalized emails** tailored to each company's specific
  focus area (procurement, data migration, cloud, security, finance, and more)
- Automates sending via **Gmail SMTP** with intelligent rate limiting
  (7 emails/day, 90 second gaps) to avoid spam filters
- Logs every contact, email address, send status, and timestamp to a
  **CSV tracker** stored locally
- **Skips already contacted companies** on re-runs — safe to run daily

---

## 🏢 Scope

- **77 sponsoring companies** covered across 5 tiers
- Double Platinum, Platinum, Gold, Silver, and Pavilion sponsors
- Target contacts: SAP Practice Manager, Recruiter, Alliance Manager,
  University Relations, Events Manager

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Core automation |
| Hunter.io API | Contact discovery by company domain |
| Gmail SMTP | Automated email delivery |
| python-dotenv | Secure credential management |
| CSV | Local outreach tracking and logging |
