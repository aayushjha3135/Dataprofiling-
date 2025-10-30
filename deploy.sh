#!/bin/bash

# Check if required environment variables are set
if [[ -z "${PROJECT_ID}" ]]; then
    echo "ERROR: PROJECT_ID environment variable is not set"
    exit 1
fi

if [[ -z "${REGION}" ]]; then
    REGION="us-central1"
    echo "Using default region: ${REGION}"
fi

# Set variables
APP_NAME="data-profiling-ai"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${APP_NAME}"
SERVICE_ACCOUNT="vertex-ai@${PROJECT_ID}.iam.gserviceaccount.com"

# Build the Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME} .

# Push the image to Google Container Registry
echo "Pushing image to GCR..."
docker push ${IMAGE_NAME}

# Deploy to Vertex AI
echo "Deploying to Vertex AI..."
gcloud ai endpoints create \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --display-name=${APP_NAME}

# Get the endpoint ID from the previous command
ENDPOINT_ID=$(gcloud ai endpoints list \
    --region=${REGION} \
    --filter="displayName=${APP_NAME}" \
    --format="value(name)")

# Deploy the model to the endpoint
gcloud ai endpoints deploy-model ${ENDPOINT_ID} \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --model=${APP_NAME} \
    --display-name=${APP_NAME} \
    --container-image-uri=${IMAGE_NAME} \
    --service-account=${SERVICE_ACCOUNT} \
    --machine-type=n1-standard-2 \
    --min-replica-count=1 \
    --max-replica-count=3 \
    --config=vertex-config.json

echo "Deployment complete! Your application is now running on Vertex AI."
echo "Endpoint ID: ${ENDPOINT_ID}"