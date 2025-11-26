import pandas as pd
import numpy as np
import re
from . import config

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_data(self):
        """Loads CSV and validates columns"""
        try:
            self.df = pd.read_csv(self.file_path)
            
            # Validate columns
            missing_cols = [col for col in config.REQUIRED_COLUMNS if col not in self.df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            print(f"✅ Data loaded successfully. Shape: {self.df.shape}")
            return self.df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None

    def preprocess_data(self):
        """Clean dates, descriptions, and amounts"""
        if self.df is None:
            return None
        
        df = self.df.copy()

        # 1. Standardize Dates
        # Coerce errors to NaT, then drop invalid rows
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])

        # 2. Standardize Amounts
        # Ensure absolute values (no negative numbers for expenses)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').abs()
        
        # 3. Clean Descriptions (Crucial for ML!)
        df['clean_description'] = df['description'].apply(self._clean_text)
        
        # 4. Standardize Type
        df['type'] = df['type'].str.lower().str.strip()
        
        self.df = df
        return df

    def _clean_text(self, text):
        """
        Removes numbers, special chars, and extra spaces.
        Example: 'UBER *TRIP 12345' -> 'uber trip'
        """
        if not isinstance(text, str):
            return ""
            
        text = text.lower()
        # Remove special chars and numbers (keep only letters and spaces)
        text = re.sub(r'[^a-z\s]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def save_processed(self, filename='processed_data.csv'):
        """Saves cleaned data to processed folder"""
        if self.df is not None:
            save_path = f"{config.PROCESSED_DATA_PATH}/{filename}"
            self.df.to_csv(save_path, index=False)
            print(f"💾 Processed data saved to: {save_path}")