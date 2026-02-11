#!/usr/bin/env python3
"""
Get Blogger Refresh Token
=========================
Run this once to get your Blogger refresh token for automated publishing.

Prerequisites:
    pip install google-auth-oauthlib

Usage:
    1. Replace CLIENT_ID and CLIENT_SECRET below with your values
    2. Run: python get_blogger_token.py
    3. Browser opens, sign in and authorize
    4. Copy the refresh token shown in terminal
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json

# =============================================================================
# STEP 1: Replace these with your values from Google Cloud Console
# =============================================================================

CLIENT_ID = "YOUR_CLIENT_ID_HERE"  # Replace with your Client ID
CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"  # Replace with your Client Secret

# =============================================================================
# Don't change anything below this line
# =============================================================================

# Blogger API scope
SCOPES = ['https://www.googleapis.com/auth/blogger']

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

# Validate input
if "YOUR_CLIENT_ID" in CLIENT_ID or "YOUR_CLIENT_SECRET" in CLIENT_SECRET:
    print("\n" + "="*60)
    print("ERROR: You need to replace CLIENT_ID and CLIENT_SECRET")
    print("="*60)
    print("\nEdit this file (get_blogger_token.py) and replace:")
    print("  Line 17: CLIENT_ID = \"your-actual-value\"")
    print("  Line 18: CLIENT_SECRET = \"your-actual-value\"")
    print("\nGet these from Google Cloud Console:")
    print("  https://console.cloud.google.com/apis/credentials")
    print("="*60)
    exit(1)

# Save credentials to file
with open('credentials.json', 'w') as f:
    json.dump(credentials, f)

print("\n" + "="*60)
print("Blogger OAuth Authentication")
print("="*60)
print("\nBrowser will open for authentication...")
print("1. Sign in with your Google account")
print("2. If you see 'Google hasn't verified this app':")
print("   - Click 'Advanced'")
print("   - Click 'Go to ORM Publisher (unsafe)'")
print("3. Click 'Allow' to grant access")
print("\nWaiting for authorization...")

try:
    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n" + "="*60)
    print("SUCCESS! Authentication Complete")
    print("="*60)
    print("\nYour Refresh Token:")
    print("-"*60)
    print(creds.refresh_token)
    print("-"*60)
    print("\nCopy this token and use it as:")
    print("  GitHub Secret: BLOGGER_REFRESH_TOKEN")
    print("  Local .env: BLOGGER_REFRESH_TOKEN=<token>")
    print("="*60)

    # Save to file as backup
    with open('blogger_refresh_token.txt', 'w') as f:
        f.write(creds.refresh_token)

    print("\nAlso saved to: blogger_refresh_token.txt")
    print("="*60)

except Exception as e:
    print("\n" + "="*60)
    print("ERROR during authentication:")
    print("="*60)
    print(str(e))
    print("\nTroubleshooting:")
    print("1. Make sure you added your email as Test User")
    print("2. Make sure Blogger API is enabled")
    print("3. Check your Client ID and Secret are correct")
    print("="*60)
