import pandas as pd
from src.data_processor import DataLoader
from src.anomaly_detector import AnomalyDetector

def main():
    # 1. Load Normal Data
    loader = DataLoader('data/sample_template.csv')
    loader.load_data()
    df = loader.preprocess_data()
    
    # 2. Inject a FAKE Anomaly
    # A Starbucks coffee for ₹50,000 (Suspicious!)
    fake_row = pd.DataFrame({
        'date': [pd.Timestamp('2024-01-10')],
        'description': ['Hacker Starbucks Hack'],
        'amount': [50000],
        'type': ['debit'],
        'clean_description': ['hacker starbucks hack']
    })
    
    # Add fake row to our data
    test_df = pd.concat([df, fake_row], ignore_index=True)
    
    # 3. Train & Detect
    detector = AnomalyDetector()
    detector.train(test_df) # Train on the mixed data
    
    results = detector.predict(test_df)
    
    # 4. Filter to show only anomalies
    anomalies = results[results['is_anomaly'] == True]
    
    print("\n--- Detected Anomalies ---")
    print(anomalies[['date', 'description', 'amount', 'is_anomaly']])

if __name__ == "__main__":
    main()