from src.data_processor import DataLoader
from src.predictor import ExpensePredictor

def main():
    # 1. Load Data
    loader = DataLoader('data/sample_template.csv')
    loader.load_data()
    df = loader.preprocess_data()
    
    # 2. Train Predictor
    predictor = ExpensePredictor()
    success = predictor.train(df)
    
    if success:
        # 3. Get Forecast
        forecast = predictor.predict_next_30_days()
        total_predicted = predictor.get_total_predicted_spend()
        
        print(f"\n🔮 Predicted Total Spending for next 30 days: ₹{total_predicted:,.2f}")
        
        print("\n--- Detailed Forecast (Next 5 Days) ---")
        # Show date and predicted amount (yhat)
        print(forecast[['ds', 'yhat']].head(5))
    else:
        print("Skipping prediction test due to insufficient data.")

if __name__ == "__main__":
    main()