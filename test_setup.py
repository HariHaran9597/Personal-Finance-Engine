from src.data_processor import DataLoader

# Point to our dummy data
loader = DataLoader('data/sample_template.csv')

# Load
df = loader.load_data()

# Process
clean_df = loader.preprocess_data()

# Show results
print("\n--- Raw Description vs Clean Description ---")
print(clean_df[['description', 'clean_description']].head())

# Save
loader.save_processed()