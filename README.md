# Weather Dashboard

A Streamlit weather dashboard powered by the OpenWeatherMap API.

## Files

- `app.py` — the dashboard
- `requirements.txt` — Python dependencies
- `api-key.txt` — your OpenWeatherMap API key (just the raw key, nothing else). Kept out of git via `.gitignore`.

## Run locally

Make sure all three files are in the same folder, then:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push `app.py` and `requirements.txt` to a **public GitHub repo**. `.gitignore` excludes `api-key.txt` — don't commit it, since API keys should never be public.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **"Create app"** → **"Deploy a public app from GitHub"**.
4. Select your repo, branch, and set the main file path to `app.py`.
5. Since `api-key.txt` won't be in the repo, the deployed app needs another way to read the key. Easiest fix: in the Streamlit Cloud dashboard, go to **App settings → Secrets** and add:
   ```
   OWM_API_KEY = "your_key_here"
   ```
   then change `load_api_key()` in `app.py` to read `st.secrets["OWM_API_KEY"]` instead of the file — reading a plain `.txt` file works great locally, but Streamlit Cloud's filesystem resets on each deploy, so a secrets-based key is more reliable there.
6. Click **Deploy**.

## Note on your API key

New OpenWeatherMap keys can take up to a couple of hours to activate — if you get 401 errors right after generating it, wait a bit and try again.
