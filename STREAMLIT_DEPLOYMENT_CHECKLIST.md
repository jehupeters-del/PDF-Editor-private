# ✅ STREAMLIT DEPLOYMENT CHECKLIST

## Pre-Flight
- [ ] Working on Streamlit branch (not main)
- [ ] `streamlit_app.py` exists in repo root
- [ ] `requirements.txt` includes `streamlit`

## Local Verification
- [ ] `pip install -r requirements.txt`
- [ ] `python -m streamlit run streamlit_app.py`
- [ ] Upload/load PDFs works
- [ ] Page select/remove works
- [ ] Merge + download works
- [ ] Extract single + batch works
- [ ] Validate single + batch works

## Streamlit Cloud App Setup
- [ ] Repository selected correctly
- [ ] Branch set to Streamlit branch
- [ ] Main file path set to `streamlit_app.py`
- [ ] Deploy button clicked

## Post-Deploy Verification
- [ ] App loads with no startup traceback
- [ ] Editor tab works end-to-end
- [ ] Extract tab works end-to-end
- [ ] Validate tab works end-to-end
- [ ] Downloads return valid PDFs

## If Deployment Fails
- [ ] Confirm app is not pointed to `app.py`
- [ ] Check deployment logs for missing dependency
- [ ] Re-run deployment after confirming settings
- [ ] Review `STREAMLIT_DEPLOYMENT.md`
