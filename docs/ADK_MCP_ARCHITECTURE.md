# DealFlow AI - ADK + MongoDB MCP Architecture

## 🏆 Google Cloud Rapid Agent Hackathon 2026

This document explains how DealFlow AI meets all hackathon requirements using **Google ADK (Agent Development Kit)** with **MongoDB MCP Server** integration.

---

## ✅ Hackathon Requirements Compliance

### 1. **Google ADK (Agent Development Kit)** ✓

We use Google's ADK framework to build three specialized agents:

- **Prospecting Agent**: Lead enrichment and scoring
- **Nurturing Agent**: Email automation and follow-ups
- **Intelligence Agent**: Analytics and predictions

**Location**: `backend/adk_agents/`

### 2. **MongoDB MCP Server Integration** ✓

All agents interact with MongoDB through the **Model Context Protocol (MCP)** server, not direct database drivers.

**Configuration**: `mcp_server_config.json`

### 3. **Gemini Model** ✓

All agents are powered by **Gemini 2.0 Flash** for reasoning and decision-making.

### 4. **Multi-Agent System** ✓

Three autonomous agents work together to manage the entire B2B sales pipeline.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
│                   (Orchestration Layer)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────┐ ┌──▼──────────┐
│ Prospecting  │ │Nurturing│ │Intelligence │
│  ADK Agent   │ │ADK Agent│ │  ADK Agent  │
└───────┬──────┘ └──┬──────┘ └──┬──────────┘
        │           │            │
        └───────────┼────────────┘
                    │
        ┌───────────▼───────────┐
        │   Gemini 2.0 Flash    │
        │  (Reasoning Engine)   │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │  MongoDB MCP Server   │
        │ (Tool/Action Layer)   │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │   MongoDB Atlas       │
        │  (Data Persistence)   │
        └───────────────────────┘
```

---

## 🔧 Component Breakdown

### 1. ADK Agents (`backend/adk_agents/`)

#### Prospecting Agent
**Purpose**: Enrich leads with external data, calculate scores, qualify opportunities

**Capabilities**:
- Find leads from MongoDB via MCP tools
- Analyze company data
- Calculate lead scores (0-100)
- Update lead status based on qualification criteria
- Log all actions for audit trail

**MCP Tools Used**:
- `find` - Query leads collection
- `update-many` - Update lead data
- `insert-many` - Log agent actions
- `aggregate` - Calculate analytics

#### Nurturing Agent
**Purpose**: Automate email outreach and follow-ups

**Capabilities**:
- Generate personalized outreach emails
- Create deals from qualified leads
- Schedule and send follow-ups
- Track engagement
- Update deal stages

**MCP Tools Used**:
- `find` - Retrieve lead/deal data
- `update-many` - Update deal status
- `insert-many` - Create deals, log activities
- `aggregate` - Find deals needing follow-up

#### Intelligence Agent
**Purpose**: Provide predictive analytics and insights

**Capabilities**:
- Predict deal win probability
- Identify at-risk deals
- Generate pipeline insights
- Analyze agent performance
- Forecast revenue

**MCP Tools Used**:
- `aggregate` - Complex pipeline analytics
- `find` - Retrieve historical data
- `db-stats` - Database performance metrics
- `explain` - Query optimization insights

### 2. MongoDB MCP Server

**What is MCP?**
Model Context Protocol is an open standard that allows AI agents to securely connect to external tools and data sources.

**Why MCP for MongoDB?**
- **Standardized Interface**: Agents use natural language to query/modify data
- **Security**: MCP provides controlled access with permissions
- **Auditability**: All agent actions are logged
- **No Direct DB Access**: Agents don't need database credentials

**Configuration** (`mcp_server_config.json`):
```json
{
  "server": {
    "command": "npx",
    "args": ["-y", "mongodb-mcp-server"],
    "env": {
      "MDB_MCP_CONNECTION_STRING": "${MONGODB_URI}",
      "MDB_MCP_READ_ONLY": "false"
    }
  }
}
```

**Available MCP Tools**:
- Database Operations: `find`, `aggregate`, `count`
- Data Modification: `insert-many`, `update-many`, `delete-many`
- Schema Management: `collection-schema`, `create-collection`
- Analytics: `db-stats`, `explain`

### 3. Gemini Integration

**Model**: `gemini-2.0-flash-exp`

**How Agents Use Gemini**:
1. Agent receives task (e.g., "Process lead ID 123")
2. Agent constructs prompt with task instructions
3. Prompt includes available MCP tools
4. Gemini reasons about the task
5. Gemini determines which MCP tools to call
6. Gemini generates natural language commands
7. MCP server executes MongoDB operations
8. Results returned to agent
9. Agent formats response

**Example Prompt Flow**:
```
User: "Process lead ABC123"
  ↓
