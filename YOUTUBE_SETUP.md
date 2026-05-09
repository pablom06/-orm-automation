# YouTube Auto-Upload Setup

One-time setup for the weekly YouTube auto-upload workflow.

## What this does

Every Monday at 11 AM EST, GitHub Actions will:
1. Pick the next article that hasn't been turned into a video
2. Generate a 90-120 second slideshow video with AI narration (Microsoft Edge TTS)
3. Upload to YouTube as **PRIVATE**
4. Email you a link to review

You then review and switch each video to **Public** in YouTube Studio. This avoids spam flags from auto-bulk uploading.

---

## Step 1 — Create your YouTube channel

1. Go to [youtube.com](https://youtube.com) and sign in with your Google account
2. Click your profile → **Create a channel**
3. Use the name **Pablo M. Rivera**
4. Customize the channel page with your photo and a brief bio

---

## Step 2 — Create a Google Cloud project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project** → **New Project**
3. Name it `pablo-rivera-orm` and click **Create**
4. Once created, make sure it's selected at the top of the page

---

## Step 3 — Enable YouTube Data API v3

1. In the Cloud Console, go to **APIs & Services → Library**
2. Search for **YouTube Data API v3**
3. Click on it → **Enable**

---

## Step 4 — Create OAuth credentials

1. Go to **APIs & Services → OAuth consent screen**
2. Choose **External** → Click **Create**
3. Fill in:
   - **App name**: Pablo Rivera ORM
   - **User support email**: your email
   - **Developer contact**: your email
4. Click **Save and Continue** through the rest (no scopes needed yet)
5. On the **Test users** step, add your own email as a test user
6. Click **Save and Continue**

7. Go to **APIs & Services → Credentials**
8. Click **+ Create Credentials → OAuth client ID**
9. Application type: **Web application**
10. Name: `oauthplayground`
11. Authorized redirect URIs — add: `https://developers.google.com/oauthplayground`
12. Click **Create**
13. **Copy the Client ID and Client Secret** — you'll need them next

---

## Step 5 — Get your refresh token

1. Go to [developers.google.com/oauthplayground](https://developers.google.com/oauthplayground)
2. Click the **gear icon** (top right) → check **Use your own OAuth credentials**
3. Paste your Client ID and Client Secret
4. Close the gear menu
5. In the left panel, scroll to **YouTube Data API v3** and select:
   - `https://www.googleapis.com/auth/youtube.upload`
6. Click **Authorize APIs**
7. Sign in with the Google account that owns your YouTube channel
8. Click **Allow** (you may see "unverified app" warning — click Advanced → Go to app)
9. You'll be returned to OAuth Playground with an authorization code
10. Click **Exchange authorization code for tokens**
11. **Copy the Refresh Token** — this is the long string under "Refresh token"

---

## Step 6 — Add the secrets to GitHub

Go to your repo → **Settings → Secrets and variables → Actions** → **New repository secret**

Add these three:

| Secret name | Value |
|---|---|
| `YT_CLIENT_ID` | The Client ID from Step 4 |
| `YT_CLIENT_SECRET` | The Client Secret from Step 4 |
| `YT_REFRESH_TOKEN` | The Refresh Token from Step 5 |

---

## Step 7 — Test it

Go to your repo → **Actions → YouTube Video Publish → Run workflow**

Optional inputs:
- **day** — leave blank to upload the next unvideoed article, or specify a day number (e.g., 2 to start with the Salesforce one)
- **dry_run** — check this first time to build the video without uploading

If you check "dry_run", it will build the video and you can download it from the workflow artifacts to preview before flipping the switch on real uploads.

---

## What to do after each weekly upload

1. You'll get an email from YouTube saying a video was uploaded as private
2. Click the link in the email — it opens YouTube Studio
3. Review the video (title, description, thumbnail)
4. If you want, edit the title or upload a custom thumbnail
5. Change visibility from **Private** to **Public**
6. Click **Save**

This whole review process takes about 2 minutes per week.

---

## Stopping or pausing

- **Pause uploads**: go to **Actions → YouTube Video Publish → ⋯ → Disable workflow**
- **Re-enable**: same menu, click **Enable workflow**
- **Skip a week**: just don't run the workflow that Monday — the cron will fire next week

---

## Troubleshooting

**"Quota exceeded"** — YouTube free tier allows ~6 video uploads per day. The weekly schedule is well under this.

**"Unauthorized" error** — refresh token expired. Repeat Step 5 to get a new one.

**"Video stuck on processing"** — normal for 1-2 minutes after upload. YouTube needs to re-encode.

**Video looks bad** — the slides and TTS quality can be tweaked in `make_video.py`. You can also disable auto-upload and just record yourself reading the generated scripts in `youtube_scripts/`.
