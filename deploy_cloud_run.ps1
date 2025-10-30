# deploy_cloud_run.ps1
# Deploy the Streamlit app to Cloud Run (recommended for web apps)

param(
    [string]$PROJECT = "wfargo-cdo25cbh-915",
    [string]$REGION = "us-central1",
    [string]$IMAGE = "gcr.io/wfargo-cdo25cbh-915/data-profiling-ai:latest",
    [string]$SERVICE = "data-profiling-ai",
    [string]$BUCKET = "synthetic-data-194769473145"
)

Write-Host "Using project: $PROJECT, region: $REGION, image: $IMAGE"

# Make sure gcloud is authenticated and configured
gcloud auth login
gcloud config set project $PROJECT

# Enable Cloud Run API (if not already enabled)
gcloud services enable run.googleapis.com

# Configure docker to use gcloud credentials for pushing to GCR
gcloud auth configure-docker --quiet

# Build the container image
docker build -t $IMAGE .

# Push the image to Container Registry
docker push $IMAGE

# Deploy to Cloud Run
gcloud run deploy $SERVICE \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT,DEFAULT_BUCKET=$BUCKET,PORT=8080,HOST=0.0.0.0"

Write-Host "Deployment complete. Visit the URL shown by gcloud run deploy to open your app."