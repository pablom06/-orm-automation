#!/usr/bin/env python3
"""
ORM Content Automation Engine — Pablo M. Rivera
================================================
Publishes SEO-optimized articles on a daily or every-other-day schedule.

Supports:
  - Medium API (auto-publish)
  - LinkedIn (generates ready-to-paste content + opens browser)
  - Local logging and tracking
  - Dry-run mode for testing

Usage:
  python publish.py                  # Publish today's article
  python publish.py --dry-run        # Preview without publishing
  python publish.py --day 5          # Publish a specific day's article
  python publish.py --status         # Show publishing status
  python publish.py --schedule       # Show full 30-day schedule
  python publish.py --daemon         # Run continuously (publishes at scheduled time daily)

Setup:
  1. Copy .env.example to .env and add your API tokens
  2. pip install requests python-dotenv schedule
  3. python publish.py --dry-run  (test first)
  4. python publish.py            (publish for real)
"""

import json
import os
import sys
import time
import logging
import argparse
import webbrowser
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
ARTICLES_FILE = BASE_DIR / "articles" / "articles.json"
LOG_DIR = BASE_DIR / "logs"
STATUS_FILE = BASE_DIR / "logs" / "publish_status.json"
ENV_FILE = BASE_DIR / ".env"

# Create dirs
LOG_DIR.mkdir(exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "publish.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("orm")


# ---------------------------------------------------------------------------
# ENV / SECRETS
# ---------------------------------------------------------------------------

def load_env():
    """Load environment variables from .env file."""
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def get_config():
    """Get configuration from environment."""
    load_env()
    return {
        "medium_token": os.environ.get("MEDIUM_TOKEN", ""),
        "medium_user_id": os.environ.get("MEDIUM_USER_ID", ""),
        "devto_token": os.environ.get("DEVTO_TOKEN", ""),
        "hashnode_token": os.environ.get("HASHNODE_TOKEN", ""),
        "hashnode_publication_id": os.environ.get("HASHNODE_PUBLICATION_ID", ""),
        "blogger_blog_id": os.environ.get("BLOGGER_BLOG_ID", ""),
        "blogger_client_id": os.environ.get("BLOGGER_CLIENT_ID", ""),
        "blogger_client_secret": os.environ.get("BLOGGER_CLIENT_SECRET", ""),
        "blogger_refresh_token": os.environ.get("BLOGGER_REFRESH_TOKEN", ""),
        "wordpress_site_url": os.environ.get("WORDPRESS_SITE_URL", ""),
        "wordpress_username": os.environ.get("WORDPRESS_USERNAME", ""),
        "wordpress_app_password": os.environ.get("WORDPRESS_APP_PASSWORD", ""),
        "tumblr_consumer_key": os.environ.get("TUMBLR_CONSUMER_KEY", ""),
        "tumblr_consumer_secret": os.environ.get("TUMBLR_CONSUMER_SECRET", ""),
        "tumblr_oauth_token": os.environ.get("TUMBLR_OAUTH_TOKEN", ""),
        "tumblr_oauth_token_secret": os.environ.get("TUMBLR_OAUTH_TOKEN_SECRET", ""),
        "github_gist_token": os.environ.get("GIST_TOKEN", ""),
        "github_pages_token": os.environ.get("GH_PAGES_TOKEN", ""),
        "github_pages_repo": os.environ.get("GH_PAGES_REPO", "pablom06.github.io"),
        "gitlab_token": os.environ.get("GITLAB_TOKEN", ""),
        "start_date": os.environ.get("START_DATE", datetime.now().strftime("%Y-%m-%d")),
        "frequency": os.environ.get("FREQUENCY", "daily"),  # "daily" or "every_other_day"
        "publish_time": os.environ.get("PUBLISH_TIME", "09:00"),  # 24hr format
        "auto_open_linkedin": os.environ.get("AUTO_OPEN_LINKEDIN", "true").lower() == "true",
    }


# ---------------------------------------------------------------------------
# ARTICLES
# ---------------------------------------------------------------------------

def load_articles():
    """Load all 30 articles from JSON."""
    with open(ARTICLES_FILE) as f:
        return json.load(f)


def get_publish_date(day_num, config):
    """Calculate the publish date for a given day number (2 articles per day)."""
    start = datetime.strptime(config["start_date"], "%Y-%m-%d")
    # With 2 articles per day: articles 1-2 on day 0, 3-4 on day 1, etc.
    offset = (day_num - 1) // 2
    if config["frequency"] == "every_other_day":
        offset *= 2
    return start + timedelta(days=offset)


def get_todays_articles(articles, config):
    """Find which articles should be published today (2 per day).
    Also catches up on any missed/unpublished articles from past days.
    Uses EST timezone since the campaign is based in East Haven, CT."""
    try:
        from datetime import timezone
        # EST is UTC-5
        est = timezone(timedelta(hours=-5))
        today = datetime.now(est).date()
    except Exception:
        today = datetime.now().date()

    todays_articles = []
    catchup_articles = []

    for article in articles:
        pub_date = get_publish_date(article["day"], config).date()
        if pub_date == today:
            todays_articles.append(article)
        elif pub_date < today and not is_published(article["day"], article.get("platforms")):
            catchup_articles.append(article)

    if catchup_articles:
        log.info(f"📋 Found {len(catchup_articles)} missed articles to catch up on")

    return catchup_articles + todays_articles


# ---------------------------------------------------------------------------
# STATUS TRACKING
# ---------------------------------------------------------------------------

def load_status():
    """Load publishing status."""
    if STATUS_FILE.exists():
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {"published": {}, "errors": {}}


def save_status(status):
    """Save publishing status."""
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def mark_published(day_num, platforms, urls=None):
    """Mark an article as published to multiple platforms."""
    status = load_status()
    if urls is None:
        urls = {}

    status["published"][str(day_num)] = {
        "platforms": platforms if isinstance(platforms, list) else [platforms],
        "published_at": datetime.now().isoformat(),
        "urls": urls
    }
    save_status(status)


def is_published(day_num, platforms=None):
    """Check if an article has already been published to all platforms."""
    status = load_status()
    if str(day_num) not in status["published"]:
        return False
    if platforms:
        published_platforms = status["published"][str(day_num)].get("platforms", [])
        return all(p in published_platforms for p in platforms)
    return True


def get_published_platforms(day_num):
    """Get list of platforms already published for a given day."""
    status = load_status()
    if str(day_num) in status["published"]:
        return status["published"][str(day_num)].get("platforms", [])
    return []


# ---------------------------------------------------------------------------
# MEDIUM API
# ---------------------------------------------------------------------------

def get_medium_user_id(token):
    """Fetch Medium user ID from token."""
    try:
        import requests
        resp = requests.get(
            "https://api.medium.com/v1/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if resp.status_code == 200:
            data = resp.json()
            return data["data"]["id"]
        else:
            log.error(f"Medium API error getting user: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        log.error(f"Failed to get Medium user ID: {e}")
        return None


def publish_to_medium(article, config):
    """Publish an article to Medium via API."""
    token = config["medium_token"]
    if not token:
        log.warning("No MEDIUM_TOKEN set. Skipping Medium publish.")
        return None

    try:
        import requests
    except ImportError:
        log.error("requests library not installed. Run: pip install requests")
        return None

    # Get user ID
    user_id = config["medium_user_id"]
    if not user_id:
        user_id = get_medium_user_id(token)
        if not user_id:
            return None

    # Publish
    url = f"https://api.medium.com/v1/users/{user_id}/posts"
    payload = {
        "title": article["title"],
        "contentFormat": "markdown",
        "content": article["body"],
        "tags": article["tags"][:5],  # Medium allows max 5 tags
        "publishStatus": "public"
    }

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        post_url = data["data"]["url"]
        log.info(f"✅ Published to Medium: {post_url}")
        return post_url
    else:
        log.error(f"❌ Medium publish failed: {resp.status_code} - {resp.text}")
        return None


# ---------------------------------------------------------------------------
# DEV.TO API
# ---------------------------------------------------------------------------

def publish_to_devto(article, config):
    """Publish an article to Dev.to via API."""
    token = config["devto_token"]
    if not token:
        log.warning("No DEVTO_TOKEN set. Skipping Dev.to publish.")
        return None

    try:
        import requests
    except ImportError:
        log.error("requests library not installed. Run: pip install requests")
        return None

    url = "https://dev.to/api/articles"

    # Clean tags for Dev.to (no periods, spaces, or special chars)
    clean_tags = []
    for tag in article["tags"][:4]:
        clean_tag = tag.replace(".", "").replace(" ", "").lower()
        if clean_tag:
            clean_tags.append(clean_tag)

    payload = {
        "article": {
            "title": article["title"],
            "published": True,
            "body_markdown": article["body"],
            "tags": clean_tags  # Dev.to allows max 4 tags
        }
    }

    resp = requests.post(
        url,
        headers={
            "api-key": token,
            "Content-Type": "application/json"
        },
        json=payload
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        post_url = data.get("url", "")
        log.info(f"✅ Published to Dev.to: {post_url}")
        return post_url
    else:
        log.error(f"❌ Dev.to publish failed: {resp.status_code} - {resp.text}")
        return None


# ---------------------------------------------------------------------------
# HASHNODE API
# ---------------------------------------------------------------------------

def publish_to_hashnode(article, config):
    """Publish an article to Hashnode via GraphQL API."""
    token = config["hashnode_token"]
    publication_id = config["hashnode_publication_id"]

    if not token:
        log.warning("No HASHNODE_TOKEN set. Skipping Hashnode publish.")
        return None

    if not publication_id:
        log.warning("No HASHNODE_PUBLICATION_ID set. Skipping Hashnode publish.")
        return None

    try:
        import requests
    except ImportError:
        log.error("requests library not installed. Run: pip install requests")
        return None

    url = "https://gql.hashnode.com"

    # Convert tags to Hashnode format (needs both slug and name for new tags)
    tag_slugs = []
    for tag in article["tags"][:5]:
        slug = tag.lower().replace(" ", "-").replace(".", "")
        tag_slugs.append({"slug": slug, "name": tag})

    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
        publishPost(input: $input) {
            post {
                url
                title
            }
        }
    }
    """

    variables = {
        "input": {
            "title": article["title"],
            "contentMarkdown": article["body"],
            "tags": tag_slugs,
            "publicationId": publication_id
        }
    }

    resp = requests.post(
        url,
        headers={
            "Authorization": token,
            "Content-Type": "application/json"
        },
        json={"query": mutation, "variables": variables}
    )

    if resp.status_code == 200:
        data = resp.json()
        if data and "data" in data and data["data"] and data["data"].get("publishPost"):
            post_url = data["data"]["publishPost"]["post"]["url"]
            log.info(f"✅ Published to Hashnode: {post_url}")
            return post_url
        else:
            error_msg = "Unknown error"
            if data and "errors" in data and data["errors"]:
                error_msg = data["errors"][0].get("message", "Unknown error")
            log.error(f"❌ Hashnode publish failed: {error_msg}")
            return None
    else:
        log.error(f"❌ Hashnode publish failed: {resp.status_code} - {resp.text}")
        return None


# ---------------------------------------------------------------------------
# BLOGGER API
# ---------------------------------------------------------------------------

def publish_to_blogger(article, config):
    """Publish an article to Blogger via API."""
    blog_id = config["blogger_blog_id"]
    client_id = config["blogger_client_id"]
    client_secret = config["blogger_client_secret"]
    refresh_token = config["blogger_refresh_token"]

    if not all([blog_id, client_id, client_secret, refresh_token]):
        log.warning("Blogger not configured. Skipping Blogger publish.")
        return None

    try:
        import requests
    except ImportError:
        log.error("requests library not installed. Run: pip install requests")
        return None

    # Get access token from refresh token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    token_resp = requests.post(token_url, data=token_data)
    if token_resp.status_code != 200:
        log.error(f"❌ Blogger auth failed: {token_resp.text}")
        return None

    access_token = token_resp.json()["access_token"]

    # Publish post
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"

    # Convert markdown to HTML (basic)
    import re
    content_html = article["body"]
    # Headers
    content_html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content_html, flags=re.MULTILINE)
    content_html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content_html, flags=re.MULTILINE)
    content_html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content_html, flags=re.MULTILINE)
    # Paragraphs
    content_html = content_html.replace('\n\n', '</p><p>')
    content_html = f'<p>{content_html}</p>'
    # Links
    content_html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', content_html)

    payload = {
        "kind": "blogger#post",
        "title": article["title"],
        "content": content_html,
        "labels": article["tags"][:10]  # Blogger allows many tags
    }

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        post_url = data.get("url", "")
        log.info(f"✅ Published to Blogger: {post_url}")
        return post_url
    else:
        log.error(f"❌ Blogger publish failed: {resp.status_code} - {resp.text}")
        return None


# ---------------------------------------------------------------------------
# WORDPRESS.COM API
# ---------------------------------------------------------------------------

def publish_to_wordpress(article, config):
    """Publish an article to WordPress.com via REST API."""
    site_url = config["wordpress_site_url"]
    username = config["wordpress_username"]
    app_password = config["wordpress_app_password"]

    if not all([site_url, username, app_password]):
        log.warning("WordPress not configured. Skipping WordPress publish.")
        return None

    try:
        import requests
    except ImportError:
        log.error("requests library not installed. Run: pip install requests")
        return None

    # WordPress.com REST API endpoint
    url = f"https://public-api.wordpress.com/wp/v2/sites/{site_url}/posts"

    # Convert markdown to HTML (basic)
    import re
    content_html = article["body"]
    # Headers
    content_html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content_html, flags=re.MULTILINE)
    content_html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content_html, flags=re.MULTILINE)
    content_html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content_html, flags=re.MULTILINE)
    # Paragraphs
    content_html = content_html.replace('\n\n', '</p><p>')
    content_html = f'<p>{content_html}</p>'
    # Links
    content_html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', content_html)

    payload = {
        "title": article["title"],
        "content": content_html,
        "status": "publish",
        "tags": ','.join(article["tags"])
    }

    resp = requests.post(
        url,
        auth=(username, app_password),
        json=payload
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        post_url = data.get("link", "")
        log.info(f"✅ Published to WordPress: {post_url}")
        return post_url
    else:
        log.error(f"❌ WordPress publish failed: {resp.status_code} - {resp.text}")
        return None


# ---------------------------------------------------------------------------
# LINKEDIN (semi-automated — copies to clipboard + opens browser)
# ---------------------------------------------------------------------------

def publish_to_linkedin(article, config):
    """
    LinkedIn doesn't have a free article publishing API for individuals.
    This function:
      1. Copies the article to clipboard
      2. Opens LinkedIn article editor in browser
      3. Logs instructions
    """
    log.info("📋 LinkedIn article prepared.")
    log.info("=" * 50)

    # Try to copy to clipboard
    text = article["body"]
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            log.info("✅ Article copied to clipboard (macOS)")
        elif sys.platform == "win32":  # Windows
            subprocess.run(["clip"], input=text.encode(), check=True)
            log.info("✅ Article copied to clipboard (Windows)")
        else:  # Linux
            try:
                subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)
                log.info("✅ Article copied to clipboard (Linux/xclip)")
            except FileNotFoundError:
                try:
                    subprocess.run(["xsel", "--clipboard", "--input"], input=text.encode(), check=True)
                    log.info("✅ Article copied to clipboard (Linux/xsel)")
                except FileNotFoundError:
                    log.warning("⚠️  Could not copy to clipboard. Install xclip or xsel.")
    except Exception as e:
        log.warning(f"⚠️  Clipboard copy failed: {e}")

    # Save to file as backup
    output_file = LOG_DIR / f"linkedin_day_{article['day']}.md"
    with open(output_file, "w") as f:
        f.write(text)
    log.info(f"📄 Article saved to: {output_file}")

    # Open LinkedIn
    if config.get("auto_open_linkedin", True):
        linkedin_url = "https://www.linkedin.com/article/new/"
        log.info(f"🌐 Opening LinkedIn article editor: {linkedin_url}")
        webbrowser.open(linkedin_url)

    log.info("")
    log.info("📌 STEPS TO COMPLETE:")
    log.info("   1. Paste the article in LinkedIn's editor (Ctrl+V / Cmd+V)")
    log.info(f"   2. Title: {article['title']}")
    log.info(f"   3. Tags: {', '.join(article['tags'])}")
    log.info("   4. Click 'Publish'")
    log.info("   5. Share the published link as a regular LinkedIn post too")
    log.info("=" * 50)

    return "linkedin_manual"


# ---------------------------------------------------------------------------
# TELEGRAPH API
# ---------------------------------------------------------------------------

def publish_to_telegraph(article, config):
    """Publish an article to Telegraph via API (no auth required!)."""
    try:
        import requests
        import re
    except ImportError:
        log.error("requests library not installed. Run: pip install requests")
        return None

    try:
        # Step 1: Create or get Telegraph account
        telegraph_token = config.get("telegraph_token", "")

        if not telegraph_token:
            create_account_url = "https://api.telegra.ph/createAccount"
            account_data = {
                "short_name": "PabloMRivera",
                "author_name": "Pablo M. Rivera"
            }

            resp = requests.post(create_account_url, data=account_data)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("ok"):
                    telegraph_token = result["result"]["access_token"]
                    log.info(f"📝 Created Telegraph account. Token: {telegraph_token[:20]}...")
                else:
                    log.error(f"❌ Telegraph account creation failed: {result}")
                    return None
            else:
                log.error(f"❌ Telegraph API error: {resp.status_code}")
                return None

        # Step 2: Convert markdown to Telegraph Node format (JSON array)
        content = article["body"]
        nodes = []

        for block in content.split('\n\n'):
            block = block.strip()
            if not block:
                continue

            # Handle markdown headers
            h_match = re.match(r'^(#{1,3})\s+(.+)$', block)
            if h_match:
                level = len(h_match.group(1))
                tag = f"h{min(level + 2, 4)}"  # Telegraph uses h3, h4
                nodes.append({"tag": tag, "children": [h_match.group(2)]})
                continue

            # Handle horizontal rules
            if block.startswith('---'):
                nodes.append({"tag": "hr"})
                continue

            # Process inline formatting
            text = block.replace('\n', ' ')
            # Convert markdown links [text](url)
            text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
            # Convert bold
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            # Convert italic
            text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

            # Build children with inline elements
            children = []
            parts = re.split(r'(<(?:a|strong|em)[^>]*>.*?</(?:a|strong|em)>)', text)
            for part in parts:
                if not part:
                    continue
                a_match = re.match(r'<a href="([^"]+)">(.+?)</a>', part)
                strong_match = re.match(r'<strong>(.+?)</strong>', part)
                em_match = re.match(r'<em>(.+?)</em>', part)
                if a_match:
                    children.append({"tag": "a", "attrs": {"href": a_match.group(1)}, "children": [a_match.group(2)]})
                elif strong_match:
                    children.append({"tag": "strong", "children": [strong_match.group(1)]})
                elif em_match:
                    children.append({"tag": "em", "children": [em_match.group(1)]})
                else:
                    children.append(part)

            nodes.append({"tag": "p", "children": children})

        # Step 3: Create the page using form data with JSON-serialized content
        create_page_url = "https://api.telegra.ph/createPage"
        page_data = {
            "access_token": telegraph_token,
            "title": article["title"],
            "author_name": "Pablo M. Rivera",
            "content": json.dumps(nodes),
            "return_content": "false"
        }

        resp = requests.post(create_page_url, data=page_data)

        if resp.status_code == 200:
            result = resp.json()
            if result.get("ok"):
                page_url = result["result"]["url"]
                log.info(f"✅ Published to Telegraph: {page_url}")
                return page_url
            else:
                log.error(f"❌ Telegraph page creation failed: {result}")
                return None
        else:
            log.error(f"❌ Telegraph publish failed: {resp.status_code} - {resp.text}")
            return None

    except Exception as e:
        log.error(f"❌ Telegraph error: {e}")
        return None


# ---------------------------------------------------------------------------
# TUMBLR API
# ---------------------------------------------------------------------------

def publish_to_tumblr(article, config):
    """Publish an article to Tumblr via OAuth 1.0a API."""
    consumer_key = config.get("tumblr_consumer_key", "").strip()
    consumer_secret = config.get("tumblr_consumer_secret", "").strip()
    oauth_token = config.get("tumblr_oauth_token", "").strip()
    oauth_token_secret = config.get("tumblr_oauth_token_secret", "").strip()

    if not all([consumer_key, consumer_secret, oauth_token, oauth_token_secret]):
        log.warning("Tumblr credentials not set. Skipping Tumblr publish.")
        log.warning(f"   consumer_key: {'set' if consumer_key else 'MISSING'}")
        log.warning(f"   consumer_secret: {'set' if consumer_secret else 'MISSING'}")
        log.warning(f"   oauth_token: {'set' if oauth_token else 'MISSING'}")
        log.warning(f"   oauth_token_secret: {'set' if oauth_token_secret else 'MISSING'}")
        return None

    try:
        import requests
        from requests_oauthlib import OAuth1
    except ImportError:
        log.error("requests or requests-oauthlib not installed. Run: pip install requests requests-oauthlib")
        return None

    try:
        # Get user info to find blog name
        auth = OAuth1(consumer_key, consumer_secret, oauth_token, oauth_token_secret)

        user_info_url = "https://api.tumblr.com/v2/user/info"
        resp = requests.get(user_info_url, auth=auth)

        if resp.status_code != 200:
            log.error(f"❌ Tumblr user info failed: {resp.status_code} - {resp.text[:200]}")
            return None

        user_data = resp.json()
        blog_name = user_data["response"]["user"]["blogs"][0]["name"]

        # Create post
        post_url = f"https://api.tumblr.com/v2/blog/{blog_name}.tumblr.com/post"

        post_data = {
            "type": "text",
            "title": article["title"],
            "body": article["body"],
            "tags": ",".join(article["tags"][:10]),  # Tumblr allows many tags
            "format": "markdown"
        }

        resp = requests.post(post_url, auth=auth, data=post_data)

        if resp.status_code == 201:
            result = resp.json()
            post_id = result["response"]["id"]
            tumblr_url = f"https://{blog_name}.tumblr.com/post/{post_id}"
            log.info(f"✅ Published to Tumblr: {tumblr_url}")
            return tumblr_url
        else:
            log.error(f"❌ Tumblr publish failed: {resp.status_code} - {resp.text}")
            return None

    except Exception as e:
        log.error(f"❌ Tumblr error: {e}")
        return None


# ---------------------------------------------------------------------------
# GITHUB GISTS API
# ---------------------------------------------------------------------------

def publish_to_gist(article, config):
    """Publish an article as a public GitHub Gist."""
    token = config.get("github_gist_token", "")

    if not token:
        log.warning("No GITHUB_GIST_TOKEN set. Skipping Gist publish.")
        return None

    try:
        import requests
    except ImportError:
        log.error("requests library not installed. Run: pip install requests")
        return None

    try:
        url = "https://api.github.com/gists"

        # Create a clean filename from the title
        filename = article["title"].replace(" ", "-").replace(":", "").replace("?", "")
        filename = filename[:80] + ".md"

        # Add tags as hashtags at the bottom
        tags_line = " ".join([f"#{tag.replace(' ', '')}" for tag in article["tags"]])

        content = f"# {article['title']}\n\n{article['body']}\n\n---\n{tags_line}"

        payload = {
            "description": f"{article['title']} - by Pablo M. Rivera",
            "public": True,
            "files": {
                filename: {
                    "content": content
                }
            }
        }

        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            json=payload
        )

        if resp.status_code == 201:
            data = resp.json()
            gist_url = data["html_url"]
            log.info(f"✅ Published to GitHub Gist: {gist_url}")
            return gist_url
        else:
            log.error(f"❌ Gist publish failed: {resp.status_code} - {resp.text}")
            return None

    except Exception as e:
        log.error(f"❌ Gist error: {e}")
        return None


# ---------------------------------------------------------------------------
# GITHUB PAGES API
# ---------------------------------------------------------------------------

def publish_to_github_pages(article, config):
    """Publish an article as a page on GitHub Pages site."""
    token = config.get("github_pages_token", "")

    if not token:
        log.warning("No GITHUB_PAGES_TOKEN set. Skipping GitHub Pages publish.")
        return None

    try:
        import requests
        import base64
    except ImportError:
        log.error("requests library not installed.")
        return None

    try:
        repo = config.get("github_pages_repo", "pablom06.github.io")
        owner = repo.split(".")[0]

        # Create a clean filename
        slug = article["title"].lower()
        slug = slug.replace(" ", "-").replace(":", "").replace("?", "").replace("'", "")
        slug = slug.replace("--", "-").replace(",", "").replace(".", "")[:80]

        # Create Jekyll-compatible markdown with front matter
        tags_str = "\n".join([f'  - "{tag}"' for tag in article["tags"]])
        content = f"""---
layout: post
title: "{article['title']}"
author: "Pablo M. Rivera"
tags:
{tags_str}
---

{article['body']}
"""

        # Encode content
        encoded = base64.b64encode(content.encode()).decode()

        filepath = f"_posts/2026-02-{11 + (article['day'] - 1) // 2:02d}-{slug}.md"

        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        # Check if file already exists (need sha to update)
        existing = requests.get(api_url, headers=headers)
        payload = {
            "message": f"Add article: {article['title'][:50]}",
            "content": encoded
        }
        if existing.status_code == 200:
            # File exists — include sha to update it
            payload["sha"] = existing.json()["sha"]

        resp = requests.put(api_url, headers=headers, json=payload)

        if resp.status_code in (200, 201):
            page_url = f"https://{repo}/{slug}"
            log.info(f"✅ Published to GitHub Pages: {page_url}")
            return page_url
        else:
            log.error(f"❌ GitHub Pages publish failed: {resp.status_code} - {resp.text}")
            return None

    except Exception as e:
        log.error(f"❌ GitHub Pages error: {e}")
        return None


# ---------------------------------------------------------------------------
# GITLAB SNIPPETS API
# ---------------------------------------------------------------------------

def publish_to_gitlab(article, config):
    """Publish an article as a public GitLab Snippet."""
    token = config.get("gitlab_token", "")

    if not token:
        log.warning("No GITLAB_TOKEN set. Skipping GitLab publish.")
        return None

    try:
        import requests
    except ImportError:
        log.error("requests library not installed.")
        return None

    try:
        url = "https://gitlab.com/api/v4/snippets"

        # Create filename from title
        filename = article["title"].replace(" ", "-").replace(":", "").replace("?", "")
        filename = filename[:80] + ".md"

        tags_line = " ".join([f"#{tag.replace(' ', '')}" for tag in article["tags"]])
        content = f"# {article['title']}\n\n{article['body']}\n\n---\n{tags_line}"

        payload = {
            "title": article["title"],
            "description": f"By Pablo M. Rivera - {', '.join(article['tags'][:3])}",
            "visibility": "public",
            "files": [
                {
                    "file_path": filename,
                    "content": content
                }
            ]
        }

        resp = requests.post(
            url,
            headers={
                "PRIVATE-TOKEN": token,
                "Content-Type": "application/json"
            },
            json=payload
        )

        if resp.status_code in (200, 201):
            data = resp.json()
            snippet_url = data.get("web_url", "")
            log.info(f"✅ Published to GitLab Snippet: {snippet_url}")
            return snippet_url
        else:
            log.error(f"❌ GitLab publish failed: {resp.status_code} - {resp.text}")
            return None

    except Exception as e:
        log.error(f"❌ GitLab error: {e}")
        return None


# ---------------------------------------------------------------------------
# MAIN PUBLISH LOGIC
# ---------------------------------------------------------------------------

def publish_article(article, config, dry_run=False):
    """Publish a single article to all configured platforms."""
    day = article["day"]
    platforms = article.get("platforms", ["devto", "hashnode", "linkedin"])
    title = article["title"]

    log.info(f"\n{'='*70}")
    log.info(f"📰 DAY {day} | {title}")
    log.info(f"   Publishing to: {', '.join([p.upper() for p in platforms])}")
    log.info(f"{'='*70}")

    if is_published(day, platforms) and not dry_run:
        log.info(f"⏭️  Day {day} already published to all platforms. Skipping.")
        return

    # Check which platforms still need publishing
    already_published = get_published_platforms(day)
    remaining_platforms = [p for p in platforms if p not in already_published]

    if dry_run:
        log.info(f"🔍 DRY RUN — Would publish to {len(remaining_platforms)} platforms:")
        log.info(f"   Title: {title}")
        log.info(f"   Tags:  {', '.join(article['tags'])}")
        log.info(f"   Body:  {len(article['body'])} chars, ~{len(article['body'].split())} words")
        log.info(f"   Platforms: {', '.join([p.upper() for p in remaining_platforms])}")
        if already_published:
            log.info(f"   Already done: {', '.join([p.upper() for p in already_published])}")
        return

    # Load existing URLs from previous publishes
    status = load_status()
    existing_urls = {}
    if str(day) in status["published"]:
        existing_urls = status["published"][str(day)].get("urls", {})

    # Publish to each remaining platform
    results = dict(existing_urls)
    for platform in remaining_platforms:
        url = ""
        if platform == "medium":
            url = publish_to_medium(article, config) or ""
        elif platform == "devto":
            url = publish_to_devto(article, config) or ""
        elif platform == "hashnode":
            url = publish_to_hashnode(article, config) or ""
        elif platform == "blogger":
            url = publish_to_blogger(article, config) or ""
        elif platform == "wordpress":
            url = publish_to_wordpress(article, config) or ""
        elif platform == "telegraph":
            url = publish_to_telegraph(article, config) or ""
        elif platform == "tumblr":
            url = publish_to_tumblr(article, config) or ""
        elif platform == "gist":
            url = publish_to_gist(article, config) or ""
        elif platform == "github_pages":
            url = publish_to_github_pages(article, config) or ""
        elif platform == "gitlab":
            url = publish_to_gitlab(article, config) or ""
        elif platform == "linkedin":
            url = publish_to_linkedin(article, config) or ""

        if url:
            results[platform] = url

    mark_published(day, platforms, results)
    new_count = len([p for p in remaining_platforms if p in results])
    log.info(f"✅ Day {day} published to {new_count}/{len(remaining_platforms)} new platforms ({len(results)}/{len(platforms)} total).")


# ---------------------------------------------------------------------------
# COMMANDS
# ---------------------------------------------------------------------------

def cmd_publish(args):
    """Publish today's article or a specific day."""
    config = get_config()
    articles = load_articles()

    if args.day:
        # Publish specific day
        article = next((a for a in articles if a["day"] == args.day), None)
        if not article:
            log.error(f"No article found for day {args.day}")
            return
        publish_article(article, config, dry_run=args.dry_run)
    else:
        # Publish today's articles (2 per day)
        todays_articles = get_todays_articles(articles, config)
        if not todays_articles:
            log.info("📅 No articles scheduled for today.")
            log.info("   Use --day N to publish a specific day, or check --schedule")
            return

        log.info(f"\n📅 Publishing {len(todays_articles)} articles for today...")
        for article in todays_articles:
            publish_article(article, config, dry_run=args.dry_run)

        # Check if campaign is complete
        if not args.dry_run:
            check_campaign_complete(articles, config)


def check_campaign_complete(articles, config):
    """Check if all articles have been published and write a flag file."""
    status = load_status()
    published = status.get("published", {})
    total = len(articles)
    done = len(published)

    if done >= total:
        flag_file = BASE_DIR / "logs" / "campaign_complete.flag"
        if not flag_file.exists():
            with open(flag_file, "w") as f:
                f.write(f"Campaign completed on {datetime.now().isoformat()}\n")
                f.write(f"Total articles: {total}\n")
                f.write(f"Published: {done}\n")
            log.info(f"\n{'='*70}")
            log.info(f"🎉 CAMPAIGN COMPLETE! All {total} articles published!")
            log.info(f"{'='*70}")
    else:
        remaining = total - done
        days_left = (remaining + 1) // 2  # 2 articles per day
        log.info(f"\n📊 Progress: {done}/{total} articles published ({days_left} days remaining)")


def cmd_status(args):
    """Show publishing status."""
    articles = load_articles()
    status = load_status()
    config = get_config()

    published = status.get("published", {})
    total = len(articles)
    done = len(published)

    print(f"\n{'='*60}")
    print(f"  ORM Publishing Status — Pablo M. Rivera")
    print(f"  {done}/{total} articles published")
    print(f"{'='*60}\n")

    for article in articles:
        day = article["day"]
        day_str = str(day)
        pub_date = get_publish_date(day, config).strftime("%a %b %d")
        platform = article["platform"].upper()
        title_short = article["title"][:50]

        if day_str in published:
            pub_info = published[day_str]
            pub_time = pub_info.get("published_at", "")[:10]
            print(f"  ✅ D{day:02d} | {pub_date} | {platform:8s} | {title_short}...")
        else:
            today = datetime.now().date()
            sched = get_publish_date(day, config).date()
            if sched < today:
                marker = "⚠️ "  # overdue
            elif sched == today:
                marker = "📌"  # today
            else:
                marker = "⬜"  # upcoming
            print(f"  {marker} D{day:02d} | {pub_date} | {platform:8s} | {title_short}...")

    print(f"\n  Legend: ✅ Published  📌 Today  ⚠️  Overdue  ⬜ Upcoming\n")


def cmd_schedule(args):
    """Show the full 30-day schedule."""
    articles = load_articles()
    config = get_config()

    print(f"\n{'='*60}")
    print(f"  30-Day Publishing Schedule")
    print(f"  Start: {config['start_date']} | Frequency: {config['frequency']}")
    print(f"{'='*60}\n")

    for article in articles:
        day = article["day"]
        pub_date = get_publish_date(day, config).strftime("%A, %b %d %Y")
        platform = article["platform"].upper()
        print(f"  Day {day:02d} | {pub_date} | {platform:8s} | {article['title']}")

    end_date = get_publish_date(30, config).strftime("%A, %b %d %Y")
    print(f"\n  📅 Campaign ends: {end_date}\n")


def cmd_daemon(args):
    """Run as a daemon, publishing at the scheduled time each day."""
    try:
        import schedule as sched_lib
    except ImportError:
        log.error("schedule library not installed. Run: pip install schedule")
        return

    config = get_config()
    publish_time = config["publish_time"]

    log.info(f"🤖 Daemon started. Will publish daily at {publish_time}")
    log.info(f"   Start date: {config['start_date']}")
    log.info(f"   Frequency: {config['frequency']}")
    log.info(f"   Press Ctrl+C to stop.\n")

    def daily_job():
        articles = load_articles()
        config_fresh = get_config()
        todays_articles = get_todays_articles(articles, config_fresh)
        if todays_articles:
            log.info(f"📅 Publishing {len(todays_articles)} articles for today...")
            for article in todays_articles:
                publish_article(article, config_fresh, dry_run=args.dry_run)
        else:
            log.info("📅 No articles scheduled for today.")

    sched_lib.every().day.at(publish_time).do(daily_job)

    # Also run immediately if there's something for today
    daily_job()

    while True:
        sched_lib.run_pending()
        time.sleep(60)


def cmd_preview(args):
    """Preview a specific day's article."""
    articles = load_articles()
    article = next((a for a in articles if a["day"] == args.day), None)
    if not article:
        print(f"No article for day {args.day}")
        return

    print(f"\n{'='*60}")
    print(f"  DAY {article['day']} | {article['platform'].upper()}")
    print(f"  {article['title']}")
    print(f"  Tags: {', '.join(article['tags'])}")
    print(f"{'='*60}\n")
    print(article["body"])
    print(f"\n{'='*60}")
    print(f"  Word count: ~{len(article['body'].split())}")
    print(f"{'='*60}\n")


def cmd_export_html(args):
    """Export all articles as a single HTML file for easy reading."""
    articles = load_articles()
    config = get_config()

    html_parts = ["""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>ORM Articles — Pablo M. Rivera</title>
<style>
body { font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; line-height: 1.8; }
h1 { color: #1a1a2e; border-bottom: 2px solid #34d399; padding-bottom: 10px; }
h2 { color: #2d3748; margin-top: 30px; }
.meta { color: #718096; font-size: 14px; margin-bottom: 20px; }
.tag { display: inline-block; background: #e2f5ec; color: #276749; padding: 2px 10px; border-radius: 12px; font-size: 12px; margin-right: 4px; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 40px 0; }
article { margin-bottom: 60px; }
</style></head><body>
<h1>ORM Content Campaign — Pablo M. Rivera</h1>
<p>30 SEO-optimized articles for reputation management</p>
<hr>"""]

    for a in articles:
        pub_date = get_publish_date(a["day"], config).strftime("%A, %B %d, %Y")
        tags_html = " ".join(f'<span class="tag">{t}</span>' for t in a["tags"])
        # Simple markdown to HTML (basic)
        body_html = a["body"].replace("\n\n", "</p><p>").replace("\n", "<br>")
        body_html = f"<p>{body_html}</p>"
        # Headers
        for i in range(3, 0, -1):
            prefix = "#" * i + " "
            body_html = body_html.replace(f"<p>{prefix}", f"<h{i}>").replace(f"<br>{prefix}", f"</p><h{i}>")

        html_parts.append(f"""
<article>
<div class="meta">Day {a['day']} | {a['platform'].upper()} | {pub_date}</div>
{body_html}
<div style="margin-top:12px">{tags_html}</div>
</article>
<hr>""")

    html_parts.append("</body></html>")

    out = BASE_DIR / "articles" / "all_articles.html"
    with open(out, "w") as f:
        f.write("\n".join(html_parts))
    print(f"✅ Exported to {out}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ORM Content Automation Engine — Pablo M. Rivera",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python publish.py --dry-run          Preview today's article without publishing
  python publish.py                    Publish today's article
  python publish.py --day 5            Publish day 5's article
  python publish.py --status           Show what's published and what's pending
  python publish.py --schedule         Show the full 30-day calendar
  python publish.py --preview 1        Read day 1's article in terminal
  python publish.py --daemon           Run continuously, auto-publish at scheduled time
  python publish.py --export-html      Export all articles as one HTML file
        """
    )

    parser.add_argument("--dry-run", action="store_true", help="Preview without publishing")
    parser.add_argument("--day", type=int, help="Publish a specific day (1-30)")
    parser.add_argument("--status", action="store_true", help="Show publishing status")
    parser.add_argument("--schedule", action="store_true", help="Show 30-day schedule")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon, auto-publish daily")
    parser.add_argument("--preview", type=int, metavar="DAY", help="Preview a specific day's article")
    parser.add_argument("--export-html", action="store_true", help="Export all articles as HTML")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.schedule:
        cmd_schedule(args)
    elif args.daemon:
        cmd_daemon(args)
    elif args.preview:
        args.day = args.preview
        cmd_preview(args)
    elif args.export_html:
        cmd_export_html(args)
    else:
        cmd_publish(args)


if __name__ == "__main__":
    main()
