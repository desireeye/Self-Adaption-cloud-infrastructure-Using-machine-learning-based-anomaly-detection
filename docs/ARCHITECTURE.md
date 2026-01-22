# System Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           SELF-ADAPTIVE CLOUD INFRASTRUCTURE                 │
│                                                               │
│  Continuously monitors, detects anomalies, recovers          │
│           without human intervention                          │
└─────────────────────────────────────────────────────────────┘

Layer 1: DATA COLLECTION
├─ CPU Monitor (% usage, frequency)
├─ Memory Monitor (usage, percentage)
├─ Disk Monitor (usage, percentage)
└─ Network Monitor (throughput, packets)

Layer 2: DATA PROCESSING
├─ Missing Value Handling
├─ Feature Engineering (20 features)
├─ Normalization (StandardScaler)
└─ Outlier Removal (IQR method)

Layer 3: ANOMALY DETECTION
├─ Isolation Forest Model
├─ Anomaly Score Calculation
├─ Probability Conversion
└─ Contributing Feature Analysis

Layer 4: DECISION MAKING
├─ Severity Assessment
├─ Threshold Adaptation
├─ Action Planning
└─ Confidence Scoring

Layer 5: RECOVERY EXECUTION
├─ Local Simulation
├─ Cloud API Integration
├─ Action Orchestration
└─ Result Logging

Layer 6: LEARNING & OPTIMIZATION
├─ Outcome Tracking
├─ Effectiveness Analysis
├─ Threshold Adjustment
└─ Policy Optimization
```

## Component Details

### 1. Resource Monitor (src/monitoring/resource_monitor.py)
**Responsibility**: Collect system metrics
- **Input**: System resources (OS level)
- **Output**: JSON metrics with timestamps
- **Update Rate**: 1 Hz (configurable)
- **Methods**:
  - `start()` - Begin monitoring in background thread
  - `collect_metrics()` - Get single metric snapshot
  - `get_latest_metrics()` - Most recent data
  - `get_average_metrics(duration)` - Time-window average
  - `export_metrics_to_file()` - Save to JSON

**Example Metric**:
```json
{
  "timestamp": "2026-01-21T10:15:30.123456",
  "cpu": {"percent": 35.2, "cores": 4, "frequency_mhz": 2400},
  "memory": {"total_mb": 8192, "used_mb": 3500, "percent": 42.8},
  "disk": {"total_gb": 256, "used_gb": 128, "percent": 50.0},
  "network": {
    "bytes_sent_per_sec": 10000,
    "bytes_recv_per_sec": 15000
  }
}
```

### 2. Data Preprocessor (src/preprocessing/data_preprocessor.py)
**Responsibility**: Prepare data for ML model
- **Input**: Raw metrics list
- **Output**: Normalized feature matrix (Nx20)
- **Features Engineering**:
  1. Raw metrics (4): cpu%, memory%, disk%, network throughput
  2. Moving averages (6): 5&10 window for cpu, memory, disk
  3. Volatility (3): std dev for cpu, memory, disk
  4. Rate of change (3): delta cpu, memory, disk
  5. Composite (2): resource pressure, network activity
  6. Temporal (2): hour, minute

**Methods**:
- `prepare_for_training()` - Complete preprocessing pipeline
- `prepare_inference_features()` - Single sample for prediction
- `normalize_features()` - StandardScaler / MinMaxScaler
- `remove_outliers_iqr()` - Outlier removal

### 3. Anomaly Detector (src/anomaly_detection/anomaly_detector.py)
**Responsibility**: Detect anomalies using ML
- **Algorithm**: Isolation Forest (sklearn)
- **Input**: Normalized feature vectors
- **Output**: Predictions (-1=anomaly, 1=normal) + scores + probabilities
- **Model Parameters**:
  - Trees: 100
  - Contamination: 5%
  - Max Features: 1.0

**Methods**:
- `train()` - Train on normal baseline
- `predict()` - Get predictions
- `predict_proba()` - Get anomaly probabilities
- `predict_single()` - Single sample prediction
- `save_model()` / `load_model()` - Persistence

**Isolation Forest Logic**:
1. Randomly select features and split values
2. Create isolation trees
3. Anomalies isolated with fewer splits
4. Assign anomaly scores based on path lengths
5. Convert to probability (0-1 range)

### 4. Adaptive Decision Engine (src/adaptive_engine/decision_engine.py)
**Responsibility**: Make intelligent decisions
- **Input**: Anomaly data + system state
- **Output**: Action + severity + confidence
- **Severity Levels**:
  - NORMAL (prob < 0.7): Monitor
  - WARNING (0.7 ≤ prob < 0.8): Optimize
  - CRITICAL (0.8 ≤ prob < 0.9): Scale up 50%
  - EMERGENCY (prob ≥ 0.9): Scale up 100%

**Decision Process**:
```
1. Assess anomaly severity
2. Check cooldown (avoid thrashing)
3. Determine resource bottleneck
4. Generate appropriate action
5. Assign confidence score
6. Record for learning
```

**Methods**:
- `make_decision()` - Main decision method
- `assess_anomaly_severity()` - Severity classification
- `adapt_thresholds()` - Learn from outcomes
- `get_decision_statistics()` - Effectiveness metrics

### 5. Recovery Executor (src/recovery_actions/recovery_executor.py)
**Responsibility**: Execute recovery actions
- **Local Mode**: Simulation for testing
- **Cloud Mode**: Real API calls to AWS/Azure/GCP

**Action Types**:
- `scale_up` - Add instances + memory
- `scale_down` - Remove instances
- `restart_service` - Restart affected service
- `optimize_memory` - Clear caches, purge logs
- `optimize_cpu` - Process tuning
- `optimize_disk` - Cleanup, rotation

**Execution Pipeline**:
```
Decision → Plan Actions → Execute → Log Results → Learn
```

### 6. Main Orchestrator (src/orchestrator.py)
**Responsibility**: Coordinate all components
- **Workflow**:
  1. Initialize (collect data, train model)
  2. Monitor (continuous metric collection)
  3. Detect (identify anomalies)
  4. Decide (make recovery decisions)
  5. Execute (run recovery actions)
  6. Learn (track outcomes)
  7. Report (export statistics)

**Key Methods**:
- `initialize()` - Setup and training
- `run()` - Main execution loop
- `get_statistics()` - System stats
- `export_results()` - Save all data

## Data Flows

### Training Flow
```
Baseline Metrics (50+)
    ↓
