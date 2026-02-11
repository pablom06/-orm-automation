# ORM Automation - Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Setup (1 minute)

Open a terminal in this directory and run:

```bash
setup.bat
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Get you ready to publish

## Step 2: Add Your Medium Token (2 minutes)

1. Go to [medium.com](https://medium.com) and log in
2. Click your profile picture → **Settings**
3. Scroll down to **Integration tokens**
4. Click **Get integration token**
5. Copy the token
6. Open the `.env` file in this folder
7. Replace `MEDIUM_TOKEN=` with `MEDIUM_TOKEN=your_token_here`
8. Save the file

## Step 3: Test It (30 seconds)

```bash
run_publisher.bat --dry-run
```

You should see output showing what would be published without actually publishing it.

## Step 4: Publish Your First Article (30 seconds)

```bash
run_publisher.bat
```

That's it! Your first article is now published to Medium.

---

## What Happens Next?

### For Medium Articles:
- The script publishes automatically using the Medium API
- You'll see a URL in the terminal when it's done
- Check your Medium profile to see the published article

### For LinkedIn Articles:
- The script copies the article to your clipboard
- It opens the LinkedIn article editor in your browser
- Paste the content (Ctrl+V)
- Add the title and tags shown in the terminal
- Click Publish

---

## Automated Daily Publishing

Choose one option:

### Option A: GitHub Actions (Free, Cloud-Based)
Best if you don't want to keep your computer on.

1. Push this folder to GitHub
2. Add your MEDIUM_TOKEN as a secret
3. It will publish automatically every day at 9 AM

See DEPLOYMENT.md for details.

### Option B: Windows Task Scheduler
Best if you want to run it on your PC.

1. Open Task Scheduler
2. Create a task to run run_publisher.bat daily at 9 AM

See DEPLOYMENT.md for step-by-step instructions.

### Option C: Keep Terminal Open
Simplest, but you need to keep the window open.

```bash
run_daemon.bat
```

---

## Useful Commands

```bash
# Check what's been published
run_publisher.bat --status

# View the 30-day schedule
run_publisher.bat --schedule

# Publish a specific day
run_publisher.bat --day 5

# Preview an article without publishing
run_publisher.bat --preview 1
```

---

## Troubleshooting

**"No MEDIUM_TOKEN set"**
→ Make sure you edited the .env file and added your token

**"Python is not installed"**
→ Install Python from https://www.python.org/downloads/

**Articles aren't publishing**
→ Check logs/publish.log for error messages

---

## Next Steps

1. Test with --dry-run
2. Publish your first article
3. Set up automated publishing (see DEPLOYMENT.md)
4. Check status daily with --status

For complete documentation, see:
- DEPLOYMENT.md - Full deployment guide
- README.md - Detailed usage guide
