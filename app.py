import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import json

# ============================================================
# PAGE CONFIG & GLOBAL STYLING
# ============================================================
st.set_page_config(
    page_title="Trading Money Management & Dynamic Compounding Calculator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Premium Dark Trading Terminal
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1A1C23;
        border-right: 1px solid #2A2D3A;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #00E676 !important;
    }
    
    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #1A1C23, #16181F);
        border: 1px solid #2A2D3A;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    
    div[data-testid="stMetric"] label {
        color: #8B8D97 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    
    /* Positive / Negative delta */
    div[data-testid="stMetricDelta"] svg {
        display: none;
    }
    
    /* Primary buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
        border: none;
    }
    
    /* WIN button */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button {
        background: linear-gradient(135deg, #00C853, #00E676) !important;
        color: #0E1117 !important;
        font-size: 1.15rem !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0, 230, 118, 0.35);
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 230, 118, 0.5);
    }
    
    /* LOSS button */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button {
        background: linear-gradient(135deg, #D50000, #FF1744) !important;
        color: #FFFFFF !important;
        font-size: 1.15rem !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 15px rgba(255, 23, 68, 0.35);
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 23, 68, 0.5);
    }
    
    /* Undo / secondary buttons */
    .stButton > button[kind="secondary"] {
        background: #2A2D3A !important;
        color: #E0E0E0 !important;
        border: 1px solid #3A3D4A !important;
    }
    
    /* Next Trade Card */
    .next-trade-card {
        background: linear-gradient(145deg, #1A1C23, #12141A);
        border: 1px solid #00E67633;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 230, 118, 0.08);
        position: relative;
        overflow: hidden;
    }
    .next-trade-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00E676, #00B0FF);
    }
    
    .next-trade-title {
        color: #8B8D97;
        font-size: 0.9rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .next-trade-value {
        color: #FFFFFF;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 4px 0;
    }
    
    .next-trade-sub {
        color: #00E676;
        font-size: 1.05rem;
        font-weight: 500;
    }
    
    .step-badge {
        display: inline-block;
        background: #00E67622;
        color: #00E676;
        border: 1px solid #00E67655;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    
    /* Section headers */
    .section-header {
        color: #FFFFFF;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 8px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #2A2D3A;
    }
    
    /* Feedback flash */
    .win-flash {
        background: linear-gradient(90deg, #00E67622, transparent);
        border-left: 4px solid #00E676;
        padding: 12px 18px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
        color: #00E676;
        font-weight: 600;
    }
    .loss-flash {
        background: linear-gradient(90deg, #FF174422, transparent);
        border-left: 4px solid #FF1744;
        padding: 12px 18px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
        color: #FF1744;
        font-weight: 600;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Input fields */
    .stNumberInput input, .stSelectbox select {
        background-color: #1A1C23 !important;
        color: #E0E0E0 !important;
        border: 1px solid #2A2D3A !important;
        border-radius: 8px !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Divider */
    hr {
        border-color: #2A2D3A !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
def init_session_state():
    defaults = {
        "initial_capital": 1000.0,
        "risk_pct": 2.0,
        "payout_pct": 85.0,
        "compound_steps": 2,          # 0 = Off (Flat)
        "current_capital": 1000.0,
        "peak_capital": 1000.0,
        "current_step": 0,            # 0-based inside cycle
        "trade_history": [],
        "equity_curve": [1000.0],
        "total_wins": 0,
        "total_losses": 0,
        "current_streak": 0,          # positive = win streak, negative = loss streak
        "last_action": None,          # "WIN" / "LOSS" / None
        "last_pl": 0.0,
        "settings_saved": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ============================================================
# CORE BUSINESS LOGIC
# ============================================================
def calculate_base_stake(capital: float, risk_pct: float) -> float:
    return round(capital * (risk_pct / 100.0), 2)

def get_current_stake() -> float:
    """Return the stake that should be used for the next trade."""
    if st.session_state.compound_steps == 0 or st.session_state.current_step == 0:
        return calculate_base_stake(st.session_state.current_capital, st.session_state.risk_pct)
    
    # In compounding mode and mid-cycle → stake is previous full return
    # We store the "pending_stake" when we win mid-cycle
    return st.session_state.get("pending_stake", 
                                calculate_base_stake(st.session_state.current_capital, st.session_state.risk_pct))

def process_win():
    stake = get_current_stake()
    payout = st.session_state.payout_pct / 100.0
    profit = round(stake * payout, 2)
    total_return = round(stake + profit, 2)
    
    max_steps = st.session_state.compound_steps
    
    # Record trade
    trade = {
        "trade_no": len(st.session_state.trade_history) + 1,
        "cycle_step": st.session_state.current_step + 1 if max_steps > 0 else 0,
        "stake": stake,
        "result": "WIN",
        "net_pl": profit,
        "balance": 0.0,  # will set below
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if max_steps == 0:
        # Flat risk – always add profit to capital
        st.session_state.current_capital = round(st.session_state.current_capital + profit, 2)
        st.session_state.current_step = 0
        st.session_state.pending_stake = None
    else:
        # Compounding active
        if st.session_state.current_step + 1 >= max_steps:
            # Cycle complete → lock full profit into capital, reset
            st.session_state.current_capital = round(st.session_state.current_capital + profit, 2)
            # Note: the original stake was already "at risk" from capital perspective
            # but because we compound the return, the net addition is just the profit
            # (the stake itself was never removed until a loss)
            st.session_state.current_step = 0
            st.session_state.pending_stake = None
        else:
            # Mid-cycle win → do NOT add to capital yet; next stake = full return
            st.session_state.current_step += 1
            st.session_state.pending_stake = total_return
            # Capital remains the same until cycle finishes or a loss occurs
    
    trade["balance"] = st.session_state.current_capital
    st.session_state.trade_history.append(trade)
    
    # Update stats
    st.session_state.total_wins += 1
    if st.session_state.current_streak >= 0:
        st.session_state.current_streak += 1
    else:
        st.session_state.current_streak = 1
    
    st.session_state.peak_capital = max(st.session_state.peak_capital, st.session_state.current_capital)
    st.session_state.equity_curve.append(st.session_state.current_capital)
    st.session_state.last_action = "WIN"
    st.session_state.last_pl = profit

def process_loss():
    stake = get_current_stake()
    
    # On loss the stake is deducted from capital
    st.session_state.current_capital = round(st.session_state.current_capital - stake, 2)
    
    trade = {
        "trade_no": len(st.session_state.trade_history) + 1,
        "cycle_step": st.session_state.current_step + 1 if st.session_state.compound_steps > 0 else 0,
        "stake": stake,
        "result": "LOSS",
        "net_pl": -stake,
        "balance": st.session_state.current_capital,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.trade_history.append(trade)
    
    # Reset compounding cycle
    st.session_state.current_step = 0
    st.session_state.pending_stake = None
    
    # Stats
    st.session_state.total_losses += 1
    if st.session_state.current_streak <= 0:
        st.session_state.current_streak -= 1
    else:
        st.session_state.current_streak = -1
    
    st.session_state.equity_curve.append(st.session_state.current_capital)
    st.session_state.last_action = "LOSS"
    st.session_state.last_pl = -stake

def undo_last_trade():
    if not st.session_state.trade_history:
        return
    
    last = st.session_state.trade_history.pop()
    
    # Revert capital
    st.session_state.current_capital = round(st.session_state.current_capital - last["net_pl"], 2)
    
    # Revert stats
    if last["result"] == "WIN":
        st.session_state.total_wins = max(0, st.session_state.total_wins - 1)
    else:
        st.session_state.total_losses = max(0, st.session_state.total_losses - 1)
    
    # Revert equity curve
    if len(st.session_state.equity_curve) > 1:
        st.session_state.equity_curve.pop()
    
    # Recalculate peak
    st.session_state.peak_capital = max(st.session_state.equity_curve) if st.session_state.equity_curve else st.session_state.initial_capital
    
    # Reset step / pending (simple conservative approach)
    st.session_state.current_step = 0
    st.session_state.pending_stake = None
    st.session_state.current_streak = 0
    st.session_state.last_action = None
    st.session_state.last_pl = 0.0

def full_reset():
    init_cap = st.session_state.initial_capital
    risk = st.session_state.risk_pct
    payout = st.session_state.payout_pct
    steps = st.session_state.compound_steps
    
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    init_session_state()
    st.session_state.initial_capital = init_cap
    st.session_state.current_capital = init_cap
    st.session_state.peak_capital = init_cap
    st.session_state.risk_pct = risk
    st.session_state.payout_pct = payout
    st.session_state.compound_steps = steps
    st.session_state.equity_curve = [init_cap]

def clear_history():
    st.session_state.trade_history = []
    st.session_state.equity_curve = [st.session_state.current_capital]
    st.session_state.total_wins = 0
    st.session_state.total_losses = 0
    st.session_state.current_streak = 0
    st.session_state.last_action = None
    st.session_state.current_step = 0
    st.session_state.pending_stake = None

# ============================================================
# SIDEBAR – SETTINGS
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Capital & Risk Config")
    st.markdown("---")
    
    init_cap = st.number_input(
        "Initial Capital ($)",
        min_value=10.0,
        max_value=1_000_000.0,
        value=float(st.session_state.initial_capital),
        step=100.0,
        format="%.2f"
    )
    
    risk = st.number_input(
        "Risk per Trade (%)",
        min_value=0.1,
        max_value=20.0,
        value=float(st.session_state.risk_pct),
        step=0.1,
        format="%.1f"
    )
    
    payout = st.number_input(
        "Payout Rate (%)",
        min_value=10.0,
        max_value=200.0,
        value=float(st.session_state.payout_pct),
        step=1.0,
        format="%.1f",
        help="Typical binary options: 70-95%. Custom risk-reward also supported."
    )
    
    st.markdown("### Compounding Engine")
    compound_options = {
        "Off (Flat Risk)": 0,
        "1-Step Compounding": 1,
        "2-Step Compounding": 2,
        "3-Step Compounding": 3,
        "4-Step Compounding": 4,
        "5-Step Compounding": 5,
    }
    # Reverse lookup for current value
    current_label = next((k for k, v in compound_options.items() if v == st.session_state.compound_steps), "2-Step Compounding")
    selected_label = st.selectbox(
        "Compounding Steps",
        options=list(compound_options.keys()),
        index=list(compound_options.keys()).index(current_label)
    )
    selected_steps = compound_options[selected_label]
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("💾 Save Settings", use_container_width=True):
            st.session_state.initial_capital = init_cap
            st.session_state.risk_pct = risk
            st.session_state.payout_pct = payout
            st.session_state.compound_steps = selected_steps
            
            # If no trades yet, also reset current capital
            if len(st.session_state.trade_history) == 0:
                st.session_state.current_capital = init_cap
                st.session_state.peak_capital = init_cap
                st.session_state.equity_curve = [init_cap]
            
            st.session_state.settings_saved = True
            st.rerun()
    
    with col_s2:
        if st.button("↺ Defaults", use_container_width=True):
            st.session_state.initial_capital = 1000.0
            st.session_state.risk_pct = 2.0
            st.session_state.payout_pct = 85.0
            st.session_state.compound_steps = 2
            if len(st.session_state.trade_history) == 0:
                st.session_state.current_capital = 1000.0
                st.session_state.peak_capital = 1000.0
                st.session_state.equity_curve = [1000.0]
            st.rerun()
    
    if st.session_state.settings_saved:
        st.success("Settings saved ✓")
        st.session_state.settings_saved = False
    
    st.markdown("---")
    st.markdown("### 📖 How Compounding Works")
    st.caption("""
**Step 0**: Base stake = Capital × Risk%  
**On WIN** (mid-cycle): Next stake = previous Stake + Profit  
**On WIN** (final step): Profit locked into capital, cycle resets  
**On LOSS**: Stake deducted, cycle immediately resets to Step 0
    """)

# ============================================================
# MAIN DASHBOARD
# ============================================================
st.markdown("# 📈 Trading Money Management")
st.markdown("##### Dynamic Compounding Calculator · Risk Engine")

# ---- Performance Metrics ----
total_trades = st.session_state.total_wins + st.session_state.total_losses
win_rate = (st.session_state.total_wins / total_trades * 100) if total_trades > 0 else 0.0
net_roi = ((st.session_state.current_capital - st.session_state.initial_capital) / st.session_state.initial_capital * 100) if st.session_state.initial_capital > 0 else 0.0

# Profit Factor
gross_profit = sum(t["net_pl"] for t in st.session_state.trade_history if t["net_pl"] > 0)
gross_loss = abs(sum(t["net_pl"] for t in st.session_state.trade_history if t["net_pl"] < 0))
profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0.0)

streak_display = f"+{st.session_state.current_streak}" if st.session_state.current_streak > 0 else str(st.session_state.current_streak)
if st.session_state.current_streak == 0:
    streak_display = "—"

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Current Balance", f"${st.session_state.current_capital:,.2f}", f"{net_roi:+.2f}% ROI")
m2.metric("Total Trades", f"{total_trades}")
m3.metric("Win Rate", f"{win_rate:.1f}%")
m4.metric("Wins / Losses", f"{st.session_state.total_wins} / {st.session_state.total_losses}")
m5.metric("Current Streak", streak_display)
m6.metric("Profit Factor", f"{profit_factor:.2f}", f"Peak ${st.session_state.peak_capital:,.2f}")

st.markdown("")

# ---- Next Trade Card + Action Buttons ----
left_col, right_col = st.columns([1.4, 1])

with left_col:
    stake = get_current_stake()
    potential_profit = round(stake * (st.session_state.payout_pct / 100.0), 2)
    
    step_text = "Flat Risk (No Compounding)"
    if st.session_state.compound_steps > 0:
        step_text = f"Step {st.session_state.current_step + 1} of {st.session_state.compound_steps}"
    
    st.markdown(f"""
    <div class="next-trade-card">
        <div class="step-badge">{step_text}</div>
        <div class="next-trade-title">RECOMMENDED STAKE</div>
        <div class="next-trade-value">${stake:,.2f}</div>
        <div class="next-trade-sub">Potential Profit on Win → +${potential_profit:,.2f}</div>
        <div style="margin-top:14px; color:#8B8D97; font-size:0.9rem;">
            Current Capital: <strong style="color:#fff;">${st.session_state.current_capital:,.2f}</strong>
            &nbsp;&nbsp;|&nbsp;&nbsp; Risk: <strong style="color:#fff;">{st.session_state.risk_pct}%</strong>
            &nbsp;&nbsp;|&nbsp;&nbsp; Payout: <strong style="color:#fff;">{st.session_state.payout_pct}%</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    b1, b2, b3 = st.columns([1, 1, 1])
    with b1:
        if st.button("🟢  WIN", use_container_width=True, key="win_btn"):
            if st.session_state.current_capital <= 0:
                st.error("Insufficient capital.")
            else:
                process_win()
                st.rerun()
    with b2:
        if st.button("🔴  LOSS", use_container_width=True, key="loss_btn"):
            if st.session_state.current_capital <= 0:
                st.error("Insufficient capital.")
            else:
                process_loss()
                st.rerun()
    with b3:
        if st.button("↩ Undo Last", use_container_width=True, key="undo_btn"):
            undo_last_trade()
            st.rerun()
    
    # Visual feedback
    if st.session_state.last_action == "WIN":
        st.markdown(f'<div class="win-flash">✓ WIN recorded · +${st.session_state.last_pl:,.2f}</div>', unsafe_allow_html=True)
    elif st.session_state.last_action == "LOSS":
        st.markdown(f'<div class="loss-flash">✗ LOSS recorded · ${st.session_state.last_pl:,.2f}</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-header">Equity Curve</div>', unsafe_allow_html=True)
    
    eq = st.session_state.equity_curve
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(eq))),
        y=eq,
        mode="lines+markers",
        line=dict(color="#00E676", width=2.5),
        marker=dict(size=5, color="#00E676"),
        fill="tozeroy",
        fillcolor="rgba(0, 230, 118, 0.08)",
        name="Capital"
    ))
    
    # Peak marker
    if len(eq) > 1:
        peak_idx = eq.index(max(eq))
        fig.add_trace(go.Scatter(
            x=[peak_idx],
            y=[eq[peak_idx]],
            mode="markers",
            marker=dict(size=10, color="#00B0FF", symbol="diamond"),
            name="Peak"
        ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=30),
        height=280,
        xaxis=dict(
            title="Trade #",
            gridcolor="#2A2D3A",
            zerolinecolor="#2A2D3A",
            color="#8B8D97"
        ),
        yaxis=dict(
            title="Capital ($)",
            gridcolor="#2A2D3A",
            zerolinecolor="#2A2D3A",
            color="#8B8D97",
            tickprefix="$"
        ),
        legend=dict(font=dict(color="#8B8D97"), bgcolor="rgba(0,0,0,0)"),
        font=dict(color="#E0E0E0")
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- Trade History ----
st.markdown('<div class="section-header">Trade History</div>', unsafe_allow_html=True)

if st.session_state.trade_history:
    df = pd.DataFrame(st.session_state.trade_history)
    df = df.rename(columns={
        "trade_no": "Trade #",
        "cycle_step": "Cycle Step",
        "stake": "Stake ($)",
        "result": "Result",
        "net_pl": "Net P/L ($)",
        "balance": "Balance ($)",
        "timestamp": "Timestamp"
    })
    
    # Color the Result column via Styler
    def color_result(val):
        if val == "WIN":
            return "color: #00E676; font-weight: 600"
        elif val == "LOSS":
            return "color: #FF1744; font-weight: 600"
        return ""
    
    styled = df.style.map(color_result, subset=["Result"]).format({
        "Stake ($)": "{:.2f}",
        "Net P/L ($)": "{:+.2f}",
        "Balance ($)": "{:.2f}"
    })
    
    st.dataframe(styled, use_container_width=True, height=320)
    
    # Export / Clear controls
    c1, c2, c3, _ = st.columns([1, 1, 1, 3])
    with c1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Export CSV",
            data=csv,
            file_name=f"trade_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        if st.button("🗑️ Clear History", use_container_width=True):
            clear_history()
            st.rerun()
    with c3:
        if st.button("🔄 Full Reset", use_container_width=True):
            full_reset()
            st.rerun()
else:
    st.info("No trades yet. Configure your risk settings and click **WIN** or **LOSS** to begin.")

# Footer
st.markdown("---")
st.caption("Trading Money Management & Dynamic Compounding Calculator · Risk carefully · Past performance ≠ future results")