Prospecting Agent: Constructs prompt with context
  ↓
Gemini: "I need to find this lead, analyze it, and update the score"
  ↓
MCP Tools: find → analyze → update-many
  ↓
MongoDB: Data retrieved → updated
  ↓
Agent: Returns success with insights
```

---

## 🔄 Data Flow Examples

### Example 1: Lead Import & Enrichment

```
1. User uploads CSV via FastAPI endpoint
   POST /api/leads/bulk-import

2. FastAPI creates lead documents in MongoDB
   (using direct driver for bulk import efficiency)

3. FastAPI triggers Prospecting ADK Agent
   POST /api/adk-agents/prospecting/process-lead/{id}

4. Prospecting Agent:
   - Sends prompt to Gemini with lead ID
   - Gemini uses MCP 'find' tool to get lead data
   - Gemini analyzes company/industry/contact quality
   - Gemini calculates lead score
   - Gemini uses MCP 'update-many' to save results
   - Gemini uses MCP 'insert-many' to log action

5. Lead now has:
   ✓ Enriched data
   ✓ Lead score (0-100)
   ✓ Qualification status
   ✓ Action logged
```

### Example 2: Automated Follow-up

```
1. User requests follow-up check
   GET /api/adk-agents/nurturing/check-follow-ups

2. Nurturing Agent:
   - Prompts Gemini to find deals needing follow-up
   - Gemini uses MCP 'aggregate' to query:
     * next_follow_up date in past
     * deals in certain stages
     * no recent activities

3. Gemini returns prioritized list

4. For each deal, send follow-up:
   POST /api/adk-agents/nurturing/follow-up/{deal_id}

5. Nurturing Agent:
   - Gemini finds deal + lead data via MCP
   - Gemini generates personalized email
   - Gemini updates deal with MCP:
     * Add activity record
     * Update next_follow_up date
     * Advance stage if appropriate
   - Gemini logs action via MCP
```

### Example 3: Pipeline Analytics

```
1. User requests insights
   GET /api/adk-agents/intelligence/pipeline-insights

2. Intelligence Agent:
   - Sends comprehensive analysis prompt to Gemini
   - Gemini uses multiple MCP tools:
     
     MCP aggregate on 'leads':
     - Count by status
     - Average lead score
     - Conversion rates
     
     MCP aggregate on 'deals':
     - Total value by stage
     - Win rate
     - Average days in stage
     
     MCP aggregate on 'agent_actions':
     - Actions by agent type
     - Success rates
     - Performance metrics

3. Gemini synthesizes all data into insights:
   - Key metrics
   - Trends
   - Bottlenecks
   - Recommendations

4. Returns comprehensive JSON report
```

---

## 🚀 Running the System

### Prerequisites

1. **Node.js** (for MongoDB MCP Server)
```bash
node --version  # Should be v18+
```

2. **Python 3.11+**
```bash
python --version
```

3. **MongoDB Atlas Account**
- Free tier works perfectly
- Get connection string

4. **Gemini API Key**
- Get from Google AI Studio: https://aistudio.google.com/apikey

### Installation

```bash
# 1. Clone repository
git clone <your-repo>
cd "Google Cloud Rapid Agent Hackathon"

# 2. Install MongoDB MCP Server (globally)
npm install -g mongodb-mcp-server

# 3. Setup Python environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your:
#   - MONGODB_URI
#   - MDB_MCP_CONNECTION_STRING (same as MONGODB_URI)
#   - GEMINI_API_KEY

# 5. Run backend
python main.py
```

### Testing ADK Agents

```bash
# Health check (shows ADK + MCP status)
curl http://localhost:8000/health

