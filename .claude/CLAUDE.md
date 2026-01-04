# Blueshield AI Project Context

## GCP Project
- **Project ID**: `blueshield-ai`
- **Region**: `us-central1`
- **BigQuery Dataset**: `blueshield_data`
- **Storage Bucket**: `gs://blueshield-ai-data`

## Deployment

### Deploy Chat Function
```bash
gcloud functions deploy blueshield-chat \
  --project=blueshield-ai \
  --region=us-central1 \
  --runtime=python311 \
  --trigger-http \
  --allow-unauthenticated \
  --source=functions/chat \
  --entry-point=chat \
  --set-secrets=ANTHROPIC_API_KEY=anthropic-api-key:latest \
  --memory=256MB \
  --timeout=60s
```

### Set up Anthropic API Key (first time)
```bash
echo -n "your-api-key" | gcloud secrets create anthropic-api-key \
  --project=blueshield-ai \
  --data-file=-
```

## Team
- Landon Colvig (colviglandon@gmail.com) - Owner
- Jack Colvig (colvigjack@gmail.com) - Editor

## Resources
- Chat Cloud Function for scenario training
- BigQuery for analytics/logging (future)
- Cloud Storage for statute data (future)
