import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Apex Compound | Professional Trade Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# CUSTOM CSS / FINTECH DARK TERMINAL THEME
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Dark Terminal Backgrounds */
    .stApp {
        background-color: #0B0E14;
        color: #E0E6ED;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
    
    /* Top Header Bar */
    .terminal-header {
        border-left: 4px solid #00F0FF;
        padding: 8px 16px;
        background: linear-gradient(90deg, rgba(0, 240, 255, 0.08) 0%, rgba(11, 14, 20, 0) 100%);
        border-radius: 4px;
        margin-bottom: 20px;
    }

    /* Bento Stat Card */
    .metric-card {
        background: #151922;
        border: 1px solid #232936;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .metric-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8A94A6;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #FFFFFF;
    }
    .metric-sub {
        font-size: 0.8rem;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Primary Next-Trade Highlight Card */
    .hero-card {
        background: linear-gradient(145deg, #181E29, #131720);
        border: 1px solid #2C3545;
        border-top: 3px solid #00E676;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(0, 230, 118, 0.05);
    }
    
    /* Buttons Customization */
    div.stButton > button:first-child {
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.03em;
        transition: all 0.2s ease;
    }
    
    /* Win Button Hook */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(180deg, #00E676 0%, #00B359 100%) !important;
        border: none !important;
        color: #05140A !important;
        box-shadow: 0 4px 14px rgba(0, 230, 118, 0.3) !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: linear-gradient(180deg, #1AFF8A 0%, #00CC66 100%) !important;
        box-shadow: 0 6px 20px rgba(0, 230, 118, 0.5) !important;
    }
    
    /* Loss Button Hook */
    div[data-testid="stButton"] button[kind="secondary"] {
        background: linear-gradient(180deg, #FF1744 0%, #D50032 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(255, 23, 68, 0.3) !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        background: linear-gradient(180deg, #FF4569 0%, #E60039 100%) !important;
        box-shadow: 0 6px 20px rgba(255, 23, 68, 0.5) !important;
    }

    /* Subtle Table/Dataframe styling */
    .stDataFrame {
        border: 1px solid #232936;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
DEFAULT_CONFIG = {
    "initial_capital": 1000.0,
    "risk_pct": 2.0,
    "payout_pct": 85.0,
    "max_steps": 2,
    "currency_symbol": "$"
}

if "config" not in st.session_state:
    st.session_state.config = DEFAULT_CONFIG.copy()

if "capital" not in st.session_state:
    st.session_state.capital = float(st.session_state.config["initial_capital"])

if "current_step" not in st.session_state:
    st.session_state.current_step = 0

if "current_stake" not in st.session_state:
    st.session_state.current_stake = (
        st.session_state.capital * (st.session_state.config["risk_pct"] / 100.0)
    )

if "trade_history" not in st.session_state:
    st.session_state.trade_history = []

if "last_action_msg" not in st.session_state:
    st.session_state.last_action_msg = None

# ---------------------------------------------------------
# BUSINESS LOGIC & CALCULATION ENGINES
# ---------------------------------------------------------
def recalculate_current_stake():
    """Recalculates stake based on cycle step and current capital."""
    if st.session_state.current_step == 0:
        st.session_state.current_stake = round(
            st.session_state.capital * (st.session_state.config["risk_pct"] / 100.0), 2
        )

def execute_trade(is_win: bool):
    """Processes a trade outcome and shifts compounding cycles."""
    curr_stake = st.session_state.current_stake
    payout_rate = st.session_state.config["payout_pct"] / 100.0
    step = st.session_state.current_step
    max_steps = st.session_state.config["max_steps"]
    
    # Save snapshot for undo capability
    state_snapshot = {
        "capital": st.session_state.capital,
        "current_step": st.session_state.current_step,
        "current_stake": st.session_state.current_stake,
    }

    if is_win:
        profit = round(curr_stake * payout_rate, 2)
        total_return = round(curr_stake + profit, 2)
        new_balance = round(st.session_state.capital + profit, 2)
        
        record = {
            "Trade #": len(st.session_state.trade_history) + 1,
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Cycle Step": f"Step {step + 1}/{max_steps if max_steps > 0 else 'Flat'}",
            "Stake": curr_stake,
            "Result": "WIN",
            "Net P/L": profit,
            "Updated Balance": new_balance,
            "_snapshot": state_snapshot
        }
        st.session_state.trade_history.append(record)
        st.session_state.capital = new_balance

        # Compounding progression logic
        if max_steps > 0 and (step + 1) < max_steps:
            st.session_state.current_step += 1
            st.session_state.current_stake = total_return
            st.session_state.last_action_msg = ("WIN", f"Won +{st.session_state.config['currency_symbol']}{profit:.2f}! Compounding forward to Step {st.session_state.current_step + 1}.")
        else:
            st.session_state.current_step = 0
            recalculate_current_stake()
            cycle_note = "Cycle completed! Profit secured." if max_steps > 0 else "Trade won!"
            st.session_state.last_action_msg = ("WIN", f"{cycle_note} Resetting to base stake.")
            
    else:  # LOSS
        loss_amount = curr_stake
        new_balance = round(st.session_state.capital - loss_amount, 2)
        
        record = {
            "Trade #": len(st.session_state.trade_history) + 1,
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Cycle Step": f"Step {step + 1}/{max_steps if max_steps > 0 else 'Flat'}",
            "Stake": curr_stake,
            "Result": "LOSS",
            "Net P/L": -loss_amount,
            "Updated Balance": new_balance,
            "_snapshot": state_snapshot
        }
        st.session_state.trade_history.append(record)
        st.session_state.capital = new_balance
        
        # Reset cycle completely
        st.session_state.current_step = 0
        recalculate_current_stake()
        st.session_state.last_action_msg = ("LOSS", f"Loss incurred (-{st.session_state.config['currency_symbol']}{loss_amount:.2f}). Compounding reset to Step 1.")

def undo_last_trade():
    """Rolls back the latest trade state."""
    if not st.session_state.trade_history:
        return
    last_trade = st.session_state.trade_history.pop()
    snapshot = last_trade["_snapshot"]
    st.session_state.capital = snapshot["capital"]
    st.session_state.current_step = snapshot["current_step"]
    st.session_state.current_stake = snapshot["current_stake"]
    st.session_state.last_action_msg = ("INFO", f"Trade #{last_trade['Trade #']} undone.")

def full_reset():
    """Resets entire app to configured defaults."""
    st.session_state.capital = float(st.session_state.config["initial_capital"])
    st.session_state.current_step = 0
    recalculate_current_stake()
    st.session_state.trade_history = []
    st.session_state.last_action_msg = None

# ---------------------------------------------------------
# SIDEBAR / CONFIGURATION PANEL
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Risk Configuration")
    st.caption("Customize account risk and execution engine parameters.")
    
    currency = st.selectbox("Display Currency", options=["$", "৳", "€", "£", "₹"], index=0)
    st.session_state.config["currency_symbol"] = currency
    
    init_cap = st.number_input("Initial Capital", min_value=1.0, value=st.session_state.config["initial_capital"], step=50.0)
    risk_pct = st.slider("Risk Per Trade (Base %)", min_value=0.5, max_value=20.0, value=st.session_state.config["risk_pct"], step=0.5)
    payout_pct = st.slider("Payout Rate (%)", min_value=10.0, max_value=200.0, value=st.session_state.config["payout_pct"], step=1.0)
    
    step_options = {
        "Off (Flat Risk)": 0,
        "1-Step Compounding": 1,
        "2-Step Compounding": 2,
        "3-Step Compounding": 3,
        "4-Step Compounding": 4
    }
    
    current_step_label = [k for k, v in step_options.items() if v == st.session_state.config["max_steps"]][0]
    comp_mode = st.selectbox("Compounding Mode", options=list(step_options.keys()), index=list(step_options.keys()).index(current_step_label))
    selected_steps = step_options[comp_mode]

    if st.button("Apply Settings", use_container_width=True):
        st.session_state.config.update({
            "initial_capital": init_cap,
            "risk_pct": risk_pct,
            "payout_pct": payout_pct,
            "max_steps": selected_steps,
        })
        if len(st.session_state.trade_history) == 0:
            st.session_state.capital = init_cap
        recalculate_current_stake()
        st.toast("Settings updated successfully.", icon="✅")

    st.markdown("---")
    if st.button("Reset Entire Account", use_container_width=True):
        full_reset()
        st.rerun()

# ---------------------------------------------------------
# ANALYTICS CALCULATIONS
# ---------------------------------------------------------
curr_cap = st.session_state.capital
init_cap = st.session_state.config["initial_capital"]
net_roi = ((curr_cap - init_cap) / init_cap) * 100.0 if init_cap > 0 else 0.0

trades = st.session_state.trade_history
total_trades = len(trades)
wins = sum(1 for t in trades if t["Result"] == "WIN")
losses = sum(1 for t in trades if t["Result"] == "LOSS")
win_rate = (wins / total_trades * 100.0) if total_trades > 0 else 0.0

total_profit = sum(t["Net P/L"] for t in trades if t["Net P/L"] > 0)
total_loss = abs(sum(t["Net P/L"] for t in trades if t["Net P/L"] < 0))
profit_factor = (total_profit / total_loss) if total_loss > 0 else (total_profit if total_profit > 0 else 1.0)

# Calculate streaks and peak capital
current_streak_type = "None"
current_streak_count = 0
peak_capital = init_cap

if trades:
    balances = [init_cap] + [t["Updated Balance"] for t in trades]
    peak_capital = max(balances)
    
    last_res = trades[-1]["Result"]
    current_streak_type = last_res
    streak = 0
    for t in reversed(trades):
        if t["Result"] == last_res:
            streak += 1
        else:
            break
    current_streak_count = streak

# ---------------------------------------------------------
# DASHBOARD HEADER & TOP STATS BENTO-GRID
# ---------------------------------------------------------
sym = st.session_state.config["currency_symbol"]

st.markdown("""
<div class="terminal-header">
    <h2 style="margin:0; font-size: 1.5rem; font-weight:700; letter-spacing: -0.01em;">
        ⚡ APEX DYNAMIC COMPOUNDING ENGINE
    </h2>
    <span style="font-size:0.85rem; color:#8A94A6;">Institutional Money Management & Systematic Position Sizer</span>
</div>
""", unsafe_allow_html=True)

# Performance Cards
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    roi_color = "#00E676" if net_roi >= 0 else "#FF1744"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Account Equity</div>
        <div class="metric-value">{sym}{curr_cap:,.2f}</div>
        <div class="metric-sub" style="color:{roi_color};">ROI: {net_roi:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Win Rate</div>
        <div class="metric-value">{win_rate:.1f}%</div>
        <div class="metric-sub" style="color:#8A94A6;">{wins}W / {losses}L (Tot: {total_trades})</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Profit Factor</div>
        <div class="metric-value">{profit_factor:.2f}</div>
        <div class="metric-sub" style="color:#8A94A6;">W/L Ratio</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    streak_color = "#00E676" if current_streak_type == "WIN" else ("#FF1744" if current_streak_type == "LOSS" else "#8A94A6")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Active Streak</div>
        <div class="metric-value" style="color:{streak_color};">{current_streak_count} {current_streak_type}</div>
        <div class="metric-sub" style="color:#8A94A6;">Consecutive run</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Peak Capital</div>
        <div class="metric-value">{sym}{peak_capital:,.2f}</div>
        <div class="metric-sub" style="color:#8A94A6;">High-water mark</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# INTERACTIVE EXECUTION DESK & NEXT TRADE CARD
# ---------------------------------------------------------
col_left, col_right = st.columns([1.1, 1.9], gap="large")

with col_left:
    current_step_display = st.session_state.current_step + 1
    total_steps = st.session_state.config["max_steps"]
    step_str = f"Step {current_step_display} of {total_steps}" if total_steps > 0 else "Flat Risk Mode"
    
    recommended_stake = min(st.session_state.current_stake, st.session_state.capital)
    potential_profit = round(recommended_stake * (st.session_state.config["payout_pct"] / 100.0), 2)
    
    st.markdown(f"""
    <div class="hero-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span style="font-size:0.8rem; text-transform:uppercase; color:#00F0FF; font-weight:700; letter-spacing:0.05em;">
                Active Execution Matrix
            </span>
            <span style="background:rgba(0,240,255,0.12); color:#00F0FF; padding:4px 8px; border-radius:4px; font-size:0.75rem; font-weight:600;">
                {step_str}
            </span>
        </div>
        <div style="font-size:0.85rem; color:#8A94A6;">Recommended Position Stake</div>
        <div style="font-size:2.8rem; font-weight:800; color:#FFFFFF; margin: 2px 0 16px 0;">
            {sym}{recommended_stake:,.2f}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; padding-top:12px; border-top:1px solid #232936;">
            <div>
                <div style="font-size:0.75rem; color:#8A94A6;">Potential Return</div>
                <div style="color:#00E676; font-weight:700; font-size:1.1rem;">+{sym}{potential_profit:,.2f}</div>
            </div>
            <div>
                <div style="font-size:0.75rem; color:#8A94A6;">Risk-to-Capital</div>
                <div style="color:#E0E6ED; font-weight:700; font-size:1.1rem;">
                    {(recommended_stake / st.session_state.capital * 100.0) if st.session_state.capital > 0 else 0:.1f}%
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # Notification Banner
    if st.session_state.last_action_msg:
        status, msg = st.session_state.last_action_msg
        if status == "WIN":
            st.success(msg)
        elif status == "LOSS":
            st.error(msg)
        else:
            st.info(msg)
            
    # Instant Execution Buttons
    btn_win_col, btn_loss_col = st.columns(2)
    with btn_win_col:
        if st.button("WIN", type="primary", use_container_width=True):
            execute_trade(is_win=True)
            st.rerun()
            
    with btn_loss_col:
        if st.button("LOSS", type="secondary", use_container_width=True):
            execute_trade(is_win=False)
            st.rerun()
            
    if st.button("↩ Undo Last Trade", use_container_width=True):
        undo_last_trade()
        st.rerun()

# ---------------------------------------------------------
# EQUITY CURVE & GROWTH VISUALIZATION
# ---------------------------------------------------------
with col_right:
    # Compile Balance Trajectory
    plot_data = [{"Trade": 0, "Balance": init_cap, "Result": "START"}]
    for t in trades:
        plot_data.append({
            "Trade": t["Trade #"],
            "Balance": t["Updated Balance"],
            "Result": t["Result"]
        })
    df_plot = pd.DataFrame(plot_data)
    
    fig = go.Figure()
    
    # Base Capital Reference Line
    fig.add_hline(
        y=init_cap, 
        line_dash="dash", 
        line_color="#4A5568", 
        annotation_text="Base Capital", 
        annotation_position="bottom right"
    )
    
    # Equity Curve
    fig.add_trace(go.Scatter(
        x=df_plot["Trade"],
        y=df_plot["Balance"],
        mode="lines+markers",
        line=dict(color="#00F0FF", width=3, shape="spline"),
        marker=dict(
            size=7,
            color=["#8A94A6" if r == "START" else "#00E676" if r == "WIN" else "#FF1744" for r in df_plot["Result"]],
            line=dict(width=1, color="#FFFFFF")
        ),
        fill="tozeroy",
        fillcolor="rgba(0, 240, 255, 0.04)",
        name="Equity",
        hovertemplate="Trade #%{x}<br>Balance: " + sym + "%{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="Equity Progression Curve", font=dict(size=14, color="#E0E6ED")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#11141C",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
        xaxis=dict(
            title="Trade Number",
            showgrid=True,
            gridcolor="#1D2330",
            dtick=1 if len(df_plot) <= 15 else None,
            tickfont=dict(color="#8A94A6")
        ),
        yaxis=dict(
            title=f"Balance ({sym})",
            showgrid=True,
            gridcolor="#1D2330",
            tickprefix=sym,
            tickfont=dict(color="#8A94A6")
        ),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ---------------------------------------------------------
# AUDIT LOG / TRADE HISTORY TABLE
# ---------------------------------------------------------
st.markdown("---")
h_col1, h_col2 = st.columns([2, 1])

with h_col1:
    st.markdown("### 📋 Trade Execution Log")

with h_col2:
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.session_state.trade_history:
            df_export = pd.DataFrame(st.session_state.trade_history).drop(columns=["_snapshot"])
            csv_data = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export CSV",
                data=csv_data,
                file_name=f"apex_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    with c_btn2:
        if st.session_state.trade_history:
            if st.button("🗑️ Clear Log", use_container_width=True):
                st.session_state.trade_history = []
                st.rerun()

if st.session_state.trade_history:
    df_display = pd.DataFrame(st.session_state.trade_history).drop(columns=["_snapshot"])
    
    # Custom format styling function
    def style_rows(val):
        if val == "WIN":
            return 'color: #00E676; font-weight: 700;'
        elif val == "LOSS":
            return 'color: #FF1744; font-weight: 700;'
        return ''

    def style_pl(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return 'color: #00E676; font-weight: 600;'
            elif val < 0:
                return 'color: #FF1744; font-weight: 600;'
        return ''

    styled_df = (
        df_display.style
        .format({
            "Stake": f"{sym}{{:,.2f}}",
            "Net P/L": f"{sym}{{:,.2f}}",
            "Updated Balance": f"{sym}{{:,.2f}}"
        })
        .map(style_rows, subset=["Result"])
        .map(style_pl, subset=["Net P/L"])
    )
    
    st.dataframe(styled_df, use_container_width=True, height=260)
else:
    st.info("No trade history recorded yet. Execute your first trade using the Win / Loss buttons above.")
