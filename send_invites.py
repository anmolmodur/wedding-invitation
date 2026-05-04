#!/usr/bin/env python3
"""
Wedding invitation mailer.

Usage:
    python send_invites.py                        # send to everyone in guests.csv
    python send_invites.py --dry-run              # preview HTML, no emails sent
    python send_invites.py --to jane@example.com  # send to one address (must be in guests.csv)
    python send_invites.py --test you@gmail.com   # send a test email to any address
"""

import argparse
import csv
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from generate_invite import (
    build_email_html,
    build_invite_html,
    make_invite_url,
)

load_dotenv()

SENDER_EMAIL    = os.environ["SENDER_EMAIL"]
SENDER_NAME     = os.environ["SENDER_NAME"]
SMTP_PASSWORD   = os.environ["SMTP_PASSWORD"]
SMTP_HOST       = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT       = int(os.environ.get("SMTP_PORT", 587))
RSVP_URL        = os.environ["RSVP_URL"]
INVITE_PAGE_URL = os.environ["INVITE_PAGE_URL"]   # e.g. https://you.github.io/wedding/invite.html
EMAIL_SUBJECT   = os.environ.get("EMAIL_SUBJECT", "You're Invited!")
INVITE_FRONT    = os.environ.get("INVITE_FRONT", "Wedding_Invitation_Front.png")
INVITE_BACK     = os.environ.get("INVITE_BACK",  "Wedding_Invitation_Back.png")
GUESTS_CSV      = "guests.csv"


def load_guests(csv_path: str) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_message(guest: dict) -> MIMEMultipart:
    invite_url = make_invite_url(INVITE_PAGE_URL, guest["name"])
    html  = build_email_html(guest["name"], invite_url, SENDER_NAME)
    plain = (
        f"Dear {guest['name']},\n\n"
        f"You are warmly invited to our wedding!\n\n"
        f"Open your personal invitation: {invite_url}\n\n"
        f"Please RSVP at: {RSVP_URL}\n\n"
        f"— {SENDER_NAME}"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"]    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"]      = guest["email"]
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))
    return msg


def send_all(guests: list[dict], dry_run: bool = False, to_filter: str | None = None):
    if to_filter:
        guests = [g for g in guests if g["email"] == to_filter]
        if not guests:
            print(f"No guest found with email: {to_filter}")
            sys.exit(1)

    if dry_run:
        _dry_run(guests)
        return

    print(f"Connecting to {SMTP_HOST}:{SMTP_PORT} …")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        print(f"Logged in as {SENDER_EMAIL}\n")

        for guest in guests:
            msg = build_message(guest)
            try:
                server.sendmail(SENDER_EMAIL, guest["email"], msg.as_string())
                print(f"  ✓  {guest['name']} <{guest['email']}>")
            except Exception as exc:
                print(f"  ✗  {guest['name']} <{guest['email']}> — {exc}")

    print(f"\nDone. {len(guests)} invitation(s) sent.")


def _dry_run(guests: list[dict]):
    out_dir = Path("dry_run_output")
    out_dir.mkdir(exist_ok=True)
    print(f"DRY RUN — writing previews to {out_dir}/\n")

    for guest in guests:
        safe_name  = guest["name"].replace(" ", "_").replace("/", "-")
        invite_url = make_invite_url(INVITE_PAGE_URL, guest["name"])

        # Email preview (what lands in the inbox)
        email_html = build_email_html(guest["name"], invite_url, SENDER_NAME)
        email_path = out_dir / f"{safe_name}_email.html"
        email_path.write_text(email_html, encoding="utf-8")

        # Invite page preview (what they see after clicking — standalone with embedded images)
        page_html  = build_invite_html(
            guest_name=guest["name"],
            rsvp_url=RSVP_URL,
            front_image_path=INVITE_FRONT,
            back_image_path=INVITE_BACK,
            sender_name=SENDER_NAME,
        )
        page_path  = out_dir / f"{safe_name}_invite.html"
        page_path.write_text(page_html, encoding="utf-8")

        print(f"  {guest['name']}")
        print(f"    email:  {email_path}")
        print(f"    invite: {page_path}")
        print(f"    url:    {invite_url}")

    print("\nOpen the HTML files in a browser to preview.")


def send_test(email: str):
    """Send a single test invitation to any email address, bypassing guests.csv."""
    guest = {"name": "Test Guest", "email": email}
    msg   = build_message(guest)
    msg.replace_header("Subject", f"[TEST] {EMAIL_SUBJECT}")

    print(f"Connecting to {SMTP_HOST}:{SMTP_PORT} …")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, msg.as_string())

    print(f"Test invitation sent to {email}")
    print("Check your inbox — the subject line starts with [TEST].")


def main():
    parser = argparse.ArgumentParser(description="Send wedding invitations by email.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate HTML previews without sending any email.")
    parser.add_argument("--to", metavar="EMAIL",
                        help="Send to a single recipient (must be in guests.csv).")
    parser.add_argument("--test", metavar="EMAIL",
                        help="Send a test invitation to any email address.")
    args = parser.parse_args()

    if args.test:
        send_test(args.test)
        return

    guests = load_guests(GUESTS_CSV)
    print(f"Loaded {len(guests)} guest(s) from {GUESTS_CSV}")
    send_all(guests, dry_run=args.dry_run, to_filter=args.to)


if __name__ == "__main__":
    main()
