# API Setup Guide - Get Your Publishing Tokens

This guide shows you how to get API tokens for all 3 publishing platforms.

---

## Dev.to (Easiest - Takes 30 seconds)

Dev.to has the simplest API access. Here's how:

### Step 1: Create a Dev.to Account

1. Go to https://dev.to
2. Click "Create account" (top right)
3. Sign up with GitHub, Twitter, or email
4. Complete your profile

### Step 2: Generate API Key

1. Go to https://dev.to/settings/extensions
2. Scroll to "DEV Community API Keys"
3. Click "Generate API Key"
4. Give it a description: "ORM Content Publisher"
5. Copy the API key (it starts with a long random string)

### Step 3: Add to .env

Open your `.env` file and add:
```
DEVTO_TOKEN=your_api_key_here
```

**That's it!** Dev.to is ready to publish.

---

## Hashnode (Takes 2-3 minutes)

Hashnode also has straightforward API access.

### Step 1: Create a Hashnode Account

1. Go to https://hashnode.com
2. Click "Sign up"
3. Sign up with GitHub, Google, or email
4. Complete your profile

### Step 2: Create a Blog

1. Go to https://hashnode.com/onboard
2. Click "Create a new blog"
3. Choose a subdomain (e.g., `pablomrivera.hashnode.dev`)
4. Complete blog setup

### Step 3: Generate Personal Access Token

1. Go to https://hashnode.com/settings/developer
2. Click "Generate New Token"
3. Give it a name: "ORM Publisher"
4. Select scopes: **Check "Write articles"**
5. Click "Generate Token"
6. Copy the token (starts with `Bearer...` or similar)

### Step 4: Get Your Publication ID

1. Go to https://hashnode.com/settings/blogs
2. Click on your blog
3. Look at the URL or dashboard - you'll see your publication ID
4. OR: After first login, check your blog's dashboard for the ID

**Alternative method to get Publication ID:**
```python
# Run this Python script after getting your token
import requests

token = "your_hashnode_token_here"
query = """
{
  me {
    publications(first: 1) {
      edges {
        node {
          id
          title
          url
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://gql.hashnode.com",
    json={"query": query},
    headers={"Authorization": token}
)

print(response.json())
# Look for the "id" field in the response
```

### Step 5: Add to .env

Open your `.env` file and add:
```
HASHNODE_TOKEN=your_token_here
HASHNODE_PUBLICATION_ID=your_publication_id_here
```

**Done!** Hashnode is configured.

---

## LinkedIn (Semi-Automated)

LinkedIn doesn't have a free article publishing API for individuals. The system handles this semi-automatically:

### How It Works:

1. The script copies the article content to your clipboard
2. Opens LinkedIn article editor in your browser
3. You paste and publish (takes 60 seconds)

### No Setup Needed!

Just make sure:
- You're logged into LinkedIn in your default browser
- `AUTO_OPEN_LINKEDIN=true` in your `.env` file

---

## Medium (Optional - Has Restrictions)

Medium has restricted API access for many users. If you can't get a token, that's okay - Dev.to and Hashnode give you excellent coverage!

### If You Want to Try:

1. Go to https://medium.com/me/settings
2. Scroll to "Security and apps"
3. Look for "Integration tokens"
4. If you don't see it, Medium hasn't enabled API access for your account

### If You See It:

1. Generate a new token
2. Copy it
3. Add to `.env`:
   ```
   MEDIUM_TOKEN=your_token_here
   ```

---

## Testing Your Setup

Once you've added your tokens to `.env`, test them:

```bash
# Test with a dry run (won't actually publish)
python publish.py --dry-run --day 1

# Publish article 1 for real (test)
python publish.py --day 1
```

## Troubleshooting

### Dev.to Errors

**"Unauthorized"**: Your API key is incorrect. Regenerate it and update `.env`

**"Article already exists"**: Dev.to detected duplicate content. Each article can only be published once.

### Hashnode Errors

**"Unauthorized"**: Check your token in `.env`

**"Publication not found"**: Your `HASHNODE_PUBLICATION_ID` is wrong. Run the Python script above to get it.

**"Write permission denied"**: When generating your token, make sure you checked "Write articles" permission

### LinkedIn

**Browser doesn't open**: Check `AUTO_OPEN_LINKEDIN=true` in `.env`

**Clipboard copy fails**: The article is also saved to `logs/linkedin_day_N.md` - you can copy from there

---

## Quick Reference

| Platform | Where to Get Token | What to Add to .env |
|----------|-------------------|---------------------|
| **Dev.to** | https://dev.to/settings/extensions | `DEVTO_TOKEN=` |
| **Hashnode** | https://hashnode.com/settings/developer | `HASHNODE_TOKEN=` and `HASHNODE_PUBLICATION_ID=` |
| **LinkedIn** | N/A (manual) | `AUTO_OPEN_LINKEDIN=true` |
| **Medium** | https://medium.com/me/settings (if available) | `MEDIUM_TOKEN=` (optional) |

---

## Your Publishing Strategy

With Dev.to + Hashnode + LinkedIn configured, you'll publish:

- **60 unique articles**
- **Each to 3 platforms** = 180 total publishes
- **2 articles per day** = 6 publishes per day
- **Over 30 days**

This creates massive SEO coverage with content on 3 high-authority platforms!

---

Need help? Check the logs at `logs/publish.log` for detailed error messages.
