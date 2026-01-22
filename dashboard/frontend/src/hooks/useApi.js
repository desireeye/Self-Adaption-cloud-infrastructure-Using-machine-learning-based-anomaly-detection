/**
 * Custom hook for fetching and managing dashboard data
 * Handles real-time updates from backend API
 */
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useMetrics = (refreshInterval = 2000) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/metrics/current`);
      setMetrics(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchMetrics, refreshInterval]);

  return { metrics, loading, error, refetch: fetchMetrics };
};

export const useAnomalyDetection = (refreshInterval = 3000) => {
  const [anomaly, setAnomaly] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const detectAnomaly = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/anomalies/detect`);
      setAnomaly(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    detectAnomaly();
    const interval = setInterval(detectAnomaly, refreshInterval);
    return () => clearInterval(interval);
  }, [detectAnomaly, refreshInterval]);

  return { anomaly, loading, error, refetch: detectAnomaly };
};

export const useSystemHealth = (refreshInterval = 5000) => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHealth = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health/status`);
      setHealth(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchHealth, refreshInterval]);

  return { health, loading, error, refetch: fetchHealth };
};

export const useMetricsHistory = (seconds = 300, refreshInterval = 10000) => {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/metrics/history`, {
        params: { seconds }
      });
      setHistory(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [seconds]);

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchHistory, refreshInterval]);

  return { history, loading, error, refetch: fetchHistory };
};

export const useActionHistory = (limit = 10, refreshInterval = 5000) => {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchActions = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health/actions/history`, {
        params: { limit }
      });
      setActions(response.data.actions || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    fetchActions();
    const interval = setInterval(fetchActions, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchActions, refreshInterval]);

  return { actions, loading, error, refetch: fetchActions };
};

export const useTriggerAction = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const trigger = useCallback(async (actionType, target, reason = '', impact = 0) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/health/trigger-action`, null, {
        params: {
          action_type: actionType,
          target,
          reason,
          impact_estimate: impact
        }
      });
      setSuccess(response.data);
      setError(null);
      return response.data;
    } catch (err) {
      setError(err.message);
      setSuccess(null);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { trigger, loading, error, success };
};

export const useModelStats = (refreshInterval = 10000) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/anomalies/model-stats`);
      setStats(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchStats, refreshInterval]);

  return { stats, loading, error, refetch: fetchStats };
};
