import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from src.data_processor import DataLoader
from src.categorizer import TransactionCategorizer
from src.anomaly_detector import AnomalyDetector
from src.predictor import ExpensePredictor
from src.insights import InsightsGenerator

# 1. Page Configuration
st.set_page_config(page_title="Personal Finance Engine", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

st.title("💰 Personal Finance Insight Engine")
st.markdown("Upload your bank statement to detect anomalies and predict future expenses. 🚀")

# 2. Sidebar - File Upload & Controls
with st.sidebar:
    st.header("📂 Data Import")
    uploaded_file = st.file_uploader("Upload CSV Statement", type=['csv'])
    
    use_demo = st.checkbox("Use Demo Data", value=False)
    
    st.markdown("---")
    
    # About section
    with st.expander("ℹ️ About this app"):
        st.write("""
        This app uses machine learning to:
        - 📊 **Categorize** your transactions automatically
        - 🚨 **Detect** unusual spending patterns
        - 🔮 **Predict** your next month's expenses
        - 💡 **Suggest** ways to save money
        """)
    
    st.markdown("---")
    st.write("Developed with ❤️ using Streamlit")

# 3. Main Logic
if uploaded_file or use_demo:
    # A. Load Data
    if use_demo:
        file_path = 'data/sample_template.csv'
    else:
        file_path = uploaded_file

    try:
        loader = DataLoader(file_path)
        loader.load_data()
        df = loader.preprocess_data()
        
        if df is None or len(df) == 0:
            st.error("❌ No valid data found. Please check your CSV file format.")
            st.info("📋 Expected columns: date, description, amount, type")
            st.stop()
        
        # B. Run AI Models
        # 1. Categorize
        categorizer = TransactionCategorizer()
        # Try to load existing model, otherwise train on this data
        try:
            categorizer.load()
        except:
            st.info("🤖 Training categorizer model...")
            categorizer.train(df)
            
        df['category'] = categorizer.predict(df)
        
        # 2. Detect Anomalies
        st.info("🔍 Analyzing transaction patterns...")
        anomaly_detector = AnomalyDetector()
        anomaly_detector.train(df)
        df_anomalies = anomaly_detector.predict(df)
        
        # 3. Predict Future
        predictor = ExpensePredictor()
        predictor.train(df)
        forecast_df = predictor.predict_next_30_days()
        
        # 4. Generate Insights
        insights_gen = InsightsGenerator()
        all_insights = insights_gen.generate_all_insights(df, df_anomalies, forecast_df)
        
        st.success("✅ Analysis complete!")
        
        # --- DASHBOARD LAYOUT ---
        
        # KPI ROW
        col1, col2, col3, col4 = st.columns(4)
        
        total_spent = df[df['type'] == 'debit']['amount'].sum()
        total_income = df[df['type'] == 'credit']['amount'].sum()
        savings = total_income - total_spent
        num_transactions = len(df)
        
        col1.metric("💸 Total Spent", f"₹{total_spent:,.0f}")
        col2.metric("💰 Total Income", f"₹{total_income:,.0f}")
        col3.metric("🐷 Net Savings", f"₹{savings:,.0f}")
        col4.metric("📊 Transactions", f"{num_transactions}")
        
        # TABS
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📈 Overview", 
            "🏷️ Categories", 
            "🚨 Anomalies", 
            "🔮 Prediction",
            "💡 Insights",
            "📊 Model Metrics",
            "📥 Export"
        ])
        
        with tab1:
            st.subheader("Spending Over Time")
            daily_spend = df[df['type']=='debit'].groupby('date')['amount'].sum().reset_index()
            fig = px.line(daily_spend, x='date', y='amount', title="Daily Spending Trend", markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary stats
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                avg_daily = daily_spend['amount'].mean()
                st.metric("📅 Average Daily Spend", f"₹{avg_daily:,.0f}")
            with col_stat2:
                max_daily = daily_spend['amount'].max()
                st.metric("📊 Highest Daily Spend", f"₹{max_daily:,.0f}")
            with col_stat3:
                min_daily = daily_spend[daily_spend['amount'] > 0]['amount'].min()
                st.metric("📉 Lowest Daily Spend", f"₹{min_daily:,.0f}")
            
            st.subheader("Recent Transactions")
            display_df = df.sort_values('date', ascending=False).head(15)[['date', 'description', 'category', 'amount', 'type']]
            st.dataframe(display_df, use_container_width=True)
            
        with tab2:
            st.subheader("Where is your money going?")
            cat_spend = df[df['type']=='debit'].groupby('category')['amount'].sum().reset_index().sort_values('amount', ascending=False)
            
            if len(cat_spend) > 0:
                col_chart, col_table = st.columns([2, 1])
                
                with col_chart:
                    fig = px.pie(cat_spend, values='amount', names='category', title="Spending by Category", hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                    
                with col_table:
                    st.write("**Category Breakdown:**")
                    for idx, row in cat_spend.iterrows():
                        pct = (row['amount'] / cat_spend['amount'].sum() * 100)
                        st.write(f"{row['category']}: ₹{row['amount']:,.0f} ({pct:.1f}%)")
                
                # Category comparison
                st.subheader("Category Comparison")
                fig = px.bar(cat_spend.head(10), x='category', y='amount', title="Top 10 Spending Categories", text='amount')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No spending data available for categorization.")
                
        with tab3:
            st.subheader("⚠️ Unusual Spending Detected")
            st.markdown("These transactions deviate significantly from your normal patterns.")
            
            # Filter for True anomalies and Debit only (ignore high income)
            anomalies = df_anomalies[
                (df_anomalies['is_anomaly'] == True) & 
                (df_anomalies['type'] == 'debit')
            ].sort_values('amount', ascending=False)
            
            if len(anomalies) > 0:
                st.error(f"🚨 Found {len(anomalies)} suspicious transactions!")
                display_anomalies = anomalies[['date', 'description', 'category', 'amount', 'anomaly_score']].head(20)
                st.dataframe(display_anomalies, use_container_width=True)
                
                # Anomaly insights
                st.subheader("Anomaly Analysis")
                col_a1, col_a2, col_a3 = st.columns(3)
                with col_a1:
                    st.metric("Total Anomalies", len(anomalies))
                with col_a2:
                    st.metric("Average Anomaly Amount", f"₹{anomalies['amount'].mean():,.0f}")
                with col_a3:
                    st.metric("Max Anomaly Amount", f"₹{anomalies['amount'].max():,.0f}")
            else:
                st.success("✅ No anomalies detected. Your spending looks normal!")
                
        with tab4:
            st.subheader("🔮 Next 30 Days Forecast")
            
            if forecast_df is not None and len(forecast_df) > 0:
                prediction = predictor.get_total_predicted_spend()
                st.metric("Expected Spending Next Month", f"₹{prediction:,.2f}")
                
                # Forecast chart
                fig = go.Figure()
                # Forecast line
                fig.add_trace(go.Scatter(
                    x=forecast_df['ds'], 
                    y=forecast_df['yhat'], 
                    name='Prediction', 
                    line=dict(color='blue', width=2)
                ))
                # Upper bound
                fig.add_trace(go.Scatter(
                    x=forecast_df['ds'], 
                    y=forecast_df['yhat_upper'], 
                    name='Upper Limit', 
                    line=dict(width=0), 
                    showlegend=False
                ))
                # Lower bound (fill down)
                fig.add_trace(go.Scatter(
                    x=forecast_df['ds'], 
                    y=forecast_df['yhat_lower'], 
                    name='Lower Limit', 
                    fill='tonexty', 
                    line=dict(width=0),
                    showlegend=False
                ))
                
                fig.update_layout(
                    title="Projected Daily Spending",
                    xaxis_title="Date",
                    yaxis_title="Amount (₹)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Forecast statistics
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    st.metric("Avg Daily Forecast", f"₹{forecast_df['yhat'].mean():,.0f}")
                with col_f2:
                    st.metric("Max Predicted Day", f"₹{forecast_df['yhat'].max():,.0f}")
                with col_f3:
                    st.metric("Min Predicted Day", f"₹{forecast_df['yhat'].min():,.0f}")
            else:
                st.warning("⚠️ Not enough data to generate forecast. Please upload at least 30 days of transaction history.")
        
        with tab5:
            st.subheader("💡 Personalized Insights & Recommendations")
            
            top_insights = insights_gen.get_top_insights(limit=10)
            
            if len(top_insights) > 0:
                for insight in top_insights:
                    if insight['severity'] == 'warning':
                        st.warning(f"**{insight['title']}**\n\n{insight['description']}\n\n💡 {insight['recommendation']}")
                    elif insight['severity'] == 'success':
                        st.success(f"**{insight['title']}**\n\n{insight['description']}\n\n✅ {insight['recommendation']}")
                    else:
                        st.info(f"**{insight['title']}**\n\n{insight['description']}\n\n💭 {insight['recommendation']}")
            else:
                st.info("No specific insights available yet. Keep adding transactions!")
        
        with tab6:
            st.subheader("📊 Model Performance Metrics")
            
            # Get metrics from models
            cat_metrics = categorizer.get_metrics()
            anom_metrics = anomaly_detector.get_metrics()
            
            st.markdown("### 🏷️ Transaction Categorizer")
            if cat_metrics['is_trained']:
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                with col_m1:
                    st.metric("Accuracy", f"{cat_metrics['accuracy']:.1%}", help="Proportion of correct predictions")
                with col_m2:
                    st.metric("Precision", f"{cat_metrics['precision']:.1%}", help="True positives / (True positives + False positives)")
                with col_m3:
                    st.metric("Recall", f"{cat_metrics['recall']:.1%}", help="True positives / (True positives + False negatives)")
                with col_m4:
                    st.metric("F1 Score", f"{cat_metrics['f1']:.1%}", help="Harmonic mean of precision and recall")
                
                st.info("""
                **Model Details:**
                - **Type:** Random Forest + TF-IDF Vectorizer
                - **Features:** Transaction descriptions
                - **Training Method:** Hybrid (keyword rules + supervised learning)
                - **Classes:** 9 transaction categories
                """)
            else:
                st.warning("Categorizer model not yet trained.")
            
            st.markdown("---")
            st.markdown("### 🚨 Anomaly Detector")
            if anom_metrics['is_trained']:
                col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                with col_a1:
                    st.metric("Anomalies Found", int(anom_metrics['num_anomalies']))
                with col_a2:
                    st.metric("Sensitivity", f"{anom_metrics['sensitivity']:.1%}", help="Detection rate of anomalies")
                with col_a3:
                    st.metric("Specificity", f"{anom_metrics['specificity']:.1%}", help="Normal transactions correctly identified")
                with col_a4:
                    st.metric("Data Coverage", f"{len(df)} transactions")
                
                st.info("""
                **Model Details:**
                - **Type:** Isolation Forest
                - **Features:** Amount, day of week, transaction type
                - **Contamination Rate:** 5% (adjustable)
                - **Scaling:** StandardScaler normalization
                """)
            else:
                st.warning("Anomaly detector not yet trained.")
            
            # Data Quality
            st.markdown("---")
            st.markdown("### 📊 Data Quality Metrics")
            
            col_dq1, col_dq2, col_dq3 = st.columns(3)
            
            with col_dq1:
                st.metric("Total Transactions", len(df))
            with col_dq2:
                date_range = (df['date'].max() - df['date'].min()).days
                st.metric("Date Range (Days)", date_range)
            with col_dq3:
                completeness = (df.notna().sum().sum() / (len(df) * len(df.columns)) * 100)
                st.metric("Data Completeness", f"{completeness:.1f}%")
            
            # Display data quality issues if any
            missing_data = df.isnull().sum()
            if missing_data.sum() > 0:
                st.warning("⚠️ Missing data detected:")
                st.write(missing_data[missing_data > 0])
            else:
                st.success("✅ No missing data detected!")
        
        with tab7:
            st.subheader("📥 Export & Download Reports")
            
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                st.write("**📊 Download Categorized Transactions**")
                # Prepare export data
                export_df = df[['date', 'description', 'category', 'amount', 'type']].copy()
                export_df['date'] = export_df['date'].astype(str)
                
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="Download Transactions as CSV",
                    data=csv,
                    file_name="transactions_categorized.csv",
                    mime="text/csv",
                    key="download_transactions"
                )
            
            with export_col2:
                st.write("**⚠️ Download Anomaly Report**")
                if len(anomalies) > 0:
                    anomaly_export = anomalies[['date', 'description', 'category', 'amount', 'anomaly_score', 'type']].copy()
                    anomaly_export['date'] = anomaly_export['date'].astype(str)
                    csv_anomalies = anomaly_export.to_csv(index=False)
                    st.download_button(
                        label="Download Anomalies as CSV",
                        data=csv_anomalies,
                        file_name="anomalies_report.csv",
                        mime="text/csv",
                        key="download_anomalies"
                    )
                else:
                    st.info("No anomalies to export.")
            
            st.markdown("---")
            
            # Category Summary Report
            st.write("**📈 Category Summary Report**")
            category_summary = df[df['type']=='debit'].groupby('category').agg({
                'amount': ['sum', 'count', 'mean', 'max']
            }).reset_index()
            category_summary.columns = ['Category', 'Total Spent', 'Transactions', 'Avg Transaction', 'Max Transaction']
            
            csv_categories = category_summary.to_csv(index=False)
            st.download_button(
                label="Download Category Summary as CSV",
                data=csv_categories,
                file_name="category_summary.csv",
                mime="text/csv",
                key="download_categories"
            )
            
            st.dataframe(category_summary, use_container_width=True)
            
            # Forecast Report
            if forecast_df is not None:
                st.markdown("---")
                st.write("**🔮 Forecast Report**")
                forecast_export = forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
                forecast_export.columns = ['Date', 'Predicted Amount', 'Lower Bound', 'Upper Bound']
                
                csv_forecast = forecast_export.to_csv(index=False)
                st.download_button(
                    label="Download Forecast as CSV",
                    data=csv_forecast,
                    file_name="forecast_30days.csv",
                    mime="text/csv",
                    key="download_forecast"
                )
                
                st.dataframe(forecast_export.head(10), use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("📋 Please ensure your CSV has columns: date, description, amount, type")
        import traceback
        with st.expander("Debug Info"):
            st.code(traceback.format_exc())

else:
    st.info("👈 Please upload a CSV file or check 'Use Demo Data' to start.")