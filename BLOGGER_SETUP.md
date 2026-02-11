# Blogger Setup - Complete Guide

Get your 4 Blogger secrets to enable automatic publishing to Google's Blogger platform (DA ~95).

---

## Part 1: Create Blogger Blog (2 minutes)

### Step 1: Go to Blogger
1. Visit https://www.blogger.com
2. Sign in with your Google account
3. Click **"Create New Blog"** (or **"New Blog"** button)

### Step 2: Create Blog
1. **Title**: `Pablo M Rivera` (or your preference)
2. **Address**: `pablomrivera.blogspot.com` (or similar - must be unique)
3. **Theme**: Choose any (you can change later)
4. Click **"Create blog!"**

### Step 3: Get Blog ID
1. In Blogger dashboard, click on your blog
2. Look at the URL in your browser: `https://www.blogger.com/blog/posts/XXXXXXXXXXXXX`
3. The long number `XXXXXXXXXXXXX` is your **Blog ID**
4. Copy it! You'll need it as: `BLOGGER_BLOG_ID`

**Example:**
```
URL: https://www.blogger.com/blog/posts/1234567890123456789
Blog ID: 1234567890123456789
```

---

## Part 2: Google Cloud Console Setup (5 minutes)

### Step 1: Create Google Cloud Project
1. Go to: https://console.cloud.google.com
2. Click **"Select a project"** (top left, near "Google Cloud")
3. Click **"New Project"**
4. **Project name**: `ORM Publisher` (or any name)
5. Click **"Create"**
6. Wait 10 seconds for project to be created
7. Select your new project from the dropdown

### Step 2: Enable Blogger API
1. In the search bar at top, type: `Blogger API`
2. Click on **"Blogger API v3"**
3. Click **"Enable"** button
4. Wait for it to enable (takes 5 seconds)

### Step 3: Create OAuth Consent Screen
1. In left sidebar, click **"OAuth consent screen"**
   - Or search for "OAuth consent screen" in top search bar
2. Select **"External"** (unless you have Google Workspace)
3. Click **"Create"**

4. Fill in required fields:
   - **App name**: `ORM Publisher`
   - **User support email**: Your email (select from dropdown)
   - **Developer contact email**: Your email
5. Click **"Save and Continue"**

6. **Scopes page**: Click **"Add or Remove Scopes"**
   - Search for: `blogger`
   - Check the box for: `https://www.googleapis.com/auth/blogger`
   - Click **"Update"**
   - Click **"Save and Continue"**

7. **Test users page**: Click **"Add Users"**
   - Enter your Gmail address
   - Click **"Add"**
   - Click **"Save and Continue"**

8. **Summary page**: Click **"Back to Dashboard"**

### Step 4: Create OAuth Credentials
1. In left sidebar, click **"Credentials"**
2. Click **"+ Create Credentials"** (top)
3. Select **"OAuth client ID"**

4. **Application type**: Select **"Desktop app"**
5. **Name**: `ORM Publisher Desktop`
6. Click **"Create"**

7. **A popup appears** with your credentials:
   - **Client ID**: Starts with something like `123456789-abc.apps.googleusercontent.com`
   - **Client Secret**: Random string like `GOCSPX-abc123xyz`
   - Copy both! Or click **"Download JSON"** to save them

**Save these as:**
- `BLOGGER_CLIENT_ID` = Your Client ID
- `BLOGGER_CLIENT_SECRET` = Your Client Secret

---

## Part 3: Get Refresh Token (3 minutes)

### Step 1: Create Python Script
1. In your orm-automation folder, create file: `get_blogger_token.py`
2. Copy this code into it:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Blogger API scope
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Your OAuth credentials from Google Cloud Console
CLIENT_ID = "YOUR_CLIENT_ID_HERE"  # Replace with your actual Client ID
CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"  # Replace with your actual Client Secret

# Create credentials dict
credentials = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

# Save to file
with open('credentials.json', 'w') as f:
    json.dump(credentials, f)

