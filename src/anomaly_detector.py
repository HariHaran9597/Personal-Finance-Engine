import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score

class AnomalyDetector:
    def __init__(self):
        # contamination='auto' lets the model decide how many anomalies to expect
        # random_state ensures consistent results
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.num_anomalies = 0
        self.sensitivity = 0.0
        self.specificity = 0.0

    def prepare_features(self, df):
        """
        Convert transaction data into numbers the model can understand.
        Key features: Amount, Day of Week, Category (encoded).
        """
        features = pd.DataFrame()
        
        # 1. Amount (The biggest signal)
        features['amount'] = df['amount']
        
        # 2. Day of Week (0=Monday, 6=Sunday)
        # Helps detect spending on unusual days
        features['day_of_week'] = df['date'].dt.dayofweek
        
        # 3. Is Credit? (1 for Income, 0 for Expense)
        features['is_credit'] = (df['type'] == 'credit').astype(int)
        
        # Note: We scale the data because 'Amount' (e.g., 50000) is much bigger 
        # than 'Day' (0-6), which confuses the model.
        return self.scaler.fit_transform(features)

    def train(self, df):
        """Train the model on your history"""
        print("Training Anomaly Detector...")
        X = self.prepare_features(df)
        self.model.fit(X)
        
        # Get predictions to calculate metrics
        predictions = self.model.predict(X)
        self.num_anomalies = (predictions == -1).sum()
        
        # Calculate sensitivity and specificity
        if self.num_anomalies > 0:
            # Sensitivity = TP / (TP + FN) ≈ detection rate
            self.sensitivity = self.num_anomalies / len(df)
            # Specificity = TN / (TN + FP) ≈ normal rate
            self.specificity = (predictions == 1).sum() / len(df)
        
        self.is_trained = True
        print(f"✅ Anomaly Detector trained. Detected {self.num_anomalies} anomalies ({self.sensitivity:.1%} of data)")
        print(f"📊 Sensitivity: {self.sensitivity:.1%} | Specificity: {self.specificity:.1%}")

    def predict(self, df):
        """
        Returns the dataframe with an 'is_anomaly' column.
        True = Anomaly, False = Normal
        """
        if not self.is_trained:
            print("⚠️ Model not trained yet!")
            return df
            
        df = df.copy()
        X = self.prepare_features(df)
        
        # Predict: -1 is anomaly, 1 is normal
        predictions = self.model.predict(X)
        
        # Convert to boolean (True if anomaly)
        df['is_anomaly'] = predictions == -1
        
        # Get anomaly score (lower is more anomalous)
        df['anomaly_score'] = self.model.score_samples(X)
        
        return df
    
    def get_metrics(self):
        """Return model performance metrics."""
        return {
            'num_anomalies': self.num_anomalies,
            'sensitivity': self.sensitivity,
            'specificity': self.specificity,
            'is_trained': self.is_trained
        }