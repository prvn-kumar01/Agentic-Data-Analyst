import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load dataset
df = pd.read_csv(csv_file_path)
# Normalize column names
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(r'[^a-zA-Z0-9_]', '', regex=True)

# Convert timestamps
# timestamp column appears to be epoch in milliseconds
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
# timestamp_ist format: '02-12-2024 22:50'
df['timestamp_ist'] = pd.to_datetime(df['timestamp_ist'], format='%d-%m-%Y %H:%M')

# Overview statistics
print('Dataset shape:', df.shape)
print('Missing values per column:\n', df.isnull().sum())
numeric_cols = ['execution_price','size_tokens','size_usd','closed_pnl','fee','trade_id','timestamp']
print('Descriptive statistics for numeric columns:\n', df[numeric_cols].describe())

# 1. Histogram of execution_price
fig1 = px.histogram(df, x='execution_price', nbins=50, title='Distribution of Execution Price')
fig1.update_layout(xaxis_title='Execution Price', yaxis_title='Count')
fig1.write_json(os.path.join(OUTPUT_DIR, 'output_1.json'))

# 2. Bar chart of coin counts
coin_counts = df['coin'].value_counts().reset_index()
coin_counts.columns = ['coin', 'count']
fig2 = px.bar(coin_counts, x='coin', y='count', title='Trade Count per Coin')
fig2.update_layout(xaxis_title='Coin', yaxis_title='Number of Trades')
fig2.write_json(os.path.join(OUTPUT_DIR, 'output_2.json'))

# 3. Grouped aggregation by coin and side
agg_df = df.groupby(['coin', 'side']).agg(
    total_size_usd=('size_usd', 'sum'),
    avg_size_usd=('size_usd', 'mean'),
    total_fee=('fee', 'sum'),
    mean_execution_price=('execution_price', 'mean')
).reset_index()
# Visualize total_size_usd by coin and side
fig3 = px.bar(agg_df, x='coin', y='total_size_usd', color='side', barmode='group',
              title='Total Size USD by Coin and Side')
fig3.update_layout(xaxis_title='Coin', yaxis_title='Total Size USD')
fig3.write_json(os.path.join(OUTPUT_DIR, 'output_3.json'))

# 4. Correlation heatmap for selected numeric columns
corr_cols = ['execution_price','size_tokens','size_usd','closed_pnl','fee','trade_id']
corr_matrix = df[corr_cols].corr()
fig4 = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns,
    y=corr_matrix.index,
    colorscale='Viridis'))
fig4.update_layout(title='Correlation Matrix Heatmap')
fig4.write_json(os.path.join(OUTPUT_DIR, 'output_4.json'))

# Additional insights: Top 10 trades by size_usd
top_size_usd = df.nlargest(10, 'size_usd')[['transaction_hash','size_usd']]
print('Top 10 trades by size_usd:\n', top_size_usd)
# Bottom 10 trades by size_usd
bottom_size_usd = df.nsmallest(10, 'size_usd')[['transaction_hash','size_usd']]
print('Bottom 10 trades by size_usd:\n', bottom_size_usd)

# End of script