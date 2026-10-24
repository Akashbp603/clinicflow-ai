# Prompt documentation - ClinicFlow AI

## Part A. Prompts used to build the project (with an AI assistant)

**Prompt 1: choose the idea**
> I'm applying for an AI Growth & Automation role. The task is to build ONE healthcare or technology project using AI, in the Automation category. Suggest realistic ideas I can build and demo in a day, and recommend one.

**Prompt 2: build the Python workflow**
> Build a Python automation for a clinic. Read a CSV of appointments, score no-show risk, use an LLM to write a personalised SMS and email reminder in the patient's language, and output a prioritised call list and a daily report. It must also run in a demo mode with no API key.

**Prompt 3: fix a privacy problem found in testing**
> In testing, the SMS included an internal note ("Anxious patient"). Fix this. Only patient-facing instructions may appear in messages. Internal notes, phone numbers, emails and visit types must never be sent to the AI or written into a message.

**Prompt 4: reliability**
> Add error handling so that if the AI call fails or returns invalid JSON, the workflow falls back to a template message instead of crashing.

**Prompt 5: build the web app**
> Build a web application version of this clinic reminder workflow. Show an appointment schedule with a no-show risk score, a "call first" list of high-risk patients, and a reminder panel for the selected patient with the SMS and email, copy buttons, and status tracking (sent, confirmed, wants to reschedule). Add a form to add appointments. The AI should write the reminders in the patient's language, with a template fallback. Use only fictional patients.

**Prompt 6: make the web app more advanced**
> Extend the web app into a fuller product. Add an inbox that reads a patient's free-text reply in any language and sorts it into confirm, reschedule, cancel or question, flags anything urgent for a person, and drafts a reply. Add a waiting list that offers freed slots to matching patients. Add automation rules (call threshold, reminder timing), a simulated activity log, an impact estimate with editable assumptions, a CSV export, a morning brief for the front desk, and an About tab that explains the objectives. A person must approve every change.

## Part B. Prompt used inside the product (final version)

See `SYSTEM_PROMPT` in `python-workflow/app.py`. The web app (`index.html`) uses the same rules.

Design choices:
1. Role and task stated up front: reminder writer for a medical clinic.
2. Strict JSON output, so the result can be used by automation.
3. Hard rules: write in the patient's language, never mention a diagnosis or visit type, never invent details, fixed reply codes (C and R).
4. Length limit: SMS under 280 characters.
5. Data minimisation: only first name, doctor, time, patient instructions and language are sent.

## Part C. Prompt iterations

| Version | Problem found | Fix |
|---|---|---|
| v1 | Reply had extra text around the JSON | Added "Return ONLY a JSON object" and code that strips code fences |
| v2 | SMS leaked an internal staff note | Split the data into patient-facing instructions and staff notes. Staff notes are never sent |
| v3 | SMS named the visit type, which can reveal a condition | Stopped sending the visit type to the AI and added the rule "never mention a diagnosis, condition or visit type" |
| v4 | Non-English replies translated the reply codes | Added "keep the letters C and R in Latin script" |
| v5 | AI could mistake a symptom message for a normal reply | Added a rule that any mention of symptoms or an emergency sets urgent to true, gives no medical advice, and tells staff to call the patient |
