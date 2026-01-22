# Deployment Guide - AWS, Azure, and GCP

## Overview
This guide covers deploying the self-adaptive system to major cloud platforms.

---

## AWS Deployment

### Prerequisites
- AWS Account
- IAM user with EC2, Auto Scaling, CloudWatch permissions
- AWS CLI configured
- boto3 Python library

### Architecture
```
Internet
    ↓
[Load Balancer]
    ↓
[Auto Scaling Group]
  ├─ EC2 Instance 1 (with system agent)
  ├─ EC2 Instance 2 (with system agent)
  └─ EC2 Instance N
    ↓
[CloudWatch Metrics]
    ↓
[SNS Notifications]
```

### Step 1: Create IAM Role
```bash
# Create role with permissions
aws iam create-role \
  --role-name self-adaptive-role \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name self-adaptive-role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess

aws iam attach-role-policy \
  --role-name self-adaptive-role \
  --policy-arn arn:aws:iam::aws:policy/AutoScalingFullAccess
```

### Step 2: Create Launch Template
```bash
aws ec2 create-launch-template \
  --launch-template-name self-adaptive \
  --version-description "Self-adaptive system" \
  --launch-template-data '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "t3.medium",
    "IamInstanceProfile": "self-adaptive-role",
    "UserData": "IyEvYmluL2Jhc2gK..."
  }'
```

### Step 3: Create Auto Scaling Group
```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name self-adaptive-asg \
  --launch-template LaunchTemplateName=self-adaptive \
  --min-size 1 \
  --max-size 10 \
  --desired-capacity 3 \
  --availability-zones us-east-1a us-east-1b
```

### Step 4: Configure CloudWatch Metrics
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def push_metrics_to_cloudwatch(metrics):
    cloudwatch.put_metric_data(
        Namespace='SelfAdaptiveSystem',
        MetricData=[
            {
                'MetricName': 'CPUAnomaly',
                'Value': metrics['cpu']['percent'],
                'Unit': 'Percent'
            },
            {
                'MetricName': 'MemoryAnomaly',
                'Value': metrics['memory']['percent'],
                'Unit': 'Percent'
            }
        ]
    )
```

### Step 5: Setup Auto Scaling Policies
```bash
# Scale up if CPU > 70%
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name self-adaptive-asg \
  --policy-name scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://scale-up.json

# Scale down if CPU < 30%
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name self-adaptive-asg \
  --policy-name scale-down \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://scale-down.json
```

### Monitoring
```bash
# View metrics
aws cloudwatch get-metric-statistics \
  --namespace SelfAdaptiveSystem \
  --metric-name CPUAnomaly \
  --start-time 2026-01-21T00:00:00Z \
  --end-time 2026-01-21T01:00:00Z \
  --period 300 \
  --statistics Average,Maximum

# View scaling activities
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name self-adaptive-asg \
  --max-records 10
```

---

## Azure Deployment

### Prerequisites
- Azure Subscription
- Azure CLI
- Azure Python SDK

### Architecture
```
Resource Group
  ├─ Virtual Network
  ├─ Virtual Machine Scale Set
  │   ├─ VM Instance 1
  │   ├─ VM Instance 2
  │   └─ VM Instance N
  ├─ Load Balancer
  ├─ Azure Monitor
  └─ Log Analytics
```

### Step 1: Create Resource Group
```bash
az group create \
  --name self-adaptive-rg \
  --location eastus
```

### Step 2: Create Virtual Network
```bash
az network vnet create \
  --resource-group self-adaptive-rg \
  --name self-adaptive-vnet \
  --address-prefix 10.0.0.0/16 \
  --subnet-name default \
  --subnet-prefix 10.0.0.0/24
```

### Step 3: Create VMSS
```bash
az vmss create \
  --resource-group self-adaptive-rg \
  --name self-adaptive-vmss \
  --image UbuntuLTS \
  --vm-sku Standard_B2s \
  --instance-count 3 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --vnet-name self-adaptive-vnet \
  --subnet default \
  --public-ip-per-vm
```

### Step 4: Configure Auto Scaling
```bash
az monitor metrics alert create \
  --resource-group self-adaptive-rg \
  --name cpu-alert \
  --scopes /subscriptions/{id}/resourceGroups/self-adaptive-rg/providers/Microsoft.Compute/virtualMachineScaleSets/self-adaptive-vmss \
  --condition "avg Percentage CPU > 70" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action create --action-group-name {action-group-name}
```

### Step 5: Push Metrics
```python
from azure.monitor.query import MetricsQueryClient
from azure.identity import DefaultAzureCredential

client = MetricsQueryClient(credential=DefaultAzureCredential())

def push_metrics_to_azure(metrics):
    # Use Azure Monitor custom metrics
    pass
```

---

## GCP Deployment

### Prerequisites
- GCP Project
- gcloud CLI
- Google Cloud Python SDK

### Architecture
```
Project
  ├─ Compute Engine
  │   ├─ Instance Template
  │   ├─ Instance Group
  │   │   ├─ VM Instance 1
  │   │   ├─ VM Instance 2
  │   │   └─ VM Instance N
  │   └─ Load Balancer
  ├─ Cloud Monitoring
  └─ Cloud Logging
```

### Step 1: Create Instance Template
```bash
gcloud compute instance-templates create self-adaptive \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --metadata-from-file startup-script=startup.sh \
  --scopes=https://www.googleapis.com/auth/cloud-platform
