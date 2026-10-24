"""
ClinicFlow AI - batch workflow (Python).

Pipeline: CSV of appointments -> rule-based no-show risk score -> AI-written SMS and
email reminder in the patient's language -> prioritised call list -> daily report.

Privacy by design: only first name, doctor, time, patient instructions and language are
sent to the AI. Phone, email, visit type and internal staff notes never leave this script.

Run:
    pip install -r requirements.txt
    python app.py                              # demo mode, no API key needed (templates)
    ANTHROPIC_API_KEY=your_key python app.py   # live AI mode
"""
import csv
import json
import os
import re
from datetime import datetime

MODEL = "claude-sonnet-4-5"  # change to any Claude model available to your key

SYSTEM_PROMPT = """You write appointment reminders for a medical clinic.
You receive JSON with: firstName, doctor, when, instructionsForPatient, language.
Return ONLY a JSON object with keys "sms", "subject", "body".
Rules:
- Write all values in the given language. Keep the letters C and R in Latin script.
- sms: under 280 characters, warm and plain. Include doctor and date/time and the
  patient instructions if given. End with the equivalent of: Reply C to confirm, R to reschedule.
- subject: short.
- body: 3 to 5 sentences with doctor, date, time and the patient instructions if given.
  Add one sentence asking them to tell the clinic if they cannot attend.
- Never mention a diagnosis, condition or visit type. Never give medical advice.
- Never invent details that are not in the data. No text outside the JSON."""


def risk_score(row):
    """Transparent rule-based score, 0-97. Returns (score, [reasons])."""
    score, reasons = 12, []
    ns = int(row["previous_no_shows"] or 0)
    if ns:
        score += min(ns, 3) * 22
        reasons.append(f"{ns} missed visit(s)")
    if row["first_visit"].strip().lower() == "yes":
        score += 10
        reasons.append("first visit")
    if re.search(r"check-up|cleaning|vaccination|consultation", row["appointment_type"], re.I):
        score += 8
        reasons.append("routine visit")
    dt = datetime.strptime(row["appointment_datetime"], "%Y-%m-%d %H:%M")
    if dt.hour >= 16 or dt.hour < 9 or dt.weekday() == 0:
        score += 6
        reasons.append("hard-to-attend slot")
    return min(score, 97), reasons or ["no risk factors"]


def when_text(row):
    dt = datetime.strptime(row["appointment_datetime"], "%Y-%m-%d %H:%M")
    return dt.strftime("%a %d %b at %I:%M %p").replace(" 0", " ")


def template_message(row):
    """Offline fallback, also used if the AI call fails."""
    first = row["patient_name"].split()[0]
    prep = f" {row['patient_instructions']}" if row["patient_instructions"] else ""
    when = when_text(row)
    return {
        "sms": f"Hi {first}, reminder of your appointment with {row['doctor']} on {when}.{prep} Reply C to confirm, R to reschedule.",
        "subject": f"Reminder: appointment on {when}",
        "body": (
            f"Dear {row['patient_name']},\n\nThis is a reminder of your appointment with "
            f"{row['doctor']} on {when}.{prep}\n\nReply C to confirm or R to reschedule. "
            "If you cannot attend, please let us know so another patient can use the slot.\n\nThank you,\nClinicFlow"
        ),
        "source": "template",
    }


def ai_message(client, row):
    payload = {
        "firstName": row["patient_name"].split()[0],
        "doctor": row["doctor"],
        "when": when_text(row),
        "instructionsForPatient": row["patient_instructions"],
        "language": row["language"],
    }
    msg = client.messages.create(
        model=MODEL,
        max_tokens=700,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
    )
    text = re.sub(r"```json|```", "", msg.content[0].text).strip()
    out = json.loads(text[text.index("{"): text.rindex("}") + 1])
    if len(out["sms"]) > 320:
        raise ValueError("SMS too long")
    out["source"] = "ai"
    return out


def main():
    client = None
    if os.getenv("ANTHROPIC_API_KEY"):
        import anthropic
        client = anthropic.Anthropic()
        print("Live AI mode")
    else:
        print("Demo mode (set ANTHROPIC_API_KEY for live AI)")

    results = []
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "sample_appointments.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            score, reasons = risk_score(row)
            try:
                msg = ai_message(client, row) if client else template_message(row)
            except Exception as exc:  # keep the workflow running if the AI call fails
                print(f"AI problem for {row['patient_name']}: {exc}. Using template.")
                msg = template_message(row)
            results.append({**row, "risk_score": score, "risk_reasons": reasons, **msg})

    results.sort(key=lambda r: r["risk_score"], reverse=True)

    with open(os.path.join(here, "reminders_output.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(os.path.join(here, "daily_report.md"), "w", encoding="utf-8") as f:
        f.write(f"# ClinicFlow daily report - {datetime.now():%d %b %Y}\n\n")
        f.write("## Call first (risk 55 or higher)\n\n")
        f.write("| Patient | When | Risk | Why |\n|---|---|---|---|\n")
        for r in results:
            if r["risk_score"] >= 55:
                f.write(f"| {r['patient_name']} | {r['appointment_datetime']} | {r['risk_score']} | {', '.join(r['risk_reasons'])} |\n")
        f.write("\n## All reminders (SMS)\n\n")
        for r in results:
            f.write(f"**{r['patient_name']}** (risk {r['risk_score']}, {r['source']}): {r['sms']}\n\n")

    print(f"Done: {len(results)} reminders -> reminders_output.json, daily_report.md")


if __name__ == "__main__":
    main()
