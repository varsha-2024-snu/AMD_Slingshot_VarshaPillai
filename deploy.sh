#!/bin/bash
set -e

echo "🚀 Starting ShopGenie Deployment"

# Configuration
export PROJECT_ID="amd-slingshot-cec69"
export REGION="us-central1"
export SERVICE_NAME="shopgenie"
export GEMINI_API_KEY="AIzaSyBzoZeW5Ozwlq09qY1KKue-ssV_-D7IxzM"

# 1. Update Cloud Run URL in frontend/app.js (placeholder for now, will override after deploy)
echo "📡 Preparing frontend configuration..."
# We will use the Cloud Run URL once we have it. For now, deploying the backend.

# 2. Build and Push Container
echo "📦 Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME --project $PROJECT_ID

echo "✅ Image built: gcr.io/$PROJECT_ID/$SERVICE_NAME"

# 3. Create or update Secret Manager for Gemini API Key
echo "🔐 Configuring secrets..."
# Check if secret exists
if gcloud secrets describe gemini-api-key --project $PROJECT_ID >/dev/null 2>&1; then
    echo "Updating existing secret..."
    echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=- --project $PROJECT_ID
else
    echo "Creating new secret..."
    echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- --project $PROJECT_ID
fi

# Need to grant Cloud Run access to the secret
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project $PROJECT_ID

# 4. Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --set-env-vars FIREBASE_PROJECT_ID=$PROJECT_ID,GCS_BUCKET_NAME=${SERVICE_NAME}-images,ENV=production \
  --min-instances 0 \
  --max-instances 3 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --concurrency 80 \
  --project $PROJECT_ID

# Capture URL
export SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)")
echo "🌟 Backend deployed: $SERVICE_URL"

# 5. Update frontend with the actual Cloud Run URL
echo "📝 Updating API_BASE in frontend..."
sed -i '' "s|https://YOUR_CLOUD_RUN_URL/api/v1|${SERVICE_URL}/api/v1|g" frontend/app.js

# Also update the CORS origins in backend for the final URL
sed -i '' "s|https://shopgenie-xxxx-uc.a.run.app|${SERVICE_URL}|g" app/main.py

echo "🔄 Re-deploying backend with updated CORS..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME --project $PROJECT_ID
gcloud run deploy $SERVICE_NAME --image gcr.io/$PROJECT_ID/$SERVICE_NAME --platform managed --region $REGION --project $PROJECT_ID

# 6. Deploy Frontend
echo "🌐 Deploying to Firebase Hosting..."
firebase deploy --only hosting --project $PROJECT_ID

echo "🎉 Deployment Complete!"
echo "Backend: $SERVICE_URL"
echo "Frontend: https://$PROJECT_ID.web.app"
