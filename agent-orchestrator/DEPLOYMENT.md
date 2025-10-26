# Deployment Guide - Google Cloud Run

This guide will help you deploy the Never-Be-Alone Agent Orchestrator to Google Cloud Run.

---

## Prerequisites

1. **Google Cloud SDK** installed
   - Windows: https://cloud.google.com/sdk/docs/install
   - Already configured for project `calhacks-omi-audio`

2. **Environment Variables** (.env file)
   - All API keys configured (Reka, ASI:One, Supermemory, etc.)

3. **Docker** (optional, Cloud Build will handle it)

---

## Quick Deploy (Recommended)

### Windows (PowerShell)

```powershell
cd D:\Projects\never-be-alone\agent-orchestrator
.\deploy.ps1
```

### Linux/Mac

```bash
cd agent-orchestrator
chmod +x deploy.sh
./deploy.sh
```

This will:
1. Build your container using Cloud Build
2. Deploy to Cloud Run
3. Configure auto-scaling (0-10 instances)
4. Set up 300-second timeout (for ASI:One)
5. Provide public HTTPS endpoint

---

## Manual Deployment Steps

### 1. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project calhacks-omi-audio
```

### 2. Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Build Container

```bash
cd agent-orchestrator
gcloud builds submit --tag gcr.io/calhacks-omi-audio/never-be-alone-orchestrator
```

### 4. Deploy to Cloud Run

```bash
gcloud run deploy never-be-alone-orchestrator \
    --image gcr.io/calhacks-omi-audio/never-be-alone-orchestrator \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "ENVIRONMENT=production,PORT=8080"
```

### 5. Set Environment Variables (API Keys)

**Option A: From .env file (Recommended)**

```bash
chmod +x set_env_vars.sh
./set_env_vars.sh
```

**Option B: Manual**

```bash
gcloud run services update never-be-alone-orchestrator \
    --region us-central1 \
    --set-env-vars="REKA_API_KEY=your_key_here" \
    --update-env-vars="ASI_ONE_API_KEY=your_key_here" \
    --update-env-vars="SUPERMEMORY_API_KEY=your_key_here" \
    --update-env-vars="AGENTVERSE_API_KEY=your_key_here" \
    --update-env-vars="GROQ_API_KEY=your_key_here" \
    --update-env-vars="OMI_API_KEY=your_key_here" \
    --update-env-vars="OMI_APP_ID=your_app_id" \
    --update-env-vars="OMI_USER_ID=your_user_id"
```

---

## Configuration Details

### Cloud Run Settings

| Setting | Value | Reason |
|---------|-------|--------|
| **Memory** | 2Gi | Handle Reka + ASI:One processing |
| **CPU** | 2 | Parallel processing of requests |
| **Timeout** | 300s | ASI:One can take 45-60s |
| **Concurrency** | 80 | Multiple users simultaneously |
| **Min Instances** | 0 | Cost optimization (scales to 0) |
| **Max Instances** | 10 | Handle spike traffic |

### Why Google Cloud Run?

✅ **Perfect for Webhooks**
- Public HTTPS endpoint automatically
- Auto-scaling based on traffic
- Pay only for actual usage

✅ **Handles Long Requests**
- Timeout up to 5 minutes (ASI:One needs 45-60s)
- No cold start issues with min-instances=1

✅ **Easy Management**
- No server management required
- Automatic SSL certificates
- Built-in load balancing

---

## Post-Deployment

### 1. Get Service URL

```bash
gcloud run services describe never-be-alone-orchestrator \
    --region us-central1 \
    --format 'value(status.url)'
```

### 2. Test Health Endpoint

```bash
curl https://your-service-url.run.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "agent-orchestrator",
  "environment": "production"
}
```

### 3. Test Orchestration Endpoint

```bash
curl -X POST https://your-service-url.run.app/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "transcription": "Remind me tomorrow at 2pm to call mom",
    "context": {
      "uid": "test_user",
      "timestamp": "2025-10-26T10:00:00Z",
      "source": "omi_devkit"
    }
  }'
```

### 4. Configure Omi Webhook

Update your Omi app configuration to point to:
```
https://your-service-url.run.app/orchestrate
```

---

## Monitoring

### View Logs

```bash
gcloud run services logs read never-be-alone-orchestrator \
    --region us-central1 \
    --limit 100
```

### View Metrics

```bash
# Open Cloud Console
gcloud run services browse never-be-alone-orchestrator --region us-central1
```

Or visit: https://console.cloud.google.com/run

---

## Updating the Service

### Deploy New Version

```bash
# Make your code changes, then:
cd agent-orchestrator
./deploy.ps1  # or ./deploy.sh
```

Cloud Run will:
1. Build new container
2. Deploy with zero downtime
3. Route traffic gradually to new version

### Rollback to Previous Version

```bash
gcloud run services update-traffic never-be-alone-orchestrator \
    --region us-central1 \
    --to-revisions PREVIOUS_REVISION=100
```

---

## Troubleshooting

### Issue: Build Fails

**Check:**
- All dependencies in requirements.txt
- Dockerfile syntax
- Build logs: `gcloud builds list`

### Issue: Service Crashes

**Check logs:**
```bash
gcloud run services logs read never-be-alone-orchestrator --region us-central1
```

**Common causes:**
- Missing environment variables
- API key issues
- Memory limit exceeded (increase to 4Gi)

### Issue: Timeout Errors

**Increase timeout:**
```bash
gcloud run services update never-be-alone-orchestrator \
    --region us-central1 \
    --timeout 600  # 10 minutes
```

### Issue: Cold Start Latency

**Set minimum instances:**
```bash
gcloud run services update never-be-alone-orchestrator \
    --region us-central1 \
    --min-instances 1
```

---

## Cost Optimization

### Current Configuration Cost Estimate

- **Min instances: 0** - No cost when idle
- **Memory: 2Gi** - $0.00000250 per GB-second
- **CPU: 2** - $0.00002400 per vCPU-second
- **Requests: 1M/month** - First 2M requests free

**Estimated cost:** ~$10-30/month for demo usage

### Reduce Costs

1. Keep min-instances=0 (scales to zero)
2. Reduce memory to 1Gi if possible
3. Set max-instances limit
4. Use CPU throttling

---

## Security

### Current Setup
- ✅ Public endpoint (required for webhooks)
- ✅ HTTPS automatically enabled
- ✅ Environment variables encrypted at rest
- ✅ Container runs as non-root

### Additional Security (Optional)

**Add Authentication:**
```bash
gcloud run services update never-be-alone-orchestrator \
    --region us-central1 \
    --no-allow-unauthenticated
```

**Use Secret Manager for API keys:**
```bash
# Store secret
gcloud secrets create reka-api-key --data-file=-
# Grant access
gcloud secrets add-iam-policy-binding reka-api-key \
    --member=serviceAccount:YOUR_SERVICE_ACCOUNT \
    --role=roles/secretmanager.secretAccessor
```

---

## Next Steps

1. ✅ Deploy service
2. ✅ Test endpoints
3. ✅ Configure Omi webhook
4. ✅ Monitor logs
5. ✅ Set up alerts (optional)

---

## Support

**Documentation:**
- Cloud Run: https://cloud.google.com/run/docs
- Project README: ../README.md
- Architecture: ../docs/ASI_ONE_AGENTIC_INTEGRATION.md

**Troubleshooting:**
- Check logs first
- Verify environment variables
- Test each API independently

---

**Deployment Status:** Ready for Production ✅
**Last Updated:** October 26, 2025