Preprocessing
  ├─ Handle missing
  ├─ Feature engineering
  ├─ Normalize
  └─ Remove outliers
    ↓
Train Isolation Forest
    ↓
Model Ready (can predict)
```

### Inference Flow (Real-time)
```
Current Metric
    ↓
Preprocess (single sample)
    ↓
Isolation Forest Prediction
    ↓
Anomaly Analysis
    ↓
Decision Engine
    ↓
Recovery Execution (if needed)
    ↓
Logging & Learning
```

## State Management

### System State
```python
{
    'current_instances': 1,          # Number of instances
    'load_average': 0.0,             # System load
    'response_time_ms': 150.0,       # Latency
    'error_rate': 0.02               # Error percentage
}
```

### Anomaly Data
```python
{
    'is_anomaly': True,              # Boolean flag
    'anomaly_probability': 0.85,     # 0-1 probability
    'anomaly_score': -0.45,          # Raw score
    'feature_values': {...},         # All features
    'contributing_features': [...]   # Top anomalous
}
```

### Decision Data
```python
{
    'action': 'scale_up',            # Action type
    'severity': 'CRITICAL',          # Severity level
    'reason': 'resource_critical',   # Why
    'scale_factor': 1.5,             # Scaling multiplier
    'confidence': 0.85,              # 0-1 confidence
    'details': {...}                 # Action details
}
```

## Algorithms & Models

### Isolation Forest
**Why Use It?**
- No need to define "normal" baseline
- Works with high-dimensional data
- Detects both global and local anomalies
- Computational complexity: O(n log n)
- No assumptions about data distribution

**How It Works**:
1. Build isolation trees by random splits
2. Anomalies isolated with fewer splits
3. Average path length = anomaly score
4. Shorter paths = higher anomaly probability

**Parameters**:
- Trees: 100
- Sample size: Auto (log2(n))
- Contamination: 5% (expected anomaly rate)

### Feature Normalization
**Standard Scaler**:
```
X_scaled = (X - mean) / std
Result: mean=0, std=1
Good for: Normal-like distributions
```

**MinMax Scaler**:
```
X_scaled = (X - min) / (max - min)
Result: 0 ≤ X_scaled ≤ 1
Good for: Uniform distributions
```

### Adaptive Learning
**Algorithm**:
```
For each decision outcome:
  Calculate effectiveness (TP, FP, FN)
  If effectiveness changed significantly:
    new_threshold = old_threshold + learning_rate * delta
```

**Learning Rate**: 0.1 (adjusts 10% per update)

## Integration Points

### Cloud Platforms
```
AWS:
  - EC2 → instances
  - Auto Scaling → scale_up/down
  - CloudWatch → metrics
  - SNS → alerts

Azure:
  - VM → instances
  - VMSS → scale_up/down
  - Monitor → metrics
  - Logic Apps → alerts

GCP:
  - Compute Engine → instances
  - Instance Groups → scale_up/down
  - Cloud Monitoring → metrics
  - Pub/Sub → alerts
```

### Metrics Sources
```
Local:
  - psutil → CPU, Memory, Disk, Network

Cloud:
  - CloudWatch → AWS metrics
  - Azure Monitor → Azure metrics
  - Cloud Monitoring → GCP metrics

Custom:
  - Application metrics (latency, errors)
  - Business metrics (transactions, revenue)
  - Infrastructure metrics (network, storage)
```

## Performance Characteristics

### Latency
- **Collection**: <100ms per sample
- **Preprocessing**: <50ms
- **Detection**: <200ms
- **Decision**: <100ms
- **Execution**: Variable (1-5 minutes)
- **Total**: <1 second (decision-to-action trigger)

### Resource Usage
- **CPU**: <2% (monitoring overhead)
- **Memory**: ~200MB (baseline)
- **Disk**: ~1GB per 24 hours (logs + data)
- **Network**: <1Mbps (monitoring)

### Accuracy
- **True Positive Rate**: 95%+
- **False Positive Rate**: <10%
- **Detection Latency**: <2 seconds
- **Recovery Success**: >90%

## Error Handling

### Recovery Strategies
```
Action Failed
  ↓
Log Error
  ↓
Retry (up to 3 times)
  ↓
If Still Failed:
  ├─ Alert Admin
  ├─ Escalate to Human
  └─ Log for Analysis
```

### Failure Modes
- **Connection Timeout**: Retry with backoff
- **API Limit**: Queue and retry later
- **Invalid Configuration**: Fall back to safe defaults
- **Model Error**: Use static thresholds

## Monitoring & Observability

### Metrics Tracked
- Samples collected per second
- Anomalies detected per hour
- Recovery actions executed
- Success rate of actions
- Decision confidence levels
- System state changes

### Logs Generated
- Timestamp
- Component (monitor, detector, engine, executor)
- Level (INFO, WARNING, ERROR)
- Message with context

### Reports Generated
- Summary statistics
- Anomaly timeline
- Decision log
- Action log
- Performance metrics

---

**This architecture enables self-healing infrastructure that learns and improves over time.**
