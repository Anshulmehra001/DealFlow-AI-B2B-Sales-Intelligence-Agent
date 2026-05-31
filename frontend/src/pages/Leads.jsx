import { useEffect, useState, useRef } from 'react'
import { Plus, Upload, Search, Bot, Mail, Star, RefreshCw, X } from 'lucide-react'
import { leadsAPI, agentsAPI } from '../services/api'
import toast from 'react-hot-toast'

const STATUS_COLORS = {
  new: 'bg-gray-100 text-gray-700',
  enriching: 'bg-yellow-100 text-yellow-700',
  qualified: 'bg-green-100 text-green-700',
  unqualified: 'bg-red-100 text-red-700',
  contacted: 'bg-blue-100 text-blue-700',
  engaged: 'bg-purple-100 text-purple-700',
  converted: 'bg-emerald-100 text-emerald-700',
}

function ScoreBadge({ score }) {
  const color = score >= 75 ? 'text-green-700 bg-green-100' : score >= 50 ? 'text-yellow-700 bg-yellow-100' : 'text-red-700 bg-red-100'
  return <span className={`text-xs font-bold px-2 py-1 rounded-full ${color}`}>{score}</span>
}

function AddLeadModal({ onClose, onSave }) {
  const [form, setForm] = useState({
    company_name: '', website: '', industry: '', company_size: '',
    contact_person: '', email: '', phone: '',
  })

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.company_name) return toast.error('Company name is required')
    try {
      await leadsAPI.create(form)
      toast.success('Lead created and queued for enrichment')
      onSave()
      onClose()
    } catch {
      toast.error('Failed to create lead')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-lg shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Add New Lead</h2>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          {[
            { key: 'company_name', label: 'Company Name *', type: 'text' },
            { key: 'website', label: 'Website', type: 'url' },
            { key: 'contact_person', label: 'Contact Person', type: 'text' },
            { key: 'email', label: 'Email', type: 'email' },
            { key: 'phone', label: 'Phone', type: 'tel' },
          ].map(({ key, label, type }) => (
            <div key={key}>
              <label className="block text-sm text-gray-600 mb-1">{label}</label>
              <input
                type={type}
                value={form[key]}
                onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          ))}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Industry</label>
              <select
                value={form.industry}
                onChange={e => setForm(f => ({ ...f, industry: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {['saas', 'fintech', 'healthcare', 'ecommerce', 'manufacturing', 'retail', 'education', 'other'].map(i => (
                  <option key={i} value={i}>{i}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Company Size</label>
              <select
                value={form.company_size}
                onChange={e => setForm(f => ({ ...f, company_size: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                {['1-10', '11-50', '51-200', '201-1000', '1000+'].map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg text-sm hover:bg-gray-50">Cancel</button>
            <button type="submit" className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm hover:bg-blue-700">Create Lead</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Leads() {
  const [leads, setLeads] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [processingId, setProcessingId] = useState(null)
  const fileRef = useRef()

  useEffect(() => { loadLeads() }, [statusFilter])

  async function loadLeads() {
    setLoading(true)
    try {
      const res = await leadsAPI.getAll({ limit: 200, status: statusFilter || undefined })
      setLeads(res.data.leads)
      setTotal(res.data.total)
    } catch {
      toast.error('Failed to load leads')
    } finally {
      setLoading(false)
    }
  }

  async function handleCSVImport(e) {
    const file = e.target.files[0]
    if (!file) return
    try {
      const res = await leadsAPI.bulkImport(file)
      toast.success(`Imported ${res.data.imported_count} leads — enrichment running in background`)
      loadLeads()
    } catch {
      toast.error('Import failed')
    }
    e.target.value = ''
  }

  async function processLead(leadId) {
    setProcessingId(leadId)
    try {
      const res = await agentsAPI.processLead(leadId)
      toast.success(`Lead scored: ${res.data.lead_score}/100`)
      loadLeads()
    } catch {
      toast.error('Processing failed')
    } finally {
      setProcessingId(null)
    }
  }

  async function sendOutreach(leadId) {
    try {
      await agentsAPI.sendOutreach(leadId)
      toast.success('Outreach email sent!')
      loadLeads()
    } catch {
      toast.error('Failed to send outreach')
    }
  }

  const filtered = leads.filter(l =>
    l.company_name?.toLowerCase().includes(search.toLowerCase()) ||
    l.email?.toLowerCase().includes(search.toLowerCase()) ||
    l.contact_person?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="p-8">
      {showAddModal && <AddLeadModal onClose={() => setShowAddModal(false)} onSave={loadLeads} />}

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
          <p className="text-gray-500 mt-1">{total} total leads</p>
        </div>
        <div className="flex gap-3">
          <input ref={fileRef} type="file" accept=".csv" className="hidden" onChange={handleCSVImport} />
          <button
            onClick={() => fileRef.current.click()}
            className="flex items-center gap-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 text-sm"
          >
            <Upload className="w-4 h-4" />
            Import CSV
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm"
          >
            <Plus className="w-4 h-4" />
            Add Lead
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search leads..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Statuses</option>
          {Object.keys(STATUS_COLORS).map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button onClick={loadLeads} className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
          <RefreshCw className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No leads yet. Import a CSV or add manually.</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {['Company', 'Contact', 'Industry', 'Size', 'Score', 'Status', 'Actions'].map(h => (
                  <th key={h} className="text-left text-xs font-medium text-gray-500 uppercase px-4 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map(lead => (
                <tr key={lead._id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{lead.company_name}</p>
                      {lead.website && (
                        <a href={lead.website} target="_blank" rel="noreferrer" className="text-xs text-blue-500 hover:underline">
                          {lead.website.replace(/https?:\/\//, '')}
                        </a>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-sm text-gray-700">{lead.contact_person || '—'}</p>
                    <p className="text-xs text-gray-400">{lead.email || ''}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-gray-600 capitalize">{lead.industry || '—'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-gray-600">{lead.company_size || '—'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <ScoreBadge score={lead.lead_score || 0} />
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[lead.status] || 'bg-gray-100 text-gray-600'}`}>
                      {lead.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => processLead(lead._id)}
                        disabled={processingId === lead._id}
                        title="Enrich & Score"
                        className="p-1.5 text-purple-600 hover:bg-purple-50 rounded-lg disabled:opacity-50"
                      >
                        {processingId === lead._id
                          ? <div className="w-4 h-4 animate-spin rounded-full border-b-2 border-purple-600" />
                          : <Bot className="w-4 h-4" />}
                      </button>
                      {lead.email && (
                        <button
                          onClick={() => sendOutreach(lead._id)}
                          title="Send Outreach"
                          className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg"
                        >
                          <Mail className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
