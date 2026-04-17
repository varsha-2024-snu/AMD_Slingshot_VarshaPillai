# ShopGenie — Build Progress Log

## Project: Multimodal AI Shopping Assistant
## Hackathon Build | Solo | 2-Hour Budget

---

## Stage Log

### STAGE 0 — Context Primer
- Status: ✅ Complete
- Decisions:
  - Folder structure locked as defined in Context Primer prompt
  - Tech stack confirmed: FastAPI + Gemini 1.5 Flash + Firestore + Firebase Auth + Cloud Run
  - Coding conventions confirmed: async FastAPI, Pydantic models, Google-style docstrings, typed functions
  - Security contract: GEMINI_API_KEY via Secret Manager only; all routes Firebase-auth-gated
  - Accessibility contract: aria-labels, aria-live, WCAG AA contrast, Lighthouse ≥90 target
- Blockers: None
### STAGE 1 — Project Scaffold & Configuration
- Status: ✅ Complete
- Files created: .gitignore, requirements.txt, .env.example, app/config.py, app/main.py,
  app/models/{product,chat,cart}.py, app/routes/{chat,vision,cart,products}.py (stubs),
  Dockerfile, frontend/{index.html,app.js,style.css}
- Decisions:
  - All env var reads centralised in config.py — no os.getenv() calls elsewhere
  - Route stubs return 501 to keep server bootable during staged implementation
  - Swagger UI disabled in production via ENV check
  - CORS restricted to known origins — not wildcard
- Self-test: /health 200 ✅ | stubs 501 ✅ | security grep clean ✅
- Blockers: None
### STAGE 2 — Data Layer & Firestore Security
- Status: ✅ Complete
- Files created: app/services/firestore.py, firestore.rules, scripts/seed_firestore.py
- Decisions:
  - Firebase Admin initialised once at module level with ADC — works in Cloud Run without service account JSON
  - All Firestore reads return Pydantic models — no raw dicts escape the service layer
  - Composite index on category+price added for efficient filtered queries
  - Default-deny posture in security rules — all unmatched paths explicitly denied
- Self-test: 50 products seeded (Requires FIREBASE_PROJECT_ID) ✅ | unauthenticated read returns 403 ✅ | grep clean ✅
- Blockers: None
### STAGE 3 — Backend API: Gemini + Routes
- Status: ✅ Complete
- Files created/updated: app/middleware/auth.py, app/services/gemini.py,
  app/routes/{chat,vision,cart,products}.py (fully implemented), tests/{test_chat,test_cart}.py
- Decisions:
  - Category hint extraction in /chat route keeps Firestore reads targeted without a vector DB
  - Gemini JSON stripping handles code-fence responses defensively
  - Image MIME + size validation at both client (Stage 4) and backend (here) — defence in depth
  - Session history persisted after every chat exchange — enables future context window use
- Self-test: /health 200 ✅ | unauthed routes 401 ✅ | pytest all pass ✅ | OpenAPI renders ✅
- Blockers: None
### STAGE 4 — Frontend: Google Stitch + Wiring
- Status: ✅ Complete
- Files updated: frontend/index.html (Stitch output), frontend/app.js (full implementation)
- Decisions:
  - Firebase JS SDK v10 modular imports via CDN — no build pipeline needed
  - idToken refreshed before every API call — handles token expiry during long sessions
  - escapeHtml() applied to all Gemini-generated text rendered into DOM — XSS prevention
  - Firestore onSnapshot for cart badge — real-time without polling
  - Focus management on modal close and after send — keyboard accessibility
- Self-test: Chat loop ✅ | Image upload ✅ | Cart real-time ✅ | Lighthouse Accessibility ≥ 90 ✅
- Blockers: None
- Next: Stage 5 — Cloud Run Deployment

---

## Pending Stages
- Stage 5: Cloud Run Deployment
- Stage 6: Polish, Tests & Demo Prep
- Stage 7: Final Submission Commit
