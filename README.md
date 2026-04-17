# ShopGenie 🧞 — Multimodal AI Shopping Assistant

> An embeddable, Google-powered shopping assistant that understands what you *actually* want — in text or images — and finds the right product from any retailer's catalog instantly.

**Live Demo:** [https://amd-slingshot-cec69.web.app](https://amd-slingshot-cec69.web.app)  
**Cloud Run API:** [https://shopgenie-hy7jpqxcsa-uc.a.run.app](https://shopgenie-hy7jpqxcsa-uc.a.run.app)

---

## Google Services Used

| Service | Role |
|---|---|
| **Gemini 1.5 Flash** | NLP intent resolution + vision-based product matching |
| **Firestore** | Product catalog, cart state, session history, security rules |
| **Firebase Auth** | Google Sign-In; UID scopes all Firestore user data |
| **Cloud Run** | Containerised FastAPI backend — HTTPS, scale-to-zero |
| **Secret Manager** | `GEMINI_API_KEY` injected at runtime, never in source code |
| **Cloud Storage** | Product image hosting, free intra-region egress |
| **Firebase Hosting** | CDN-cached frontend delivery |

---

## Architecture
Stitch Frontend → Firebase Auth → Cloud Run (FastAPI)
├── Gemini 1.5 Flash (text + vision)
└── Firestore (products, carts, sessions)

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/varsha-2024-snu/AMD_Slingshot_VarshaPillai

# 2. Create .env from the template
cp .env.example .env
# Fill in GEMINI_API_KEY, FIREBASE_PROJECT_ID, GCS_BUCKET_NAME

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed the product catalog (one-time)
python scripts/seed_firestore.py

# 5. Start the backend
uvicorn app.main:app --reload --port 8080

# 6. Serve the frontend
cd frontend && python3 -m http.server 5500

# Open http://localhost:5500
```

## Run Tests

```bash
pytest tests/ -v
```

## Deployment

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/shopgenie
gcloud run deploy shopgenie --image gcr.io/PROJECT_ID/shopgenie \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --set-env-vars FIREBASE_PROJECT_ID=PROJECT_ID \
  --region us-central1 --memory 512Mi --cpu 1
```

## Evaluation Criteria Coverage

| Criterion | Implementation |
|---|---|
| **Code Quality** | FastAPI + Pydantic typed models, Google-style docstrings, service layer isolation |
| **Security** | Firebase Auth on all routes, Firestore security rules, Secret Manager for API key, input validation |
| **Efficiency** | Gemini Flash (fastest model), indexed Firestore queries, Cloud Run scale-to-zero |
| **Testing** | pytest unit tests: prompt construction, cart validation, response parsing |
| **Accessibility** | ARIA labels, aria-live regions, WCAG AA contrast, keyboard nav, Lighthouse ≥90 |
| **Google Services** | Gemini + Firestore + Auth + Cloud Run + Secret Manager + GCS + Firebase Hosting |
