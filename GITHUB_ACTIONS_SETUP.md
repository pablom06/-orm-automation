# GitHub Actions Setup Guide

Complete automation - publish 2 articles daily to 4 platforms without lifting a finger!

---

## Quick Setup (10 minutes)

### Step 1: Create GitHub Repository

```bash
# In your orm-automation folder
git init
git add .
git commit -m "Initial commit - ORM automation system"
git branch -M main

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/orm-automation.git
git push -u origin main
```

### Step 2: Add Secrets to GitHub

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

#### Required (Dev.to + Hashnode):
- `DEVTO_TOKEN` = `gnTMhr7HFwivsbsJiwC9Vfsd`
- `HASHNODE_TOKEN` = `9374311b-2f4f-4107-868a-37562a319f5f`
- `HASHNODE_PUBLICATION_ID` = `698c167a7ee84b600b3963a8`

#### Optional (Blogger + WordPress for 4-platform coverage):
See setup guides below to get these tokens:
- `BLOGGER_BLOG_ID`
- `BLOGGER_CLIENT_ID`
- `BLOGGER_CLIENT_SECRET`
- `BLOGGER_REFRESH_TOKEN`
- `WORDPRESS_SITE_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APP_PASSWORD`

### Step 3: Enable Actions

1. Go to your repo → **Actions** tab
2. Click "I understand my workflows, go ahead and enable them"
3. Done! The workflow will run daily at 9 AM EST

---

## Blogger Setup (Optional - 5 minutes)

Adds Google's Blogger platform (DA ~95)

### 1. Create Blogger Blog
1. Go to https://www.blogger.com
2. Create account (use your Google account)
3. Create a new blog (e.g., `pablomrivera.blogspot.com`)

### 2. Get Blog ID
1. In Blogger dashboard, go to Settings
2. Your Blog ID is in the URL or under Settings

### 3. Set Up OAuth (API Access)
1. Go to https://console.cloud.google.com
2. Create new project: "ORM Publisher"
3. Enable "Blogger API v3"
4. Create OAuth 2.0 credentials:
   - Application type: Desktop app
   - Name: "ORM Publisher"
5. Download credentials JSON

### 4. Get Refresh Token
Run this script once:
```python
# save as get_blogger_token.py
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/blogger']
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

print(f"Refresh Token: {creds.refresh_token}")
```

Run: `pip install google-auth-oauthlib` then `python get_blogger_token.py`

### 5. Add to GitHub Secrets
- `BLOGGER_BLOG_ID` = Your blog ID
- `BLOGGER_CLIENT_ID` = From credentials.json
- `BLOGGER_CLIENT_SECRET` = From credentials.json
- `BLOGGER_REFRESH_TOKEN` = From script above

---

## WordPress.com Setup (Optional - 3 minutes)

Adds WordPress.com platform (DA ~94)

### 1. Create WordPress.com Blog
1. Go to https://wordpress.com/start
2. Create free blog (e.g., `pablomrivera.wordpress.com`)

### 2. Generate App Password
1. Go to https://wordpress.com/me/security
2. Scroll to "Application Passwords"
3. Create new password: "ORM Publisher"
4. Copy the password

### 3. Add to GitHub Secrets
- `WORDPRESS_SITE_URL` = `pablomrivera.wordpress.com`
- `WORDPRESS_USERNAME` = Your WordPress username
- `WORDPRESS_APP_PASSWORD` = The app password from step 2

---

## Testing

### Manual Test Run
1. Go to your repo → Actions tab
2. Click "Auto-Publish ORM Content"
3. Click "Run workflow"
4. Check "Dry run mode" if you want to test
5. Click "Run workflow"

### Check Logs
- Actions tab → Click on the workflow run
- View logs to see what published

---

## What Happens Daily

**Every day at 9:00 AM EST:**
1. GitHub Actions triggers automatically
2. Publishes 2 articles to all configured platforms:
   - Dev.to ✅
   - Hashnode ✅
   - Blogger ✅ (if configured)
   - WordPress ✅ (if configured)
3. Updates status files
4. Commits changes back to repo

**You do nothing!**

---

## Monitoring

### Check Status
View in GitHub:
- Actions tab → Recent runs
- Green checkmark = success
- Red X = failure (check logs)

### Email Notifications
GitHub sends email if workflow fails

### Manual Check
```bash
git pull  # Get latest status
python publish.py --status
```

---

## Platform Coverage

| Setup | Platforms | Daily Publishes | Total (30 days) |
|-------|-----------|-----------------|-----------------|
| **Minimum** | Dev.to + Hashnode | 4/day | 120 |
| **Recommended** | + Blogger + WordPress | 8/day | 240 |
| **Maximum** | + LinkedIn (manual) | 8-12/day | 240-360 |

---

## Troubleshooting

**"Workflow not running"**
→ Check Actions tab is enabled
→ Verify secrets are added

**"Publishing failed"**
→ Check Actions logs for error details
→ Verify API tokens are still valid

**"No articles scheduled"**
→ Check START_DATE in workflow file matches your .env

---

## Cost

**$0/month** - GitHub Actions is free for public repos (2,000 minutes/month)

For private repos: Still free under free tier limits

---

**That's it! Fully automated publishing to 2-4 high-authority platforms!** 🚀
