#!/usr/bin/env python3
"""
Get Tumblr Access Tokens
========================
Run this once to get your Tumblr OAuth tokens for automated publishing.

Prerequisites:
    pip install requests-oauthlib

Usage:
    1. Make sure Consumer Key and Secret are set below
    2. Run: python get_tumblr_tokens.py
    3. Browser opens, authorize the app
    4. Copy the complete callback URL and paste it
    5. Script will display your oauth_token and oauth_token_secret
"""

from requests_oauthlib import OAuth1Session
import webbrowser

# =============================================================================
# Your Tumblr OAuth Credentials
# =============================================================================

CONSUMER_KEY = "NNKVIBsxkeaD5LXGdIs9TgYd6aYsUcJ9LK7CLXgWJcipO6K0nu"
CONSUMER_SECRET = "Hm7gcCuKKwpmrKA2VadxB7kDl2hFkhw129o0dxwfdCH6ApzVLa"

# Tumblr OAuth URLs
REQUEST_TOKEN_URL = 'https://www.tumblr.com/oauth/request_token'
AUTHORIZE_URL = 'https://www.tumblr.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://www.tumblr.com/oauth/access_token'

# =============================================================================
# Don't change anything below this line
# =============================================================================

print("\n" + "="*60)
print("Tumblr OAuth Authentication")
print("="*60)

try:
    # Step 1: Get request token
    print("\nStep 1: Getting request token...")
    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri='http://localhost:8080/callback')

    fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    # Step 2: Get authorization
    print("Step 2: Getting authorization URL...")
    authorization_url = oauth.authorization_url(AUTHORIZE_URL)

    print("\n" + "="*60)
    print("STEP 2: Authorize the App")
    print("="*60)
    print("\nOpening browser to authorize...")
    print(f"If browser doesn't open, go to:\n{authorization_url}\n")

    webbrowser.open(authorization_url)

    print("\nAfter authorizing:")
    print("1. You'll be redirected to a URL")
    print("2. Copy the ENTIRE URL from your browser")
    print("3. Paste it below")
    print("\nExample URL:")
    print("http://localhost:8080/callback?oauth_token=xxx&oauth_verifier=yyy")

    print("\n" + "="*60)
    callback_url = input("Paste the full callback URL here: ").strip()

    # Parse verifier (handle both full URL and partial URL)
    # Remove fragment if present
    callback_url = callback_url.split("#")[0]

    if "oauth_verifier=" in callback_url:
        oauth_verifier = callback_url.split("oauth_verifier=")[1].split("&")[0]
    else:
        print("\n❌ ERROR: No oauth_verifier found in URL")
        print("Make sure you copied the complete URL after authorization")
        exit(1)

    print(f"Extracted verifier: {oauth_verifier[:20]}...")

    # Step 3: Get access tokens
    print("\nStep 3: Exchanging verifier for access tokens...")
    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=oauth_verifier
    )

    oauth_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
    oauth_token = oauth_tokens.get('oauth_token')
    oauth_token_secret = oauth_tokens.get('oauth_token_secret')

    print("\n" + "="*60)
    print("SUCCESS! Your Tumblr Access Tokens")
    print("="*60)
    print(f"\nOAuth Token:")
    print(oauth_token)
    print(f"\nOAuth Token Secret:")
    print(oauth_token_secret)
    print("\n" + "="*60)

    print("\nAdd these to your .env file:")
    print(f"TUMBLR_CONSUMER_KEY={CONSUMER_KEY}")
    print(f"TUMBLR_CONSUMER_SECRET={CONSUMER_SECRET}")
    print(f"TUMBLR_OAUTH_TOKEN={oauth_token}")
    print(f"TUMBLR_OAUTH_TOKEN_SECRET={oauth_token_secret}")

    print("\nAnd to your GitHub secrets:")
    print("  Name: TUMBLR_CONSUMER_KEY → Value: " + CONSUMER_KEY)
    print("  Name: TUMBLR_CONSUMER_SECRET → Value: " + CONSUMER_SECRET)
    print("  Name: TUMBLR_OAUTH_TOKEN → Value: " + oauth_token)
    print("  Name: TUMBLR_OAUTH_TOKEN_SECRET → Value: " + oauth_token_secret)

    print("\n" + "="*60)

    # Save to file
    with open('tumblr_tokens.txt', 'w') as f:
        f.write(f"TUMBLR_CONSUMER_KEY={CONSUMER_KEY}\n")
        f.write(f"TUMBLR_CONSUMER_SECRET={CONSUMER_SECRET}\n")
        f.write(f"TUMBLR_OAUTH_TOKEN={oauth_token}\n")
        f.write(f"TUMBLR_OAUTH_TOKEN_SECRET={oauth_token_secret}\n")

    print("\nTokens also saved to: tumblr_tokens.txt")
    print("="*60)

except ImportError:
    print("\n" + "="*60)
    print("ERROR: requests-oauthlib library not installed")
    print("="*60)
    print("\nPlease install it:")
    print("  pip install requests-oauthlib")
    print("="*60)
except Exception as e:
    print("\n" + "="*60)
    print("ERROR:")
    print("="*60)
    print(str(e))
    print("\nTroubleshooting:")
    print("1. Make sure you authorized the app in the browser")
    print("2. Make sure you copied the complete callback URL")
    print("3. Make sure your Consumer Key and Secret are correct")
    print("="*60)
