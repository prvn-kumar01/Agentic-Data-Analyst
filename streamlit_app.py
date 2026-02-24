"""
╔══════════════════════════════════════════════════════════════╗
║        🤖 AUTO-ANALYST AI — Streamlit Frontend               ║
║     Premium Dark UI for the Autonomous Data Analysis Agent   ║
╚══════════════════════════════════════════════════════════════╝

Run:  streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import os
import time
import pandas as pd
from io import StringIO

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="Auto-Analyst AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CUSTOM CSS — Premium Dark Theme v2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary: #060610;
    --bg-secondary: #0d0d1a;
    --bg-tertiary: #141425;
    --bg-card: #1a1a2e;
    --bg-card-hover: #1f1f38;
    --bg-glass: rgba(20, 20, 37, 0.65);
    --border-color: rgba(102, 126, 234, 0.12);
    --border-hover: rgba(102, 126, 234, 0.35);
    --border-active: rgba(102, 126, 234, 0.6);
    --text-primary: #eaeaf2;
    --text-secondary: #9090ab;
    --text-muted: #555570;
    --text-dim: #3a3a52;
    --accent-1: #667eea;
    --accent-2: #764ba2;
    --accent-3: #f093fb;
    --accent-4: #4facfe;
    --gradient-main: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-warm: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --gradient-cool: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --gradient-subtle: linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%);
    --success: #34d399;
    --success-bg: rgba(52, 211, 153, 0.08);
    --warning: #fbbf24;
    --error: #f87171;
    --error-bg: rgba(248, 113, 113, 0.08);
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.25);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.35);
    --shadow-lg: 0 8px 32px rgba(0,0,0,0.45);
    --shadow-glow: 0 0 40px rgba(102,126,234,0.12);
    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-xl: 24px;
}

/* ── Global ── */
.stApp {
    background: var(--bg-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Ambient background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
        radial-gradient(ellipse 800px 600px at 15% 30%, rgba(102,126,234,0.06) 0%, transparent 70%),
        radial-gradient(ellipse 600px 500px at 85% 15%, rgba(118,75,162,0.05) 0%, transparent 70%),
        radial-gradient(ellipse 900px 400px at 50% 95%, rgba(79,172,254,0.04) 0%, transparent 70%),
        radial-gradient(ellipse 400px 400px at 70% 60%, rgba(240,147,251,0.03) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
    border-right: 1px solid var(--border-color) !important;
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span {
    color: var(--text-secondary) !important;
}

/* ── Logo ── */
.sidebar-logo {
    text-align: center;
    padding: 1.2rem 0 0.6rem;
}

.sidebar-logo .logo-icon {
    font-size: 2.5rem;
    line-height: 1;
    filter: drop-shadow(0 0 20px rgba(102,126,234,0.4));
    animation: logoPulse 3s ease-in-out infinite;
}

.sidebar-logo .logo-text {
    font-size: 1.2rem;
    font-weight: 800;
    background: var(--gradient-main);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.03em;
    margin-top: 0.3rem;
}

.sidebar-logo .logo-sub {
    font-size: 0.68rem;
    color: var(--text-dim);
    margin-top: 0.15rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

@keyframes logoPulse {
    0%, 100% { filter: drop-shadow(0 0 20px rgba(102,126,234,0.4)); }
    50%      { filter: drop-shadow(0 0 30px rgba(118,75,162,0.5)); }
}

/* ── Divider ── */
.divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    margin: 0.8rem 0;
}

/* ── Section Label ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-dim);
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.45rem;
}

/* ── Hero Header ── */
.hero-header {
    text-align: center;
    padding: 2.5rem 0 0.5rem;
    animation: fadeInDown 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero-header h1 {
    font-size: 3.2rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 40%, #f093fb 70%, #4facfe 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
    line-height: 1.15 !important;
    margin-bottom: 0 !important;
    animation: gradientShift 6s ease infinite;
}

@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.hero-subtitle {
    color: var(--text-muted) !important;
    font-size: 1.05rem;
    font-weight: 400;
    margin-top: 0.3rem;
    letter-spacing: 0.01em;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--gradient-subtle);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 0.35rem 1rem;
    font-size: 0.72rem;
    color: var(--accent-1);
    font-weight: 500;
    margin-top: 0.8rem;
}

.hero-badge .dot {
    width: 6px;
    height: 6px;
    background: var(--success);
    border-radius: 50%;
    animation: dotPulse 2s ease-in-out infinite;
}

@keyframes dotPulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(52,211,153,0.4); }
    50%      { opacity: 0.7; box-shadow: 0 0 0 4px rgba(52,211,153,0); }
}

/* ── Glass Card ── */
.glass-card {
    background: var(--bg-glass);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.6rem;
    margin-bottom: 1.2rem;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(102,126,234,0.3), transparent);
    opacity: 0;
    transition: opacity 0.35s ease;
}

.glass-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-glow);
    transform: translateY(-1px);
}

.glass-card:hover::before {
    opacity: 1;
}

/* ── Insight Panel ── */
.insight-panel {
    background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.06), rgba(79,172,254,0.04));
    border: 1px solid rgba(102,126,234,0.2);
    border-radius: var(--radius-lg);
    padding: 2rem;
    line-height: 1.9;
    font-size: 0.95rem;
    color: var(--text-primary);
    margin-bottom: 1.2rem;
    animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
}

.insight-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--gradient-main);
    border-radius: 2px 2px 0 0;
}

.insight-icon-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(102,126,234,0.12);
    border: 1px solid rgba(102,126,234,0.2);
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--accent-1);
    margin-bottom: 1rem;
}

/* ── Pipeline Steps ── */
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.6rem 0.9rem;
    border-radius: var(--radius-sm);
    font-size: 0.82rem;
    font-weight: 500;
    transition: all 0.3s ease;
    margin-bottom: 0.4rem;
    position: relative;
}

.pipeline-step.completed {
    border: 1px solid rgba(52,211,153,0.2);
    background: rgba(52,211,153,0.06);
    color: var(--success);
}

.pipeline-step.running {
    border: 1px solid rgba(102,126,234,0.35);
    background: rgba(102,126,234,0.08);
    color: var(--accent-1);
    animation: stepPulse 1.8s ease-in-out infinite;
}

.pipeline-step.waiting {
    border: 1px solid transparent;
    background: rgba(255,255,255,0.02);
    color: var(--text-dim);
}

.pipeline-step.error {
    border: 1px solid rgba(248,113,113,0.2);
    background: var(--error-bg);
    color: var(--error);
}

@keyframes stepPulse {
    0%, 100% { opacity: 1; box-shadow: none; }
    50%      { opacity: 0.75; box-shadow: inset 0 0 20px rgba(102,126,234,0.05); }
}

/* ── Chips / Quick Prompts ── */
.chip-btn {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 22px !important;
    padding: 0.4rem 1rem !important;
    font-size: 0.78rem !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

.chip-btn:hover {
    background: rgba(102,126,234,0.1) !important;
    border-color: var(--accent-1) !important;
    color: var(--text-primary) !important;
    transform: translateY(-1px);
}

/* ── Code Block ── */
.code-container {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1.2rem 1.3rem;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.8rem;
    color: var(--text-secondary);
    overflow-x: auto;
    white-space: pre-wrap;
    max-height: 400px;
    overflow-y: auto;
    line-height: 1.6;
}

/* ── Chart Gallery ── */
.chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 1rem;
    position: relative;
}

.chart-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--gradient-main);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.chart-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-lg);
    transform: translateY(-3px) scale(1.005);
}

.chart-card:hover::before {
    opacity: 1;
}

.chart-label {
    padding: 0.7rem 1.1rem;
    font-size: 0.78rem;
    color: var(--text-secondary);
    font-weight: 500;
    border-top: 1px solid rgba(255,255,255,0.04);
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── File Info Badge ── */
.file-info {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 0.9rem 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin: 0.5rem 0;
    transition: all 0.3s ease;
}

.file-info:hover {
    border-color: var(--border-hover);
}

.file-info .file-icon {
    font-size: 1.6rem;
    filter: drop-shadow(0 0 8px rgba(102,126,234,0.3));
}

.file-info .details h4 {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
}

.file-info .details p {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin: 0.15rem 0 0;
}

/* ── Metric Cards ── */
.metric-row {
    display: flex;
    gap: 0.7rem;
    margin: 0.8rem 0;
}

.metric-card {
    flex: 1;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 0.75rem 0.6rem;
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card:hover {
    border-color: var(--border-hover);
    transform: translateY(-1px);
}

.metric-card .value {
    font-size: 1.35rem;
    font-weight: 800;
    background: var(--gradient-main);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-card .label {
    font-size: 0.65rem;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 0.15rem;
    font-weight: 600;
}

/* ── Column Tag ── */
.col-tag {
    display: inline-block;
    background: rgba(102,126,234,0.08);
    border: 1px solid rgba(102,126,234,0.15);
    border-radius: 6px;
    padding: 0.2rem 0.55rem;
    font-size: 0.68rem;
    color: var(--accent-1);
    margin: 0.12rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.col-tag:hover {
    background: rgba(102,126,234,0.15);
    border-color: var(--accent-1);
}

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 5rem 2rem;
    color: var(--text-dim);
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.empty-state .empty-icon {
    font-size: 4rem;
    margin-bottom: 1.2rem;
    opacity: 0.4;
    filter: drop-shadow(0 0 15px rgba(102,126,234,0.2));
}

.empty-state h3 {
    font-size: 1.2rem;
    color: var(--text-secondary);
    margin-bottom: 0.3rem;
    font-weight: 600;
}

.empty-state p {
    font-size: 0.9rem;
    color: var(--text-dim);
}

/* ── Error Card ── */
.error-card {
    background: var(--error-bg);
    border: 1px solid rgba(248,113,113,0.2);
    border-radius: var(--radius-md);
    padding: 1.3rem;
    color: #fca5a5;
    margin-bottom: 1rem;
    animation: fadeInUp 0.4s ease;
}

/* ── Chat Bubble ── */
.chat-user {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md) var(--radius-md) 4px var(--radius-md);
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.7rem;
    font-size: 0.88rem;
    color: var(--text-primary);
    max-width: 80%;
    margin-left: auto;
    text-align: right;
    animation: slideInRight 0.3s ease;
}

.chat-ai {
    background: linear-gradient(135deg, rgba(102,126,234,0.06), rgba(118,75,162,0.04));
    border: 1px solid rgba(102,126,234,0.15);
    border-radius: var(--radius-md) var(--radius-md) var(--radius-md) 4px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.7rem;
    font-size: 0.88rem;
    color: var(--text-secondary);
    max-width: 85%;
    animation: slideInLeft 0.3s ease;
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}

/* ── Shimmer Loading ── */
.shimmer-line {
    height: 14px;
    background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-card-hover) 50%, var(--bg-card) 75%);
    background-size: 200% 100%;
    border-radius: 6px;
    margin-bottom: 0.6rem;
    animation: shimmer 1.5s ease-in-out infinite;
}

.shimmer-line.short { width: 60%; }
.shimmer-line.medium { width: 80%; }
.shimmer-line.long { width: 95%; }

@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* ── Accent Buttons ── */
.stButton > button {
    background: var(--gradient-main) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.65rem 1.8rem !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 2px 12px rgba(102,126,234,0.25) !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button:hover {
    box-shadow: 0 6px 28px rgba(102,126,234,0.4) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Streamlit overrides ── */
.stTextInput > div > div > input {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.75rem 1.1rem !important;
    font-size: 0.9rem !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent-1) !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.12) !important;
}

.stTextInput > div > div > input::placeholder {
    color: var(--text-dim) !important;
}

.stFileUploader {
    background: transparent !important;
}

.stFileUploader > div {
    border: 2px dashed var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.35s ease;
}

.stFileUploader > div:hover {
    border-color: var(--accent-1) !important;
    background: rgba(102,126,234,0.04) !important;
}

div[data-testid="stExpander"] {
    background: var(--bg-glass) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden;
    transition: all 0.3s ease;
}

div[data-testid="stExpander"]:hover {
    border-color: var(--border-hover) !important;
}

div[data-testid="stExpander"] summary {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}

.stDataFrame {
    border-radius: var(--radius-sm) !important;
    overflow: hidden;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 1px solid var(--border-color) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    border: 1px solid transparent !important;
    border-bottom: none !important;
    color: var(--text-muted) !important;
    padding: 0.55rem 1.1rem !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(102,126,234,0.1) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.25); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-1); }

/* ── Animations ── */
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-25px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(25px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

/* ── History item ── */
.history-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.7rem;
    border-radius: var(--radius-sm);
    font-size: 0.78rem;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.2s ease;
    margin-bottom: 0.25rem;
}

.history-item:hover {
    background: rgba(102,126,234,0.06);
    color: var(--text-secondary);
}

/* ── Query section label tag ── */
.query-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: var(--gradient-main);
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.65rem;
    color: white;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Footer ── */
.footer-bar {
    text-align: center;
    padding: 2rem 0 1rem;
    font-size: 0.7rem;
    color: var(--text-dim);
    border-top: 1px solid var(--border-color);
    margin-top: 3rem;
}

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE INIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if "file_data" not in st.session_state:
    st.session_state.file_data = None
if "result" not in st.session_state:
    st.session_state.result = None
if "node_log" not in st.session_state:
    st.session_state.node_log = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "query_input" not in st.session_state:
    st.session_state.query_input = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER: Pipeline Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PIPELINE_NODES = [
    ("📋", "profiler", "Data Profiler"),
    ("🗺️", "planner", "Analysis Planner"),
    ("💻", "generator", "Code Generator"),
    ("⚡", "executor", "Code Executor"),
    ("🧠", "insight", "Insight Engine"),
]

def render_pipeline_status(node_log, is_loading):
    """Render pipeline status as styled HTML."""
    completed_nodes = {entry.get("node", "") for entry in node_log}

    html = '<div class="section-label">⚙️ Pipeline Status</div>'

    for icon, node_key, label in PIPELINE_NODES:
        if node_key in completed_nodes:
            entry = next((e for e in node_log if e.get("node") == node_key), {})
            if entry.get("error"):
                css_class = "error"
                status_icon = "❌"
            else:
                css_class = "completed"
                status_icon = "✅"
        elif is_loading and node_key not in completed_nodes:
            first_non_completed = None
            for _, nk, _ in PIPELINE_NODES:
                if nk not in completed_nodes:
                    first_non_completed = nk
                    break
            if node_key == first_non_completed:
                css_class = "running"
                status_icon = "⏳"
            else:
                css_class = "waiting"
                status_icon = "○"
        else:
            css_class = "waiting"
            status_icon = "○"

        html += f'<div class="pipeline-step {css_class}">{status_icon} {icon} {label}</div>'

    return html


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">🤖</div>
        <div class="logo-text">Auto-Analyst AI</div>
        <div class="logo-sub">Powered by LangGraph • Llama 3.3</div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    # ── File Uploader (Single unified uploader) ──
    st.markdown('<div class="section-label">📂 Upload Dataset</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv", "pdf", "xlsx", "xls", "json"],
        label_visibility="collapsed",
        help="Upload CSV, PDF, Excel, or JSON files to analyze",
        key="dataset_uploader"
    )

    if uploaded_file is not None:
        # Determine if this is a new file
        prev = st.session_state.file_data
        is_new_file = (
            prev is None
            or prev.get("filename") != uploaded_file.name
            and prev.get("original_pdf") != uploaded_file.name
        )

        if is_new_file:
            file_ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""

            if file_ext == "pdf":
                # PDF → extract tables via /api/upload-pdf
                with st.spinner("📑 Extracting tables from PDF..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        resp = requests.post(f"{API_BASE}/api/upload-pdf", files=files, timeout=60)
                        data = resp.json()

                        if data.get("success"):
                            st.session_state.file_data = data
                            st.session_state.result = None
                            st.session_state.node_log = []
                            st.session_state.chat_history = []
                            st.toast(f"✅ Tables extracted from {uploaded_file.name}!", icon="📑")
                        else:
                            st.error(f"PDF extraction failed: {data.get('error', 'Unknown error')}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API server. Make sure FastAPI is running on port 8000.")
                    except Exception as e:
                        st.error(f"❌ Upload error: {e}")
            else:
                # CSV / Excel / JSON → upload via /api/upload
                mime_map = {
                    "csv": "text/csv",
                    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "xls": "application/vnd.ms-excel",
                    "json": "application/json",
                }
                mime = mime_map.get(file_ext, "application/octet-stream")

                with st.spinner("📂 Uploading..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), mime)}
                        resp = requests.post(f"{API_BASE}/api/upload", files=files, timeout=30)
                        data = resp.json()

                        if data.get("success"):
                            st.session_state.file_data = data
                            st.session_state.result = None
                            st.session_state.node_log = []
                            st.session_state.chat_history = []
                            st.toast(f"✅ {uploaded_file.name} loaded!", icon="📂")
                        else:
                            st.error(f"Upload failed: {data.get('error', 'Unknown error')}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API server. Make sure FastAPI is running on port 8000.")
                    except Exception as e:
                        st.error(f"❌ Upload error: {e}")

    # ── File Info ──
    if st.session_state.file_data:
        fd = st.session_state.file_data
        st.markdown(f"""
        <div class="file-info">
            <div class="file-icon">📄</div>
            <div class="details">
                <h4>{fd['filename']}</h4>
                <p>{fd['rows']:,} rows × {fd['cols']} columns</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="value">{fd['rows']:,}</div>
                <div class="label">Rows</div>
            </div>
            <div class="metric-card">
                <div class="value">{fd['cols']}</div>
                <div class="label">Columns</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Column tags
        if fd.get("column_names"):
            cols_html = ""
            for col_name in fd["column_names"]:
                cols_html += f'<span class="col-tag">{col_name}</span>'
            st.markdown(f"""
            <div class="section-label" style="margin-top: 0.8rem;">📊 Columns</div>
            <div>{cols_html}</div>
            """, unsafe_allow_html=True)

        # Data Preview
        if fd.get("preview"):
            st.markdown('<div class="section-label" style="margin-top: 1rem;">👁️ Preview</div>', unsafe_allow_html=True)
            preview_df = pd.DataFrame(fd["preview"])
            st.dataframe(preview_df, use_container_width=True, height=180)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Pipeline Status ──
    if st.session_state.node_log or st.session_state.is_loading:
        pipeline_html = render_pipeline_status(
            st.session_state.node_log,
            st.session_state.is_loading
        )
        st.markdown(pipeline_html, unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Query History ──
    if st.session_state.chat_history:
        st.markdown('<div class="section-label">🕐 Query History</div>', unsafe_allow_html=True)
        for i, entry in enumerate(reversed(st.session_state.chat_history[-5:])):
            query_text = entry.get("query", "")[:40]
            if len(entry.get("query", "")) > 40:
                query_text += "..."
            st.markdown(f'<div class="history-item">💬 {query_text}</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN CONTENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── Hero ──
st.markdown("""
<div class="hero-header">
    <h1>Auto-Analyst AI</h1>
</div>
<p class="hero-subtitle" style="text-align:center;">
    Upload a dataset · Ask in plain English · Get instant multi-chart analysis
</p>
<div style="text-align:center;">
    <span class="hero-badge">
        <span class="dot"></span>
        AI Agent Ready
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Empty State ──
if not st.session_state.file_data:
    st.markdown("""
    <div class="glass-card empty-state">
        <div class="empty-icon">📂</div>
        <h3>No Data Loaded</h3>
        <p>Upload a CSV file from the sidebar to get started</p>
    </div>
    """, unsafe_allow_html=True)

    # Features showcase
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding: 1.5rem;">
            <div style="font-size:2rem; margin-bottom:0.5rem;">📊</div>
            <div style="font-weight:600; color:var(--text-primary); font-size:0.9rem;">Smart Profiling</div>
            <div style="font-size:0.78rem; color:var(--text-muted); margin-top:0.3rem;">
                Auto-detects data types, patterns &amp; distributions
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding: 1.5rem;">
            <div style="font-size:2rem; margin-bottom:0.5rem;">🧠</div>
            <div style="font-weight:600; color:var(--text-primary); font-size:0.9rem;">AI-Powered Insights</div>
            <div style="font-size:0.78rem; color:var(--text-muted); margin-top:0.3rem;">
                LLM generates analysis plans &amp; interprets results
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding: 1.5rem;">
            <div style="font-size:2rem; margin-bottom:0.5rem;">📈</div>
            <div style="font-weight:600; color:var(--text-primary); font-size:0.9rem;">Multi-Chart Output</div>
            <div style="font-size:0.78rem; color:var(--text-muted); margin-top:0.3rem;">
                Auto-generates multiple publication-quality charts
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # ── Query Section ──
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.8rem;">
        <span class="query-tag">💬 ASK</span>
        <span style="font-size:0.88rem; font-weight:500; color:var(--text-secondary);">
            What would you like to know about your data?
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Quick prompt chips
    quick_prompts = [
        "📊 Full summary",
        "📈 Show trends",
        "🔝 Top 10 values",
        "📉 Correlations",
        "🗺️ Distribution",
    ]

    chip_cols = st.columns(len(quick_prompts))
    for i, prompt in enumerate(quick_prompts):
        with chip_cols[i]:
            if st.button(prompt, key=f"chip_{i}", use_container_width=True):
                st.session_state.query_input = prompt

    # Query input
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        query = st.text_input(
            "Query",
            value=st.session_state.query_input,
            placeholder="e.g., What are the top selling products by region?",
            label_visibility="collapsed",
            key="query_text"
        )
    with col_btn:
        analyze_clicked = st.button(
            "🚀 Analyze",
            use_container_width=True,
            disabled=st.session_state.is_loading
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Run Analysis ──
    if analyze_clicked and query:
        st.session_state.is_loading = True
        st.session_state.result = None
        st.session_state.node_log = []

        # Add to chat history
        st.session_state.chat_history.append({"query": query, "type": "user"})

        progress_placeholder = st.empty()

        with progress_placeholder.container():
            # Shimmer loading skeleton
            st.markdown("""
            <div class="glass-card" style="animation: fadeIn 0.3s ease;">
                <div class="section-label">🔄 Analyzing your data...</div>
                <div class="shimmer-line long"></div>
                <div class="shimmer-line medium"></div>
                <div class="shimmer-line short"></div>
                <div class="shimmer-line long"></div>
                <div class="shimmer-line medium"></div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("🚀 Running analysis pipeline..."):
                pipeline_steps = ["profiler", "planner", "generator", "executor", "insight"]
                step_labels = {
                    "profiler": "📋 Profiling data...",
                    "planner": "🗺️ Planning analysis...",
                    "generator": "💻 Generating code...",
                    "executor": "⚡ Executing analysis...",
                    "insight": "🧠 Generating insights...",
                }

                progress_bar = st.progress(0, text="Initializing pipeline...")

                try:
                    form_data = {
                        "filepath": st.session_state.file_data["filepath"],
                        "query": query,
                    }
                    resp = requests.post(f"{API_BASE}/api/analyze", data=form_data, timeout=300)
                    result = resp.json()

                    for i, step in enumerate(pipeline_steps):
                        progress_bar.progress(
                            (i + 1) / len(pipeline_steps),
                            text=step_labels.get(step, f"Completing {step}...")
                        )
                        time.sleep(0.15)

                    if result.get("node_log"):
                        st.session_state.node_log = result["node_log"]

                    st.session_state.result = result

                    # Add AI response to chat history
                    st.session_state.chat_history.append({
                        "type": "ai",
                        "insight": result.get("insight", ""),
                        "charts_count": len(result.get("charts", [])),
                    })

                except requests.exceptions.ConnectionError:
                    st.session_state.result = {
                        "success": False,
                        "error": "Cannot connect to API server. Make sure FastAPI is running on port 8000."
                    }
                except requests.exceptions.Timeout:
                    st.session_state.result = {
                        "success": False,
                        "error": "Analysis timed out. The query may be too complex."
                    }
                except Exception as e:
                    st.session_state.result = {
                        "success": False,
                        "error": str(e)
                    }

        st.session_state.is_loading = False
        progress_placeholder.empty()
        st.rerun()

    # ── Display Results ──
    if st.session_state.result:
        result = st.session_state.result

        # Show last query as chat bubble
        if st.session_state.chat_history:
            last_user = next((h for h in reversed(st.session_state.chat_history) if h["type"] == "user"), None)
            if last_user:
                st.markdown(f"""
                <div class="chat-user">
                    {last_user['query']}
                </div>
                """, unsafe_allow_html=True)

        # Error
        if result.get("error") and not result.get("insight"):
            st.markdown(f"""
            <div class="error-card">
                <div class="section-label" style="color: var(--error);">❌ Error</div>
                <div class="code-container">{result['error']}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Insight Panel ──
        if result.get("insight"):
            st.markdown(f"""
            <div class="insight-panel">
                <div class="insight-icon-badge">🧠 AI Insight</div>
                {result['insight']}
            </div>
            """, unsafe_allow_html=True)

        # ── Chart Gallery ──
        if result.get("charts"):
            st.markdown("""
            <div style="display:flex; align-items:center; gap:0.6rem; margin: 1.5rem 0 0.8rem;">
                <span class="query-tag" style="background: var(--gradient-cool);">📈 CHARTS</span>
                <span style="font-size:0.85rem; color:var(--text-secondary);">
                    Generated Visualizations
                </span>
            </div>
            """, unsafe_allow_html=True)

            chart_cols = st.columns(min(len(result["charts"]), 2))
            for idx, chart_url in enumerate(result["charts"]):
                with chart_cols[idx % 2]:
                    full_url = f"{API_BASE}{chart_url}"
                    chart_name = os.path.basename(chart_url).replace(".png", "").replace("_", " ").title()
                    st.markdown(f'<div class="chart-card">', unsafe_allow_html=True)
                    st.image(full_url, use_container_width=True)
                    st.markdown(f'<div class="chart-label">📊 {chart_name}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

        # ── Code Panel ──
        if result.get("code"):
            with st.expander("💻 Generated Python Code", expanded=False):
                st.code(result["code"], language="python")

        # ── Code Output ──
        if result.get("code_output"):
            with st.expander("📤 Execution Output", expanded=False):
                st.markdown(f'<div class="code-container">{result["code_output"]}</div>', unsafe_allow_html=True)

        # ── Analysis Plan ──
        if result.get("plan"):
            with st.expander("🗺️ Analysis Plan", expanded=False):
                plan = result["plan"]
                if isinstance(plan, list):
                    for i, step in enumerate(plan, 1):
                        st.markdown(f"**{i}.** {step}")
                else:
                    st.write(plan)

# ── Footer ──
st.markdown("""
<div class="footer-bar">
    Built with ❤️ using LangGraph, Groq &amp; Streamlit · Auto-Analyst AI v2.0
</div>
""", unsafe_allow_html=True)
