# Quick Start Guide - 10 Minutes to Running Self-Adaptive System

## Step 1: Install (2 minutes)
```bash
cd self-adaptive-project
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Run System (5 minutes)
```bash
python main.py run --duration 300
```

**What you'll see:**
- Resource metrics being collected
- Anomalies being detected
- Decisions being made
- Recovery actions executing
- Final statistics showing results

## Step 3: View Results (3 minutes)
```bash
# Check the statistics
python -c "
import json
import glob
with open(glob.glob('data/summary*.json')[-1]) as f:
    print(json.dumps(json.load(f), indent=2))
"

# Create visualizations
python main.py visualize --metrics data/metrics_*.json --output-dir visualizations
```

## Expected Output

### During Execution
```
==========================================================
SELF-ADAPTIVE SYSTEM STATUS
==========================================================
Uptime: 300s
Anomalies Detected: 12
Recoveries Executed: 8

Anomaly Statistics:
  Total Samples: 300
  Anomalies: 12
  Anomaly Rate: 4.00%

Recovery Statistics:
  Actions Executed: 15
  Success Rate: 100%
==========================================================
```

### Generated Files
```
data/
├── metrics_20260121_101530.json      # 300 metric samples
├── anomalies_20260121_101530.json    # 12 detected anomalies
├── decisions_20260121_101530.json    # 12 decisions made
├── actions_20260121_101530.json      # 15 recovery actions
└── summary_20260121_101530.json      # Summary statistics
```

### Visualizations
```
visualizations/
├── metrics_plot.png          # CPU/Memory/Disk over time
├── anomalies_plot.png        # Anomalies highlighted
├── anomaly_scores_plot.png   # Detection analysis
└── actions_plot.png          # Recovery timeline
```

## Run Tests (Optional)
```bash
# Test all scenarios
python main.py test --test-type all

# Test specific anomaly
python main.py simulate --scenario cpu-spike
```

## Key Commands Reference

| Command | What It Does |
|---------|-------------|
| `python main.py run --duration 120` | Run for 2 minutes |
| `python main.py test --test-type all` | Run all tests |
| `python main.py simulate --scenario cpu-spike` | Simulate CPU spike |
| `python main.py visualize --metrics data/*.json` | Create graphs |
| `python -m pytest tests/` | Run unit tests |

## Common Questions

**Q: System says "Insufficient training data"?**
A: Let it run for at least 30 seconds before training (5+ metric samples needed)

**Q: No anomalies detected?**
A: That's normal! System starts with low anomaly rate. Try: `python main.py simulate --scenario cpu-spike`

**Q: How long should I run it?**
A: 5 minutes (300s) is good for testing. For real deployment, run 24/7

**Q: Can I use cloud services?**
A: Yes! Check `docs/DEPLOYMENT.md` for AWS/Azure/GCP setup

## Next Steps

1. **Understand the code**: Read `src/orchestrator.py`
2. **Customize settings**: Edit `config/default_config.json`
3. **Deploy to cloud**: Follow `docs/DEPLOYMENT.md`
4. **Run in production**: Use Docker or Kubernetes
5. **Publish results**: Write up findings for IEEE paper

## Support

- Detailed docs: See `docs/PROJECT_DOCUMENTATION.md`
- Code examples: Check `tests/test_simulator.py`
- Configuration: Edit `config/default_config.json`
- Logs: Check `logs/system.log` for details

---

**You're all set! Your self-adaptive cloud system is running. 🎉**
