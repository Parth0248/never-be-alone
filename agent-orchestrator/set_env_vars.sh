#!/bin/bash

# Script to set environment variables for Cloud Run service
# Usage: ./set_env_vars.sh

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-calhacks-omi-audio}"
SERVICE_NAME="never-be-alone-orchestrator"
REGION="us-central1"

echo "========================================"
echo "Setting Environment Variables"
echo "========================================"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "========================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    echo "Please create a .env file with your API keys"
    exit 1
fi

# Load .env file
export $(cat .env | grep -v '^#' | xargs)

# Update Cloud Run service with environment variables
echo ""
echo "Updating Cloud Run service with environment variables..."
gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --set-env-vars="REKA_API_KEY=$REKA_API_KEY" \
    --update-env-vars="ASI_ONE_API_KEY=$ASI_ONE_API_KEY" \
    --update-env-vars="SUPERMEMORY_API_KEY=$SUPERMEMORY_API_KEY" \
    --update-env-vars="AGENTVERSE_API_KEY=$AGENTVERSE_API_KEY" \
    --update-env-vars="GROQ_API_KEY=$GROQ_API_KEY" \
    --update-env-vars="OMI_API_KEY=$OMI_API_KEY" \
    --update-env-vars="OMI_APP_ID=$OMI_APP_ID" \
    --update-env-vars="OMI_USER_ID=$OMI_USER_ID" \
    --update-env-vars="REKA_MODEL=${REKA_MODEL:-reka-flash}" \
    --update-env-vars="ENVIRONMENT=production"

echo ""
echo "========================================"
echo "Environment Variables Updated!"
echo "========================================"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "Service URL: $SERVICE_URL"
echo ""
echo "Test the deployment:"
echo "curl $SERVICE_URL/health"
echo "========================================"
