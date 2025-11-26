from src.data_processor import DataLoader
from src.categorizer import TransactionCategorizer
import pandas as pd

def main():
    # 1. Load Data
    loader = DataLoader('data/sample_template.csv')
    loader.load_data()
    df = loader.preprocess_data()
    
    # 2. Initialize and Train Categorizer
    model = TransactionCategorizer()
    model.train(df)
    
    # 3. Test Predictions
    print("\n--- Testing Predictions ---")
    # Let's test with a mix of known keywords and unknown descriptions
    test_cases = pd.DataFrame({
        'clean_description': [
            'starbucks coffee',      # Keyword match (Food)
            'salary credit',         # Keyword match (Income)
            'unknown store 123',     # No Keyword -> ML should guess or say Other
            'shell petrol pump',     # Keyword match (Transport)
            'netflix subscription'   # Keyword match (Entertainment)
        ]
    })
    
    predictions = model.predict(test_cases)
    test_cases['predicted_category'] = predictions
    
    print(test_cases)
    
    # 4. Save Model
    model.save()

if __name__ == "__main__":
    main()