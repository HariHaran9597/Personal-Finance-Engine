"""
Test SARIMA implementation
"""
import pandas as pd
from src.predictor import ExpensePredictor

# Create sample data
dates = pd.date_range('2024-01-01', periods=60, freq='D')
amounts = [500, 600, 450, 700, 800, 550, 400] * 8 + [500, 600, 450, 700]  # 60 days
data = pd.DataFrame({
    'date': dates,
    'description': ['Test'] * 60,
    'amount': amounts,
    'type': ['debit'] * 60
})

# Test predictor
print("Testing SARIMA Expense Predictor...")
print("=" * 50)

predictor = ExpensePredictor()
predictor.train(data)

print("\nGenerating 30-day forecast...")
forecast = predictor.predict_next_30_days()

if forecast is not None:
    print(f"\n✅ Forecast generated successfully!")
    print(f"Total predicted spend: ₹{predictor.get_total_predicted_spend():,.2f}")
    print(f"\nFirst 5 days of forecast:")
    print(forecast.head())
    
    # Get model info
    model_info = predictor.get_model_info()
    print(f"\nModel Information:")
    for key, value in model_info.items():
        print(f"  {key}: {value}")
else:
    print("❌ Forecast generation failed")
