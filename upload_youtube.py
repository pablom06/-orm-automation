#!/usr/bin/env python3
"""
YouTube Uploader — Pablo M. Rivera ORM
========================================
Uploads videos to YouTube using OAuth 2.0 refresh token (no browser needed).
Uploads as PRIVATE so you can review before making public.

Usage:
  python upload_youtube.py --next        # Generate + upload next unvideoed article
  python upload_youtube.py --day 25      # Upload video for a specific day
  python upload_youtube.py --status      # Show upload status

Environment variables required:
  YT_CLIENT_ID         OAuth client ID from Google Cloud
  YT_CLIENT_SECRET     OAuth client secret
  YT_REFRESH_TOKEN     OAuth refresh token (from one-time setup)
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
ARTICLES_FILE = BASE_DIR / "articles" / "articles.json"
VIDEOS_DIR = BASE_DIR / "videos"
LOG_DIR = BASE_DIR / "logs"
YT_STATUS_FILE = LOG_DIR / "youtube_status.json"
ENV_FILE = BASE_DIR / ".env"

LOG_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "youtube_upload.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("yt")


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
        "client_id": os.environ.get("YT_CLIENT_ID", ""),
        "client_secret": os.environ.get("YT_CLIENT_SECRET", ""),
        "refresh_token": os.environ.get("YT_REFRESH_TOKEN", ""),
        "personal_site_url": os.environ.get("PERSONAL_SITE_URL", "https://pablomrivera.com"),
    }


# ---------------------------------------------------------------------------
# STATUS TRACKING
# ---------------------------------------------------------------------------

def load_status():
    if YT_STATUS_FILE.exists():
        with open(YT_STATUS_FILE) as f:
            return json.load(f)
    return {"uploaded": {}}


def save_status(status):
    with open(YT_STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def mark_uploaded(day, video_id, video_url):
    status = load_status()
    status["uploaded"][str(day)] = {
        "video_id": video_id,
        "video_url": video_url,
        "uploaded_at": datetime.now().isoformat(),
    }
    save_status(status)


def is_uploaded(day):
    status = load_status()
    return str(day) in status["uploaded"]


# ---------------------------------------------------------------------------
# ARTICLE / VIDEO FILES
# ---------------------------------------------------------------------------

def load_articles():
    with open(ARTICLES_FILE, encoding="utf-8") as f:
        return json.load(f)


def find_video_for_day(day):
    candidates = list(VIDEOS_DIR.glob(f"day_{day:03d}_*.mp4"))
    return candidates[0] if candidates else None


def get_next_unvideoed_day(articles):
    """Pick the next article that hasn't been uploaded yet."""
    status = load_status()
    uploaded = set(status["uploaded"].keys())
    for article in articles:
        if str(article["day"]) not in uploaded:
            return article
    return None


# ---------------------------------------------------------------------------
# YOUTUBE UPLOAD
# ---------------------------------------------------------------------------

