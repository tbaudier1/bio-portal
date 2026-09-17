# BIO — Business Intelligence Officer

Portal tile **14** (`bio-business-intelligence-officer`) for **Tereo, LLC**.

FastAPI on port **8504**, mount `/bio`, SSO cookie `portal_token_bio`, open `/healthz`, `VERSION=1`.

```bash
pip install -r requirements.txt
export PORTAL_SSO_PUBLIC_KEY="<EdDSA PEM>"
export BIO_STRIP_PREFIX=true
uvicorn bio.main:app --host 127.0.0.1 --port 8504
pytest -q
```

Deploy: [DEPLOY.md](DEPLOY.md).
