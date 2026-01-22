"""
Visualization Module
Creates graphs and plots for metrics and anomalies
"""

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


class MetricsVisualizer:
    """Visualizes system metrics over time"""
    
    @staticmethod
    def plot_metrics_timeseries(metrics_file: str, output_file: Optional[str] = None) -> None:
        """
        Plot resource metrics as time series
        
        Args:
            metrics_file: Path to metrics JSON file
            output_file: Output file path (if None, just display)
        """
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
        
        if not metrics:
            print("No metrics data to plot")
            return
        
        # Extract data
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        cpu = [m['cpu']['percent'] for m in metrics]
        memory = [m['memory']['percent'] for m in metrics]
        disk = [m['disk']['percent'] for m in metrics]
        
        # Create figure
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        fig.suptitle('System Resource Metrics Over Time', fontsize=16, fontweight='bold')
        
        # CPU plot
        axes[0].plot(timestamps, cpu, label='CPU %', color='#FF6B6B', linewidth=2)
        axes[0].axhline(y=80, color='red', linestyle='--', label='Critical (80%)', alpha=0.7)
        axes[0].axhline(y=60, color='orange', linestyle='--', label='Warning (60%)', alpha=0.7)
        axes[0].set_ylabel('CPU Usage (%)', fontsize=11)
        axes[0].set_title('CPU Utilization', fontsize=12, fontweight='bold')
        axes[0].legend(loc='upper left')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_ylim([0, 100])
        
        # Memory plot
        axes[1].plot(timestamps, memory, label='Memory %', color='#4ECDC4', linewidth=2)
        axes[1].axhline(y=85, color='red', linestyle='--', label='Critical (85%)', alpha=0.7)
        axes[1].axhline(y=65, color='orange', linestyle='--', label='Warning (65%)', alpha=0.7)
        axes[1].set_ylabel('Memory Usage (%)', fontsize=11)
        axes[1].set_title('Memory Utilization', fontsize=12, fontweight='bold')
        axes[1].legend(loc='upper left')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_ylim([0, 100])
        
        # Disk plot
        axes[2].plot(timestamps, disk, label='Disk %', color='#95E1D3', linewidth=2)
        axes[2].axhline(y=90, color='red', linestyle='--', label='Critical (90%)', alpha=0.7)
        axes[2].axhline(y=75, color='orange', linestyle='--', label='Warning (75%)', alpha=0.7)
        axes[2].set_ylabel('Disk Usage (%)', fontsize=11)
        axes[2].set_xlabel('Time', fontsize=11)
        axes[2].set_title('Disk Utilization', fontsize=12, fontweight='bold')
        axes[2].legend(loc='upper left')
        axes[2].grid(True, alpha=0.3)
        axes[2].set_ylim([0, 100])
        
        # Format x-axis
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved to {output_file}")
        else:
            plt.show()
    
    @staticmethod
    def plot_anomalies(anomaly_file: str, metrics_file: str, output_file: Optional[str] = None) -> None:
        """
        Plot metrics with anomalies highlighted
        
        Args:
            anomaly_file: Path to anomalies JSON file
            metrics_file: Path to metrics JSON file
            output_file: Output file path
        """
        with open(anomaly_file, 'r') as f:
            anomalies = json.load(f)
        
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
        
        # Create timestamp mapping
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        cpu = [m['cpu']['percent'] for m in metrics]
        
        # Extract anomaly timestamps and probabilities
        anomaly_times = []
        anomaly_probs = []
        for a in anomalies:
            if a['is_anomaly']:
                anomaly_times.append(datetime.fromisoformat(a['timestamp']))
                anomaly_probs.append(a['anomaly_probability'])
        
        # Plot
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Plot normal metrics
        ax.plot(timestamps, cpu, label='CPU %', color='#4ECDC4', linewidth=2)
        
        # Highlight anomalies
        for atime, aprob in zip(anomaly_times, anomaly_probs):
            color_intensity = aprob
            ax.axvline(x=atime, color='red', alpha=color_intensity*0.7, linewidth=2)
        
        ax.set_ylabel('CPU Usage (%)', fontsize=12)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_title('Anomaly Detection Results', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            plt.Line2D([0], [0], color='#4ECDC4', linewidth=2, label='CPU Utilization'),
            Patch(facecolor='red', alpha=0.5, label='Detected Anomalies')
        ]
        ax.legend(handles=legend_elements, loc='upper left')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved to {output_file}")
        else:
            plt.show()
    
    @staticmethod
    def plot_anomaly_scores(anomaly_file: str, output_file: Optional[str] = None) -> None:
        """
        Plot anomaly probability distribution
        
        Args:
            anomaly_file: Path to anomalies JSON file
            output_file: Output file path
        """
        with open(anomaly_file, 'r') as f:
            anomalies = json.load(f)
        
        if not anomalies:
            print("No anomaly data")
            return
        
        scores = [a['anomaly_score'] for a in anomalies]
        probs = [a['anomaly_probability'] for a in anomalies]
        timestamps = [datetime.fromisoformat(a['timestamp']) for a in anomalies]
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Anomaly Detection Analysis', fontsize=16, fontweight='bold')
        
        # Time series of anomaly scores
        axes[0, 0].plot(timestamps, scores, color='#FF6B6B', linewidth=1)
        axes[0, 0].set_title('Anomaly Scores Over Time', fontweight='bold')
        axes[0, 0].set_ylabel('Anomaly Score')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(axes[0, 0].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Histogram of anomaly scores
        axes[0, 1].hist(scores, bins=30, color='#4ECDC4', edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('Distribution of Anomaly Scores', fontweight='bold')
        axes[0, 1].set_xlabel('Anomaly Score')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Time series of probabilities
        axes[1, 0].plot(timestamps, probs, color='#95E1D3', linewidth=1)
        axes[1, 0].axhline(y=0.7, color='red', linestyle='--', label='Threshold (0.7)', alpha=0.7)
        axes[1, 0].set_title('Anomaly Probability Over Time', fontweight='bold')
        axes[1, 0].set_ylabel('Probability')
        axes[1, 0].set_ylim([0, 1])
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(axes[1, 0].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Statistics
        axes[1, 1].axis('off')
        stats_text = f"""
        Statistics:
        
        Total Samples: {len(anomalies)}
        Anomalies Detected: {sum(1 for a in anomalies if a['is_anomaly'])}
        
        Anomaly Score:
          Min: {min(scores):.4f}
          Max: {max(scores):.4f}
          Mean: {np.mean(scores):.4f}
          Std: {np.std(scores):.4f}
        
        Anomaly Probability:
          Min: {min(probs):.4f}
          Max: {max(probs):.4f}
          Mean: {np.mean(probs):.4f}
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
                       verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved to {output_file}")
        else:
            plt.show()
    
    @staticmethod
    def plot_recovery_actions(action_file: str, output_file: Optional[str] = None) -> None:
        """
        Plot recovery actions timeline
        
        Args:
            action_file: Path to actions JSON file
            output_file: Output file path
        """
        with open(action_file, 'r') as f:
            actions = json.load(f)
        
        if not actions:
            print("No action data")
            return
        
        # Filter successful actions only
        successful = [a for a in actions if a['status'] == 'success']
        
        if not successful:
            print("No successful actions to plot")
            return
        
        # Extract data
        action_types = [a['action_type'] for a in successful]
        start_times = [datetime.fromisoformat(a['start_time']) for a in successful]
        durations = []
        
        for a in successful:
            if a['start_time'] and a['end_time']:
                start = datetime.fromisoformat(a['start_time'])
                end = datetime.fromisoformat(a['end_time'])
                durations.append((end - start).total_seconds())
            else:
                durations.append(0)
        
        # Count by type
        from collections import Counter
        action_counts = Counter(action_types)
        
        # Create figure
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Recovery Actions Analysis', fontsize=16, fontweight='bold')
        
        # Timeline
        colors = {'scale_up': '#FF6B6B', 'optimize_memory': '#4ECDC4', 
                 'optimize_cpu': '#95E1D3', 'restart_service': '#FFE66D'}
        
        for i, (atype, start, duration) in enumerate(zip(action_types, start_times, durations)):
            color = colors.get(atype, '#999999')
            axes[0].barh(i, duration, left=start, color=color, height=0.6, alpha=0.8)
        
        axes[0].set_xlabel('Time', fontsize=11)
        axes[0].set_ylabel('Action', fontsize=11)
        axes[0].set_title('Recovery Actions Timeline', fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='x')
        axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Action distribution
        types = list(action_counts.keys())
        counts = list(action_counts.values())
        
        bars = axes[1].bar(types, counts, color=[colors.get(t, '#999999') for t in types], alpha=0.8)
        axes[1].set_ylabel('Count', fontsize=11)
        axes[1].set_title('Action Distribution', fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
        
        plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved to {output_file}")
        else:
            plt.show()


if __name__ == "__main__":
    # Example usage
    print("Visualization module loaded")
    print("Use MetricsVisualizer class to create plots")