```

### Step 2: Create Instance Group
```bash
gcloud compute instance-groups managed create self-adaptive-ig \
  --base-instance-name=self-adaptive \
  --template=self-adaptive \
  --size=3 \
  --zone=us-central1-a
```

### Step 3: Set Autoscaling
```bash
gcloud compute instance-groups managed set-autoscaling self-adaptive-ig \
  --max-num-replicas=10 \
  --min-num-replicas=1 \
  --target-cpu-utilization=0.7 \
  --zone=us-central1-a
```

### Step 4: Create Load Balancer
```bash
gcloud compute backend-services create self-adaptive-backend \
  --protocol=HTTP \
  --port-name=http \
  --health-checks=basic-check \
  --global

gcloud compute backend-services add-backend self-adaptive-backend \
  --instance-group=self-adaptive-ig \
  --instance-group-zone=us-central1-a \
  --global
```

### Step 5: Push Metrics
```python
from google.cloud import monitoring_v3

def push_metrics_to_gcp(metrics):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/YOUR_PROJECT"
    
    series = monitoring_v3.TimeSeries()
    series.metric.type = 'custom.googleapis.com/cpu_anomaly'
    series.resource.type = 'global'
    
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )
    point = monitoring_v3.Point(
        {"interval": interval, "value": {"double_value": metrics['cpu']}}
    )
    series.points = [point]
    
    client.create_time_series(name=project_name, time_series=[series])
```

---

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs data visualizations

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import psutil; psutil.cpu_percent()" || exit 1

# Run application
CMD ["python", "main.py", "run", "--duration", "86400"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  self-adaptive-system:
    build: .
    container_name: self-adaptive-system
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./visualizations:/app/visualizations
    environment:
      - LOG_LEVEL=INFO
      - SAMPLING_INTERVAL=1.0
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Build & Run
```bash
# Build image
docker build -t self-adaptive-system .

# Run container
docker run -d \
  --name adaptive-system \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  self-adaptive-system

# View logs
docker logs -f adaptive-system

# Stop container
docker stop adaptive-system
```

---

## Kubernetes Deployment

### Deployment Manifest
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: self-adaptive-system
  labels:
    app: self-adaptive
spec:
  replicas: 3
  selector:
    matchLabels:
      app: self-adaptive
  template:
    metadata:
      labels:
        app: self-adaptive
    spec:
      containers:
      - name: system
        image: self-adaptive-system:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import psutil; exit(0 if psutil.cpu_percent() >= 0 else 1)"
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import psutil; exit(0 if psutil.cpu_percent() >= 0 else 1)"
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: self-adaptive-data
      - name: logs
        persistentVolumeClaim:
          claimName: self-adaptive-logs

---
apiVersion: v1
kind: Service
metadata:
  name: self-adaptive-service
spec:
  selector:
    app: self-adaptive
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: self-adaptive-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: self-adaptive-system
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes
```bash
# Create namespaces
kubectl create namespace self-adaptive

# Create persistent volumes
kubectl apply -f pv.yaml -n self-adaptive

# Deploy application
kubectl apply -f deployment.yaml -n self-adaptive

# Check status
kubectl get all -n self-adaptive

# View logs
kubectl logs -f deployment/self-adaptive-system -n self-adaptive

# Port forward
kubectl port-forward svc/self-adaptive-service 8080:80 -n self-adaptive
```

---

## Monitoring & Alerting

### CloudWatch Dashboards (AWS)
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_dashboard(
    DashboardName='SelfAdaptiveSystem',
    DashboardBody=json.dumps({
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["SelfAdaptiveSystem", "CPUAnomaly"],
                        [".", "MemoryAnomaly"],
                        [".", "DiskAnomaly"]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "Anomaly Detection"
                }
            }
        ]
    })
)
```

### Grafana Dashboards
Import JSON dashboard configuration for visualization of metrics.

### Alert Rules
```yaml
# Prometheus alert rule
groups:
- name: self-adaptive
  rules:
  - alert: HighAnomalyRate
    expr: anomaly_rate > 0.1
    for: 5m
    annotations:
      summary: "High anomaly detection rate"
```

---

## Cost Optimization

### AWS
- Use Spot Instances for non-critical workloads
- Configure Reserved Instances for baseline
- Use Auto Scaling to match demand
- Enable detailed monitoring only for critical metrics

### Azure
- Use Spot VMs for flexible workloads
- Reserve capacity for 1-year/3-year terms
- Use managed disks for better performance
- Monitor cost with Azure Cost Management

### GCP
- Use Committed Use Discounts
- Enable auto-scaling with right sizing
- Use Preemptible VMs for batch jobs
- Monitor with Google Cloud Cost Management

---

## Troubleshooting

### Issue: Autoscaling not triggering
**Solution**: Check metrics are being published correctly
```bash
# AWS
aws cloudwatch get-metric-statistics \
  --namespace SelfAdaptiveSystem \
  --metric-name CPUAnomaly \
  --start-time 2026-01-21T00:00:00Z \
  --end-time 2026-01-21T01:00:00Z \
  --period 60 \
  --statistics Average
```

### Issue: High latency in recovery
**Solution**: Check cloud API rate limits and increase timeout values
```python
config['recovery']['execution_timeout'] = 300  # 5 minutes
```

### Issue: Data not persisting
**Solution**: Ensure volumes are properly mounted in containers/K8s
```bash
# Docker
docker inspect adaptive-system | grep -A 10 Mounts

# Kubernetes
kubectl describe pvc self-adaptive-data -n self-adaptive
```

---

**Your self-adaptive system is now running in the cloud!**
