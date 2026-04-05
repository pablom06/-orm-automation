#!/usr/bin/env python3
"""
Press Release Auto-Submitter — Pablo M. Rivera
================================================
Submits press releases to PRlog and OpenPR using Playwright browser automation.
Picks the next unsubmitted press release and submits one to each site per run.

Usage:
  python submit_pr.py              # Submit next press release to both sites
  python submit_pr.py --dry-run    # Show which PR would be submitted
  python submit_pr.py --status     # Show submission status
  python submit_pr.py --index 5    # Submit a specific press release by index

Setup:
  pip install playwright
  playwright install chromium
  Set PRLOG_EMAIL, PRLOG_PASSWORD, OPENPR_EMAIL, OPENPR_PASSWORD in .env
"""

import json
import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
PR_DIR = BASE_DIR / "press_releases"
LOG_DIR = BASE_DIR / "logs"
PR_STATUS_FILE = LOG_DIR / "pr_submission_status.json"
ENV_FILE = BASE_DIR / ".env"

LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pr_submit.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("pr_submit")


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

def load_env():
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def get_config():
    load_env()
    return {
        "prlog_email": os.environ.get("PRLOG_EMAIL", ""),
        "prlog_password": os.environ.get("PRLOG_PASSWORD", ""),
        "personal_site_url": os.environ.get("PERSONAL_SITE_URL", "https://pablomrivera.com"),
    }


# ---------------------------------------------------------------------------
# STATUS TRACKING
# ---------------------------------------------------------------------------

def load_status():
    if PR_STATUS_FILE.exists():
        with open(PR_STATUS_FILE) as f:
            return json.load(f)
    return {"submitted": {}}


