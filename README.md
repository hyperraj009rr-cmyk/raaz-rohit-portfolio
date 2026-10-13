# Rohit Raj — Creator Portfolio

## Features
- Premium responsive dark-blue design with animated intro and reveal effects
- Public portfolio and dynamic categories for projects, e-books, websites, apps, photos, videos, audio, trading and other creations
- Admin login/dashboard; upload cover and asset files; edit/delete; public/private; publish/unpublish
- Hire Me / Contact form with inbox and request status tracking
- Database fields reserved for future paid e-books; payment processing is NOT yet enabled

## Run on Windows PowerShell
1. Extract the ZIP and open PowerShell in this folder.
2. `py -m venv .venv`
3. `\.venv\Scripts\Activate.ps1`
4. `py -m pip install -r requirements.txt`
5. `py app.py`
6. Open http://127.0.0.1:5000
7. Admin: http://127.0.0.1:5000/admin/login

Local starter credentials: `admin` / `ChangeMe-123!`. Change them before deploying publicly by setting `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and a long random `SECRET_KEY` as environment variables. The `.env.example` is a reference file; this starter does not automatically load `.env`.

## Deployment notes
- Use HTTPS and a persistent disk/database for uploads and database. Some free hosts erase local files when restarting/redeploying.
- Before enabling paid e-books, implement buyer accounts, verified server-side payment webhooks, purchase entitlements, and protected/private storage. The current Paid setting intentionally locks an item rather than granting access.
- A website cannot guarantee blocking screenshots, screen recording, or photography from another device. Watermarks/access controls can discourage copying but not eliminate it.
- Before a broad public launch, add CSRF protection, rate limiting, backup strategy, and email/Telegram notifications.


## Google Drive persistence setup (Render)
The site design/templates are unchanged. This version can keep uploaded media and a JSON backup of database records in Google Drive, then restore the records when the local database is empty. Google Drive must be authorized once and the refresh token must be stored as a Render secret. This is a small-site backup approach, not a substitute for PostgreSQL for busy/multi-instance production deployments.

1. In Google Cloud, enable Google Drive API and configure the OAuth consent screen. For an External app in Testing, Google refresh tokens can expire after 7 days; set the app to In production for ongoing personal use (verification may depend on scopes/policy).
2. In the OAuth Client, add this exact **Authorized redirect URI**: `https://raj-rohit-portfolio.onrender.com/admin/drive/callback`. Keep the authorized JavaScript origin as `https://raj-rohit-portfolio.onrender.com`.
3. In Render → your service → Environment, add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from the OAuth client. Never commit these values to Git or share them in chat. Also set a strong `SECRET_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`.
4. Deploy the updated code. Log in to `/admin/login`, then visit `https://raj-rohit-portfolio.onrender.com/admin/drive/connect`. Choose the correct Google account and approve access.
5. The callback page displays a refresh token once. Copy it into Render Environment as `GOOGLE_REFRESH_TOKEN`, save, and allow redeploy. Never share the token.
6. New uploads are copied to Drive; the database backup is refreshed after requests. If Render starts with an empty database, the app attempts to restore records from Drive. Keep in mind a Google Drive connection is not active until all three environment variables are set.

If the app is deployed at a different domain, replace the callback URL in Google Cloud with that exact domain and use the matching `/admin/drive/callback` URL.
