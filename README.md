# Ranking App

A Flask web application for ranking items, deployed on AWS Lightsail Containers with DynamoDB storage.

## Architecture

```
GitHub (push to main)
    ↓
GitHub Actions (build Docker image)
    ↓
AWS Lightsail Container Service
    ↓
DynamoDB (items table)
```

### Components

| Component | Description |
|-----------|-------------|
| **Flask App** | Python web app with Gunicorn (2 workers) |
| **Lightsail Containers** | Nano tier ($7/mo), auto-restart, built-in HTTPS |
| **DynamoDB** | Serverless NoSQL for item storage |
| **GitHub Actions** | CI/CD on push to main + weekly security rebuilds |

## Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally
python run.py
```

## Infrastructure Setup

### Prerequisites

1. AWS CLI configured with admin credentials
2. GitHub repo with Actions enabled

### 1. Deploy DynamoDB Table

```bash
aws cloudformation deploy \
  --template-file app/infra/dynamodb.yaml \
  --stack-name items-db
```

### 2. Create Container Service

```bash
aws cloudformation deploy \
  --template-file app/infra/container.yaml \
  --stack-name my-app-container \
  --parameter-overrides ServiceName=my-app Power=nano Scale=1
```

### 3. Create IAM Users

Create two IAM users with these policies:

| User | Policy File | Purpose |
|------|-------------|---------|
| Deploy user | `app/infra/deploy-policy.json` | Push images, deploy containers |
| DynamoDB user | `app/infra/container-policy.json` | Container reads/writes DynamoDB |

### 4. Configure GitHub Secrets

Go to repo Settings → Secrets and variables → Actions, add:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | Deploy user access key |
| `AWS_SECRET_ACCESS_KEY` | Deploy user secret key |
| `DYNAMODB_AWS_ACCESS_KEY_ID` | DynamoDB user access key |
| `DYNAMODB_AWS_SECRET_ACCESS_KEY` | DynamoDB user secret key |

### 5. Deploy

Push to `main` branch — GitHub Actions will build and deploy automatically.

## Manual Deploy

For local deploys without GitHub Actions:

```bash
# Create .env file with DynamoDB credentials
echo "DYNAMODB_AWS_ACCESS_KEY_ID=AKIA..." > .env
echo "DYNAMODB_AWS_SECRET_ACCESS_KEY=..." >> .env

# Run deploy script
./app/infra/deploy.sh
```

## Files

```
app/
├── infra/
│   ├── container.yaml      # CloudFormation: Lightsail Container Service
│   ├── dynamodb.yaml       # CloudFormation: DynamoDB table
│   ├── deploy.sh           # Manual deploy script
│   ├── deploy-policy.json  # IAM policy for deploy user
│   ├── container-policy.json # IAM policy for DynamoDB access
│   └── policy.json         # Admin IAM policy (initial setup)
├── routes.py               # Flask routes
├── data.py                 # DynamoDB operations
└── templates/              # Jinja2 templates
.github/
└── workflows/
    └── deploy.yml          # GitHub Actions CI/CD
Dockerfile                  # Container image definition
.dockerignore               # Excludes from Docker build
```
