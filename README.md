# ShopGenie — AI Shopping Assistant

**Live Frontend (Firebase Hosting): [https://amd-slingshot-cec69.web.app](https://amd-slingshot-cec69.web.app)**
**Live Backend API (Google Cloud Run): [https://shopgenie-hy7jpqxcsa-uc.a.run.app](https://shopgenie-hy7jpqxcsa-uc.a.run.app)**

---

## Overview
ShopGenie is a multimodal AI-powered shopping assistant built as a fast, accessible single-page web application. It leverages Gemini 1.5 Flash to allow users to search for products using natural language queries (e.g., *"dinosaur toys under ₹800"*) or by uploading an image to find visually and functionally similar items from the catalog.

## Key Features
- **Multimodal AI Search**: Grounded product recommendations using Gemini 1.5 Flash models (Text and Vision).
- **Real‑time Shopping Cart**: Leverages Firebase Firestore real-time listeners (`onSnapshot`) to instantly update cart states across sessions.
- **Secure Architecture**: Google Sign-In authentication on the frontend with strict Firebase ID token verification middleware on the FastAPI backend.
- **Serverless Scale-to-Zero Deployment**: A reliable Python FastAPI application deployed on Google Cloud Run, with a lightweight, responsive frontend distributed via Firebase Hosting.

## Technology Stack
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (Google Material Design styling)
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: Google Cloud Firestore (Native Mode)
- **Cloud & AI**: Google Gemini API, Firebase Auth, Google Cloud Run, Firebase Hosting
