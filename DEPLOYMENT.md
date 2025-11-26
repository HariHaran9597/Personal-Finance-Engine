# 🚀 Deployment Guide - Personal Finance Insight Engine

This guide covers deploying the Personal Finance Insight Engine to various platforms.

---

## 📋 Pre-Deployment Checklist

- [ ] All tests passing (`python test_*.py`)
- [ ] Model trained and saved (`models/categorizer.pkl`)
- [ ] Requirements.txt up to date
- [ ] README.md documented
- [ ] .gitignore configured
- [ ] Environment variables configured (if any)

---

## 🌐 Deploy to Streamlit Cloud (Recommended)

### Step 1: Prepare Your Repository

```bash
# Make sure everything is committed
git add .
git commit -m "Add complete finance engine with ML models"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Choose branch: `main`
5. Set main file path: `app.py`
6. Click "Deploy"

### Step 3: Monitor Deployment

- Deployment typically takes 2-5 minutes
- View logs in real-time
- Once deployed, you'll get a public URL
- Share with friends: `https://[your-app].streamlit.app`

### Configuration for Cloud

The `.streamlit/config.toml` is already configured for cloud deployment:

```toml
[server]
headless = true  # Runs without UI elements
maxUploadSize = 200  # 200 MB file upload limit
```

---

## 🐳 Deploy with Docker

### Step 1: Build Docker Image

```bash
docker build -t finance-engine:latest .
```

### Step 2: Run Locally

```bash
docker run -p 8501:8501 finance-engine:latest
```

Visit `http://localhost:8501` in your browser.

### Step 3: Deploy to Container Registry

**Docker Hub:**
```bash
docker tag finance-engine:latest yourusername/finance-engine:latest
docker push yourusername/finance-engine:latest
```

**Azure Container Registry:**
```bash
az acr build --registry myacr --image finance-engine:latest .
```

### Dockerfile Content

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py"]
```

---

## ☁️ Deploy to Heroku

### Step 1: Create Heroku App

```bash
heroku login
heroku create your-finance-app
```

### Step 2: Create Procfile

```
web: sh setup.sh && streamlit run app.py
```

### Step 3: Create setup.sh

```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = \$PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

### Step 4: Deploy

```bash
git push heroku main
```

---

## AWS Deployment

### Option 1: AWS App Runner (Easiest)

1. Push code to GitHub/CodeCommit
2. Go to AWS App Runner
3. Select repository and branch
4. Choose Python runtime
5. Deploy

### Option 2: EC2 Instance

```bash
# SSH into EC2 instance
ssh -i key.pem ec2-user@your-instance.amazonaws.com

# Clone repository
git clone https://github.com/yourusername/finance-engine.git
cd finance-engine

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Streamlit
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

---

## Azure Deployment

### Option 1: Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name finance-app \
  --image myregistry.azurecr.io/finance-engine:latest \
  --ports 8501 \
  --environment-variables PORT=8501
```

### Option 2: Azure App Service

```bash
az webapp up \
  --name finance-app \
  --resource-group myResourceGroup \
  --runtime PYTHON:3.9
```

---

## Google Cloud Deployment

### Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/finance-engine

# Deploy
gcloud run deploy finance-app \
  --image gcr.io/PROJECT_ID/finance-engine \
  --platform managed \
  --region us-central1 \
  --port 8501
```

---

## 🔐 Production Best Practices

### 1. Environment Variables

Create `.env` file (not committed):
```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_CLIENT_TOOLBAR_MODE=minimal
```

Load in `app.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
```

### 2. API Rate Limiting

Add to `.streamlit/config.toml`:
```toml
[client]
showErrorDetails = false  # Hide details from users
toolbarMode = "minimal"   # Minimal toolbar
```

### 3. SSL/HTTPS

All platforms above support HTTPS by default. Use:
```
https://your-app.streamlit.app
```

### 4. Monitoring & Logging

```python
# Add to app.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("App loaded successfully")
```

### 5. Backup & Recovery

```bash
# Backup important files
git push origin main  # Always backup to git
```

---

## 📊 Performance Tips

### 1. Cache Data

```python
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')
```

### 2. Cache Models

```python
@st.cache_resource
def load_model():
    model = TransactionCategorizer()
    model.load()
    return model
```

### 3. Optimize File Size

- Keep CSV uploads under 100 MB
- Compress processed data
- Store models efficiently

---

## 🧪 Testing Before Deployment

```bash
# Run all tests
python test_setup.py
python test_anomaly.py
python test_prediction.py

# Test Streamlit locally
streamlit run app.py

# Check for errors
streamlit run app.py --logger.level=debug
```

---

## ✅ Post-Deployment

### 1. Verify App Works

- [ ] Upload sample CSV
- [ ] Check categorization
- [ ] Verify anomaly detection
- [ ] Test predictions
- [ ] Download reports
- [ ] Mobile responsiveness

### 2. Share with Users

```
Share this link with friends/family:
https://your-app.streamlit.app
```

### 3. Monitor Performance

- Check app logs regularly
- Monitor response times
- Track user feedback
- Fix bugs quickly

### 4. Update & Maintain

```bash
# Pull latest changes
git pull origin main

# Redeploy
git push origin main  # For Streamlit Cloud, this auto-deploys
```

---

## 🐛 Troubleshooting

### App Won't Start

```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip list

# Run tests
python test_setup.py
```

### Model Loading Error

```bash
# Retrain model
python train_model.py

# Check model path
python -c "import os; print(os.path.exists('models/categorizer.pkl'))"
```

### File Upload Issues

- Check file format (must be CSV with columns: date, description, amount, type)
- Check file size (max 200 MB)
- Verify date format (YYYY-MM-DD)

### Memory Issues

- Reduce contamination rate in `src/anomaly_detector.py`
- Limit prediction window in `src/predictor.py`
- Process smaller batches

---

## 📞 Support

- **Issue?** Check logs: `streamlit run app.py --logger.level=debug`
- **Questions?** Review README.md
- **Bug Report?** Create GitHub issue

---

## 🎯 Next Steps

1. Deploy to Streamlit Cloud
2. Share with friends for feedback
3. Monitor usage and improve
4. Add more features based on feedback
5. Consider mobile app version

---

**Version:** 1.0.0
**Last Updated:** November 2024
