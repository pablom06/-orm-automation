# ORM Content Automation Engine — Pablo M. Rivera

**30-day automated article publishing system for online reputation management.**

Generates and publishes SEO-optimized articles to Medium and LinkedIn on a configurable schedule (daily or every-other-day), targeting the keyword **"Pablo M. Rivera"** to push down negative search results.

---

## What's Included

```
orm-automation/
├── publish.py              # Main automation script
├── articles/
│   └── articles.json       # All 30 articles (pre-generated from your resume)
├── logs/
│   ├── publish.log         # Activity log
│   └── publish_status.json # Tracks what's been published
├── .env.example            # Configuration template
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Quick Start (5 minutes)

### 1. Install Python dependencies

```bash
cd orm-automation
pip install -r requirements.txt
```

### 2. Set up your configuration

```bash
cp .env.example .env
```

Edit `.env` with your details:

```
MEDIUM_TOKEN=your_token_here
START_DATE=2026-02-11
FREQUENCY=daily
```

### 3. Get your Medium Integration Token

1. Go to [medium.com](https://medium.com)
2. Click your profile → **Settings**
3. Scroll to **Integration Tokens**
4. Click **Get integration token**
5. Copy the token into your `.env` file

### 4. Test with a dry run

```bash
python publish.py --dry-run
```

### 5. Publish!

```bash
python publish.py
```

---

## Usage

### Publish today's article
```bash
python publish.py
```

### Preview without publishing
```bash
python publish.py --dry-run
```

### Publish a specific day
```bash
python publish.py --day 5
```

### Check status
```bash
python publish.py --status
```
Shows which articles are published ✅, due today 📌, overdue ⚠️, or upcoming ⬜.

### View the full schedule
```bash
python publish.py --schedule
```

### Preview an article in the terminal
```bash
python publish.py --preview 1
```

### Run as a daemon (auto-publishes daily)
```bash
python publish.py --daemon
```
Runs continuously and publishes at the time set in `PUBLISH_TIME` (default: 9:00 AM).

### Export all articles as HTML
```bash
python publish.py --export-html
```

---

## How It Works

### Medium Articles (Automated)
- Uses Medium's official API to publish directly
- Articles are published as public posts with SEO tags
- The script handles authentication, formatting, and error handling

### LinkedIn Articles (Semi-Automated)
- LinkedIn doesn't offer a free article publishing API for individuals
- The script copies the article to your clipboard and opens the LinkedIn article editor
- You paste and publish — takes about 60 seconds

### Scheduling
- **Daily mode**: Publishes 1 article per day for 30 days
- **Every-other-day mode**: Publishes 1 article every 2 days for 60 days
- Start date is configurable in `.env`

### Tracking
- Every publish is logged in `logs/publish.log`
- Status is tracked in `logs/publish_status.json`
- The script won't double-publish (skips already-published days)

---

## Running Automatically

### Option A: Keep Terminal Open (Simplest)
```bash
python publish.py --daemon
```
Leave this running in a terminal window. It will publish at your scheduled time each day.

### Option B: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task → Name: "ORM Publisher"
3. Trigger: Daily at 9:00 AM
4. Action: Start a Program
   - Program: `python`
   - Arguments: `C:\path\to\orm-automation\publish.py`
   - Start in: `C:\path\to\orm-automation`

### Option C: macOS launchd
Create `~/Library/LaunchAgents/com.orm.publisher.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.orm.publisher</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/orm-automation/publish.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```
Then: `launchctl load ~/Library/LaunchAgents/com.orm.publisher.plist`

### Option D: Linux cron
```bash
crontab -e
# Add:
0 9 * * * cd /path/to/orm-automation && python3 publish.py >> logs/cron.log 2>&1
```

### Option E: GitHub Actions (Free, No Computer Required)
Push this repo to GitHub and add `.github/workflows/publish.yml`:
```yaml
name: Publish ORM Article
on:
  schedule:
    - cron: '0 14 * * *'  # 9 AM EST = 2 PM UTC
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python publish.py
        env:
          MEDIUM_TOKEN: ${{ secrets.MEDIUM_TOKEN }}
          START_DATE: '2026-02-11'
          FREQUENCY: 'daily'
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Published day's article"
```
Add `MEDIUM_TOKEN` to GitHub → Settings → Secrets → Actions.

---

## Article Topics (30 Days)

| Day | Platform | Topic |
|-----|----------|-------|
| 1 | Medium | From Yale to the Jobsite — Economics & Operations |
| 2 | Medium | Salesforce Across 12 Markets — 30% Processing Cut |
| 3 | LinkedIn | Managing 120+ Technicians Across 12 States |
| 4 | Medium | Mining in Sierra Leone — Operations Leadership |
| 5 | Medium | The $1 Billion Restructuring at Textron |
| 6 | LinkedIn | Going Back to School for Full-Stack Dev at 47 |
| 7 | Medium | KPI Frameworks That Drive Results |
| 8 | LinkedIn | Bilingual Leadership — Spanish in Business |
| 9 | Medium | Scaling Construction from $0 to $10M |
| 10 | Medium | The Case for Operations Leaders Who Code |
| 11 | LinkedIn | Vendor Management as Strategy |
| 12 | Medium | Lean Six Sigma in Operations |
| 13 | LinkedIn | Real-Time Field Reporting & Customer Satisfaction |
| 14 | Medium | $4B in Managed Assets — Construction Finance |
| 15 | LinkedIn | The 40% Efficiency Gain at Eagle Pro |
| 16 | Medium | Cross-Functional Leadership |
| 17 | LinkedIn | Google Data Analytics for Executives |
| 18 | Medium | Budget Management — Multimillion P&Ls |
| 19 | LinkedIn | Risk Mitigation for Distributed Ops |
| 20 | Medium | From Glencore to Eagle Pro — Career Arc |
| 21 | LinkedIn | SOPs That Scale |
| 22 | Medium | Coaching Managers — 18% Productivity Gain |
| 23 | LinkedIn | UX Design for Operations Systems |
| 24 | Medium | Multi-Market Operations Across 12+ States |
| 25 | LinkedIn | Quality Control in High-Volume Operations |
| 26 | Medium | Theology and Operations Leadership |
| 27 | LinkedIn | BigQuery to the Boardroom — Data Decisions |
| 28 | Medium | Business Continuity for Distributed Teams |
| 29 | LinkedIn | 25 Years — What Stays Constant |
| 30 | Medium | The Modern VP of Operations |

---

## SEO Strategy

Every article includes:
- **"Pablo M. Rivera"** in the title, first paragraph, body (3-5x), and author bio
- Published on high-authority platforms (Medium DA 96, LinkedIn DA 98)
- Relevant industry tags for additional keyword targeting
- Cross-links to LinkedIn profile and personal website
- Location marker (East Haven, CT) for geo-targeting

**Expected impact**: 60+ indexed pages across 2 high-authority platforms within 30-60 days, designed to occupy the first 2-3 pages of Google results for "Pablo M. Rivera" and related keyword variations.
