## Infrastructure

### Deploy DynamoDB Table

```bash
aws cloudformation deploy \
  --template-file app/infra/dynamodb.yaml \
  --stack-name items-db
```

### Deploy Lightsail Container Service

```bash
aws cloudformation deploy \
  --template-file app/infra/container.yaml \
  --stack-name my-app-container \
  --parameter-overrides ServiceName=my-app Power=nano Scale=1
```

### IAM Policies

| File | Purpose |
|------|---------|
| `policy.json` | Admin policy for initial setup (CloudFormation, DynamoDB, Lightsail) |
| `deploy-policy.json` | CI/CD user: push images + deploy only (no create/delete) |
| `container-policy.json` | Container runtime: DynamoDB read/write only |

### Useful Commands

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name my-app-container

# View container service
aws lightsail get-container-services --service-name my-app

# View container logs
aws lightsail get-container-log --service-name my-app --container-name app

# Manual deploy
./app/infra/deploy.sh

# Delete stack
aws cloudformation delete-stack --stack-name my-app-container
```

