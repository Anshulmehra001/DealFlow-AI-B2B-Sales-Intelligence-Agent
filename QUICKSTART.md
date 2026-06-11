# 🚀 DealFlow AI - Quick Start Guide

## Prerequisites

1. **Python 3.11+** installed
2. **Gemini API Key** - Get free at https://aistudio.google.com/apikey
3. **MongoDB Atlas** (Optional - app works without it)

---

## 📦 Installation (5 Minutes)

### Step 1: Activate Virtual Environment & Install Dependencies

```powershell
cd backend

# Activate venv (already exists)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Motor (async MongoDB driver)
- Google GenAI (Gemini SDK)
- Uvicorn (server)
- Pydantic (data validation)

### Step 2: Configure Environment

Your `.env` file should have:

```env
# Gemini AI (REQUIRED)
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.5-flash

# MongoDB (OPTIONAL - app works without it)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=dealflow_db

# Application
BACKEND_PORT=8000
ENVIRONMENT=production
```

**IMPORTANT**: Gemini API key is REQUIRED. MongoDB is optional.

---

## ▶️ Running the Application

### Option 1: Simple Version (No MongoDB Required)

```powershell
cd backend
.\venv\Scripts\activate
python simple_main.py
```

- ✅ Works without MongoDB
- ✅ All 3 AI agents functional
- ✅ Uses in-memory storage
- ✅ Perfect for demos

### Option 2: Production Version (MongoDB Required)

```powershell
cd backend
.\venv\Scripts\activate
python main_production.py
```

- ✅ Full MongoDB integration
- ✅ Real Gemini AI responses
- ✅ Persistent data storage
- ⚠️ Requires MongoDB connection

---

## 🧪 Testing the Application

### 1. Check Health

Open browser: http://localhost:8000/health

Should show:
```json
{
  "status": "healthy",
  "gemini_ai": "configured",
  "mongodb": "connected",
  "adk_agents": "enabled"
}
```

### 2. Open API Docs

Open browser: http://localhost:8000/docs

Interactive Swagger UI with all endpoints.

### 3. Run Test Script

```powershell
.\demo.ps1
```

Tests all 5 endpoints:
1. Health check ✅
2. Create lead ✅
3. Prospecting Agent ✅
4. Nurturing Agent ✅
5. Intelligence Agent ✅

---

## 🎥 Recording Demo Video

### What You Need:

1. **8 PNG Graphics** - Generate from `index.html`
2. **15-second screen recording** - Follow VIDEO_SCRIPT.md

### Generate Graphics:

1. Open `index.html` in browser
2. Click "Download All Graphics as ZIP"
3. Extract files, rename to:
   - `1_title_card.png`
   - `2_problem.png`
   - `3_solution.png`
   - `4_how_it_works.png`
   - `5_time_savings.png`
   - `6_global_impact.png`
   - `7_dashboard.png`
   - `8_success_metrics.png`

### Record 15-Second Demo:

**URL**: http://localhost:8000/docs

**Timeline**:
- [0-3s] Show API homepage with all endpoints
- [3-6s] POST /api/leads → Execute → Show lead_id
- [6-9s] POST /prospecting/process-lead/{id} → Show score=75
- [9-12s] POST /nurturing/send-outreach/{id} → Show email
- [12-15s] GET /intelligence/pipeline-insights → Show report

**Practice 2-3 times before final recording!**

### Edit Video:

1. Import 8 PNGs + 15s recording
2. Arrange per VIDEO_SCRIPT.md timeline
3. Add voiceover/text overlays
4. Export as MP4, 1080p, 30fps
5. Total length: ~3 minutes

---

## 🔧 Troubleshooting

### MongoDB Not Working?

**No problem!** Use `simple_main.py` - works perfectly without MongoDB.

### Gemini API Error?

Check your API key:
1. Go to https://aistudio.google.com/apikey
2. Copy the key
3. Update `.env` file: `GEMINI_API_KEY=your_key_here`
4. Restart server

### Port 8000 Already in Use?

Change port in `.env`:
```env
BACKEND_PORT=8001
```

Then restart.

---

## 📁 Project Structure

```
backend/
├── simple_main.py          ⭐ Use this (no MongoDB needed)
├── main_production.py      💎 Full version (MongoDB required)
├── config.py               ⚙️ Configuration
├── requirements.txt        📦 Dependencies
├── adk_agents/             🤖 3 AI Agents
├── models/                 📊 Data models
└── services/               🛠️ Services

Root/
├── demo.ps1                🧪 Test script
├── VIDEO_SCRIPT.md         🎬 Video guide
├── QUICKSTART.md           📖 This file
├── README.md               📘 Full documentation
└── index.html              🎨 Graphics generator
```

---

## ✅ Pre-Submission Checklist

- [ ] Application runs successfully
- [ ] All 5 tests pass (run `demo.ps1`)
- [ ] 8 PNG graphics generated
- [ ] 15-second demo recorded
- [ ] Video edited and exported (3 minutes total)
- [ ] README.md is complete
- [ ] GitHub repo is clean
- [ ] .env file NOT committed (in .gitignore)
- [ ] Video uploaded to YouTube
- [ ] Hackathon submission form filled

---

## 🆘 Need Help?

1. **Check logs** - Server prints errors to terminal
2. **Test health endpoint** - http://localhost:8000/health
3. **Use simple_main.py** - Works without MongoDB
4. **Check .env file** - Gemini API key is required

---

## 🎯 Summary

**REQUIRED**:
- ✅ Gemini API key
- ✅ Python 3.11+
- ✅ Virtual environment (venv already exists)
- ✅ Dependencies installed

**OPTIONAL**:
- MongoDB Atlas (app works without it)

**TO RUN**:
```powershell
cd backend
.\venv\Scripts\activate
python simple_main.py
```

**TO TEST**:
```powershell
.\demo.ps1
```

**TO DEMO**:
Open http://localhost:8000/docs

---

**You're ready to go! 🚀**
