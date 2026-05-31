# DealFlow AI - Setup Guide

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- MongoDB Atlas account (free tier)
- Google Cloud account with credits
- Gmail account for SMTP

## Step 1: MongoDB Atlas Setup

1. **Create a MongoDB Atlas account**
   - Go to https://cloud.mongodb.com
   - Sign up for a free account
   - Create a new cluster (M0 Free Tier)

2. **Configure database access**
   - Go to Database Access
   - Add a new database user
   - Save username and password

3. **Configure network access**
   - Go to Network Access
   - Add IP Address: `0.0.0.0/0` (allow from anywhere)
   - Or add your specific IP

4. **Get connection string**
   - Go to Database → Connect
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database password

## Step 2: Google Cloud Setup

1. **Create a Google Cloud project**
   - Go to https://console.cloud.google.com
   - Create a new project
   - Enable billing (use free credits)

2. **Enable Gemini API**
   - Go to APIs & Services
   - Enable "Generative Language API"
   - Create API credentials
   - Copy the API key

3. **Create service account (optional)**
   - Go to IAM & Admin → Service Accounts
   - Create a new service account
   - Download the JSON key file

## Step 3: Gmail SMTP Setup

1. **Enable 2-Factor Authentication**
   - Go to Google Account settings
   - Security → 2-Step Verification
   - Enable it

2. **Create App Password**
   - Go to Security → App passwords
   - Select "Mail" and "Other"
   - Generate password
   - Copy the 16-character password

## Step 4: Backend Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd dealflow-ai
```

2. **Create virtual environment**
```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp ../.env.example .env
```

Edit `.env` file with your credentials:
```env
# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/dealflow_db?retryWrites=true&w=majority
MONGODB_DATABASE=dealflow_db

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GEMINI_API_KEY=your-gemini-api-key

# Gmail SMTP
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Security
SECRET_KEY=generate-a-random-secret-key-here
```

5. **Run the backend**
```bash
python main.py
```

Backend will be available at: http://localhost:8000

## Step 5: Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
VITE_API_URL=http://localhost:8000
```

4. **Run the frontend**
```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

## Step 6: Test the Application

1. **Import sample leads**
   - Go to http://localhost:5173
   - Click "Import Leads"
   - Upload `sample-data/sample_leads.csv`

2. **Process leads**
   - Leads will be automatically enriched
   - Check the dashboard for lead scores

3. **Test agents**
   - Click on a high-score lead
   - Click "Send Outreach"
   - Check your email logs

## Step 7: Deploy to Google Cloud Run

1. **Install Google Cloud SDK**
```bash
# Follow instructions at:
# https://cloud.google.com/sdk/docs/install
```

2. **Authenticate**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Build and deploy backend**
```bash
cd backend
gcloud run deploy dealflow-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

4. **Build and deploy frontend**
```bash
cd ../frontend
npm run build
gcloud run deploy dealflow-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Troubleshooting

### MongoDB Connection Issues
- Check if IP is whitelisted
- Verify username/password
- Ensure connection string format is correct

### Gemini API Issues
- Verify API key is correct
- Check if API is enabled in Google Cloud Console
- Ensure billing is enabled

### Email Sending Issues
- Verify app password (not regular password)
- Check if 2FA is enabled
- Ensure SMTP settings are correct

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system
- Read [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) for demo preparation
- Customize email templates in `backend/services/email_service.py`
- Add more enrichment sources in `backend/services/enrichment_service.py`

## Support

For issues or questions:
- Check the GitHub Issues
- Review the documentation
- Contact the team

## License

MIT License - See LICENSE file for details
