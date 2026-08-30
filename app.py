import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TradeMaster - Money Management",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (HIGH-END TRADING TERMINAL UI) ---
st.markdown("""
<style>
    .main { background-color: #0d1117; color: #f0f6fc; }
    .stMetric {
        background: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .trade-card {
        background: linear-gradient(145deg, #1c2128, #161b22);
        padding: 24px;
        border-radius: 14px;
        border: 1px solid #388bfd;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }
    div[data-testid="stButton"] > button:first-child {
        border-radius: 8px;
        font-weight: 700;
        font-size: 16px;
        height: 50px;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "capital" not in st.session_state:
    st.session_state.initial_capital = 1000.0
    st.session_state.capital = 1000.0
    st.session_state.risk_percent = 2.0
    st.session_state.payout_percent = 85.0
    st.session_state.compounding_steps = 1
    st.session_state.current_step = 0
    st.session_state.history = []
    st.session_state.current_stake = 20.0

# --- HELPER: CALCULATE CURRENT STAKE ---
def update_stake():
    base_stake = round(st.session_state.capital * (st.session_state.risk_percent / 100.0), 2)
    if st.session_state.current_step == 0:
        st.session_state.current_stake = max(base_stake, 1.0)

# --- TRADE PROCESSING HANDLERS ---
def handle_trade(is_win):
    stake = st.session_state.current_stake
    payout_rate = st.session_state.payout_percent / 100.0
    
    if is_win:
        profit = round(stake * payout_rate, 2)
        total_return = round(stake + profit, 2)
        st.session_state.capital = round(st.session_state.capital + profit, 2)
        result_text = "WIN"
        
        # Compounding logic check
        if st.session_state.compounding_steps > 0:
            if st.session_state.current_step < st.session_state.compounding_steps:
                st.session_state.current_step += 1
                # Next trade stake will be full returned amount (Stake + Profit)
                st.session_state.current_stake = total_return
            else:
                # Cycle Completed! Reset to base
                st.session_state.current_step = 0
                update_stake()
        else:
            st.session_state.current_step = 0
            update_stake()
    else:
        # LOSS
        loss_amount = stake
        st.session_state.capital = round(st.session_state.capital - loss_amount, 2)
        profit = -loss_amount
        result_text = "LOSS"
        
        # Loss breaks compounding cycle immediately
        st.session_state.current_step = 0
        update_stake()

    # Record trade history
    st.session_state.history.append({
        "Trade #": len(st.session_state.history) + 1,
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Step": f"Step {st.session_state.current_step if is_win and st.session_state.current_step > 0 else 'Base'}",
        "Stake ($)": stake,
        "Result": result_text,
        "P/L ($)": profit,
        "Balance ($)": st.session_state.capital
    })

def reset_all():
    st.session_state.capital = st.session_state.initial_capital
    st.session_state.current_step = 0
    st.session_state.history = []
    update_stake()

def clear_history():
    st.session_state.history = []
    st.session_state.current_step = 0
    update_stake()

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.title("⚙️ Settings")
    
    init_cap = st.number_input("Initial Capital ($)", min_value=10.0, max_value=1000000.0, value=st.session_state.initial_capital, step=50.0)
    risk_pct = st.slider("Risk Per Trade (%)", min_value=0.5, max_value=20.0, value=st.session_state.risk_percent, step=0.5)
    payout_pct = st.number_input("Broker Payout Rate (%)", min_value=10.0, max_value=100.0, value=st.session_state.payout_percent, step=1.0)
    
    comp_steps = st.selectbox(
        "Compounding Cycle",
        options=[0, 1, 2, 3, 4],
        format_func=lambda x: "Off (Flat Risk)" if x == 0 else f"{x}-Step Compounding",
        index=1
    )
    
    if st.button("💾 Apply & Save Settings", use_container_width=True):
        st.session_state.initial_capital = init_cap
        st.session_state.risk_percent = risk_pct
        st.session_state.payout_percent = payout_pct
        st.session_state.compounding_steps = comp_steps
        if not st.session_state.history:
            st.session_state.capital = init_cap
        update_stake()
        st.success("Settings updated!")

    st.markdown("---")
    if st.button("🔄 Reset All to Default", use_container_width=True):
        reset_all()
        st.rerun()

# Ensure stake is synchronized
if len(st.session_state.history) == 0 and st.session_state.current_step == 0:
    update_stake()

# --- MAIN DASHBOARD ---
st.title("📊 Precision Trade & Compounding Manager")

# 1. Top Metrics Bar
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
total_trades = len(st.session_state.history)
wins = sum(1 for t in st.session_state.history if t["Result"] == "WIN")
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
net_roi = ((st.session_state.capital - st.session_state.initial_capital) / st.session_state.initial_capital) * 100

col_m1.metric("Current Balance", f"${st.session_state.capital:,.2f}", f"{net_roi:+.2f}% ROI")
col_m2.metric("Total Trades", total_trades)
col_m3.metric("Win Rate", f"{win_rate:.1f}%", f"{wins}W / {total_trades - wins}L")
col_m4.metric("Active Cycle Step", f"Step {st.session_state.current_step}/{st.session_state.compounding_steps}")

st.markdown("<br>", unsafe_allow_html=True)

# 2. Next Trade Execution Card
with st.container():
    st.markdown(f"""
    <div class="trade-card">
        <h3 style="margin-top:0; color:#58a6ff;">🎯 Next Trade Execution</h3>
        <div style="display: flex; gap: 30px; font-size: 18px;">
            <div>Next Stake: <strong style="font-size:24px; color:#f0f6fc;">${st.session_state.current_stake:,.2f}</strong></div>
            <div>Expected Profit: <strong style="font-size:24px; color:#3fb950;">+${(st.session_state.current_stake * (st.session_state.payout_percent/100)):,.2f}</strong></div>
            <div>Mode: <span style="color:#e3b341;">{'Base Trade' if st.session_state.current_step == 0 else f'Compounding (Step {st.session_state.current_step})'}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 1])

with btn_col1:
    if st.button("✅ WIN", use_container_width=True, type="primary"):
        handle_trade(is_win=True)
        st.rerun()

with btn_col2:
    if st.button("❌ LOSS", use_container_width=True):
        handle_trade(is_win=False)
        st.rerun()

with btn_col3:
    if st.button("🗑️ Clear Log", use_container_width=True):
        clear_history()
        st.rerun()

# 3. Chart & Trade History
if st.session_state.history:
    st.markdown("### 📈 Equity Progression")
    df = pd.DataFrame(st.session_state.history)
    
    # Plotly Equity Chart
    fig = go.Figure()
    balances = [st.session_state.initial_capital] + df["Balance ($)"].tolist()
    fig.add_trace(go.Scatter(
        y=balances,
        mode="lines+markers",
        name="Balance",
        line=dict(color="#2ea043", width=3),
        marker=dict(size=6, color="#58a6ff")
    ))
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=20, b=20),
        height=280,
        xaxis_title="Trade Count",
        yaxis_title="Balance ($)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📜 Trade Log")
    st.dataframe(df.iloc[::-1], use_container_width=True)
else:
    st.info("💡 নো ট্রেড হিস্ট্রি। ট্রেড শুরু করতে উপরে 'WIN' বা 'LOSS' বাটনে ক্লিক করুন।")
