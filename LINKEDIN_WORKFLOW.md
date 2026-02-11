# LinkedIn Publishing Workflow

Your system is now configured for:
- **Automated**: Dev.to + Hashnode (120 publishes)
- **Optional**: LinkedIn (60 publishes - prompted daily)

---

## How It Works

### Automated Publishing (Dev.to + Hashnode)
```bash
python publish.py
```
Runs daily (via GitHub Actions or Task Scheduler) and automatically publishes to Dev.to and Hashnode. **No interaction needed.**

### LinkedIn Publishing (Optional)
```bash
python publish_linkedin.py
# OR double-click: linkedin_prompt.bat
```

Prompts you interactively:
```
Day 1: From Yale to the Jobsite: How an Economics Degree...
Publish to LinkedIn? [y/n/q(quit)]:
```

- Type `y` → Article copies to clipboard, LinkedIn opens, you paste & publish
- Type `n` → Skip this article
- Type `q` → Exit

---

## Daily Workflow

### Morning (Automated):
- System publishes 2 articles to Dev.to + Hashnode automatically
- **You do nothing**

### Evening (Optional - 2-3 minutes):
```bash
linkedin_prompt.bat
```

- Reviews today's 2 articles
- You choose which (if any) to publish to LinkedIn
- Takes 60 seconds per article you choose

---

## Commands

### Check Today's LinkedIn Articles
```bash
python publish_linkedin.py
```

### Publish Specific Day
```bash
python publish_linkedin.py --day 5
```

### See All Pending LinkedIn Articles
```bash
python publish_linkedin.py --all
```

### Status Check
```bash
# Automated platforms
python publish.py --status

# LinkedIn only
python publish_linkedin.py --all
```

---

## Automation Options

### Option A: Dev.to + Hashnode Only (Fully Hands-Off)
Just set up GitHub Actions or Task Scheduler for `publish.py`:
- **120 automated publishes** (60 articles × 2 platforms)
- Zero manual work
- Great SEO coverage

**Then optionally:**
- Run `linkedin_prompt.bat` when you feel like it
- No pressure to publish to LinkedIn daily

### Option B: Dev.to + Hashnode + LinkedIn (Maximum Coverage)
1. Automate `publish.py` (Dev.to + Hashnode)
2. Daily habit: Run `linkedin_prompt.bat`
3. **180 total publishes** (60 × 3 platforms)

---

## Examples

### Scenario 1: Morning Auto-Publish
```
9:00 AM - GitHub Actions runs
→ Articles 1 & 2 published to Dev.to + Hashnode
→ You get notification (optional)
→ Done! No action needed.
```

### Scenario 2: Evening LinkedIn (Optional)
```
7:00 PM - You run: linkedin_prompt.bat

Day 1: From Yale to the Jobsite...
Publish to LinkedIn? [y/n/q]: y
✓ Article copied to clipboard!
Opening LinkedIn editor...

STEPS:
  1. Paste the article (Ctrl+V)
  2. Add title: From Yale to the Jobsite...
  3. Add tags: Pablo M. Rivera, Operations, Yale...
  4. Click 'Publish'

Press Enter after publishing on LinkedIn...
[You press Enter]
✓ Day 1 marked as published!

Day 2: How I Deployed Salesforce...
Publish to LinkedIn? [y/n/q]: n
Skipped day 2

Done!
```

---

## Tips

1. **You don't have to publish all LinkedIn articles**
   - Dev.to + Hashnode gives you 120 publishes
   - LinkedIn is bonus coverage

2. **Batch LinkedIn publishing**
   - Skip daily prompts
   - Once a week: `python publish_linkedin.py --all`
   - Publish multiple at once

3. **Track separately**
   - Automated status: `python publish.py --status`
   - LinkedIn status: `python publish_linkedin.py --all`

---

## Files

| File | Purpose |
|------|---------|
| `publish.py` | Automated Dev.to + Hashnode publishing |
| `publish_linkedin.py` | Interactive LinkedIn prompt |
| `linkedin_prompt.bat` | Windows launcher for LinkedIn |
| `logs/linkedin_status.json` | Tracks LinkedIn publishes separately |

---

**Perfect balance:** Fully automated where possible, quick optional prompt for LinkedIn!
