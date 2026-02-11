#!/usr/bin/env python3
"""
LinkedIn Publisher - Interactive Daily Prompt
==============================================
Prompts you daily to publish articles to LinkedIn.
Independent of the automated Dev.to + Hashnode publishing.

Usage:
  python publish_linkedin.py              # Check today's articles
  python publish_linkedin.py --day 5      # Publish specific day
  python publish_linkedin.py --all        # Show all pending LinkedIn articles
"""

import json
import sys
import webbrowser
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
ARTICLES_FILE = BASE_DIR / "articles" / "articles.json"
LOG_DIR = BASE_DIR / "logs"
LINKEDIN_STATUS_FILE = LOG_DIR / "linkedin_status.json"

LOG_DIR.mkdir(exist_ok=True)


def load_articles():
    """Load articles."""
    with open(ARTICLES_FILE, encoding='utf-8') as f:
        return json.load(f)


def load_linkedin_status():
    """Load LinkedIn publishing status."""
    if LINKEDIN_STATUS_FILE.exists():
        with open(LINKEDIN_STATUS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {"published": {}}


def save_linkedin_status(status):
    """Save LinkedIn publishing status."""
    with open(LINKEDIN_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2)


def mark_linkedin_published(day_num):
    """Mark article as published to LinkedIn."""
    status = load_linkedin_status()
    status["published"][str(day_num)] = {
        "published_at": datetime.now().isoformat()
    }
    save_linkedin_status(status)


def is_linkedin_published(day_num):
    """Check if published to LinkedIn."""
    status = load_linkedin_status()
    return str(day_num) in status["published"]


def get_publish_date(day_num):
    """Calculate publish date (2 articles per day)."""
    start_date = "2026-02-11"  # Update if needed
    start = datetime.strptime(start_date, "%Y-%m-%d")
    offset = (day_num - 1) // 2
    return start + timedelta(days=offset)


def copy_to_clipboard(text):
    """Copy text to clipboard."""
    try:
        if sys.platform == "win32":
            subprocess.run(["clip"], input=text.encode(), check=True)
            return True
        elif sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            return True
        else:
            try:
                subprocess.run(["xclip", "-selection", "clipboard"],
                             input=text.encode(), check=True)
                return True
            except FileNotFoundError:
                try:
                    subprocess.run(["xsel", "--clipboard", "--input"],
                                 input=text.encode(), check=True)
                    return True
                except FileNotFoundError:
                    return False
    except Exception:
        return False


def publish_to_linkedin(article):
    """Prepare article for LinkedIn publishing."""
    day = article["day"]
    title = article["title"]
    body = article["body"]
    tags = article["tags"]

    print(f"\n{'='*70}")
    print(f"  LinkedIn Article - Day {day}")
    print(f"{'='*70}")
    print(f"Title: {title}")
    print(f"Tags:  {', '.join(tags)}")
    print(f"Words: ~{len(body.split())}")
    print(f"{'='*70}\n")

    # Copy to clipboard
    if copy_to_clipboard(body):
        print("✓ Article copied to clipboard!")
    else:
        print("⚠ Could not copy to clipboard")
        # Save to file as backup
        output_file = LOG_DIR / f"linkedin_day_{day}.md"
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(body)
        print(f"✓ Article saved to: {output_file}")

    # Open LinkedIn
    linkedin_url = "https://www.linkedin.com/article/new/"
    print(f"\nOpening LinkedIn editor: {linkedin_url}")
    webbrowser.open(linkedin_url)

    print("\nSTEPS:")
    print("  1. Paste the article (Ctrl+V / Cmd+V)")
    print(f"  2. Add title: {title}")
    print(f"  3. Add tags: {', '.join(tags)}")
    print("  4. Click 'Publish'")
    print("  5. (Optional) Share as a post too")

    return True


def get_todays_articles(articles):
    """Get today's articles."""
    today = datetime.now().date()
    todays = []
    for article in articles:
        pub_date = get_publish_date(article["day"]).date()
        if pub_date == today:
            todays.append(article)
    return todays


def interactive_publish(articles_to_publish):
    """Interactively prompt for each article."""
    for article in articles_to_publish:
        day = article["day"]

        if is_linkedin_published(day):
            print(f"\n✓ Day {day} already published to LinkedIn. Skipping.")
            continue

        title_short = article["title"][:60]
        print(f"\n{'='*70}")
        print(f"Day {day}: {title_short}...")
        print(f"{'='*70}")

        response = input("\nPublish to LinkedIn? [y/n/q(quit)]: ").strip().lower()

        if response == 'q':
            print("\nExiting...")
            break
        elif response == 'y':
            publish_to_linkedin(article)

            # Confirm after they've published
            input("\nPress Enter after publishing on LinkedIn...")
            mark_linkedin_published(day)
            print(f"✓ Day {day} marked as published!")
        else:
            print(f"Skipped day {day}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LinkedIn Publisher - Interactive Prompt"
    )
    parser.add_argument("--day", type=int, help="Publish specific day")
    parser.add_argument("--all", action="store_true",
                       help="Show all pending articles")

    args = parser.parse_args()
    articles = load_articles()

    if args.day:
        # Specific day
        article = next((a for a in articles if a["day"] == args.day), None)
        if not article:
            print(f"No article found for day {args.day}")
            return

        if is_linkedin_published(args.day):
            print(f"Day {args.day} already published to LinkedIn.")
            response = input("Publish again? [y/n]: ").strip().lower()
            if response != 'y':
                return

        publish_to_linkedin(article)
        input("\nPress Enter after publishing on LinkedIn...")
        mark_linkedin_published(args.day)
        print(f"✓ Day {args.day} marked as published!")

    elif args.all:
        # Show all pending
        status = load_linkedin_status()
        published = status.get("published", {})

        pending = [a for a in articles if str(a["day"]) not in published]

        print(f"\n{'='*70}")
        print(f"  LinkedIn Publishing Status")
        print(f"  {len(published)}/{len(articles)} published")
        print(f"{'='*70}\n")

        if pending:
            print("Pending articles:")
            for article in pending[:10]:  # Show first 10
                day = article["day"]
                title = article["title"][:50]
                pub_date = get_publish_date(day).strftime("%b %d")
                print(f"  Day {day:2d} ({pub_date}): {title}...")

            if len(pending) > 10:
                print(f"  ... and {len(pending) - 10} more")

            print(f"\nRun: python publish_linkedin.py   (to publish today's)")
            print(f"Or:  python publish_linkedin.py --day N")
        else:
            print("All articles published to LinkedIn!")

    else:
        # Today's articles
        todays = get_todays_articles(articles)

        if not todays:
            print("No articles scheduled for today.")
            print("Use --all to see all pending articles")
            print("Use --day N to publish a specific day")
            return

        print(f"\n{'='*70}")
        print(f"  LinkedIn Publisher - {datetime.now().strftime('%A, %B %d, %Y')}")
        print(f"  {len(todays)} article(s) scheduled for today")
        print(f"{'='*70}")

        interactive_publish(todays)

        print(f"\n{'='*70}")
        print("Done!")
        print(f"{'='*70}")


if __name__ == "__main__":
    main()
