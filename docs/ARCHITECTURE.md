# DealFlow AI - Architecture Documentation

## System Overview

DealFlow AI is a multi-agent B2B sales intelligence system that automates lead management, nurturing, and analytics using Google Gemini 3.1 Pro and MongoDB Atlas.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│                   React + Vite + Tailwind                    │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │  Leads   │  │  Deals   │  │Analytics │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                      Backend Layer                           │
│                   FastAPI + Python 3.11                      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Routes & Controllers                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                     │
│  ┌──────────────────────▼────────────────────────────────┐  │
│  │              Agent Orchestration Layer                 │  │
│  │                                                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │Prospecting  │  │  Nurturing  │  │Intelligence │  │  │
│  │  │   Agent     │  │    Agent    │  │   Agent     │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                     │
│  ┌──────────────────────▼────────────────────────────────┐  │
│  │                 Service Layer                          │  │
│  │                                                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │  │
│  │  │ MongoDB  │  │  Email   │  │   Enrichment     │   │  │
│  │  │ Service  │  │ Service  │  │    Service       │   │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │  │
│  └──────────────────────┬────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌─────▼──────┐ ┌───────▼────────┐
│  Google ADK    │ │  MongoDB   │ │  Gmail SMTP    │
│  + Gemini 3.1  │ │   Atlas    │ │                │
│                │ │            │ │                │
│ ┌────────────┐ │ │ ┌────────┐ │ │                │
│ │    MCP     │ │ │ │Vector  │ │ │                │
│ │   Server   │ │ │ │Search  │ │ │                │
│ └────────────┘ │ │ └────────┘ │ │                │
└────────────────┘ └────────────┘ └────────────────┘
```

## Component Details

### 1. Frontend Layer

**Technology**: React 18 + Vite + Tailwind CSS

**Components**:
- **Dashboard**: Overview of pipeline, metrics, and agent activity
- **Leads Management**: CRUD operations for leads, bulk import
- **Deals Management**: Pipeline view, deal details, activities
- **Analytics**: Charts, insights, predictions

**Key Features**:
- Real-time updates via WebSocket (future)
- Responsive design for mobile/tablet
- Dark mode support
- CSV import/export

### 2. Backend Layer

**Technology**: FastAPI + Python 3.11

**API Routes**:
```
/api/leads              - Lead CRUD operations
/api/deals              - Deal CRUD operations
/api/agents/*           - Agent action endpoints
/api/analytics/*        - Analytics endpoints
/health                 - Health check
```

**Middleware**:
- CORS for cross-origin requests
- Request logging
- Error handling
- Rate limiting (future)

### 3. Agent Layer

#### Prospecting Agent

**Responsibilities**:
- Enrich leads from public data sources
- Score leads based on multiple factors
- Identify high-value opportunities
- Generate embeddings for vector search

**Scoring Algorithm**:
```python
score = (
    contact_info_score +      # 0-40 points
    company_size_score +      # 0-30 points
    industry_score +          # 0-20 points
    tech_stack_score +        # 0-20 points
    social_presence_score     # 0-10 points
)
```

**MongoDB Operations**:
- `insert_one` - Create lead
- `update_one` - Update enriched data
- `find` - Query leads
- `aggregate` - Lead analytics

#### Nurturing Agent

**Responsibilities**:
- Send initial outreach emails
- Automated follow-ups
- Move deals through pipeline
- Schedule next actions

**Email Templates**:
- Initial outreach
- Follow-up
- Proposal
- Meeting request
- Check-in

**MongoDB Operations**:
- `find` - Get leads/deals
- `update_one` - Update deal stage
- `push` - Add activities
- `aggregate` - Find deals needing follow-up

#### Intelligence Agent

**Responsibilities**:
- Predict deal outcomes
- Identify at-risk deals
- Generate pipeline insights
- Calculate conversion rates

**Prediction Model**:
```python
probability = (
    stage_base_probability +
    activity_bonus +
    time_penalty +
    contact_penalty
)
```

**MongoDB Operations**:
- `aggregate` - Complex analytics
- `find` - Query deals
- `group` - Pipeline statistics
- `bucket` - Score distribution

### 4. Service Layer

#### MongoDB Service

**Features**:
- Connection pooling
- Automatic reconnection
- Index management
- Query optimization

**Collections**:

**leads**:
```javascript
{
  _id: ObjectId,
  company_name: String,
  website: String,
  industry: Enum,
  company_size: Enum,
  contact_person: String,
  email: String,
  phone: String,
  lead_score: Number (0-100),
  status: Enum,
  enriched_data: {
    tech_stack: [String],
    funding_stage: String,
    social_media: Object,
    keywords: [String]
  },
  embedding: [Float],  // Vector for semantic search
  created_at: Date,
  updated_at: Date
}
```

**deals** (Time-Series):
```javascript
{
  _id: ObjectId,
  lead_id: ObjectId,
  deal_name: String,
  deal_value: Number,
  stage: Enum,
  probability: Number (0-100),
  activities: [{
    type: Enum,
    timestamp: Date,
    description: String,
    outcome: String
  }],
  predicted_close_date: Date,
  risk_score: Number,
  created_at: Date,
  updated_at: Date
}
```

**agent_actions**:
```javascript
{
  _id: ObjectId,
  agent_type: Enum,
  action_type: Enum,
  lead_id: ObjectId,
  deal_id: ObjectId,
  input_data: Object,
  output_data: Object,
  reasoning: String,
  status: Enum,
  started_at: Date,
  completed_at: Date,
  duration_seconds: Number
}
```

**Indexes**:
- `leads.company_name` - Text search
- `leads.lead_score` - Sorting
- `leads.embedding` - Vector search
- `deals.stage` - Pipeline queries
- `deals.expected_close_date` - Follow-up queries
- `agent_actions.agent_type` - Performance metrics

#### Email Service

**Features**:
- Gmail SMTP integration
- Rate limiting (500/day)
- Template generation
- Personalization
- HTML email support

**Rate Limiting**:
- Daily counter reset at midnight
- Graceful degradation when limit reached
- Queue system (future)

#### Enrichment Service

**Data Sources**:
- Company website scraping
- Meta tag extraction
- Tech stack detection
- Social media links

**Tech Stack Detection**:
- HTML content analysis
- HTTP headers inspection
- JavaScript framework detection
- Server identification

### 5. External Services

#### Google Cloud ADK + Gemini

**Integration**:
```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset

agent = Agent(
    model="gemini-1.5-pro",
    name="sales_agent",
    instruction="Help manage B2B sales pipeline",
    tools=[McpToolset(...)]
)
```

**Use Cases**:
- Natural language query processing
- Email content generation
- Reasoning about deal outcomes
- Insight generation

#### MongoDB MCP Server

**Configuration**:
```python
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "mongodb-mcp-server"],
            env={
                "MDB_MCP_CONNECTION_STRING": CONNECTION_STRING
            }
        )
    )
)
```

**Available Tools**:
- `find` - Query documents
- `aggregate` - Run aggregation pipelines
- `insert-many` - Bulk insert
- `update-many` - Bulk update
- `collection-schema` - Inspect schema
- `db-stats` - Database statistics

#### Gmail SMTP

**Configuration**:
```python
aiosmtplib.send(
    message,
    hostname="smtp.gmail.com",
    port=587,
    username=SMTP_USERNAME,
    password=SMTP_APP_PASSWORD,
    start_tls=True
)
```

## Data Flow

### Lead Processing Flow

```
1. User uploads CSV
   ↓
2. Backend creates leads in MongoDB
   ↓
3. Prospecting Agent triggered
   ↓
4. Enrichment Service scrapes website
   ↓
5. Lead scored and updated in MongoDB
   ↓
6. High-score leads flagged
   ↓
7. Frontend updates in real-time
```

### Email Outreach Flow

```
1. User clicks "Send Outreach"
   ↓
2. Nurturing Agent retrieves lead data
   ↓
3. Gemini generates personalized email
   ↓
4. Email Service sends via Gmail SMTP
   ↓
5. Activity logged in MongoDB
   ↓
6. Lead status updated to "contacted"
   ↓
7. Next follow-up scheduled
```

### Deal Prediction Flow

```
1. Intelligence Agent triggered
   ↓
2. MongoDB aggregation retrieves deal history
   ↓
3. Gemini analyzes patterns
   ↓
4. Prediction calculated
   ↓
5. Deal updated with prediction
   ↓
6. Agent action logged
   ↓
7. Dashboard displays prediction
```

## Scalability Considerations

### Current Architecture (MVP)
- Single backend instance
- MongoDB Atlas M0 (Free Tier)
- Synchronous agent execution
- In-memory rate limiting

### Production Architecture (Future)
- Multiple backend instances with load balancer
- MongoDB Atlas M10+ with sharding
- Async agent execution with Celery
- Redis for caching and rate limiting
- WebSocket for real-time updates
- CDN for frontend assets

## Security

### Current Implementation
- Environment variables for secrets
- CORS restrictions
- Input validation with Pydantic
- MongoDB connection encryption

### Future Enhancements
- JWT authentication
- Role-based access control (RBAC)
- API key management
- Audit logging
- Data encryption at rest

## Monitoring & Logging

### Current
- Python logging to console
- Agent action logging in MongoDB
- Error tracking

### Future
- Google Cloud Logging
- Prometheus metrics
- Grafana dashboards
- Alert system for failures

## Performance Optimization

### MongoDB
- Indexes on frequently queried fields
- Aggregation pipeline optimization
- Connection pooling
- Query result caching (future)

### Backend
- Async/await for I/O operations
- Background tasks for long-running operations
- Response compression
- Database query batching

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- Service worker caching (future)

## Testing Strategy

### Unit Tests
- Service layer functions
- Agent logic
- Utility functions

### Integration Tests
- API endpoints
- MongoDB operations
- Email sending

### End-to-End Tests
- User workflows
- Agent orchestration
- Data consistency

## Deployment

### Development
```bash
# Backend
cd backend
python main.py

# Frontend
cd frontend
npm run dev
```

### Production (Google Cloud Run)
```bash
# Backend
gcloud run deploy dealflow-backend --source .

# Frontend
gcloud run deploy dealflow-frontend --source .
```

### Environment Variables
- Development: `.env` file
- Production: Google Cloud Secret Manager

## Future Enhancements

### Phase 2
- [ ] WebSocket for real-time updates
- [ ] Advanced vector search with filters
- [ ] Multi-language support
- [ ] Mobile app (React Native)

### Phase 3
- [ ] Integration with CRMs (Salesforce, HubSpot)
- [ ] Calendar integration (Google Calendar)
- [ ] Video call scheduling (Google Meet)
- [ ] Advanced analytics with ML models

### Phase 4
- [ ] Multi-tenant support
- [ ] White-label solution
- [ ] API marketplace
- [ ] Enterprise features (SSO, SAML)

## License

MIT License - See LICENSE file for details
