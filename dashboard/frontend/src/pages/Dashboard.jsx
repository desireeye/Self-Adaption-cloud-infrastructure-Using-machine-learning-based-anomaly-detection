/**
 * Main Dashboard Page
 * Bento-grid layout with real-time metrics and anomaly detection
 */
import React, { useState } from 'react';
import {
  Activity,
  Cpu,
  HardDrive,
  MemoryStick,
  Wifi,
  AlertTriangle,
  Zap,
  TrendingUp
} from 'lucide-react';
import {
  MetricCard,
  StatusBadge,
  HealthGauge,
  BentoCard,
  ActionButton,
  Sparkline,
  CardSkeleton,
  ErrorDisplay
} from '../components/MetricCards';
import {
  MetricsTimeline,
  AnomalyScoreChart,
  NetworkChart,
  ActionsTimeline
} from '../components/Charts';
import {
  useMetrics,
  useAnomalyDetection,
  useSystemHealth,
  useMetricsHistory,
  useActionHistory,
  useTriggerAction,
  useModelStats
} from '../hooks/useApi';

export const Dashboard = () => {
  const { metrics, loading: metricsLoading, error: metricsError, refetch: refetchMetrics } = useMetrics();
  const { anomaly, loading: anomalyLoading, error: anomalyError, refetch: refetchAnomaly } = useAnomalyDetection();
  const { health, loading: healthLoading, error: healthError, refetch: refetchHealth } = useSystemHealth();
  const { history, loading: historyLoading } = useMetricsHistory(300);
  const { actions, loading: actionsLoading } = useActionHistory(10);
  const { stats: modelStats } = useModelStats();
  const { trigger: triggerAction, loading: actionLoading } = useTriggerAction();

  const [activeTab, setActiveTab] = useState('overview');

  const handleTriggerAction = async (type, target) => {
    try {
      await triggerAction(type, target, `Manual trigger: ${type} on ${target}`);
      setTimeout(() => refetchHealth(), 1000);
    } catch (err) {
      console.error('Action failed:', err);
    }
  };

  const renderContent = () => {
    if (healthLoading || metricsLoading) {
      return <div className="grid grid-cols-4 gap-4">{[...Array(8)].map((_, i) => <CardSkeleton key={i} />)}</div>;
    }

    if (metricsError || healthError) {
      return <ErrorDisplay error={metricsError || healthError} retry={refetchMetrics} />;
    }

    return (
      <>
        {/* Header with Status */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">System Dashboard</h1>
          <div className="flex items-center gap-4">
            <StatusBadge status={health?.status || 'stable'} />
            <span className="text-sm text-slate-400">
              Last updated: {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-4 gap-4 auto-rows-auto">
          {/* Health Score - Large Card */}
          <div className="col-span-1 row-span-2">
            <BentoCard className="h-full flex flex-col items-center justify-center">
              <div className="mb-4">
                <HealthGauge score={health?.health_score || 0} size="lg" />
              </div>
              <div className="text-sm text-slate-400 text-center">System Health</div>
            </BentoCard>
          </div>

          {/* CPU Metric */}
          <MetricCard
            label="CPU Usage"
            value={metrics?.cpu_percent || 0}
            icon={Cpu}
            status={metrics?.cpu_percent > 80 ? 'critical' : metrics?.cpu_percent > 60 ? 'warning' : 'healthy'}
          />

          {/* Memory Metric */}
          <MetricCard
            label="Memory Usage"
            value={metrics?.memory_percent || 0}
            icon={MemoryStick}
            status={metrics?.memory_percent > 85 ? 'critical' : metrics?.memory_percent > 70 ? 'warning' : 'healthy'}
          />

          {/* Disk Metric */}
          <MetricCard
            label="Disk Usage"
            value={metrics?.disk_percent || 0}
            icon={HardDrive}
            status={metrics?.disk_percent > 90 ? 'critical' : metrics?.disk_percent > 80 ? 'warning' : 'healthy'}
          />

          {/* Anomaly Status */}
          <div className="bento-card border-slate-700 bg-slate-800">
            <div className="flex items-center justify-between mb-4">
              <AlertTriangle className="w-5 h-5 text-slate-400" />
              <span className="metric-label">Anomaly Status</span>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <div className={`text-2xl font-bold ${anomaly?.is_anomaly ? 'text-red-400' : 'text-green-400'}`}>
                  {anomaly?.anomaly_level?.toUpperCase() || 'NORMAL'}
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Score: {((anomaly?.anomaly_score || 0) * 100).toFixed(1)}%
                </div>
              </div>
              <div className={`w-3 h-3 rounded-full ${anomaly?.is_anomaly ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`}></div>
            </div>
          </div>

          {/* Metrics Timeline - Wide Card */}
          <div className="col-span-2 row-span-2">
            <BentoCard>
              <h3 className="text-sm font-semibold text-white mb-4">System Metrics (5 min)</h3>
              {historyLoading ? (
                <div className="chart-container flex items-center justify-center text-slate-400">Loading...</div>
              ) : (
                <MetricsTimeline data={history?.metrics || []} />
              )}
            </BentoCard>
          </div>

          {/* Network */}
          <MetricCard
            label="Network"
            value={(metrics?.network_bytes_sent + metrics?.network_bytes_recv) / 1024 / 1024 || 0}
            unit="MB/s"
            icon={Wifi}
            status="healthy"
          />

          {/* Anomaly Score Chart */}
          <div className="col-span-2">
            <BentoCard>
              <h3 className="text-sm font-semibold text-white mb-4">Anomaly Score Distribution</h3>
              <AnomalyScoreChart currentScore={anomaly?.anomaly_score || 0} />
            </BentoCard>
          </div>

          {/* ML Model Stats */}
          <div className="col-span-1">
            <BentoCard>
              <h3 className="text-xs font-semibold text-white mb-4 uppercase">Model Stats</h3>
              <div className="space-y-3">
                <div>
                  <div className="text-xs text-slate-400">Accuracy</div>
                  <div className="text-lg font-bold text-green-400">{(modelStats?.accuracy * 100 || 0).toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-xs text-slate-400">Precision</div>
                  <div className="text-lg font-bold text-blue-400">{(modelStats?.precision * 100 || 0).toFixed(1)}%</div>
                </div>
              </div>
            </BentoCard>
          </div>

          {/* Recent Actions - Wide Card */}
          <div className="col-span-2">
            <BentoCard>
              <h3 className="text-sm font-semibold text-white mb-4">Recent Actions</h3>
              {actionsLoading ? (
                <div className="text-slate-400">Loading...</div>
              ) : (
                <ActionsTimeline actions={actions} />
              )}
            </BentoCard>
          </div>

          {/* Quick Actions */}
          <div className="col-span-2">
            <BentoCard>
              <h3 className="text-sm font-semibold text-white mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-2">
                <ActionButton
                  label="Scale Up"
                  variant="primary"
                  loading={actionLoading}
                  onClick={() => handleTriggerAction('scale_up', 'compute')}
                />
                <ActionButton
                  label="Scale Down"
                  variant="primary"
                  loading={actionLoading}
                  onClick={() => handleTriggerAction('scale_down', 'compute')}
                />
                <ActionButton
                  label="Clear Cache"
                  variant="warning"
                  loading={actionLoading}
                  onClick={() => handleTriggerAction('clear_cache', 'memory')}
                />
                <ActionButton
                  label="Optimize CPU"
                  variant="success"
                  loading={actionLoading}
                  onClick={() => handleTriggerAction('optimize_cpu', 'scheduler')}
                />
              </div>
            </BentoCard>
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {renderContent()}
      </div>
    </div>
  );
};
