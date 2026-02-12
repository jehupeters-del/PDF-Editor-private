# Streamlit Deployment Guide

This branch is prepared for Streamlit Community Cloud deployment while preserving the Flask/PythonAnywhere deployment path in main.

## 1) Branch Safety (Do This First)

```bash
git checkout -b migration/streamlit-full-parity
```

Use this branch (or your own Streamlit branch) for deployment, and keep `main` reserved for PythonAnywhere.

## 2) Local Smoke Test

```bash
pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Open `http://localhost:8501` and verify:
- Upload one or more PDFs
- Select/remove pages from a loaded PDF
- Merge and download
- Extract questions (single and batch)
- Validate questions (single and batch)

## 3) Streamlit Community Cloud Settings

When creating the app:
- **Repository**: your GitHub repo
- **Branch**: your Streamlit branch
- **Main file path**: `streamlit_app.py`
- **Python version**: leave default unless you need a specific pin

## 4) Why Prior Deployment Failed

Your previous deployment used `app.py` as the main module. That starts Flask's development server inside Streamlit's runner, causing runtime conflicts and the `signal only works in main thread` crash.

Use `streamlit_app.py` as the entrypoint for Streamlit Cloud.

## 5) Notes for Existing PythonAnywhere Deployment

- Keep current PythonAnywhere config pointing at Flask app and WSGI setup.
- Do not replace WSGI entrypoint with Streamlit files.
- Merge this branch into main only when you intentionally switch deployment strategy.

## 6) Troubleshooting

### App does not start
- Confirm main file path is exactly `streamlit_app.py`.
- Check logs for missing packages and confirm `requirements.txt` installed.

### Upload issues
- Streamlit upload limit is configured in `.streamlit/config.toml` (`maxUploadSize = 50`).

### PyMuPDF install issues
- Re-deploy once (transient wheel/build issue sometimes resolves).
- If needed later, add a `packages.txt` with required system libs.
