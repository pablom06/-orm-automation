# Substack Cookie Auth Setup

Substack disabled password login for most accounts (they use magic links now).
The fix is to use a **session cookie** instead — works the same way for the API.

Cookies last ~30 days. When yours expires, just repeat these steps to refresh.

---

## Step 1 — Log into Substack in your browser

1. Open Chrome, Firefox, or Edge
2. Go to [substack.com](https://substack.com) and log in (magic link or however you normally do)
3. Once logged in, navigate to your publication: `https://paulmriv.substack.com`

---

## Step 2 — Open DevTools

- **Chrome / Edge**: Press `F12` or right-click anywhere → **Inspect**
- **Firefox**: Press `F12` or right-click → **Inspect**

---

## Step 3 — Find the cookie

### Chrome / Edge:

1. Click the **Application** tab in DevTools (top bar)
2. In the left sidebar, expand **Cookies**
3. Click on `https://substack.com`
4. In the list of cookies, find the row named **`substack.sid`**
5. **Double-click the value** column for that row to select it
6. Copy the value (it's a long string starting with `s%3A` or similar)

### Firefox:

1. Click the **Storage** tab in DevTools
2. Expand **Cookies** → click `https://substack.com`
3. Find the row named `substack.sid`
4. Copy the **Value** column

---

## Step 4 — Add it as a GitHub secret

1. Go to your repo → **Settings → Secrets and variables → Actions**
2. If `SUBSTACK_COOKIE` already exists, click it → **Update secret**
3. If it doesn't, click **New repository secret**
   - Name: `SUBSTACK_COOKIE`
   - Value: paste the long string from Step 3
4. Click **Add secret** / **Update secret**

---

## Step 5 — Test it

1. Go to your repo → **Actions → Auto-Publish ORM Content → Run workflow**
2. Check the box: **"Run Substack diagnostic test only"**
3. Click **Run workflow**
4. Wait ~30 seconds, open the run, expand the publisher step
5. Look for `✅ Published to Substack:` in the log

If it works: the next daily run will auto-publish to Substack alongside everything else.

If it fails: paste the log output here and we'll debug.

---

## When the cookie expires

You'll see Substack publishes start failing again. Just repeat Steps 1-4 to grab a fresh cookie. Takes 60 seconds.

To avoid surprise expiration, mark your calendar to refresh the cookie every 3-4 weeks.
