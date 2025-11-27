import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Try to import SARIMA, fallback to simple method if not available
try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tools.sm_exceptions import ConvergenceWarning
    SARIMA_AVAILABLE = True
except ImportError:
    SARIMA_AVAILABLE = False

class ExpensePredictor:
    """
    Time Series Expense Predictor using SARIMA (Seasonal AutoRegressive Integrated Moving Average)
    
    SARIMA Model Components:
    - AR (AutoRegressive): Uses past values to predict future
    - I (Integrated): Differencing to make data stationary
    - MA (Moving Average): Uses past forecast errors
    - Seasonal: Captures weekly/monthly patterns in spending
    
    Model: SARIMA(1,1,1)(1,1,1,7)
    - (1,1,1): Non-seasonal (p,d,q) - captures short-term trends
    - (1,1,1,7): Seasonal (P,D,Q,s) - captures weekly patterns (s=7 days)
    """
    
    def __init__(self):
        self.is_trained = False
        self.model = None
        self.fitted_model = None
        self.daily_spend_series = None
        self.last_date = None
        self.use_sarima = SARIMA_AVAILABLE
        self.daily_avg = 0  # Fallback for simple method

    def train(self, df):
        """
        Train SARIMA model on historical spending data.
        Falls back to moving average if insufficient data or SARIMA unavailable.
        """
        df = df.copy()
        
        # 1. Filter for Debits only (expenses)
        df = df[df['type'] == 'debit']
        
        if len(df) < 14:
            print("⚠️ Not enough data to train predictor (need at least 14 days).")
            return False
        
        # 2. Group by Date and resample to daily frequency
        daily_spend = df.groupby('date')['amount'].sum()
        daily_spend = daily_spend.resample('D').sum().fillna(0)
        
        self.daily_spend_series = daily_spend
        self.last_date = daily_spend.index.max()
        
        # 3. Try SARIMA if available and enough data
        if self.use_sarima and len(daily_spend) >= 21:
            try:
                print("🤖 Training SARIMA model for time series forecasting...")
                
                # SARIMA Parameters:
                # order=(1,1,1): AR=1, differencing=1, MA=1
                # seasonal_order=(1,1,1,7): Seasonal AR=1, D=1, MA=1, period=7 (weekly)
                # This captures both daily trends and weekly spending patterns
                
                self.model = SARIMAX(
                    daily_spend,
                    order=(1, 1, 1),  # (p, d, q) - non-seasonal parameters
                    seasonal_order=(1, 1, 1, 7),  # (P, D, Q, s) - seasonal parameters
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
                
                # Fit the model
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=ConvergenceWarning)
                    self.fitted_model = self.model.fit(disp=False, maxiter=100)
                
                self.is_trained = True
                print(f"✅ SARIMA model trained successfully!")
                print(f"   Model: SARIMA(1,1,1)(1,1,1,7)")
                print(f"   Training data: {len(daily_spend)} days")
                print(f"   AIC Score: {self.fitted_model.aic:.2f}")
                return True
                
            except Exception as e:
                print(f"⚠️ SARIMA training failed: {str(e)}")
                print("   Falling back to moving average method...")
                self.use_sarima = False
        
        # 4. Fallback: Simple Moving Average
        if not self.use_sarima or len(daily_spend) < 21:
            window = min(len(daily_spend), 30)
            self.daily_avg = daily_spend.tail(window).mean()
            self.is_trained = True
            print(f"✅ Moving Average predictor trained.")
            print(f"   Average Daily Spend: ₹{self.daily_avg:.2f}")
            return True

    def predict_next_30_days(self):
        """
        Forecast next 30 days of spending using SARIMA or moving average.
        
        Returns:
            DataFrame with columns: ds (date), yhat (prediction), yhat_lower, yhat_upper
        """
        if not self.is_trained:
            return None
        
        # Generate future dates
        future_dates = pd.date_range(
            start=self.last_date + pd.Timedelta(days=1), 
            periods=30, 
            freq='D'
        )
        
        # SARIMA Prediction
        if self.use_sarima and self.fitted_model is not None:
            try:
                # Get forecast with confidence intervals
                forecast_result = self.fitted_model.get_forecast(steps=30)
                forecast_mean = forecast_result.predicted_mean
                forecast_ci = forecast_result.conf_int(alpha=0.2)  # 80% confidence interval
                
                # Ensure non-negative predictions (can't have negative spending)
                forecast_mean = np.maximum(forecast_mean, 0)
                forecast_lower = np.maximum(forecast_ci.iloc[:, 0].values, 0)
                forecast_upper = np.maximum(forecast_ci.iloc[:, 1].values, 0)
                
                forecast_df = pd.DataFrame({
                    'ds': future_dates,
                    'yhat': forecast_mean.values,
                    'yhat_lower': forecast_lower,
                    'yhat_upper': forecast_upper
                })
                
                return forecast_df
                
            except Exception as e:
                print(f"⚠️ SARIMA prediction failed: {str(e)}")
                print("   Using moving average fallback...")
        
        # Fallback: Moving Average with variance
        random_variation = np.random.uniform(0.85, 1.15, 30)
        predicted_values = self.daily_avg * random_variation
        
        forecast_df = pd.DataFrame({
            'ds': future_dates,
            'yhat': predicted_values,
            'yhat_lower': predicted_values * 0.8,
            'yhat_upper': predicted_values * 1.2
        })
        
        return forecast_df

    def get_total_predicted_spend(self):
        """
        Calculate total predicted spending for next 30 days.
        
        Returns:
            float: Total predicted amount
        """
        if not self.is_trained:
            return 0
        
        forecast = self.predict_next_30_days()
        if forecast is not None:
            return forecast['yhat'].sum()
        
        return self.daily_avg * 30
    
    def get_model_info(self):
        """
        Get information about the trained model for display.
        
        Returns:
            dict: Model information
        """
        if not self.is_trained:
            return {'model_type': 'Not Trained', 'details': 'No model trained yet'}
        
        if self.use_sarima and self.fitted_model is not None:
            return {
                'model_type': 'SARIMA',
                'order': '(1,1,1)',
                'seasonal_order': '(1,1,1,7)',
                'aic': f"{self.fitted_model.aic:.2f}",
                'bic': f"{self.fitted_model.bic:.2f}",
                'training_samples': len(self.daily_spend_series),
                'description': 'Seasonal AutoRegressive Integrated Moving Average'
            }
        else:
            return {
                'model_type': 'Moving Average',
                'window': '30 days',
                'avg_daily': f"₹{self.daily_avg:.2f}",
                'training_samples': len(self.daily_spend_series) if self.daily_spend_series is not None else 0,
                'description': 'Simple moving average with variance modeling'
            }