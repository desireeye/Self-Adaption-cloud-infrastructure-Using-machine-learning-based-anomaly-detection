#!/usr/bin/env python
"""
Dashboard Integration Verification Script
Checks if dashboard is properly integrated with main system
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_check(status, message):
    """Print check result"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {message}")

def check_file_exists(path):
    """Check if file exists"""
    return os.path.exists(path)

def check_data_files():
    """Check if main system has generated data files"""
    print_header("📊 DATA FILES CHECK")
    
    project_root = r"C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
    data_dir = os.path.join(project_root, "data")
    
    # Check data directory
    data_exists = os.path.isdir(data_dir)
    print_check(data_exists, f"Data directory exists: {data_dir}")
    
    if not data_exists:
        print("  ⚠️  Run main system first: python main.py run --duration 60")
        return False
    
    # Check for latest metrics file
    try:
        metrics_files = [f for f in os.listdir(data_dir) if f.startswith('metrics_') and f.endswith('.json')]
        if metrics_files:
            latest_metrics = sorted(metrics_files)[-1]
            metrics_path = os.path.join(data_dir, latest_metrics)
            print_check(True, f"Latest metrics file: {latest_metrics}")
            
            # Load and show sample
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            print(f"    📈 Samples collected: {len(metrics)}")
            if metrics:
                latest = metrics[-1]
                print(f"    💾 Latest: CPU {latest.get('cpu_percent', 'N/A')}% | Memory {latest.get('memory_percent', 'N/A')}%")
        else:
            print_check(False, "No metrics files found")
            return False
    except Exception as e:
        print_check(False, f"Error reading metrics files: {e}")
        return False
    
    # Check for anomalies file
    try:
        anomaly_files = [f for f in os.listdir(data_dir) if f.startswith('anomalies_') and f.endswith('.json')]
        if anomaly_files:
            latest_anomalies = sorted(anomaly_files)[-1]
            print_check(True, f"Latest anomalies file: {latest_anomalies}")
        else:
            print_check(False, "No anomalies files found")
    except Exception as e:
        print_check(False, f"Error reading anomalies files: {e}")
    
    # Check for decisions file
    try:
        decision_files = [f for f in os.listdir(data_dir) if f.startswith('decisions_') and f.endswith('.json')]
        if decision_files:
            latest_decisions = sorted(decision_files)[-1]
            print_check(True, f"Latest decisions file: {latest_decisions}")
        else:
            print_check(False, "No decisions files found")
    except Exception as e:
        print_check(False, f"Error reading decisions files: {e}")
    
    return bool(metrics_files)

