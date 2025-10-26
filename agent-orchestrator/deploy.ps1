# Never-Be-Alone Agent Orchestrator Deployment Script (PowerShell)
# Deploys to Google Cloud Run

$ErrorActionPreference = "Stop"

# Configuration
$PROJECT_ID = if ($env:GOOGLE_CLOUD_PROJECT) { $env:GOOGLE_CLOUD_PROJECT } else { "calhacks-omi-audio" }
$SERVICE_NAME = "never-be-alone-orchestrator"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "========================================"
Write-Host "Deploying Never-Be-Alone to Cloud Run"
Write-Host "========================================"
Write-Host "Project: $PROJECT_ID"
Write-Host "Service: $SERVICE_NAME"
Write-Host "Region: $REGION"
Write-Host "========================================"

# Check if gcloud is installed
Write-Host ""
Write-Host "Checking gcloud installation..."
try {
    $null = Get-Command gcloud -ErrorAction Stop
} catch {
    Write-Host "ERROR: gcloud CLI not found"
    Write-Host "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Check authentication
Write-Host ""
Write-Host "Checking gcloud authentication..."
$authAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($authAccount)) {
    Write-Host "ERROR: Not authenticated with gcloud"
    Write-Host "Run: gcloud auth login"
    exit 1
}

# Set project
Write-Host ""
Write-Host "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Build container using Cloud Build
Write-Host ""
Write-Host "Building container image..."
gcloud builds submit --tag $IMAGE_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed"
    exit 1
}

# Deploy to Cloud Run
Write-Host ""
Write-Host "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --concurrency 80 `
    --min-instances 0 `
    --max-instances 10 `
    --set-env-vars "ENVIRONMENT=production" `
    --set-env-vars "PORT=8080"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Deployment failed"
    exit 1
}

# Get service URL
Write-Host ""
Write-Host "========================================"
Write-Host "Deployment Complete!"
Write-Host "========================================"
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"
Write-Host "Service URL: $SERVICE_URL"
Write-Host ""
Write-Host "Endpoints:"
Write-Host "  - GET  $SERVICE_URL/health"
Write-Host "  - POST $SERVICE_URL/orchestrate"
Write-Host ""
Write-Host "To set environment variables (API keys):"
Write-Host "gcloud run services update $SERVICE_NAME --region $REGION \"
Write-Host "  --set-env-vars=`"REKA_API_KEY=your_key,ASI_ONE_API_KEY=your_key,SUPERMEMORY_API_KEY=your_key`""
Write-Host ""
Write-Host "========================================"
