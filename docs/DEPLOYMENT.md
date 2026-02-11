# Deployment Guide

## Prerequisites

- Docker and Docker Compose
- Terraform (for infrastructure)
- Cloud provider account (AWS/Azure/GCP)
- API keys for LLM providers

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/VenkataAnilKumar/GenerativeAIProjects.git
cd GenerativeAIProjects
```

### 2. Setup Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Start Services with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Check service status
docker-compose ps
```

### 4. Access the Platform

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Cloud Deployment

### AWS Deployment

#### 1. Configure AWS Credentials

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

#### 2. Initialize Terraform

```bash
cd terraform/aws
terraform init
```

#### 3. Configure Variables

Create `terraform.tfvars`:

```hcl
project_name    = "genai-platform"
environment     = "production"
aws_region      = "us-east-1"
db_instance_class = "db.t3.medium"
redis_node_type   = "cache.t3.medium"
```

#### 4. Deploy Infrastructure

```bash
# Plan deployment
terraform plan

# Apply changes
terraform apply

# Note the outputs
terraform output
```

#### 5. Build and Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t genai-platform .

# Tag image
docker tag genai-platform:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/genai-platform-api:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/genai-platform-api:latest
```

#### 6. Deploy to ECS

```bash
# Update ECS service
aws ecs update-service \
  --cluster genai-platform-cluster \
  --service genai-platform-api \
  --force-new-deployment
```

### Azure Deployment

#### 1. Configure Azure CLI

```bash
az login
az account set --subscription "your-subscription-id"
```

#### 2. Deploy with Terraform

```bash
cd terraform/azure
terraform init
terraform apply
```

#### 3. Deploy Container

```bash
# Build and push to ACR
az acr build --registry genaiplatform --image genai-platform:latest .

# Deploy to Container Instances
az container create \
  --resource-group genai-platform \
  --name genai-api \
  --image genaiplatform.azurecr.io/genai-platform:latest \
  --ports 8000
```

### Google Cloud Deployment

#### 1. Configure GCP

```bash
gcloud auth login
gcloud config set project your-project-id
```

#### 2. Deploy with Terraform

```bash
cd terraform/gcp
terraform init
terraform apply
```

#### 3. Deploy to Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/your-project-id/genai-platform

# Deploy to Cloud Run
gcloud run deploy genai-api \
  --image gcr.io/your-project-id/genai-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

### Environment Variables

Key environment variables to configure:

```bash
# Provider Keys
OPENAI_API_KEY=sk-...
AZURE_OPENAI_API_KEY=...
GOOGLE_PROJECT_ID=...
AWS_ACCESS_KEY_ID=...

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis
REDIS_URL=redis://host:6379/0

# Security
SECRET_KEY=your-strong-secret-key
```

### Scaling Configuration

#### Horizontal Pod Autoscaler (Kubernetes)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: genai-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: genai-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

#### AWS ECS Auto Scaling

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/genai-platform-cluster/genai-platform-api \
  --min-capacity 2 \
  --max-capacity 10
```

## Monitoring Setup

### Prometheus Configuration

The platform exposes metrics at `/metrics`:

- `http_requests_total`
- `http_request_duration_seconds`
- `llm_tokens_used_total`
- `llm_cost_usd_total`

### Grafana Dashboards

Import the provided dashboard:

```bash
# Access Grafana
open http://localhost:3000

# Login (default: admin/admin)
# Import dashboard from docs/grafana-dashboard.json
```

## Troubleshooting

### API Not Starting

```bash
# Check logs
docker-compose logs api

# Check environment variables
docker-compose exec api env

# Test database connection
docker-compose exec api python -c "from src.core.config import get_settings; print(get_settings())"
```

### High Latency

1. Check provider API status
2. Monitor database connections
3. Review cache hit rates
4. Scale horizontally

### Cost Overruns

1. Review usage metrics
2. Set rate limits
3. Enable caching
4. Use cheaper models for testing

## Security Checklist

- [ ] Rotate all API keys
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Set up monitoring alerts
- [ ] Implement rate limiting
- [ ] Enable WAF (Web Application Firewall)
- [ ] Configure backup strategy
- [ ] Test disaster recovery

## Maintenance

### Database Backups

```bash
# Automated backups (AWS RDS)
# Configured in terraform/aws/main.tf
backup_retention_period = 7

# Manual backup
pg_dump -h <host> -U <user> genai > backup.sql
```

### Updates

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Rebuild containers
docker-compose build --no-cache

# Rolling update (Kubernetes)
kubectl set image deployment/genai-api api=genai-platform:v2.0.0
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/VenkataAnilKumar/GenerativeAIProjects/issues
- Documentation: ./docs/
