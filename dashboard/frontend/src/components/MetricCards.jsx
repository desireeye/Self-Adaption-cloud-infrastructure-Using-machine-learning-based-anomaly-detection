/**
 * Metric Card Component
 * Displays single metric in Bento-style card
 */
import React from 'react';
import clsx from 'clsx';

export const MetricCard = ({ 
  label, 
  value, 
  unit = '%', 
  icon: Icon,
  status = 'normal',
  trend = null
}) => {
  const getStatusColor = () => {
    switch(status) {
      case 'critical': return 'border-red-500/30 bg-red-500/10';
      case 'warning': return 'border-yellow-500/30 bg-yellow-500/10';
      case 'healthy': return 'border-green-500/30 bg-green-500/10';
      default: return 'border-slate-700 bg-slate-800';
    }
  };

  const getTextColor = () => {
    switch(status) {
      case 'critical': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      case 'healthy': return 'text-green-400';
      default: return 'text-white';
    }
  };

  const getTrendIndicator = () => {
    if (!trend) return null;
    if (trend > 0) {
      return <span className="text-red-400 ml-2">↑ {trend.toFixed(1)}%</span>;
    } else if (trend < 0) {
      return <span className="text-green-400 ml-2">↓ {Math.abs(trend).toFixed(1)}%</span>;
    }
    return null;
  };

  return (
    <div className={clsx(
      'bento-card border',
      getStatusColor()
    )}>
      <div className="flex items-center justify-between mb-4">
        {Icon && <Icon className="w-6 h-6 text-slate-400" />}
        <span className="metric-label">{label}</span>
      </div>
      <div className="flex items-baseline gap-1">
        <span className={clsx('metric-value', getTextColor())}>
          {typeof value === 'number' ? value.toFixed(1) : value}
        </span>
        <span className="text-sm text-slate-400">{unit}</span>
        {getTrendIndicator()}
      </div>
    </div>
  );
};

/**
 * Status Badge Component
 */
export const StatusBadge = ({ status, label }) => {
  const getStatusClass = () => {
    switch(status) {
      case 'stable': return 'status-stable';
      case 'adapting': return 'status-adapting';
      case 'recovering': return 'status-critical';
      case 'critical': return 'status-critical';
      default: return 'status-stable';
    }
  };

  return (
    <span className={clsx('status-badge', getStatusClass())}>
      <span className="w-2 h-2 bg-current rounded-full animate-pulse"></span>
      {label || status}
    </span>
  );
};

/**
 * Health Score Gauge
 */
export const HealthGauge = ({ score = 0, size = 'md' }) => {
  const getGaugeColor = () => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#eab308';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  };

  const sizeClass = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32'
  }[size] || 'w-24 h-24';

  return (
    <div className={clsx('relative flex items-center justify-center', sizeClass)}>
      <svg className="transform -rotate-90 w-full h-full" viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="#334155"
          strokeWidth="8"
        />
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke={getGaugeColor()}
          strokeWidth="8"
          strokeDasharray={`${2 * Math.PI * 45 * (score / 100)} ${2 * Math.PI * 45}`}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute text-center">
        <div className="text-2xl font-bold text-white">{score.toFixed(0)}</div>
        <div className="text-xs text-slate-400">Score</div>
      </div>
    </div>
  );
};

/**
 * Large Card Container for Bento Layout
 */
export const BentoCard = ({ 
  children, 
  span = 1, 
  className = '' 
}) => {
  const spanClass = {
    1: 'col-span-1',
    2: 'col-span-2',
    3: 'col-span-3'
  }[span] || 'col-span-1';

  return (
    <div className={clsx('bento-card', spanClass, className)}>
      {children}
    </div>
  );
};

/**
 * Action Button Component
 */
export const ActionButton = ({ 
  label, 
  onClick, 
  variant = 'primary',
  loading = false,
  disabled = false
}) => {
  const getVariantClass = () => {
    switch(variant) {
      case 'danger':
        return 'bg-red-600 hover:bg-red-700 text-white';
      case 'warning':
        return 'bg-yellow-600 hover:bg-yellow-700 text-white';
      case 'success':
        return 'bg-green-600 hover:bg-green-700 text-white';
      default:
        return 'bg-blue-600 hover:bg-blue-700 text-white';
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={clsx(
        'px-4 py-2 rounded-lg font-medium transition-colors',
        getVariantClass(),
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      {loading ? 'Loading...' : label}
    </button>
  );
};

/**
 * Sparkline Component (mini chart)
 */
export const Sparkline = ({ data = [], color = '#22c55e', height = 40 }) => {
  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((value - min) / range) * 100;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg className="w-full" viewBox="0 0 100 40" preserveAspectRatio="none">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
};

/**
 * Loading Skeleton
 */
export const CardSkeleton = () => (
  <div className="bento-card animate-pulse">
    <div className="h-4 bg-slate-700 rounded w-1/3 mb-4"></div>
    <div className="h-8 bg-slate-700 rounded w-2/3"></div>
  </div>
);

/**
 * Error Display
 */
export const ErrorDisplay = ({ error, retry }) => (
  <div className="bento-card border-red-500/30 bg-red-500/10">
    <div className="text-red-400 mb-2">⚠️ Error</div>
    <div className="text-sm text-red-300 mb-4">{error}</div>
    {retry && (
      <button
        onClick={retry}
        className="text-xs text-red-400 hover:text-red-300 underline"
      >
        Retry
      </button>
    )}
  </div>
);