# Import sample leads
curl -X POST http://localhost:8000/api/leads/bulk-import \
  -F "file=@../sample-data/sample_leads.csv"

# Process lead with ADK Prospecting Agent
curl -X POST http://localhost:8000/api/adk-agents/prospecting/process-lead/{lead_id}

# Send outreach with ADK Nurturing Agent
curl -X POST http://localhost:8000/api/adk-agents/nurturing/send-outreach/{lead_id}

# Get pipeline insights with ADK Intelligence Agent
curl http://localhost:8000/api/adk-agents/intelligence/pipeline-insights
```

---

## 📊 MongoDB Collections Schema

### leads
```javascript
{
  _id: ObjectId,
  company_name: String,
  email: String,
  contact_name: String,
  industry: String,
  company_size: String,
  website: String,
  phone: String,
  lead_score: Number,  // 0-100, calculated by Prospecting Agent
  status: String,      // 'new', 'qualified', 'contacted'
  enriched_data: {
    tech_stack: [String],
    employee_count: Number,
    annual_revenue: Number,
    // ... other enriched data
  },
  created_at: Date,
  updated_at: Date
}
```

### deals
```javascript
{
  _id: ObjectId,
  lead_id: String,     // Reference to leads collection
  deal_name: String,
  stage: String,       // 'new', 'contacted', 'qualified', 'proposal', etc.
  deal_value: Number,
  probability: Number, // 0-100, predicted by Intelligence Agent
  next_follow_up: Date,
  activities: [
    {
      type: String,    // 'email_sent', 'call', 'meeting'
      timestamp: Date,
      description: String,
      agent: String    // Which agent performed this
    }
  ],
  created_at: Date,
  updated_at: Date
}
```

### agent_actions
```javascript
{
  _id: ObjectId,
  agent_type: String,  // 'prospecting_agent', 'nurturing_agent', 'intelligence_agent'
  action: String,      // 'process_lead', 'send_outreach', 'predict_outcome'
  lead_id: String,
  deal_id: String,
  status: String,      // 'success', 'failed'
  started_at: Date,
  completed_at: Date,
  duration_seconds: Number,
  details: Object      // Action-specific data
}
```

---

## 🎯 Hackathon Demo Script

### Part 1: Architecture Overview (30 seconds)
"DealFlow AI uses Google ADK with three specialized agents—Prospecting, Nurturing, and Intelligence—all powered by Gemini 2.0. The agents interact with MongoDB exclusively through the MCP Server, demonstrating a production-ready, secure architecture."

### Part 2: Lead Processing (60 seconds)
1. Import sample CSV
2. Show MongoDB: raw leads appear
3. Call ADK Prospecting Agent API
4. Show Gemini reasoning in logs
5. Show MongoDB: leads now have scores and enrichment
6. Show agent_actions collection: audit trail

### Part 3: Automated Nurturing (45 seconds)
1. Call ADK Nurturing Agent
2. Show email generation by Gemini
3. Show MongoDB: deal created, activities logged
4. Show follow-up scheduling

### Part 4: Intelligence & Analytics (45 seconds)
1. Call Intelligence Agent for predictions
2. Show at-risk deals identified
3. Call pipeline insights API
4. Show comprehensive analytics JSON
5. Show MCP aggregate queries in action

---

## 🏅 Why This Wins

1. **✓ Full ADK Implementation**: Not just API calls—real agent architecture
2. **✓ Complete MCP Integration**: All data operations through MongoDB MCP
3. **✓ Multi-Agent Collaboration**: Three agents working together
4. **✓ Production-Ready**: Error handling, logging, audit trails
5. **✓ MongoDB Showcase**: Aggregations, updates, analytics via MCP
6. **✓ Real Automation**: Actual lead processing, email generation, predictions
7. **✓ Comprehensive Docs**: Architecture, setup, demo script
8. **✓ Extensible**: Easy to add more agents or tools

---

## 📚 References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [MongoDB MCP Server](https://github.com/mongodb-js/mongodb-mcp-server)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google Gemini API](https://ai.google.dev/)

---

## 🤝 Support

For questions about the architecture:
1. See SETUP.md for installation
2. See DEMO_SCRIPT.md for presentation guide
3. Check logs in `logs/` directory
4. Review agent actions in MongoDB `agent_actions` collection
