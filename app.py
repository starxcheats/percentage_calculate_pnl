
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

DATA_FILE = Path("trading_settings.json")

st.set_page_config(
    page_title="TradeFlow Money Manager",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme / CSS ----------
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(88, 166, 255, .10), transparent 28%),
            radial-gradient(circle at 85% 0%, rgba(0, 220, 150, .08), transparent 25%),
            #07111f;
        color: #eaf2ff;
    }
    [data-testid="stSidebar"] {
        background: #091626;
        border-right: 1px solid rgba(255,255,255,.07);
    }
    .hero {
        padding: 26px 30px;
        border: 1px solid rgba(125,180,255,.16);
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(18,42,69,.95), rgba(8,25,43,.92));
        box-shadow: 0 18px 50px rgba(0,0,0,.22);
        margin-bottom: 20px;
    }
    .hero h1 { margin: 0; font-size: 34px; letter-spacing: -.8px; }
    .hero p { margin: 7px 0 0; color: #9fb4cc; }
    .card {
        padding: 18px 20px;
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 18px;
        background: rgba(12,28,47,.78);
        box-shadow: 0 10px 28px rgba(0,0,0,.14);
        min-height: 112px;
    }
    .label { color:#8da4bf; font-size:13px; text-transform:uppercase; letter-spacing:.8px; }
    .value { font-size:28px; font-weight:800; margin-top:7px; }
    .positive { color:#35d39a; }
    .negative { color:#ff6b7a; }
    .accent { color:#69a9ff; }
    .muted { color:#8da4bf; }
    .trade-row {
        padding: 12px 14px;
        margin: 8px 0;
        border-radius: 14px;
        background: #0b1a2c;
        border: 1px solid rgba(255,255,255,.06);
    }
    .small { font-size: 12px; color:#8da4bf; }
    div.stButton > button {
        border-radius: 12px;
        min-height: 44px;
        font-weight: 700;
    }
    .section-title { font-size:20px; font-weight:800; margin: 5px 0 14px; }
    .formula {
        padding: 14px 16px;
        border-radius: 14px;
        background: #081525;
        border: 1px dashed rgba(105,169,255,.25);
        color:#b8c9dc;
    }
</style>
""", unsafe_allow_html=True)

# ---------- State ----------
DEFAULT = {
    "initial_capital": 100.0,
    "risk_pct": 5.0,
    "win_return_pct": 85.0,
    "session_name": "My Trading Session",
    "trades": [],
}

def load_settings():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return DEFAULT.copy()

if "initialized" not in st.session_state:
    saved = load_settings()
    for k, v in saved.items():
        st.session_state[k] = v
    st.session_state.initialized = True

for k, v in DEFAULT.items():
    if k not in st.session_state:
        st.session_state[k] = v

def current_capital():
    return st.session_state.initial_capital + sum(t["pnl"] for t in st.session_state.trades)

def trade_amount():
    return current_capital() * st.session_state.risk_pct / 100

def save_all():
    payload = {k: st.session_state[k] for k in DEFAULT}
    DATA_FILE.write_text(json.dumps(payload, indent=2))

def clear_session():
    st.session_state.trades = []

def reset_all():
    st.session_state.initial_capital = DEFAULT["initial_capital"]
    st.session_state.risk_pct = DEFAULT["risk_pct"]
    st.session_state.win_return_pct = DEFAULT["win_return_pct"]
    st.session_state.session_name = DEFAULT["session_name"]
    st.session_state.trades = []

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ⚙️ Money Manager")
    st.caption("Dynamic % risk • live capital • trade journal")
    st.divider()

    st.session_state.session_name = st.text_input(
        "Session name", st.session_state.session_name
    )
    st.session_state.initial_capital = st.number_input(
        "Initial capital",
        min_value=0.01,
        value=float(st.session_state.initial_capital),
        step=10.0,
        format="%.2f",
    )
    st.session_state.risk_pct = st.number_input(
        "Per-trade %", min_value=0.01, max_value=100.0,
        value=float(st.session_state.risk_pct), step=0.5, format="%.2f"
    )
    st.session_state.win_return_pct = st.number_input(
        "Win return %", min_value=0.01, max_value=1000.0,
        value=float(st.session_state.win_return_pct), step=1.0, format="%.2f"
    )

    st.divider()
    if st.button("💾 Save Settings", use_container_width=True):
        save_all()
        st.success("Settings saved.")

    if st.button("🧹 Clear Trades", use_container_width=True):
        clear_session()
        st.rerun()

    if st.button("🔄 Full Reset", use_container_width=True):
        reset_all()
        save_all()
        st.rerun()

    st.divider()
    st.caption("Win: capital × risk% × return%")
    st.caption("Loss: capital × risk%")

# ---------- Header ----------
st.markdown(f"""
<div class="hero">
    <h1>📈 TradeFlow</h1>
    <p>{st.session_state.session_name} · Dynamic percentage money management dashboard</p>
</div>
""", unsafe_allow_html=True)

capital = current_capital()
amount = trade_amount()
wins = sum(t["result"] == "WIN" for t in st.session_state.trades)
losses = sum(t["result"] == "LOSS" for t in st.session_state.trades)
total = wins + losses
winrate = (wins / total * 100) if total else 0
net = capital - st.session_state.initial_capital

# ---------- KPI cards ----------
c1, c2, c3, c4, c5 = st.columns(5)
cards = [
    (c1, "Current Capital", f"{capital:,.2f}", "accent"),
    (c2, "Next Trade Size", f"{amount:,.2f}", "accent"),
    (c3, "Net P/L", f"{net:+,.2f}", "positive" if net >= 0 else "negative"),
    (c4, "Win Rate", f"{winrate:.1f}%", "positive" if winrate >= 50 else "negative"),
    (c5, "Trades", str(total), "accent"),
]
for col, label, value, cls in cards:
    with col:
        st.markdown(
            f'<div class="card"><div class="label">{label}</div>'
            f'<div class="value {cls}">{value}</div></div>',
            unsafe_allow_html=True
        )

st.write("")

# ---------- Trade controls ----------
left, right = st.columns([1.35, 1])
with left:
    st.markdown('<div class="section-title">🎯 Next Trade</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="formula">'
        f'<b>Live calculation:</b> {capital:,.2f} × {st.session_state.risk_pct:.2f}% '
        f'= <b>{amount:,.2f}</b> risk amount. '
        f'Each new trade uses the <b>updated capital</b>, not the initial capital.'
        f'</div>', unsafe_allow_html=True
    )
    st.write("")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("✅ WIN", use_container_width=True, type="primary"):
            pnl = amount * st.session_state.win_return_pct / 100
            before = capital
            after = before + pnl
            st.session_state.trades.append({
                "trade": len(st.session_state.trades) + 1,
                "time": datetime.now().strftime("%H:%M:%S"),
                "result": "WIN",
                "capital_before": before,
                "amount": amount,
                "pnl": pnl,
                "capital_after": after,
            })
            st.rerun()
    with b2:
        if st.button("❌ LOSS", use_container_width=True):
            pnl = -amount
            before = capital
            after = before + pnl
            st.session_state.trades.append({
                "trade": len(st.session_state.trades) + 1,
                "time": datetime.now().strftime("%H:%M:%S"),
                "result": "LOSS",
                "capital_before": before,
                "amount": amount,
                "pnl": pnl,
                "capital_after": after,
            })
            st.rerun()

with right:
    st.markdown('<div class="section-title">📊 Session Stats</div>', unsafe_allow_html=True)
    avg = (net / total) if total else 0
    st.markdown(f"""
    <div class="card">
      <div class="label">Initial Capital</div><div class="value">{st.session_state.initial_capital:,.2f}</div>
      <hr style="border-color:rgba(255,255,255,.06)">
      <div class="label">Wins / Losses</div><div style="font-size:22px;font-weight:800">
        <span class="positive">{wins}</span> / <span class="negative">{losses}</span>
      </div>
      <div class="small" style="margin-top:12px">Average P/L per trade: {avg:+,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Trade history ----------
st.write("")
st.markdown('<div class="section-title">📜 Trade History</div>', unsafe_allow_html=True)

if not st.session_state.trades:
    st.info("No trades yet. Set your rules on the left, then press WIN or LOSS.")
else:
    for t in reversed(st.session_state.trades):
        cls = "positive" if t["result"] == "WIN" else "negative"
        icon = "🟢" if t["result"] == "WIN" else "🔴"
        st.markdown(f"""
        <div class="trade-row">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div><b>Trade #{t["trade"]}</b> &nbsp; {icon} <span class="{cls}"><b>{t["result"]}</b></span>
              <span class="small"> · {t["time"]}</span></div>
            <div class="{cls}" style="font-size:18px;font-weight:800">{t["pnl"]:+,.2f}</div>
          </div>
          <div class="small" style="margin-top:7px">
            Before: {t["capital_before"]:,.2f} &nbsp;•&nbsp;
            Trade amount: {t["amount"]:,.2f} &nbsp;•&nbsp;
            After: <b>{t["capital_after"]:,.2f}</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ---------- Footer ----------
st.divider()
st.caption(
    "TradeFlow calculates every next trade from the latest updated capital. "
    "Example: 100 → 5% trade → LOSS = 95 → next 5% = 4.75."
)
