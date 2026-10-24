# ClinicFlow AI

An AI-powered appointment reminder workflow for clinics. It scores each appointment for no-show risk, lists who staff should phone first, and drafts SMS and email reminders in the patient's language.

All patients in this project are fictional. The project drafts messages only. It does not send anything.

## What is in this folder

| Path | What it is |
|---|---|
| `index.html` | The web application. Open it in any browser, no install needed |
| `python-workflow/app.py` | The batch version of the workflow in Python |
| `python-workflow/sample_appointments.csv` | Fictional sample data |
| `python-workflow/requirements.txt` | Python dependency (`anthropic`) |
| `PROMPTS.md` | All prompts used, with revisions |
| `VIDEO_SCRIPT.md` | Outline for the presentation video |

## Features

- Overview: stats, reminder pipeline, a slot map coloured by no-show risk, a call-first list and an AI morning brief
- Schedule: every appointment with risk score, AI-written SMS and email, planned send times, status tracking, add-appointment form
- Inbox: reads patient replies in any language, finds intent and urgency, drafts a reply, applies changes only after approval
- Waitlist: offers freed slots to matching patients and books them on acceptance
- Automation: reminder timing, call threshold, simulated activity log, estimated impact, CSV export
- About: objectives, where AI is used, limits

## Live web app

https://claude.ai/artifact/QVFBWwQ169ojcj78RPdkxQ (set to "anyone with the link can view" before sharing)

## Run the web app locally

Double-click `index.html`. Without the live AI connection it uses template messages. The risk scoring, call list, status tracking and add-appointment form all work.

## Run the Python workflow

    cd python-workflow
    pip install -r requirements.txt
    python app.py                              # demo mode, no key needed
    ANTHROPIC_API_KEY=your_key python app.py   # live AI mode

Outputs: `reminders_output.json` and `daily_report.md`.

## How risk is scored

Start at 12. Add 22 per missed visit (up to 3), 10 for a first visit, 8 for a routine visit (check-up, cleaning, vaccination, consultation), 6 for a hard-to-attend slot (before 9, after 4 pm, or Monday). Cap at 97. Confirmed appointments are reduced to 30 percent of their score. Scores of 55 or more go on the call-first list.

## Privacy choices

Only first name, doctor, time, patient instructions and language are sent to the AI. Phone numbers, emails, visit types and staff notes are never sent, and messages never name a diagnosis or visit type.