def save_status(status):
    with open(PR_STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def mark_submitted(filename, site, url=""):
    status = load_status()
    if filename not in status["submitted"]:
        status["submitted"][filename] = {}
    status["submitted"][filename][site] = {
        "submitted_at": datetime.now().isoformat(),
        "url": url
    }
    save_status(status)


def is_submitted(filename, site):
    status = load_status()
    return site in status["submitted"].get(filename, {})


# ---------------------------------------------------------------------------
# PRESS RELEASE LOADER
# ---------------------------------------------------------------------------

def load_press_releases():
    """Load all press release files sorted by day number."""
    if not PR_DIR.exists():
        log.error(f"Press releases directory not found: {PR_DIR}")
        log.error("Run: python publish.py --generate-press-releases")
        return []
    files = sorted(PR_DIR.glob("day_*.txt"))
    return files


def parse_press_release(filepath):
    """Parse a press release file into components."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")

    # Extract headline (ALL CAPS line after the blank line following contact block)
    headline = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() and line.strip() == line.strip().upper() and len(line.strip()) > 20 and i > 5:
            headline = line.strip().title()  # Convert back to title case
            body_start = i
            break

    # Extract body (everything from subheadline to ###)
    body_lines = []
    in_body = False
    for line in lines[body_start:]:
        if line.strip() == "###":
            break
        if in_body:
            body_lines.append(line)
        elif line.strip() and not line.strip() == line.strip().upper():
            in_body = True
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    # Extract contact info
    contact_name = "Pablo M. Rivera"
    contact_email = ""
    for line in lines[:15]:
        if "@" in line:
            contact_email = line.strip()

    return {
        "headline": headline,
        "body": body,
        "full_text": content,
        "contact_name": contact_name,
        "contact_email": contact_email,
        "filename": filepath.name,
    }


def get_next_pr(site):
    """Get the next press release not yet submitted to a given site."""
    files = load_press_releases()
    for f in files:
        if not is_submitted(f.name, site):
            return f
    return None


# ---------------------------------------------------------------------------
# PRLOG SUBMISSION
# ---------------------------------------------------------------------------

def submit_to_prlog(pr_data, config, dry_run=False):
    """Submit a press release to PRlog.org using Playwright."""
    email = config["prlog_email"]
    password = config["prlog_password"]

    if not email or not password:
        log.warning("PRLOG_EMAIL or PRLOG_PASSWORD not set. Skipping PRlog.")
        return None

    if dry_run:
        log.info(f"🔍 DRY RUN — Would submit to PRlog: {pr_data['headline'][:60]}")
        return "dry-run"

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        log.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
        return None

    log.info(f"📤 Submitting to PRlog: {pr_data['headline'][:60]}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        try:
            # Step 1: Login
            log.info("   Logging into PRlog...")
            page.goto("https://www.prlog.org/login.html", timeout=30000)
            page.wait_for_load_state("networkidle")

            # Check for CAPTCHA on login page
            if page.locator("iframe[src*='recaptcha']").count() > 0:
                log.warning("⚠️  PRlog login CAPTCHA detected — skipping this run")
                browser.close()
                return None

            page.fill("input[name='email']", email)
            page.fill("input[name='password']", password)
            page.click("input[type='submit'], button[type='submit']")
            page.wait_for_load_state("networkidle")

            # Verify login
            if "login" in page.url.lower() or "error" in page.url.lower():
                log.error("❌ PRlog login failed — check credentials")
                browser.close()
                return None

            log.info("   Logged in successfully")

            # Step 2: Navigate to submit page
            page.goto("https://www.prlog.org/submit/", timeout=30000)
            page.wait_for_load_state("networkidle")

            # Check for CAPTCHA
            if page.locator("iframe[src*='recaptcha']").count() > 0:
                log.warning("⚠️  PRlog submission CAPTCHA detected — skipping this run")
                browser.close()
                return None

            # Step 3: Fill headline
            headline_field = page.locator("input[name='title'], input[name='headline'], #title")
            if headline_field.count() > 0:
                headline_field.first.fill(pr_data["headline"][:100])

            # Step 4: Fill body
            body_field = page.locator("textarea[name='body'], textarea[name='content'], #body, #content")
            if body_field.count() > 0:
                body_field.first.fill(pr_data["body"][:5000])

            # Step 5: Select category (Business)
            try:
                category = page.locator("select[name='category'], select[name='cat']")
                if category.count() > 0:
                    category.first.select_option(label="Business")
            except Exception:
                pass  # Category field may vary

            # Step 6: Fill contact fields if present
            try:
                contact_field = page.locator("input[name='contact_name'], input[name='cname']")
                if contact_field.count() > 0:
                    contact_field.first.fill("Pablo M. Rivera")
            except Exception:
                pass

            # Step 7: Submit
            submit_btn = page.locator("input[type='submit'][value*='Submit'], button[type='submit']:not([name='login'])")
            if submit_btn.count() > 0:
                submit_btn.first.click()
                page.wait_for_load_state("networkidle", timeout=30000)

            # Check for CAPTCHA after submit
            if page.locator("iframe[src*='recaptcha']").count() > 0:
                log.warning("⚠️  PRlog post-submit CAPTCHA detected — submission may need manual completion")
                browser.close()
                return None

            # Get URL of submitted PR
            current_url = page.url
            log.info(f"✅ Submitted to PRlog: {current_url}")
            browser.close()
            return current_url

        except PlaywrightTimeout:
            log.error("❌ PRlog timed out — site may be slow or layout changed")
            browser.close()
            return None
        except Exception as e:
            log.error(f"❌ PRlog error: {e}")
            browser.close()
            return None


# ---------------------------------------------------------------------------
# COMMANDS
# ---------------------------------------------------------------------------

def cmd_submit(args):
    config = get_config()

    if args.index is not None:
        files = load_press_releases()
        if args.index >= len(files):
            log.error(f"Index {args.index} out of range (have {len(files)} press releases)")
            return
        pr_file = files[args.index]
    else:
        pr_file = get_next_pr("prlog")

    if not pr_file:
        log.info("✅ All press releases already submitted to PRlog!")
        return

    pr_data = parse_press_release(pr_file)
    log.info(f"\n{'='*60}")
    log.info(f"📰 Next up for PRLOG: {pr_file.name}")
    log.info(f"{'='*60}")

    url = submit_to_prlog(pr_data, config, dry_run=args.dry_run)
    if url and not args.dry_run:
        mark_submitted(pr_file.name, "prlog", url)


def cmd_status(args):
    files = load_press_releases()
    status = load_status()
    submitted = status.get("submitted", {})

    total = len(files)
    prlog_done = sum(1 for f in files if "prlog" in submitted.get(f.name, {}))

    print(f"\n{'='*60}")
    print(f"  Press Release Submission Status — PRlog")
    print(f"  Total PRs: {total}")
    print(f"  PRlog: {prlog_done}/{total} submitted")
    print(f"{'='*60}\n")

    for f in files[:30]:
        p = "✅" if "prlog" in submitted.get(f.name, {}) else "⬜"
        print(f"  {p} {f.name[:65]}")

    if total > 30:
        print(f"\n  ... and {total - 30} more")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Press Release Auto-Submitter — Pablo M. Rivera"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without submitting")
    parser.add_argument("--status", action="store_true", help="Show submission status")
    parser.add_argument("--index", type=int, help="Submit a specific PR by index (0-based)")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    else:
        cmd_submit(args)


if __name__ == "__main__":
    main()
