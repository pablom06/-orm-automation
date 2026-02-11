# ORM Automation - Deployment Guide

This guide walks you through deploying your ORM content automation system for hands-free publishing.

## Quick Start (5 Minutes)

### 1. Initial Setup

Run the setup script:
```bash
# Windows
setup.bat

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Your Credentials

Edit the `.env` file and add your Medium token:

```bash
MEDIUM_TOKEN=your_token_here
START_DATE=2026-02-11
FREQUENCY=daily
PUBLISH_TIME=09:00
```

**Get your Medium token:**
1. Go to [medium.com](https://medium.com)
2. Click your profile → Settings
3. Scroll to "Integration Tokens"
4. Generate a new token
5. Copy it into your `.env` file

### 3. Test It

```bash
# Windows
run_publisher.bat --dry-run

# Mac/Linux
python publish.py --dry-run
```

### 4. Publish!

```bash
# Windows
run_publisher.bat

# Mac/Linux
python publish.py
```

---

## Deployment Options

Choose the deployment method that fits your workflow:

### Option 1: GitHub Actions (Recommended - Free & Fully Automated)

**Best for:** Hands-off automation with no computer required

**Setup:**

1. **Create a GitHub repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - ORM automation"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/orm-automation.git
   git push -u origin main
   ```

2. **Add your Medium token as a GitHub secret:**
   - Go to your repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `MEDIUM_TOKEN`
   - Value: Your Medium integration token
   - Click "Add secret"

3. **Configure variables (optional):**
   - Go to Settings → Secrets and variables → Actions → Variables tab
   - Add these variables (or use defaults):
     - `START_DATE`: 2026-02-11
     - `FREQUENCY`: daily
     - `PUBLISH_TIME`: 09:00

4. **Enable GitHub Actions:**
   - The workflow file is already in `.github/workflows/publish.yml`
   - It will run automatically every day at 9 AM EST
   - You can also trigger it manually from the Actions tab

5. **Manual triggers:**
   - Go to Actions → ORM Content Publisher → Run workflow
   - You can enable dry-run mode or publish a specific day

**Cost:** Free (GitHub Actions gives 2,000 minutes/month on free plan)

---

### Option 2: Windows Task Scheduler

**Best for:** Running on your Windows PC automatically

**Setup:**

1. Open Task Scheduler (Win + R → `taskschd.msc`)

2. Click "Create Basic Task"
   - Name: `ORM Publisher`
   - Description: `Daily content publishing automation`

3. Trigger: **Daily**
   - Start date: Today
   - Start time: 9:00 AM
   - Recur every: 1 day

4. Action: **Start a program**
   - Program: `C:\Windows\System32\cmd.exe`
   - Arguments: `/c "C:\Users\pablo\Downloads\orm-automation\run_publisher.bat"`
   - Start in: `C:\Users\pablo\Downloads\orm-automation`

5. Click Finish

6. **Edit the task** (important):
   - Right-click the task → Properties
   - Under "General":
     - Check "Run whether user is logged on or not"
     - Check "Run with highest privileges"
   - Click OK

**Test it:**
- Right-click the task → Run
- Check `logs/publish.log` to verify it worked

---

### Option 3: Daemon Mode (Keep Terminal Open)

**Best for:** Testing or short-term automation

**Setup:**

```bash
# Windows
run_daemon.bat

# Mac/Linux
python publish.py --daemon
```

The script will:
- Run continuously
- Publish at your scheduled time (9:00 AM by default)
- Stay active until you press Ctrl+C

**Pros:**
- Simplest setup
- Immediate feedback in terminal

**Cons:**
- Must keep terminal window open
- Stops if computer restarts

---

### Option 4: macOS launchd

**Best for:** Mac users who want set-it-and-forget-it automation

**Setup:**

1. Create a launch agent file:

```bash
nano ~/Library/LaunchAgents/com.orm.publisher.plist
```

2. Add this content (update paths to match your setup):

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
        <string>/Users/YOUR_USERNAME/orm-automation/venv/bin/python</string>
        <string>/Users/YOUR_USERNAME/orm-automation/publish.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/orm-automation</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/orm-automation/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/orm-automation/logs/launchd.error.log</string>
</dict>
</plist>
```

3. Load the agent:

```bash
launchctl load ~/Library/LaunchAgents/com.orm.publisher.plist
```

4. Verify it's loaded:

```bash
launchctl list | grep orm
```

**To unload:**
```bash
launchctl unload ~/Library/LaunchAgents/com.orm.publisher.plist
```

---

### Option 5: Linux cron

**Best for:** Linux servers or WSL

**Setup:**

1. Open crontab:
```bash
crontab -e
```

2. Add this line (runs daily at 9 AM):
```bash
0 9 * * * cd /path/to/orm-automation && /path/to/orm-automation/venv/bin/python publish.py >> logs/cron.log 2>&1
```

3. Save and exit

**Verify:**
```bash
crontab -l
```

---

## Monitoring & Maintenance

### Check Status

```bash
# Windows
run_publisher.bat --status

# Mac/Linux
python publish.py --status
```

Shows:
- ✅ Published articles
- 📌 Today's article
- ⚠️ Overdue articles
- ⬜ Upcoming articles

### View Schedule

```bash
python publish.py --schedule
```

### Check Logs

```bash
# View recent activity
tail -n 50 logs/publish.log

# View status file
cat logs/publish_status.json
```

### Manual Publishing

```bash
# Publish a specific day
python publish.py --day 5

# Preview an article
python publish.py --preview 1

# Dry run (test without publishing)
python publish.py --dry-run
```

---

## Troubleshooting

### "No MEDIUM_TOKEN set"
- Check your `.env` file exists
- Verify `MEDIUM_TOKEN=` has a value (no spaces)
- Make sure you're running from the correct directory

### "requests library not installed"
- Run: `pip install -r requirements.txt`
- If using virtual environment, make sure it's activated

### Articles not publishing
- Check `logs/publish.log` for errors
- Verify your Medium token is valid
- Run `python publish.py --status` to see what's scheduled
- Make sure `START_DATE` in `.env` is correct

### GitHub Actions not running
- Check Settings → Actions → General → "Allow all actions"
- Verify `MEDIUM_TOKEN` secret is set
- Check the Actions tab for error messages
- Make sure the workflow file is in `.github/workflows/publish.yml`

### Windows Task Scheduler not working
- Open Task Scheduler → Task Scheduler Library
- Find "ORM Publisher" → Right-click → Run
- Check "Last Run Result" (0x0 = success)
- View `logs/publish.log` for details

---

## Security Notes

- **Never commit your `.env` file** to GitHub (it's in `.gitignore`)
- Store your `MEDIUM_TOKEN` securely
- If using GitHub Actions, only use GitHub Secrets (never hardcode tokens)
- Rotate your Medium token if it's ever exposed

---

## Next Steps

1. ✅ Complete initial setup
2. ✅ Test with `--dry-run`
3. ✅ Choose a deployment method
4. ✅ Set up automation
5. ✅ Monitor first few publishes
6. ✅ Adjust `PUBLISH_TIME` or `FREQUENCY` as needed

---

## Support

If you encounter issues:
1. Check `logs/publish.log` for error messages
2. Run `python publish.py --status` to verify configuration
3. Test with `--dry-run` to isolate issues
4. Verify your Medium token is valid

For LinkedIn publishing:
- The script copies content to clipboard
- Opens the LinkedIn article editor
- Follow on-screen instructions to paste and publish
- Takes about 60 seconds per article
