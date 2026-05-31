import { useEffect, useState } from 'react'
import { Plus, Bot, Mail, TrendingUp, X, RefreshCw } from 'lucide-react'
import { dealsAPI, leadsAPI, agentsAPI } from '../services/api'
import toast from 'react-hot-toast'

const STAGES = ['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost']

const STAGE_COLORS = {
  new: 'bg-gray-100 text-gray-700 border-gray-200',
  contacted: 'bg-blue-100 text-blue-700 border-blue-200',
  qualified: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  proposal: 'bg-orange-100 text-orange-700 border-orange-200',
  negotiation: 'bg-purple-100 text-purple-700 border-purple-200',
  closed_won: 'bg-green-100 text-green-700 border-green-200',
  closed_lost: 'bg-red-100 text-red-700 border-red-200',
}

function AddDealModal({ onClose, onSave }) {
  const [leads, setLeads] = useState([])
  const [form, setForm] = useState({
    lead_id: '', deal_name: '', deal_value: '', stage: 'new',
    expected_close_date: '',
  })

  useEffect(() => {
    leadsAPI.getAll({ limit: 200 }).then(r => setLeads(r.data.leads)).catch(() => {})
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.lead_id || !form.deal_name || !form.deal_value) {
      return toast.error('Lead, name and value are required')
    }
    try {
      await dealsAPI.create({ ...form, deal_value: parseFloat(form.deal_value) })
      toast.success('Deal created!')
      onSave()
      onClose()
    } catch {
      toast.error('Failed to create deal')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-lg shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Create New Deal</h2>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Lead *</label>
            <select
              value={form.lead_id}
              onChange={e => setForm(f => ({ ...f, lead_id: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a lead...</option>
              {leads.map(l => (
                <option key={l._id} value={l._id}>{l.company_name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Deal Name *</label>
            <input
              type="text"
              value={form.deal_name}
              onChange={e => setForm(f => ({ ...f, deal_name: e.target.value }))}
              placeholder="e.g. Acme Corp - Enterprise Plan"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Deal Value ($) *</label>
              <input
                type="number"
                value={form.deal_value}
                onChange={e => setForm(f => ({ ...f, deal_value: e.target.value }))}
                placeholder="50000"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Stage</label>
              <select
                value={form.stage}
                onChange={e => setForm(f => ({ ...f, stage: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {STAGES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Expected Close Date</label>
            <input
              type="date"
              value={form.expected_close_date}
              onChange={e => setForm(f => ({ ...f, expected_close_date: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg text-sm hover:bg-gray-50">Cancel</button>
            <button type="submit" className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm hover:bg-blue-700">Create Deal</button>
          </div>
        </form>
      </div>
    </div>
  )
}

function DealCard({ deal, onPredict, onFollowUp, onStageChange }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-sm font-semibold text-gray-900 leading-tight">{deal.deal_name}</h3>
        <span className="text-sm font-bold text-green-700 ml-2 shrink-0">
          ${(deal.deal_value / 1000).toFixed(0)}K
        </span>
      </div>

      <div className="flex items-center gap-2 mb-3">
        <div className="flex-1 bg-gray-100 rounded-full h-1.5">
          <div
            className="bg-blue-500 h-1.5 rounded-full"
            style={{ width: `${deal.probability || 0}%` }}
          />
        </div>
        <span className="text-xs text-gray-500">{deal.probability || 0}%</span>
      </div>

      {deal.predicted_close_date && (
        <p className="text-xs text-gray-400 mb-3">
          Predicted close: {new Date(deal.predicted_close_date).toLocaleDateString()}
        </p>
      )}

      <div className="flex gap-1">
        <button
          onClick={() => onPredict(deal._id)}
          title="Predict Outcome"
          className="flex-1 flex items-center justify-center gap-1 text-xs py-1.5 text-purple-600 bg-purple-50 rounded hover:bg-purple-100"
        >
          <TrendingUp className="w-3 h-3" />
          Predict
        </button>
        <button
          onClick={() => onFollowUp(deal._id)}
          title="Send Follow-up"
          className="flex-1 flex items-center justify-center gap-1 text-xs py-1.5 text-blue-600 bg-blue-50 rounded hover:bg-blue-100"
        >
          <Mail className="w-3 h-3" />
          Follow-up
        </button>
      </div>

      <select
        value={deal.stage}
        onChange={e => onStageChange(deal._id, e.target.value)}
        className="w-full mt-2 text-xs border border-gray-200 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        {STAGES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
      </select>
    </div>
  )
}

export default function Deals() {
  const [deals, setDeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)

  useEffect(() => { loadDeals() }, [])

  async function loadDeals() {
    setLoading(true)
    try {
      const res = await dealsAPI.getAll({ limit: 200 })
      setDeals(res.data.deals)
    } catch {
      toast.error('Failed to load deals')
    } finally {
      setLoading(false)
    }
  }

  async function predictDeal(dealId) {
    try {
      const res = await agentsAPI.predictDeal(dealId)
      toast.success(`Prediction: ${res.data.close_probability}% close probability`)
      loadDeals()
    } catch {
      toast.error('Prediction failed')
    }
  }

  async function sendFollowUp(dealId) {
    try {
      await agentsAPI.sendFollowUp(dealId)
      toast.success('Follow-up email sent!')
    } catch {
      toast.error('Failed to send follow-up')
    }
  }

  async function changeStage(dealId, stage) {
    try {
      await dealsAPI.update(dealId, { stage })
      toast.success(`Stage updated to ${stage}`)
      loadDeals()
    } catch {
      toast.error('Failed to update stage')
    }
  }

  const dealsByStage = STAGES.reduce((acc, stage) => {
    acc[stage] = deals.filter(d => d.stage === stage)
    return acc
  }, {})

  const totalValue = deals.reduce((s, d) => s + (d.deal_value || 0), 0)
  const wonValue = deals.filter(d => d.stage === 'closed_won').reduce((s, d) => s + (d.deal_value || 0), 0)

  return (
    <div className="p-8">
      {showAddModal && <AddDealModal onClose={() => setShowAddModal(false)} onSave={loadDeals} />}

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Deals Pipeline</h1>
          <p className="text-gray-500 mt-1">
            {deals.length} deals · ${(totalValue / 1000).toFixed(0)}K pipeline · ${(wonValue / 1000).toFixed(0)}K won
          </p>
        </div>
        <div className="flex gap-3">
          <button onClick={loadDeals} className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <RefreshCw className="w-4 h-4 text-gray-500" />
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm"
          >
            <Plus className="w-4 h-4" />
            New Deal
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-4">
          {STAGES.map(stage => (
            <div key={stage} className="flex-shrink-0 w-64">
              <div className={`flex items-center justify-between px-3 py-2 rounded-t-lg border ${STAGE_COLORS[stage]}`}>
                <span className="text-xs font-semibold capitalize">{stage.replace('_', ' ')}</span>
                <span className="text-xs font-bold">{dealsByStage[stage].length}</span>
              </div>
              <div className="bg-gray-50 rounded-b-lg border border-t-0 border-gray-200 p-2 min-h-32 space-y-2">
                {dealsByStage[stage].length === 0 ? (
                  <p className="text-xs text-gray-400 text-center py-4">No deals</p>
                ) : (
                  dealsByStage[stage].map(deal => (
                    <DealCard
                      key={deal._id}
                      deal={deal}
                      onPredict={predictDeal}
                      onFollowUp={sendFollowUp}
                      onStageChange={changeStage}
                    />
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
