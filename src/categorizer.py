import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from . import config

class TransactionCategorizer:
    def __init__(self):
        # The ML Pipeline: Convert text to numbers (TF-IDF) -> Classify (Random Forest)
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        self.is_trained = False
        self.accuracy = 0.0
        self.precision = 0.0
        self.recall = 0.0
        self.f1 = 0.0
        
        # 🛡️ LAYER 1: The Rule Engine
        # Define keywords for auto-labeling
        self.keyword_map = {
            'Food & Dining': ['swiggy', 'zomato', 'starbucks', 'mcdonalds', 'kfc', 'pizza', 'burger', 'cafe', 'restaurant', 'coffee', 'dining'],
            'Transportation': ['uber', 'ola', 'rapido', 'metro', 'fuel', 'petrol', 'pump', 'parking', 'toll', 'irctc', 'rail'],
            'Shopping': ['amazon', 'flipkart', 'myntra', 'zara', 'h&m', 'store', 'mart', 'market', 'mall', 'ikea'],
            'Bills & Utilities': ['electricity', 'water', 'gas', 'broadband', 'wifi', 'airtel', 'jio', 'vodafone', 'bill', 'recharge'],
            'Entertainment': ['netflix', 'prime', 'spotify', 'movie', 'cinema', 'bookmyshow', 'hotstar', 'youtube', 'game'],
            'Health & Wellness': ['pharmacy', 'medplus', 'apollo', 'doctor', 'hospital', 'clinic', 'gym', 'fitness', 'cult'],
            'Income': ['salary', 'credit', 'refund', 'cashback', 'interest', 'dividend'],
            'Transfer': ['upi', 'transfer', 'sent', 'paid to'],
        }

    def _get_keyword_category(self, description):
        """Check if description contains any keyword"""
        description = description.lower()
        for category, keywords in self.keyword_map.items():
            for keyword in keywords:
                if keyword in description:
                    return category
        return None

    def train(self, df):
        """
        Train the model using a mix of Rule-Based labels and Manual labels.
        """
        print("Training Categorizer...")
        
        # 1. Auto-label data using rules (Create a 'ground truth' for the ML to learn from)
        # In a real scenario, you would also load a manually labeled CSV here.
        train_data = df.copy()
        
        # Apply rules to generate labels
        train_data['category'] = train_data['clean_description'].apply(self._get_keyword_category)
        
        # Drop rows where rules couldn't find a category (we can't train on unknowns)
        train_data = train_data.dropna(subset=['category'])
        
        if len(train_data) < 5:
            print("⚠️ Not enough labeled data to train ML model yet. relying on rules only.")
            return

        # 2. Train the ML model with train/test split for accuracy calculation
        X = train_data['clean_description']
        y = train_data['category']
        
        # Split data for training and testing
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None)
        
        # Train model
        self.pipeline.fit(X_train, y_train)
        
        # Calculate metrics
        y_pred = self.pipeline.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)
        
        # Calculate precision, recall, f1 with weighted average for imbalanced data
        try:
            self.precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            self.recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            self.f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        except:
            self.precision = self.accuracy
            self.recall = self.accuracy
            self.f1 = self.accuracy
        
        self.is_trained = True
        print(f"✅ Model trained on {len(train_data)} transactions.")
        print(f"📊 Model Accuracy: {self.accuracy:.2%} | Precision: {self.precision:.2%} | Recall: {self.recall:.2%} | F1: {self.f1:.2%}")

    def predict(self, df):
        """
        Hybrid Prediction:
        1. Try Rule Engine
        2. If Rule fails, use ML Model
        """
        df = df.copy()
        predictions = []
        
        for _, row in df.iterrows():
            desc = row['clean_description']
            
            # Layer 1: Rules
            rule_cat = self._get_keyword_category(desc)
            
            if rule_cat:
                predictions.append(rule_cat)
            
            # Layer 2: ML Model (only if trained)
            elif self.is_trained:
                try:
                    ml_cat = self.pipeline.predict([desc])[0]
                    predictions.append(ml_cat)
                except:
                    predictions.append('Other')
            else:
                predictions.append('Other')
                
        return predictions

    def get_metrics(self):
        """Return model performance metrics."""
        return {
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1': self.f1,
            'is_trained': self.is_trained
        }

    def save(self):
        """Save the trained model to disk"""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'categorizer.pkl')
        with open(path, 'wb') as f:
            pickle.dump(self.pipeline, f)
        print("💾 Model saved.")

    def load(self):
        """Load the model from disk"""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'categorizer.pkl')
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.pipeline = pickle.load(f)
            self.is_trained = True
            print("✅ Model loaded.")
        else:
            print("⚠️ No saved model found.")