def upload_to_youtube(video_path, article, config):
    """Upload a video to YouTube as PRIVATE for manual review."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        log.error("Google API libs not installed. Run: pip install google-api-python-client google-auth")
        return None

    client_id = config["client_id"]
    client_secret = config["client_secret"]
    refresh_token = config["refresh_token"]
    personal_site = config["personal_site_url"]

    if not all([client_id, client_secret, refresh_token]):
        log.error("YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN must all be set.")
        return None

    log.info("🔐 Authenticating with YouTube API...")
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )

    youtube = build("youtube", "v3", credentials=creds)

    # Build video metadata
    title = f"{article['title']} | Pablo M. Rivera"
    if len(title) > 100:
        title = title[:97] + "..."

    description = (
        f"{article['title']}\n\n"
        f"In this video, Pablo M. Rivera discusses {article['title'].lower()}.\n\n"
        f"Connect with Pablo M. Rivera:\n"
        f"Website: {personal_site}\n"
        f"LinkedIn: https://www.linkedin.com/in/pablo-rivera-74861a234/\n\n"
        f"Pablo M. Rivera is a bilingual operations executive with 25+ years of experience "
        f"in construction, finance, technology, and property management. Yale economics graduate "
        f"with certifications from Columbia Business School, Google, and Lean Six Sigma.\n\n"
        f"Tags: {' '.join('#' + t.replace(' ', '') for t in article['tags'][:8])}\n"
    )
    description = description[:4900]

    # YouTube tags: lowercase, no special chars, max 500 chars total
    yt_tags = []
    total_len = 0
    for t in ["Pablo M. Rivera", "Pablo Rivera", "Operations"] + article["tags"]:
        clean = t[:60]
        if total_len + len(clean) + 1 < 480:
            yt_tags.append(clean)
            total_len += len(clean) + 1

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": yt_tags,
            "categoryId": "22",  # People & Blogs
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",  # Private until user reviews
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
        }
    }

    log.info(f"📤 Uploading {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.1f} MB)...")
    media = MediaFileUpload(str(video_path), chunksize=1024 * 1024, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                log.info(f"   Upload progress: {int(status.progress() * 100)}%")
        except Exception as e:
            log.error(f"❌ Upload error: {e}")
            return None

    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    log.info(f"✅ Uploaded as PRIVATE: {video_url}")
    log.info(f"   Review and set to PUBLIC at: https://studio.youtube.com/video/{video_id}/edit")
    return video_id, video_url


# ---------------------------------------------------------------------------
# COMMANDS
# ---------------------------------------------------------------------------

def cmd_upload(args):
    config = get_config()
    articles = load_articles()

    if args.day:
        article = next((a for a in articles if a["day"] == args.day), None)
        if not article:
            log.error(f"No article for day {args.day}")
            return
    else:
        article = get_next_unvideoed_day(articles)
        if not article:
            log.info("✅ All articles already uploaded to YouTube!")
            return

    day = article["day"]
    log.info(f"\n{'='*60}")
    log.info(f"📹 Day {day}: {article['title'][:60]}")
    log.info(f"{'='*60}")

    if is_uploaded(day) and not args.force:
        log.info(f"⏭️  Day {day} already uploaded. Use --force to re-upload.")
        return

    # Check for existing video file or build one
    video_path = find_video_for_day(day)
    if not video_path:
        log.info(f"📹 No video found for Day {day} — generating with make_video.py...")
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / "make_video.py"), "--day", str(day)],
            cwd=str(BASE_DIR),
        )
        if result.returncode != 0:
            log.error("❌ Video generation failed")
            return
        video_path = find_video_for_day(day)

    if not video_path or not video_path.exists():
        log.error(f"❌ Video file not found for Day {day}")
        return

    if args.dry_run:
        log.info(f"🔍 DRY RUN — would upload {video_path.name}")
        return

    result = upload_to_youtube(video_path, article, config)
    if result:
        video_id, video_url = result
        mark_uploaded(day, video_id, video_url)


def cmd_status(args):
    articles = load_articles()
    status = load_status()
    uploaded = status.get("uploaded", {})

    print(f"\n{'='*60}")
    print(f"  YouTube Upload Status")
    print(f"  {len(uploaded)}/{len(articles)} articles uploaded")
    print(f"{'='*60}\n")

    for day_str, info in sorted(uploaded.items(), key=lambda x: int(x[0]))[-20:]:
        url = info.get("video_url", "")
        print(f"  ✅ Day {day_str}: {url}")

    if len(uploaded) > 20:
        print(f"\n  (showing last 20)")
    print()


def main():
    parser = argparse.ArgumentParser(description="YouTube Uploader — Pablo M. Rivera")
    parser.add_argument("--day", type=int, help="Upload video for a specific day")
    parser.add_argument("--status", action="store_true", help="Show upload status")
    parser.add_argument("--dry-run", action="store_true", help="Build video but don't upload")
    parser.add_argument("--force", action="store_true", help="Force re-upload even if already done")
    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    else:
        cmd_upload(args)


if __name__ == "__main__":
    main()
