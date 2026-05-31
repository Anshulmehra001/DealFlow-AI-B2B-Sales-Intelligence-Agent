import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { analyticsAPI, agentsAPI } from '../services/api'
import { RefreshCw, Bot, TrendingUp, Target, Zap } from 'lucide-react'
import toast from 'react-hot-toast'

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899']

function MetricCard({ title, value, sub, icon: Icon, color }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center gap-3 mb-2">
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <p className="text-sm text-gray-500">{title}</p>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function Analytics() {
  const [pipelineStats, setPipelineStats] = useState({})
  const [scoreDistribution, setScoreDistribution] = useState([])
  const [agentPerformance, setAgentPerformance] = useState([])
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { loadAll() }, [])

  async function loadAll() {
    setLoading(true)
    try {
      const [pipelineRes, scoreRes, perfRes, insightsRes] = await Promise.allSettled([
        analyticsAPI.getPipelineStats(),
        analyticsAPI.getLeadScoreDistribution(),
        agentsAPI.getPerformance(),
        agentsAPI.getPipelineInsights(),
      ])

      if (pipelineRes.status === 'fulfilled') setPipelineStats(pipelineRes.value.data)
      if (scoreRes.status === 'fulfilled') setScoreDistribution(scoreRes.value.data.distribution || [])
      if (perfRes.status === 'fulfilled') setAgentPerformance(perfRes.value.data.agents || [])
      if (insightsRes.status === 'fulfilled') setInsights(insightsRes.value.data)
    } catch {
      toast.error('Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  // Format pipeline data for chart
  const pipelineChartData = Object.entries(pipelineStats).map(([stage, data]) => ({
    stage: stage.replace('_', ' '),
    deals: data.count,
    value: Math.round(data.total_value / 1000),
    probability: Math.round(data.avg_probability),
  }))

  // Format score distribution for pie chart
  const scoreLabels = { 0: '0-24', 25: '25-49', 50: '50-74', 75: '75-100' }
  const scoreChartData = scoreDistribution.map(d => ({
    name: scoreLabels[d._id] || d._id,
    value: d.count,
  }))

  // Agent performance chart data
  const agentChartData = agentPerformance.map(a => ({
    agent: a._id,
    total: a.total,
    success: a.success,
    failed: a.failed,
    rate: Math.round(a.success_rate),
  }))

  const totalDeals = Object.values(pipelineStats).reduce((s, v) => s + v.count, 0)
  const totalValue = Object.values(pipelineStats).reduce((s, v) => s + v.total_value, 0)
  const wonDeals = pipelineStats['closed_won']?.count || 0
  const winRate = totalDeals > 0 ? Math.round((wonDeals / totalDeals) * 100) : 0

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-500 mt-1">Pipeline performance and agent metrics</p>
        </div>
        <button onClick={loadAll} className="flex items-center gap-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 text-sm">
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard title="Total Pipeline" value={`$${(totalValue / 1000).toFixed(0)}K`} icon={TrendingUp} color="bg-blue-500" />
        <MetricCard title="Total Deals" value={totalDeals} icon={Target} color="bg-purple-500" sub={`${wonDeals} won`} />
        <MetricCard title="Win Rate" value={`${winRate}%`} icon={Zap} color="bg-green-500" />
        <MetricCard
          title="Agent Actions"
          value={agentPerformance.reduce((s, a) => s + a.total, 0)}
          icon={Bot}
          color="bg-orange-500"
          sub={`${Math.round(agentPerformance.reduce((s, a) => s + a.success_rate, 0) / (agentPerformance.length || 1))}% success rate`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Pipeline by Stage */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Pipeline by Stage (Value $K)</h2>
          {pipelineChartData.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-8">No deal data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={pipelineChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="stage" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Value ($K)" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Lead Score Distribution */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Lead Score Distribution</h2>
          {scoreChartData.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-8">No lead data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={scoreChartData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {scoreChartData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Agent Performance */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-500" />
          Agent Performance
        </h2>
        {agentChartData.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-8">No agent activity yet</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {agentChartData.map((agent) => (
              <div key={agent.agent} className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-900 capitalize mb-3">{agent.agent} Agent</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Total Actions</span>
                    <span className="font-medium">{agent.total}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Successful</span>
                    <span className="font-medium text-green-600">{agent.success}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Failed</span>
                    <span className="font-medium text-red-600">{agent.failed}</span>
                  </div>
                  <div className="mt-2">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-500">Success Rate</span>
                      <span className="font-bold text-blue-600">{agent.rate}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${agent.rate}%` }} />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pipeline Insights */}
      {insights && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Pipeline Insights</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-700">{insights.total_deals || 0}</p>
              <p className="text-xs text-gray-500 mt-1">Total Deals</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-700">${((insights.total_pipeline_value || 0) / 1000).toFixed(0)}K</p>
              <p className="text-xs text-gray-500 mt-1">Pipeline Value</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-700">{Math.round(insights.weighted_probability || 0)}%</p>
              <p className="text-xs text-gray-500 mt-1">Avg Probability</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <p className="text-2xl font-bold text-orange-700">${((insights.expected_revenue || 0) / 1000).toFixed(0)}K</p>
              <p className="text-xs text-gray-500 mt-1">Expected Revenue</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
