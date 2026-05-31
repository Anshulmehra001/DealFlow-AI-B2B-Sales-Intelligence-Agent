import { useEffect, useState } from 'react'
import { Users, Briefcase, DollarSign, TrendingUp, Bot, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import { analyticsAPI, agentsAPI } from '../services/api'
import toast from 'react-hot-toast'

function StatCard({ title, value, icon: Icon, color, sub }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  )
}

function AgentActivityItem({ action }) {
  const statusColor = {
    success: 'text-green-600 bg-green-50',
    failed: 'text-red-600 bg-red-50',
    in_progress: 'text-blue-600 bg-blue-50',
    pending: 'text-yellow-600 bg-yellow-50',
  }
  const agentColor = {
    prospecting: 'bg-purple-100 text-purple-700',
    nurturing: 'bg-blue-100 text-blue-700',
    intelligence: 'bg-green-100 text-green-700',
  }
  return (
    <div className="flex items-center gap-3 py-3 border-b border-gray-100 last:border-0">
      <span className={`text-xs px-2 py-1 rounded-full font-medium ${agentColor[action.agent_type] || 'bg-gray-100 text-gray-600'}`}>
        {action.agent_type}
      </span>
      <span className="text-sm text-gray-700 flex-1">{action.action_type?.replace(/_/g, ' ')}</span>
      <span className={`text-xs px-2 py-1 rounded-full ${statusColor[action.status] || 'bg-gray-100 text-gray-600'}`}>
        {action.status}
      </span>
    </div>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [pipelineStats, setPipelineStats] = useState({})
  const [atRisk, setAtRisk] = useState([])
  const [agentActions, setAgentActions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  async function loadDashboard() {
    setLoading(true)
    try {
      const [summaryRes, pipelineRes, atRiskRes, actionsRes] = await Promise.allSettled([
        analyticsAPI.getSummaryStats(),
        analyticsAPI.getPipelineStats(),
        agentsAPI.getAtRiskDeals(),
        agentsAPI.getActions(10),
      ])

      if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value.data)
      if (pipelineRes.status === 'fulfilled') setPipelineStats(pipelineRes.value.data)
      if (atRiskRes.status === 'fulfilled') setAtRisk(atRiskRes.value.data.at_risk_deals || [])
      if (actionsRes.status === 'fulfilled') setAgentActions(actionsRes.value.data.actions || [])
    } catch (e) {
      toast.error('Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  async function runAutoFollowUp() {
    try {
      const res = await agentsAPI.autoFollowUp()
      toast.success(`Auto follow-up: ${res.data.sent} emails sent`)
      loadDashboard()
    } catch {
      toast.error('Auto follow-up failed')
    }
  }

  const totalPipelineValue = Object.values(pipelineStats).reduce((s, v) => s + (v.total_value || 0), 0)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Your sales pipeline at a glance</p>
        </div>
        <button
          onClick={runAutoFollowUp}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Bot className="w-4 h-4" />
          Run Auto Follow-Up
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Leads"
          value={summary?.total_leads ?? 0}
          icon={Users}
          color="bg-blue-500"
          sub={`${summary?.qualified_leads ?? 0} qualified`}
        />
        <StatCard
          title="Active Deals"
          value={summary?.total_deals ?? 0}
          icon={Briefcase}
          color="bg-purple-500"
        />
        <StatCard
          title="Pipeline Value"
          value={`$${((summary?.pipeline_value ?? totalPipelineValue) / 1000).toFixed(0)}K`}
          icon={DollarSign}
          color="bg-green-500"
          sub={`$${((summary?.won_value ?? 0) / 1000).toFixed(0)}K won`}
        />
        <StatCard
          title="At-Risk Deals"
          value={atRisk.length}
          icon={AlertTriangle}
          color="bg-red-500"
          sub="Need attention"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pipeline by Stage */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline by Stage</h2>
          {Object.keys(pipelineStats).length === 0 ? (
            <p className="text-gray-400 text-sm">No deals yet. Create your first deal.</p>
          ) : (
            <div className="space-y-3">
              {Object.entries(pipelineStats).map(([stage, data]) => (
                <div key={stage}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="capitalize text-gray-700">{stage.replace('_', ' ')}</span>
                    <span className="text-gray-500">{data.count} deals · ${(data.total_value / 1000).toFixed(0)}K</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${Math.min(data.avg_probability, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* At-Risk Deals */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            At-Risk Deals
          </h2>
          {atRisk.length === 0 ? (
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm">All deals are on track!</span>
            </div>
          ) : (
            <div className="space-y-3">
              {atRisk.slice(0, 5).map((deal) => (
                <div key={deal.deal_id} className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
                  <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{deal.deal_name}</p>
                    <p className="text-xs text-gray-500">${(deal.deal_value / 1000).toFixed(0)}K · {deal.stage}</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {deal.risk_factors?.map((f, i) => (
                        <span key={i} className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">{f}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Agent Activity */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-500" />
            Recent Agent Activity
          </h2>
          {agentActions.length === 0 ? (
            <p className="text-gray-400 text-sm">No agent activity yet. Import leads to get started.</p>
          ) : (
            <div>
              {agentActions.map((action, i) => (
                <AgentActivityItem key={i} action={action} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
