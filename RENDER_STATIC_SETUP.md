# 🚀 Render Static Assets: The "Zero-Python" Strategy

To achieve maximum efficiency on the Free Tier (512MB RAM), we must stop Python from serving images/CSS. Render's Nginx layer can do this 100x faster.

## Option A: Render "Static Site" Service (Recommended)
This approach completely decouples assets from your API.

1.  **Create a New Web Service** in Render.
2.  Connect the same GitHub Repo.
3.  **Name:** `jorge-web-assets` (or similar).
4.  **Root Directory:** `core/static`.
5.  **Environment:** `Static Site`.
6.  **Build Command:** `echo "Assets ready"` (or leave empty).
7.  **Publish Directory:** `.`.

**Outcome:** You get a URL like `https://jorge-web-assets.onrender.com`.
**Action:** Update `settings.STATIC_URL` in your `.env` to point to this new URL.

## Option B: Nginx Header Rules (Advanced)
If you stick to the Docker service:

1.  Go to your Service **Settings** > **Headers**.
2.  Add a rule:
    *   **Path:** `/static/*`
    *   **Name:** `Cache-Control`
    *   **Value:** `public, max-age=31536000, immutable`

*Note: This still involves Python serving the bytes, but Nginx might cache it if configured correctly. Option A is superior.*

## Option C: Cloudflare R2 / S3 (Pro Level)
1.  Upload `core/static` folder to a bucket (R2 is free mostly).
2.  Point your `.env` `STATIC_URL` to the bucket URL.

---
**✅ Current Status:**
We have removed the heavy `CachedStaticFiles` Python class. The app now uses standard `StaticFiles` as a fallback, but for production speed, **Option A** is the target.