# Run OAuth flow
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

print("\n" + "="*60)
print("SUCCESS! Your Refresh Token:")
print("="*60)
print(creds.refresh_token)
print("="*60)
print("\nSave this as: BLOGGER_REFRESH_TOKEN")
```

3. **IMPORTANT:** Replace these lines with your actual values:
   - Line 7: `CLIENT_ID = "your-actual-client-id.apps.googleusercontent.com"`
   - Line 8: `CLIENT_SECRET = "your-actual-client-secret"`

### Step 2: Install Required Library
```bash
pip install google-auth-oauthlib
```

### Step 3: Run the Script
```bash
python get_blogger_token.py
```

**What happens:**
1. Browser opens automatically
2. Google asks you to sign in (if not already)
3. Shows: "Google hasn't verified this app" warning
   - Click **"Advanced"**
   - Click **"Go to ORM Publisher (unsafe)"**
4. Shows: "ORM Publisher wants to access your Google Account"
   - Click **"Allow"**
5. Browser shows: "The authentication flow has completed"
6. Terminal shows your **Refresh Token**

**Copy the refresh token!** Save as: `BLOGGER_REFRESH_TOKEN`

---

## Part 4: Add All 4 Secrets

You now have all 4 Blogger secrets:

1. `BLOGGER_BLOG_ID` = From Part 1 (the long number)
2. `BLOGGER_CLIENT_ID` = From Part 2 Step 4 (ends with .apps.googleusercontent.com)
3. `BLOGGER_CLIENT_SECRET` = From Part 2 Step 4 (starts with GOCSPX-)
4. `BLOGGER_REFRESH_TOKEN` = From Part 3 (long string from the script)

### Add to GitHub:
1. Go to: `https://github.com/YOUR_USERNAME/orm-automation/settings/secrets/actions`
2. Click **"New repository secret"** for each:
   - Name: `BLOGGER_BLOG_ID` → Value: [your blog ID]
   - Name: `BLOGGER_CLIENT_ID` → Value: [your client ID]
   - Name: `BLOGGER_CLIENT_SECRET` → Value: [your client secret]
   - Name: `BLOGGER_REFRESH_TOKEN` → Value: [your refresh token]

### Add to Local .env (for testing):
Open `.env` file and add:
```
BLOGGER_BLOG_ID=your_blog_id_here
BLOGGER_CLIENT_ID=your_client_id_here
BLOGGER_CLIENT_SECRET=your_client_secret_here
BLOGGER_REFRESH_TOKEN=your_refresh_token_here
```

---

## Test It!

```bash
# Test locally first
python publish.py --day 3

# Check if it published to Blogger
# Go to: https://YOUR_BLOG.blogspot.com
```

---

## Troubleshooting

### "Google hasn't verified this app"
- This is normal for personal OAuth apps
- Click "Advanced" → "Go to ORM Publisher (unsafe)"
- It's safe - it's YOUR app

### "Access blocked: This app's request is invalid"
- Make sure you added your email as a Test User in OAuth consent screen
- Make sure Blogger API is enabled

### "Invalid grant" error
- Your refresh token may have expired
- Re-run `get_blogger_token.py` to get a new one

### "Blog not found"
- Double-check your Blog ID
- Make sure you're using the blog ID (number), not the blog URL

---

## Summary

**4 Blogger Secrets:**
1. Blog ID → From Blogger dashboard URL
2. Client ID → From Google Cloud Console OAuth credentials
3. Client Secret → From Google Cloud Console OAuth credentials
4. Refresh Token → From running the Python script

**Once added:** Your articles will auto-publish to Blogger (Google's platform with DA ~95)!

---

## Quick Reference Links

- Blogger: https://www.blogger.com
- Google Cloud Console: https://console.cloud.google.com
- OAuth Consent Screen: https://console.cloud.google.com/apis/credentials/consent
- Credentials: https://console.cloud.google.com/apis/credentials

Need help? Check the script output or re-run any step!
