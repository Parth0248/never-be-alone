#!/bin/bash

# Never-Be-Alone Agent Orchestrator Deployment Script
# Deploys to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-calhacks-omi-audio}"
SERVICE_NAME="never-be-alone-orchestrator"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================"
echo "Deploying Never-Be-Alone to Cloud Run"
echo "========================================"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "========================================"

# Check if gcloud is authenticated
echo ""
echo "Checking gcloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "ERROR: Not authenticated with gcloud"
    echo "Run: gcloud auth login"
    exit 1
fi

# Set project
echo ""
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Build container using Cloud Build
echo ""
echo "Building container image..."
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "ENVIRONMENT=production" \
    --set-env-vars "PORT=8080"

# Get service URL
echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "Service URL: $SERVICE_URL"
echo ""
echo "Endpoints:"
echo "  - GET  $SERVICE_URL/health"
echo "  - POST $SERVICE_URL/orchestrate"
echo ""
echo "To set environment variables (API keys):"
echo "gcloud run services update $SERVICE_NAME --region $REGION \\"
echo "  --set-env-vars=\"REKA_API_KEY=your_key,ASI_ONE_API_KEY=your_key,SUPERMEMORY_API_KEY=your_key\""
echo ""
echo "========================================"
