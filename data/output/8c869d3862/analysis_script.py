import os
import warnings
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

warnings.filterwarnings('ignore')

# Load dataset
df = pd.read_csv(csv_file_path)

# Normalize column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(r'[^a-zA-Z0-9_]', '', regex=True)

# Convert timestamps
# 'timestamp' appears to be in milliseconds since epoch
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
# 'timestamp_ist' is a string like '02-12-2024 22:50'
df['timestamp_ist'] = pd.to_datetime(df['timestamp_ist'], format='%d-%m-%Y %H:%M', errors='coerce')

# Extract additional time features
df['date'] = df['timestamp'].dt.date
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.day_name()

# Summary statistics for numeric columns
numeric_cols = ['execution_price', 'size_tokens', 'size_usd', 'fee', 'closed_pnl', 'start_position', 'trade_id', 'timestamp']
print('Numeric summary:')
print(df[numeric_cols].describe())

# Value counts for categorical columns
categorical_cols = ['account', 'coin', 'side', 'direction', 'crossed']
for col in categorical_cols:
    print(f'Value counts for {col}:')
    print(df[col].value_counts())

# 1. Histogram of execution_price
fig1 = px.histogram(df, x='execution_price', nbins=50, title='Distribution of Execution Price')
fig1.update_layout(bargap=0.1)
fig1.write_json(os.path.join(OUTPUT_DIR, 'output_1.json'))

# 2. Bar chart of side frequencies
side_counts = df['side'].value_counts().reset_index()
side_counts.columns = ['side', 'count']
fig2 = px.bar(side_counts, x='side', y='count', title='Trade Side Frequency', text='count')
fig2.update_traces(textposition='outside')
fig2.write_json(os.path.join(OUTPUT_DIR, 'output_2.json'))

# 3. Grouped bar chart: total size_usd by coin and side
agg_coin_side = df.groupby(['coin', 'side'])['size_usd'].sum().reset_index()
fig3 = px.bar(agg_coin_side, x='coin', y='size_usd', color='side', barmode='group', title='Total USD Volume by Coin and Side')
fig3.write_json(os.path.join(OUTPUT_DIR, 'output_3.json'))

# 4. Daily total USD volume line chart
daily_volume = df.groupby('date')['size_usd'].sum().reset_index()
fig4 = px.line(daily_volume, x='date', y='size_usd', title='Daily Total USD Volume')
fig4.update_layout(xaxis_title='Date', yaxis_title='Total Size USD')
fig4.write_json(os.path.join(OUTPUT_DIR, 'output_4.json'))

# Optional: Correlation heatmap (saved as JSON as well)
corr = df[numeric_cols].corr()
fig_corr = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, colorscale='Viridis'))
fig_corr.update_layout(title='Correlation Matrix of Numeric Features')
fig_corr.write_json(os.path.join(OUTPUT_DIR, 'output_5.json'))

print('Charts saved to', OUTPUT_DIR)