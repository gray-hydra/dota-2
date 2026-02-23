#!/bin/bash
set -e

# Load .env if exists (for local deploys)
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Configuration
SERVICE_NAME="${SERVICE_NAME:-my-app}"
REGION="${AWS_REGION:-us-west-2}"
IMAGE_LABEL="app"

# DynamoDB credentials (from .env or environment)
DYNAMO_KEY="${DYNAMODB_AWS_ACCESS_KEY_ID:?Set DYNAMODB_AWS_ACCESS_KEY_ID in .env or environment}"
DYNAMO_SECRET="${DYNAMODB_AWS_SECRET_ACCESS_KEY:?Set DYNAMODB_AWS_SECRET_ACCESS_KEY in .env or environment}"

echo "=== Building Docker image ==="
docker build --pull -t "$SERVICE_NAME" .

echo "=== Pushing to Lightsail ==="
IMAGE_TAG=$(aws lightsail push-container-image \
  --service-name "$SERVICE_NAME" \
  --label "$IMAGE_LABEL" \
  --image "$SERVICE_NAME" \
  --region "$REGION" \
  --query 'imageDigest' \
  --output text)

echo "Pushed image: $IMAGE_TAG"

echo "=== Deploying ==="
aws lightsail create-container-service-deployment \
  --service-name "$SERVICE_NAME" \
  --region "$REGION" \
  --containers "{
    \"app\": {
      \"image\": \"$IMAGE_TAG\",
      \"ports\": {
        \"5000\": \"HTTP\"
      },
      \"environment\": {
        \"DYNAMODB_TABLE\": \"items\",
        \"AWS_DEFAULT_REGION\": \"$REGION\",
        \"AWS_ACCESS_KEY_ID\": \"$DYNAMO_KEY\",
        \"AWS_SECRET_ACCESS_KEY\": \"$DYNAMO_SECRET\"
      }
    }
  }" \
  --public-endpoint "{
    \"containerName\": \"app\",
    \"containerPort\": 5000,
    \"healthCheck\": {
      \"path\": \"/health\",
      \"intervalSeconds\": 30,
      \"timeoutSeconds\": 5,
      \"healthyThreshold\": 2,
      \"unhealthyThreshold\": 2
    }
  }"

echo "=== Deployment started ==="
echo "Check status: aws lightsail get-container-services --service-name $SERVICE_NAME --region $REGION"
echo "View logs: aws lightsail get-container-log --service-name $SERVICE_NAME --container-name app --region $REGION"
