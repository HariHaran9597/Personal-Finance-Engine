import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class InsightsGenerator:
    """Generate personalized financial insights based on spending patterns."""
    
    def __init__(self):
        self.insights = []
        
    def generate_all_insights(self, df, anomalies, forecast):
        """Generate comprehensive insights from transaction data."""
        self.insights = []
        
        # Calculate basic metrics
        self.analyze_spending_patterns(df)
        self.analyze_category_trends(df)
        self.analyze_anomalies(anomalies)
        self.analyze_savings_potential(df)
        self.analyze_predictions(df, forecast)
        
        return self.insights
    
    def analyze_spending_patterns(self, df):
        """Analyze overall spending patterns."""
        debit_df = df[df['type'] == 'debit']
        
        if len(debit_df) == 0:
            return
        
        total_spent = debit_df['amount'].sum()
        avg_daily = debit_df.groupby('date')['amount'].sum().mean()
        max_transaction = debit_df['amount'].max()
        num_transactions = len(debit_df)
        
        self.insights.append({
            'category': 'Spending Pattern',
            'title': '📊 Your Spending Overview',
            'description': f'You made {num_transactions} transactions, spending ₹{total_spent:,.0f}',
            'recommendation': f'Average daily spending: ₹{avg_daily:,.0f}',
            'severity': 'info'
        })
        
        # High transaction alert
        if max_transaction > avg_daily * 5:
            self.insights.append({
                'category': 'Large Transaction',
                'title': '💸 Large Purchase Detected',
                'description': f'Your highest transaction was ₹{max_transaction:,.0f} - {max_transaction/avg_daily:.1f}x your daily average',
                'recommendation': 'Review this transaction to ensure it was planned',
                'severity': 'warning'
            })
    
    def analyze_category_trends(self, df):
        """Analyze spending by category."""
        debit_df = df[df['type'] == 'debit'].copy()
        
        if len(debit_df) == 0 or 'category' not in debit_df.columns:
            return
        
        category_spend = debit_df.groupby('category')['amount'].sum().sort_values(ascending=False)
        total_spend = category_spend.sum()
        
        # Top spending category
        if len(category_spend) > 0:
            top_category = category_spend.idxmax()
            top_amount = category_spend.max()
            top_pct = (top_amount / total_spend * 100) if total_spend > 0 else 0
            
            if top_pct > 40:
                severity = 'warning'
                icon = '⚠️'
                rec = f'Consider reviewing {top_category} spending - it represents {top_pct:.1f}% of your budget!'
            else:
                severity = 'info'
                icon = '📈'
                rec = f'{top_category} is your top spending category at {top_pct:.1f}% of total.'
            
            self.insights.append({
                'category': 'Category Trend',
                'title': f'{icon} Top Spending: {top_category}',
                'description': f'₹{top_amount:,.0f} spent ({top_pct:.1f}% of total)',
                'recommendation': rec,
                'severity': severity
            })
    
    def analyze_anomalies(self, anomalies_df):
        """Provide insights on detected anomalies."""
        if anomalies_df is None or len(anomalies_df) == 0:
            self.insights.append({
                'category': 'Security',
                'title': '✅ No Anomalies Detected',
                'description': 'Your spending patterns look normal!',
                'recommendation': 'Continue monitoring your transactions',
                'severity': 'success'
            })
            return
        
        debit_anomalies = anomalies_df[anomalies_df['type'] == 'debit']
        
        if len(debit_anomalies) > 0:
            max_anomaly = debit_anomalies['amount'].max()
            self.insights.append({
                'category': 'Security',
                'title': f'🚨 {len(debit_anomalies)} Unusual Transactions Found',
                'description': f'Found {len(debit_anomalies)} transactions that deviate from your normal patterns',
                'recommendation': f'Highest anomaly: ₹{max_anomaly:,.0f}. Please review these transactions.',
                'severity': 'warning'
            })
    
    def analyze_savings_potential(self, df):
        """Identify opportunities to save money."""
        debit_df = df[df['type'] == 'debit'].copy()
        
        if len(debit_df) == 0 or 'category' not in debit_df.columns:
            return
        
        # Check for recurring subscriptions/entertainment
        entertainment = debit_df[debit_df['category'] == 'Entertainment']['amount'].sum()
        shopping = debit_df[debit_df['category'] == 'Shopping']['amount'].sum()
        total_spend = debit_df['amount'].sum()
        
        # Entertainment savings tip
        if entertainment > 0:
            entertainment_pct = (entertainment / total_spend * 100)
            if entertainment_pct > 5:
                self.insights.append({
                    'category': 'Savings',
                    'title': '💰 Entertainment Opportunity',
                    'description': f'You spend ₹{entertainment:,.0f} on entertainment ({entertainment_pct:.1f}%)',
                    'recommendation': f'Consider canceling unused subscriptions (Netflix, Spotify, etc.) to save ~₹{entertainment * 0.3:,.0f}/month',
                    'severity': 'info'
                })
        
        # Shopping savings tip
        if shopping > 0:
            shopping_pct = (shopping / total_spend * 100)
            if shopping_pct > 10:
                self.insights.append({
                    'category': 'Savings',
                    'title': '🛍️ Shopping Spending Alert',
                    'description': f'You spend ₹{shopping:,.0f} on shopping ({shopping_pct:.1f}%)',
                    'recommendation': f'Consider creating a shopping budget or wishlist. You could save ~₹{shopping * 0.2:,.0f}/month by being selective.',
                    'severity': 'info'
                })
    
    def analyze_predictions(self, df, forecast_df):
        """Provide insights on future spending predictions."""
        if forecast_df is None or len(forecast_df) == 0:
            return
        
        predicted_total = forecast_df['yhat'].sum()
        debit_df = df[df['type'] == 'debit']
        
        if len(debit_df) > 0:
            avg_monthly = debit_df.groupby(debit_df['date'].dt.to_period('M'))['amount'].sum().mean()
            
            self.insights.append({
                'category': 'Prediction',
                'title': '🔮 Next 30 Days Forecast',
                'description': f'Predicted spending: ₹{predicted_total:,.0f}',
                'recommendation': f'Historical average: ₹{avg_monthly:,.0f}/month. Budget accordingly.',
                'severity': 'info'
            })
    
    def get_top_insights(self, limit=5):
        """Get top insights sorted by severity."""
        severity_order = {'warning': 0, 'success': 1, 'info': 2}
        sorted_insights = sorted(self.insights, key=lambda x: severity_order.get(x.get('severity', 'info'), 99))
        return sorted_insights[:limit]
    
    def format_insights(self, insights):
        """Format insights for display."""
        formatted = []
        for insight in insights:
            formatted.append({
                'title': insight['title'],
                'description': insight['description'],
                'recommendation': insight['recommendation'],
                'type': insight['severity']
            })
        return formatted
