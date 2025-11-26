# 🚀 Quick Start Guide

Get started with the Personal Finance Insight Engine in just 5 minutes!

---

## ⚡ 5-Minute Setup

### 1. Install Dependencies (2 min)

```bash
cd finance-engine
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the App (1 min)

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

### 3. Try Demo (2 min)

1. Check the "Use Demo Data" checkbox
2. View transaction analysis
3. Explore all 7 tabs:
   - 📈 Overview
   - 🏷️ Categories
   - 🚨 Anomalies
   - 🔮 Prediction
   - 💡 Insights
   - 📊 Model Metrics
   - 📥 Export

---

## 📊 Use Your Own Data

### Create CSV File

Create `bank_statement.csv`:

```csv
date,description,amount,type
2024-11-01,Salary,50000,credit
2024-11-02,Starbucks,450,debit
2024-11-02,Amazon Purchase,1500,debit
2024-11-03,Electricity Bill,1200,debit
2024-11-04,Uber Ride,250,debit
```

**Required Columns:**
- `date` - Format: YYYY-MM-DD
- `description` - Transaction description
- `amount` - Transaction amount (positive number)
- `type` - "credit" or "debit"

### Upload & Analyze

1. Open the app: `streamlit run app.py`
2. Click "Browse files" → Select your CSV
3. Wait for analysis (usually < 30 seconds)
4. Explore all tabs and insights!

---

## 🎯 What You Can Do

### 📈 View Spending Trends
- Daily, weekly, monthly patterns
- Income vs Expenses
- Net savings tracking

### 🏷️ Auto-Categorize Transactions
- 9 categories (Food, Transport, Shopping, etc.)
- 85%+ accuracy
- Manual review available

### 🚨 Detect Anomalies
- Unusual transactions highlighted
- Fraud detection
- Spending pattern violations

### 🔮 Predict Future Spending
- 30-day expense forecast
- Budget planning
- Confidence intervals

### 💡 Get Smart Insights
- Spending recommendations
- Savings opportunities
- Pattern analysis

### 📊 Monitor Model Performance
- Accuracy metrics
- Model details
- Data quality scores

### 📥 Export Reports
- CSV downloads
- Category summaries
- Anomaly reports
- Forecast data

---

## 🧪 Run Tests

```bash
# Test data processing
python test_setup.py

# Test anomaly detection
python test_anomaly.py

# Test predictions
python test_prediction.py
```

---

## 🔧 Train Your Own Model

```bash
python train_model.py
```

This:
1. Loads sample data
2. Trains categorizer model
3. Tests predictions
4. Saves model to `models/categorizer.pkl`

---

## ⚙️ Configuration

### Adjust Settings

Edit `src/config.py`:

```python
# Categories
CATEGORIES = [
    'Food & Dining',
    'Transportation',
    'Shopping',
    # Add more...
]

# Data paths
DATA_DIR = 'data/'
MODELS_DIR = 'models/'
```

### Add Custom Keywords

Edit `src/categorizer.py`:

```python
self.keyword_map = {
    'My Restaurant': ['restaurant_name', 'place_name'],
    # Add more patterns
}
```

---

## 🐛 Troubleshooting

### "Import Error: No module named 'streamlit'"

```bash
pip install -r requirements.txt
```

### "CSV file has incorrect format"

Check columns:
- `date` (YYYY-MM-DD)
- `description` (text)
- `amount` (number)
- `type` (credit/debit)

### "Model not found"

```bash
python train_model.py
```

### App runs slowly

- Reduce file size (limit to 5000 rows)
- Clear cache: `streamlit cache clear`
- Close other applications

---

## 📚 Next Steps

1. **Analyze Your Data** - Upload your full bank statement
2. **Review Anomalies** - Check detected unusual transactions
3. **Plan Budget** - Use predictions for next month
4. **Share Insights** - Export reports and share
5. **Deploy Online** - Share app with family/friends
   - See `DEPLOYMENT.md` for cloud hosting

---

## 🎓 Learn More

- **README.md** - Full documentation
- **DEPLOYMENT.md** - Deploy to cloud
- **src/config.py** - Customization options
- **Test files** - See examples in `test_*.py`

---

## 💬 Tips

### For Best Results

✅ Upload 3-6 months of data
✅ Keep merchant descriptions consistent
✅ Ensure dates are in YYYY-MM-DD format
✅ Use "credit" and "debit" consistently

### Customize Categories

Add to `keyword_map` in `src/categorizer.py`:
```python
'Your Bank': ['bankname', 'atm'],
'Your Shop': ['shopname', 'storename'],
```

### Improve Predictions

- More data = better predictions
- 30+ days recommended
- Include seasonal variations
- Consistent transaction history

---

## ❓ FAQ

**Q: Can I use credit card statements?**
A: Yes! Any CSV with the required columns works.

**Q: Is my data safe?**
A: Data processed locally, not sent anywhere.

**Q: Can I export results?**
A: Yes! Use the Export tab to download CSV files.

**Q: How accurate is categorization?**
A: 85%+ on typical transactions. Improves with more data.

**Q: Can I deploy this online?**
A: Yes! See DEPLOYMENT.md for Streamlit Cloud, Docker, etc.

---

## 🎉 You're Ready!

```bash
streamlit run app.py
```

Enjoy analyzing your finances! 💰

---

**Version:** 1.0.0
**Last Updated:** November 2024