def check_dashboard_files():
    """Check if dashboard files exist"""
    print_header("🎨 DASHBOARD FILES CHECK")
    
    project_root = r"C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
    
    files_to_check = {
        "Backend Main": os.path.join(project_root, "dashboard/backend/main.py"),
        "Backend Requirements": os.path.join(project_root, "dashboard/backend/requirements_clean.txt"),
        "Frontend App": os.path.join(project_root, "dashboard/frontend/src/App.jsx"),
        "Frontend Package": os.path.join(project_root, "dashboard/frontend/package.json"),
        "Integration Service": os.path.join(project_root, "dashboard/backend/app/services/system_integration.py"),
        "Health API": os.path.join(project_root, "dashboard/backend/app/api/health.py"),
    }
    
    all_exist = True
    for name, path in files_to_check.items():
        exists = os.path.exists(path)
        print_check(exists, f"{name}: {path}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_integration():
    """Check if integration is properly configured"""
    print_header("🔗 INTEGRATION CHECK")
    
    project_root = r"C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
    integration_file = os.path.join(project_root, "dashboard/backend/app/services/system_integration.py")
    
    if not os.path.exists(integration_file):
        print_check(False, f"Integration module not found: {integration_file}")
        return False
    
    print_check(True, f"Integration module exists: {integration_file}")
    
    # Check if it imports correctly
    try:
        sys.path.insert(0, os.path.join(project_root, "dashboard/backend"))
        from app.services.system_integration import SystemIntegration, get_system_integration
        print_check(True, "Integration module imports successfully")
        
        # Test instantiation
        integration = SystemIntegration(project_root)
        print_check(True, f"Integration initialized: {integration.project_root}")
        
        # Check for key methods
        methods = ['get_latest_metrics_file', 'load_metrics_history', 'get_system_summary', 'get_health_status']
        for method in methods:
            has_method = hasattr(integration, method)
            print_check(has_method, f"Method available: {method}")
        
        return True
    except Exception as e:
        print_check(False, f"Integration import error: {e}")
        return False

def check_api_endpoints():
    """Check if new integration endpoints exist"""
    print_header("🔌 API ENDPOINTS CHECK")
    
    project_root = r"C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
    health_api = os.path.join(project_root, "dashboard/backend/app/api/health.py")
    
    if not os.path.exists(health_api):
        print_check(False, f"Health API file not found: {health_api}")
        return False
    
    try:
        with open(health_api, 'r', encoding='utf-8') as f:
            content = f.read()
        
        endpoints = {
            "/api/health/system-summary": "system-summary" in content,
            "/api/health/integrated-status": "integrated-status" in content,
            "/api/health/data-availability": "data-availability" in content,
        }
        
        all_present = True
        for endpoint, present in endpoints.items():
            print_check(present, f"Endpoint implemented: {endpoint}")
            if not present:
                all_present = False
        
        return all_present
    except Exception as e:
        print_check(False, f"Error reading API file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("📦 DEPENDENCIES CHECK")
    
    project_root = r"C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
    requirements_file = os.path.join(project_root, "dashboard/backend/requirements_clean.txt")
    
    try:
        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"Required packages ({len(packages)}):")
        for pkg in packages:
            print(f"  - {pkg}")
        
        # Try importing key packages
        print("\nImport check:")
        imports_ok = True
        for pkg in ['fastapi', 'uvicorn', 'pydantic', 'psutil']:
            try:
                __import__(pkg)
                print_check(True, f"{pkg} installed")
            except ImportError:
                print_check(False, f"{pkg} not installed (run: pip install -r requirements_clean.txt)")
                imports_ok = False
        
        return imports_ok
    except Exception as e:
        print_check(False, f"Error checking dependencies: {e}")
        return False

def print_summary(checks):
    """Print summary of all checks"""
    print_header("📋 SUMMARY")
    
    total = len(checks)
    passed = sum(1 for v in checks.values() if v)
    
    for name, status in checks.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}")
    
    print(f"\n{'='*60}")
    if passed == total:
        print(f"🎉 ALL CHECKS PASSED ({passed}/{total})")
        print("✅ DASHBOARD IS READY TO RUN")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("🔧 Some issues need to be fixed")
    print(f"{'='*60}\n")
    
    return passed == total

def print_next_steps():
    """Print next steps"""
    print_header("🚀 NEXT STEPS")
    
    print("1. Ensure main system has run:")
    print("   python main.py run --duration 60\n")
    
    print("2. Start backend (Terminal 1):")
    print("   cd dashboard/backend")
    print("   pip install -r requirements_clean.txt")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload\n")
    
    print("3. Start frontend (Terminal 2):")
    print("   cd dashboard/frontend")
    print("   npm install")
    print("   npm start\n")
    
    print("4. Access dashboard:")
    print("   http://localhost:3000\n")
    
    print("5. Check API documentation:")
    print("   http://localhost:8000/docs\n")
    
    print("6. Verify integration:")
    print("   http://localhost:8000/api/health/data-availability\n")

def main():
    """Run all checks"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Self-Adaptive Dashboard Integration Verification       ║")
    print("║              January 21, 2026                           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    checks = {
        "Data Files": check_data_files(),
        "Dashboard Files": check_dashboard_files(),
        "Integration Module": check_integration(),
        "API Endpoints": check_api_endpoints(),
        "Dependencies": check_dependencies(),
    }
    
    all_passed = print_summary(checks)
    print_next_steps()
    
    if all_passed:
        print("✅ Everything is ready! Run the dashboard with:")
        print("   .\\RUN_DASHBOARD.ps1\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
