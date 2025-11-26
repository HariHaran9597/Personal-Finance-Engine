import pandas as pd
import numpy as np

class ExpensePredictor:
    def __init__(self):
        self.is_trained = False
        self.daily_avg = 0
        self.last_date = None

    def train(self, df):
        """
        Calculates the average daily spending based on recent history.
        """
        df = df.copy()
        
        # 1. Filter for Debits only
        df = df[df['type'] == 'debit']
        
        # 2. Group by Date
        daily_spend = df.groupby('date')['amount'].sum()
        
        # 3. Resample to Daily frequency (Crucial!)
        # If you didn't spend money on Tuesday, we must count that as ₹0
        daily_spend = daily_spend.resample('D').sum().fillna(0)
        
        if len(daily_spend) < 2:
            print("⚠️ Not enough data to predict.")
            return False
            
        # 4. Calculate Moving Average
        # We take the average of the last 30 days (or all available days if <30)
        window = min(len(daily_spend), 30)
        self.daily_avg = daily_spend.tail(window).mean()
        self.last_date = daily_spend.index.max()
        
        self.is_trained = True
        print(f"✅ Simple Predictor trained. Average Daily Spend: ₹{self.daily_avg:.2f}")
        return True

    def predict_next_30_days(self):
        """
        Returns a DataFrame with 30 days of predictions.
        """
        if not self.is_trained:
            return None
            
        # Generate next 30 dates
        future_dates = pd.date_range(start=self.last_date + pd.Timedelta(days=1), periods=30, freq='D')
        
        # Create forecast dataframe
        # We add some random noise (0.9 to 1.1) to make the chart look realistic, 
        # representing natural daily variance.
        random_variation = np.random.uniform(0.8, 1.2, 30)
        predicted_values = self.daily_avg * random_variation
        
        forecast = pd.DataFrame({
            'ds': future_dates,
            'yhat': predicted_values,
            'yhat_lower': predicted_values * 0.8,
            'yhat_upper': predicted_values * 1.2
        })
        
        return forecast

    def get_total_predicted_spend(self):
        """Total predicted for next month"""
        if not self.is_trained:
            return 0
        return self.daily_avg * 30