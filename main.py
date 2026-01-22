"""
Main entry point for the Self-Adaptive Cloud Infrastructure system
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator import SelfAdaptiveOrchestrator
from tests.test_simulator import SystemTester, AnomalySimulator
from visualization.visualizer import MetricsVisualizer


def setup_logging(level=logging.INFO):
    """Configure logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/system.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Self-Adaptive Cloud Infrastructure with ML Anomaly Detection'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the self-adaptive system')
    run_parser.add_argument('--duration', type=int, default=120,
                          help='Duration to run in seconds (default: 120)')
    run_parser.add_argument('--config', type=str, help='Configuration file path')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run system tests')
    test_parser.add_argument('--test-type', choices=['all', 'normal', 'cpu', 'memory', 'network'],
                            default='all', help='Type of test to run')
    
    # Simulate command
    sim_parser = subparsers.add_parser('simulate', help='Run with simulated anomalies')
    sim_parser.add_argument('--scenario', choices=['cpu-spike', 'memory-leak', 'network-burst', 'combined'],
                           default='cpu-spike', help='Anomaly scenario to simulate')
    sim_parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Visualize results')
    viz_parser.add_argument('--metrics', type=str, help='Metrics JSON file')
    viz_parser.add_argument('--anomalies', type=str, help='Anomalies JSON file')
    viz_parser.add_argument('--actions', type=str, help='Actions JSON file')
    viz_parser.add_argument('--output-dir', type=str, default='visualizations',
                          help='Output directory for visualizations')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create necessary directories
    Path('logs').mkdir(exist_ok=True)
    Path('data').mkdir(exist_ok=True)
    Path('visualizations').mkdir(exist_ok=True)
    
    if args.command == 'run':
        logger.info("Starting Self-Adaptive Cloud Infrastructure system...")
        orchestrator = SelfAdaptiveOrchestrator()
        
        try:
            orchestrator.initialize()
            orchestrator.run(duration_seconds=args.duration)
        finally:
            orchestrator.print_status()
            orchestrator.export_results(output_dir='data')
    
    elif args.command == 'test':
        logger.info(f"Running tests: {args.test_type}")
        orchestrator = SelfAdaptiveOrchestrator()
        orchestrator.initialize()
        
        tester = SystemTester(orchestrator)
        
        if args.test_type == 'all':
            tester.run_all_tests()
        elif args.test_type == 'normal':
            result = tester.test_normal_operation()
            print(f"Result: {result}")
        elif args.test_type == 'cpu':
            result = tester.test_cpu_spike()
            print(f"Result: {result}")
        elif args.test_type == 'memory':
            result = tester.test_memory_leak()
            print(f"Result: {result}")
        elif args.test_type == 'network':
            result = tester.test_network_burst()
            print(f"Result: {result}")
    
    elif args.command == 'simulate':
        logger.info(f"Running simulation: {args.scenario}")
        
        simulator = AnomalySimulator()
        normal_metrics = simulator.create_normal_metrics(samples=100)
        
        if args.scenario == 'cpu-spike':
            anomaly_metrics = simulator.create_cpu_spike_anomaly(normal_metrics)
        elif args.scenario == 'memory-leak':
            anomaly_metrics = simulator.create_memory_leak_anomaly(normal_metrics)
        elif args.scenario == 'network-burst':
            anomaly_metrics = simulator.create_network_burst_anomaly(normal_metrics)
        elif args.scenario == 'combined':
            anomaly_metrics = simulator.create_combined_anomaly(normal_metrics)
        
        # Train and test
        orchestrator = SelfAdaptiveOrchestrator()
        X, df = orchestrator.preprocessor.prepare_for_training(normal_metrics)
        orchestrator.detector.train(X)
        orchestrator.analyzer = orchestrator.analyzer.__class__(
            orchestrator.detector,
            orchestrator.preprocessor.feature_names
        )
        
        # Test on anomaly metrics
        logger.info(f"Testing on {args.scenario} scenario...")
        anomalies_detected = 0
        for metric in anomaly_metrics:
            feature_vector = orchestrator.preprocessor.prepare_inference_features(metric)
            anomaly_data = orchestrator.analyzer.analyze_sample(feature_vector)
            if anomaly_data['is_anomaly']:
                anomalies_detected += 1
        
        print(f"\n{'='*60}")
        print(f"SIMULATION RESULTS: {args.scenario}")
        print(f"{'='*60}")
        print(f"Total samples: {len(anomaly_metrics)}")
        print(f"Anomalies detected: {anomalies_detected}")
        print(f"Detection rate: {anomalies_detected/len(anomaly_metrics):.2%}")
        print(f"{'='*60}\n")
        
        # Export results
        orchestrator.export_results(output_dir='data')
    
    elif args.command == 'visualize':
        logger.info("Creating visualizations...")
        visualizer = MetricsVisualizer()
        
        if args.metrics:
            output_file = f"{args.output_dir}/metrics_plot.png"
            visualizer.plot_metrics_timeseries(args.metrics, output_file)
        
        if args.anomalies and args.metrics:
            output_file = f"{args.output_dir}/anomalies_plot.png"
            visualizer.plot_anomalies(args.anomalies, args.metrics, output_file)
            
            output_file = f"{args.output_dir}/anomaly_scores_plot.png"
            visualizer.plot_anomaly_scores(args.anomalies, output_file)
        
        if args.actions:
            output_file = f"{args.output_dir}/actions_plot.png"
            visualizer.plot_recovery_actions(args.actions, output_file)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
