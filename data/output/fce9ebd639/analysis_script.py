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

# Verify shape
print(f'Dataset shape: {df.shape}')
print('Column dtypes:')
print(df.dtypes)

# Summary statistics for numeric columns
numeric_cols = ['execution_price', 'size_tokens', 'size_usd', 'fee', 'closed_pnl', 'start_position', 'trade_id', 'timestamp']
summary_stats = df[numeric_cols].describe().T
summary_stats['median'] = df[numeric_cols].median()
print('Summary statistics for numeric columns:')
print(summary_stats[['mean', 'median', 'std', 'min', 'max']])

# Unique counts for categorical columns
categorical_cols = ['account', 'coin', 'side', 'timestamp_ist', 'direction', 'transaction_hash']
for col in categorical_cols:
    uniq = df[col].nunique()
    print(f'Unique values in {col}: {uniq}')

# Group‑by analysis by coin
coin_group = df.groupby('coin').agg(total_size_usd=('size_usd', 'sum'),
                                    avg_closed_pnl=('closed_pnl', 'mean'),
                                    trade_count=('trade_id', 'count')).reset_index()
print('Aggregated metrics by coin:')
print(coin_group)

# Group‑by analysis by side
side_group = df.groupby('side').agg(total_size_usd=('size_usd', 'sum'),
                                    avg_closed_pnl=('closed_pnl', 'mean'),
                                    trade_count=('trade_id', 'count')).reset_index()
print('Aggregated metrics by side:')
print(side_group)

# Plot 1: Histogram of execution_price
fig1 = px.histogram(df, x='execution_price', nbins=50, title='Distribution of Execution Price')
fig1.update_layout(xaxis_title='Execution Price', yaxis_title='Count')
fig1.write_json(os.path.join(OUTPUT_DIR, 'output_1.json'))

# Plot 2: Bar chart of side frequencies
side_counts = df['side'].value_counts().reset_index()
side_counts.columns = ['side', 'count']
fig2 = px.bar(side_counts, x='side', y='count', title='Trade Side Frequency', text='count')
fig2.update_layout(xaxis_title='Side', yaxis_title='Number of Trades')
fig2.write_json(os.path.join(OUTPUT_DIR, 'output_2.json'))

# Plot 3: Grouped bar chart of total size_usd by coin
fig3 = px.bar(coin_group, x='coin', y='total_size_usd', title='Total Size USD by Coin', text='total_size_usd')
fig3.update_layout(xaxis_title='Coin', yaxis_title='Total Size USD')
fig3.write_json(os.path.join(OUTPUT_DIR, 'output_3.json'))

# Plot 4: Heatmap of correlations among numeric columns
corr_matrix = df[numeric_cols].corr()
fig4 = go.Figure(data=go.Heatmap(z=corr_matrix.values,
                                x=corr_matrix.columns,
                                y=corr_matrix.index,
                                colorscale='Viridis'))
fig4.update_layout(title='Correlation Heatmap of Numeric Features')
fig4.write_json(os.path.join(OUTPUT_DIR, 'output_4.json'))

# Identify top and bottom performers by size_usd
top_size = df.nlargest(5, 'size_usd')[['account','coin','size_usd','fee','closed_pnl']]
bottom_size = df.nsmallest(5, 'size_usd')[['account','coin','size_usd','fee','closed_pnl']]
print('Top 5 trades by size_usd:')
print(top_size)
print('Bottom 5 trades by size_usd:')
print(bottom_size)

# Box plot for fee to highlight outliers (saved as PNG)
import matplotlib.pyplot as plt
plt.figure(figsize=(8,6))
plt.boxplot(df['fee'].dropna(), vert=False)
plt.title('Box Plot of Fee')
plt.xlabel('Fee')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'output_5.png'), dpi=150)
plt.close()