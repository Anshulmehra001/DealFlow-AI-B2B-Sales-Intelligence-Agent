import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE })

// ── Leads ─────────────────────────────────────────────────────────────────────
export const leadsAPI = {
  getAll: (params) => api.get('/api/leads', { params }),
  getById: (id) => api.get(`/api/leads/${id}`),
  create: (data) => api.post('/api/leads', data),
  update: (id, data) => api.put(`/api/leads/${id}`, data),
  bulkImport: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post('/api/leads/bulk-import', fd)
  },
}

// ── Deals ─────────────────────────────────────────────────────────────────────
export const dealsAPI = {
  getAll: (params) => api.get('/api/deals', { params }),
  getById: (id) => api.get(`/api/deals/${id}`),
  create: (data) => api.post('/api/deals', data),
  update: (id, data) => api.put(`/api/deals/${id}`, data),
}

// ── Agents ────────────────────────────────────────────────────────────────────
export const agentsAPI = {
  processLead: (id) => api.post(`/api/agents/prospecting/process-lead/${id}`),
  getTopLeads: (limit = 10) => api.get('/api/agents/prospecting/top-leads', { params: { limit } }),
  sendOutreach: (id) => api.post(`/api/agents/nurturing/send-outreach/${id}`),
  sendFollowUp: (id) => api.post(`/api/agents/nurturing/follow-up/${id}`),
  checkFollowUps: () => api.get('/api/agents/nurturing/check-follow-ups'),
  autoFollowUp: () => api.post('/api/agents/nurturing/auto-follow-up'),
  predictDeal: (id) => api.post(`/api/agents/intelligence/predict/${id}`),
  getAtRiskDeals: () => api.get('/api/agents/intelligence/at-risk-deals'),
  getPipelineInsights: () => api.get('/api/agents/intelligence/pipeline-insights'),
  getPerformance: () => api.get('/api/agents/performance'),
  getActions: (limit = 50) => api.get('/api/agents/actions', { params: { limit } }),
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export const analyticsAPI = {
  getPipelineStats: () => api.get('/api/analytics/pipeline-stats'),
  getLeadScoreDistribution: () => api.get('/api/analytics/lead-score-distribution'),
  getSummaryStats: () => api.get('/api/analytics/summary'),
}

export default api
