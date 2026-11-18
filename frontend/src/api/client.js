/**
 * Central API Client for MotorGuard AI Backend.
 */

const BASE_URL = ''; // Relative URL handled by Vite proxy to localhost:8000

export async function fetchJson(endpoint, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `HTTP Error ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

// Dataset APIs
export const getDatasetCatalog = () => fetchJson('/api/dataset/catalog');
export const getDatasetSummary = () => fetchJson('/api/dataset/summary');
export const getRawSignalPreview = (fileId, points = 2048) => 
  fetchJson(`/api/dataset/raw-signal/${fileId}?points=${points}`);

// Playback APIs
export const getPlaybackOptions = () => fetchJson('/api/playback/options');
export const getPlaybackWindow = (fileId, windowIdx, model = 'rf', saveLog = true, downsample = 256) =>
  fetchJson(`/api/playback/window/${fileId}/${windowIdx}?model=${model}&save_log=${saveLog}&downsample_points=${downsample}`);

// Math APIs
export const getMathOverview = () => fetchJson('/api/math/overview');
export const getFeatureDistribution = (feature = 'rms', condition = null) => 
  fetchJson(`/api/math/distribution?feature=${feature}${condition ? `&condition=${encodeURIComponent(condition)}` : ''}`);
export const getConditionComparison = (feature = 'rms') => 
  fetchJson(`/api/math/condition-comparison?feature=${feature}`);
export const getZScoreAnalysis = (feature = 'rms', targetCondition = 'Outer Race Fault') =>
  fetchJson(`/api/math/zscore?feature=${feature}&target_condition=${encodeURIComponent(targetCondition)}`);
export const getMultivariateAnalytics = (featX = 'rms', featY = 'kurtosis') =>
  fetchJson(`/api/math/multivariate?feat_x=${featX}&feat_y=${featY}`);
export const getJointDistribution = (featX = 'rms', featY = 'kurtosis', bins = 15) =>
  fetchJson(`/api/math/joint?feat_x=${featX}&feat_y=${featY}&bins=${bins}`);
export const getEducationalDemos = () => fetchJson('/api/math/educational');

// ML APIs
export const getModelMetrics = () => fetchJson('/api/ml/metrics');
export const getFeatureImportance = () => fetchJson('/api/ml/feature-importance');
export const predictFeatures = (features, model = 'rf') =>
  fetchJson(`/api/ml/predict?model=${model}`, {
    method: 'POST',
    body: JSON.stringify(features),
  });

// History & Maintenance APIs
export const getHistoryLogs = (limit = 50, condition = null) =>
  fetchJson(`/api/history/logs?limit=${limit}${condition ? `&condition=${encodeURIComponent(condition)}` : ''}`);
export const getHistoryStats = () => fetchJson('/api/history/stats');
export const clearHistoryLogs = () =>
  fetchJson('/api/history/clear', { method: 'DELETE' });
export const getMaintenancePlaybook = () => fetchJson('/api/maintenance/playbook');
export const getMaintenanceRecords = () => fetchJson('/api/maintenance/records');
export const createMaintenanceRecord = (record) =>
  fetchJson('/api/maintenance/records', {
    method: 'POST',
    body: JSON.stringify(record),
  });
export const updateMaintenanceStatus = (recordId, status) =>
  fetchJson(`/api/maintenance/records/${recordId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
export const getHealth = () => fetchJson('/api/health');
