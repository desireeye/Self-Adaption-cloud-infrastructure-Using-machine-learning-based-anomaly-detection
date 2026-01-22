/**
 * Charts and Visualization Components
 */
import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart
} from 'recharts';

/**
 * Metrics Timeline Chart
 */
export const MetricsTimeline = ({ data = [] }) => {
  if (!data || data.length === 0) {
    return <div className="chart-container flex items-center justify-center text-slate-400">No data</div>;
  }

  const chartData = data.map((item, index) => ({
    timestamp: new Date(item.timestamp).toLocaleTimeString(),
    cpu: item.cpu_percent || 0,
    memory: item.memory_percent || 0,
    disk: item.disk_percent || 0
  }));

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="timestamp" stroke="#94a3b8" style={{ fontSize: '12px' }} />
          <YAxis stroke="#94a3b8" domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#e2e8f0' }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="cpu"
            stroke="#3b82f6"
            fillOpacity={0.1}
            fill="url(#colorCpu)"
            name="CPU %"
          />
          <Area
            type="monotone"
            dataKey="memory"
            stroke="#ef4444"
            fillOpacity={0.1}
            fill="url(#colorMemory)"
            name="Memory %"
          />
          <Line
            type="monotone"
            dataKey="disk"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={false}
            name="Disk %"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Anomaly Score Distribution
 */
export const AnomalyScoreChart = ({ data = [], currentScore = 0 }) => {
  const chartData = [
    { range: '0-20', count: Math.random() * 50, name: 'Normal' },
    { range: '20-40', count: Math.random() * 30, name: 'Low Risk' },
    { range: '40-60', count: Math.random() * 20, name: 'Medium' },
    { range: '60-80', count: Math.random() * 10, name: 'High' },
    { range: '80-100', count: Math.random() * 5, name: 'Critical' }
  ];

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="range" stroke="#94a3b8" style={{ fontSize: '12px' }} />
          <YAxis stroke="#94a3b8" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#e2e8f0' }}
          />
          <Bar dataKey="count" fill="#8b5cf6" name="Samples" />
          <Line
            type="monotone"
            dataKey={() => currentScore}
            stroke="#ef4444"
            strokeWidth={2}
            name={`Current: ${(currentScore * 100).toFixed(1)}%`}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Network Throughput Chart
 */
export const NetworkChart = ({ data = [] }) => {
  if (!data || data.length === 0) {
    return <div className="chart-container flex items-center justify-center text-slate-400">No data</div>;
  }

  const chartData = data.map(item => ({
    timestamp: new Date(item.timestamp).toLocaleTimeString(),
    sent: (item.network_bytes_sent_per_sec || 0) / 1024 / 1024, // MB/s
    received: (item.network_bytes_recv_per_sec || 0) / 1024 / 1024  // MB/s
  }));

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="timestamp" stroke="#94a3b8" style={{ fontSize: '12px' }} />
          <YAxis stroke="#94a3b8" label={{ value: 'MB/s', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            labelStyle={{ color: '#e2e8f0' }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="sent"
            stroke="#06b6d4"
            strokeWidth={2}
            dot={false}
            name="Sent (MB/s)"
          />
          <Line
            type="monotone"
            dataKey="received"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Received (MB/s)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Recovery Actions Timeline
 */
export const ActionsTimeline = ({ actions = [] }) => {
  if (!actions || actions.length === 0) {
    return (
      <div className="chart-container flex items-center justify-center text-slate-400">
        No recent actions
      </div>
    );
  }

  const sortedActions = [...actions].sort((a, b) => 
    new Date(b.timestamp) - new Date(a.timestamp)
  ).slice(0, 8);

  return (
    <div className="space-y-3">
      {sortedActions.map((action, idx) => (
        <div
          key={idx}
          className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 border border-slate-700"
        >
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
          <div className="flex-1 min-w-0">
            <div className="font-medium text-white text-sm">
              {action.action_type} ({action.target})
            </div>
            <div className="text-xs text-slate-400 truncate">
              {action.reason || 'No reason specified'}
            </div>
          </div>
          <div className="text-right">
            <div className={clsx(
              'text-xs font-medium px-2 py-1 rounded',
              action.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
            )}>
              {action.status}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

import clsx from 'clsx';
