import json
from pathlib import Path
from datetime import datetime
import streamlit as st

st.set_page_config(page_title='TradeFlow Money Manager', page_icon='📈', layout='wide')
DATA=Path('trading_settings.json')
DEFAULT={'initial_capital':100.0,'risk_pct':5.0,'win_return_pct':85.0,'compounding_steps':1,'session_name':'My Trading Session','trades':[]}

def load():
    try: return json.loads(DATA.read_text())
    except: return DEFAULT.copy()
if 'ready' not in st.session_state:
    saved=load(); st.session_state.update(saved); st.session_state.cycle_step=0; st.session_state.ready=True

def capital(): return st.session_state.initial_capital+sum(x['pnl'] for x in st.session_state.trades)
def base_stake(): return capital()*st.session_state.risk_pct/100
def stake():
    base=base_stake(); step=st.session_state.cycle_step
    if step==0 or not st.session_state.trades or st.session_state.trades[-1]['result']!='WIN': return base
    last=st.session_state.trades[-1]
    return min(capital(), last['amount']+last['pnl'])
def save(): DATA.write_text(json.dumps({k:st.session_state[k] for k in DEFAULT},indent=2))
def clear(): st.session_state.trades=[]; st.session_state.cycle_step=0
def reset():
    for k,v in DEFAULT.items(): st.session_state[k]=v
    st.session_state.cycle_step=0

st.markdown('''<style>
.stApp{background:radial-gradient(circle at 15% 10%,rgba(88,166,255,.10),transparent 28%),radial-gradient(circle at 85% 0%,rgba(0,220,150,.08),transparent 25%),#07111f;color:#eaf2ff}
[data-testid="stSidebar"]{background:#091626}
.hero,.card{border:1px solid rgba(255,255,255,.08);border-radius:20px;background:rgba(12,28,47,.82);box-shadow:0 14px 40px rgba(0,0,0,.18)}
.hero{padding:26px 30px;margin-bottom:20px}.hero h1{margin:0;font-size:34px}.hero p{color:#9fb4cc}.card{padding:17px;min-height:105px}.label{color:#8da4bf;font-size:12px;text-transform:uppercase;letter-spacing:.8px}.value{font-size:25px;font-weight:800;margin-top:7px}.pos{color:#35d39a}.neg{color:#ff6b7a}.acc{color:#69a9ff}.trade{padding:12px 15px;margin:7px 0;border-radius:14px;background:#0b1a2c;border:1px solid rgba(255,255,255,.06)}
</style>''',unsafe_allow_html=True)

with st.sidebar:
    st.markdown('## ⚙️ Money Manager')
    st.session_state.session_name=st.text_input('Session name',st.session_state.session_name)
    st.session_state.initial_capital=st.number_input('Initial capital',min_value=.01,value=float(st.session_state.initial_capital),step=10.)
    st.session_state.risk_pct=st.number_input('Per-trade %',min_value=.01,max_value=100.,value=float(st.session_state.risk_pct),step=.5)
    st.session_state.win_return_pct=st.number_input('Win return %',min_value=.01,max_value=1000.,value=float(st.session_state.win_return_pct),step=1.)
    opts=[1,2,3,4,5,10]
    st.session_state.compounding_steps=st.selectbox('Compounding steps',opts,index=opts.index(int(st.session_state.compounding_steps)),format_func=lambda x:f'{x}-Step Compounding')
    st.divider()
    if st.button('💾 Save Settings',use_container_width=True): save(); st.success('Settings saved')
    if st.button('🧹 Clear Trades',use_container_width=True): clear(); st.rerun()
    if st.button('🔄 Full Reset',use_container_width=True): reset(); save(); st.rerun()

cap=capital(); amt=stake(); wins=sum(x['result']=='WIN' for x in st.session_state.trades); losses=sum(x['result']=='LOSS' for x in st.session_state.trades); total=wins+losses; wr=wins/total*100 if total else 0; net=cap-st.session_state.initial_capital
st.markdown(f'<div class="hero"><h1>📈 TradeFlow</h1><p>{st.session_state.session_name} · Dynamic percentage + step compounding</p></div>',unsafe_allow_html=True)
cols=st.columns(6)
vals=[('Current Capital',f'{cap:,.2f}','acc'),('Next Trade Size',f'{amt:,.2f}','acc'),('Net P/L',f'{net:+,.2f}','pos' if net>=0 else 'neg'),('Win Rate',f'{wr:.1f}%','pos' if wr>=50 else 'neg'),('Trades',str(total),'acc'),('Cycle',f"{min(st.session_state.cycle_step+1,st.session_state.compounding_steps)}/{st.session_state.compounding_steps}",'acc')]
for c,(lab,val,cl) in zip(cols,vals):
    with c: st.markdown(f'<div class="card"><div class="label">{lab}</div><div class="value {cl}">{val}</div></div>',unsafe_allow_html=True)

st.write('')
left,right=st.columns([1.35,1])
with left:
    st.subheader('🎯 Next Trade')
    st.info(f"{st.session_state.compounding_steps}-Step Compounding • Base stake = {base_stake():,.2f} • Current cycle stake = {amt:,.2f}\n\nWIN compounds the next stake. LOSS resets the cycle to the new balance's base percentage.")
    a,b=st.columns(2)
    with a:
        if st.button('✅ WIN',use_container_width=True,type='primary'):
            before=cap; pnl=amt*st.session_state.win_return_pct/100; after=before+pnl
            step=st.session_state.cycle_step+1
            st.session_state.trades.append({'trade':len(st.session_state.trades)+1,'time':datetime.now().strftime('%H:%M:%S'),'result':'WIN','capital_before':before,'amount':amt,'pnl':pnl,'capital_after':after,'cycle_step':step})
            st.session_state.cycle_step=0 if step>=st.session_state.compounding_steps else step; st.rerun()
    with b:
        if st.button('❌ LOSS',use_container_width=True):
            before=cap; pnl=-amt; after=before+pnl
            st.session_state.trades.append({'trade':len(st.session_state.trades)+1,'time':datetime.now().strftime('%H:%M:%S'),'result':'LOSS','capital_before':before,'amount':amt,'pnl':pnl,'capital_after':after,'cycle_step':st.session_state.cycle_step+1})
            st.session_state.cycle_step=0; st.rerun()
with right:
    st.subheader('📊 Session Stats')
    st.markdown(f'<div class="card"><div class="label">Initial Capital</div><div class="value">{st.session_state.initial_capital:,.2f}</div><hr><b class="pos">{wins} Wins</b> &nbsp; / &nbsp; <b class="neg">{losses} Losses</b><br><span style="color:#8da4bf">Current cycle: {st.session_state.cycle_step}/{st.session_state.compounding_steps} wins</span></div>',unsafe_allow_html=True)

st.subheader('📜 Trade History')
if not st.session_state.trades: st.info('No trades yet. Set your rules and press WIN or LOSS.')
for t in reversed(st.session_state.trades):
    cl='pos' if t['result']=='WIN' else 'neg'; icon='🟢' if t['result']=='WIN' else '🔴'
    st.markdown(f'<div class="trade"><b>Trade #{t["trade"]}</b> {icon} <span class="{cl}"><b>{t["result"]}</b></span> · {t["time"]}<br><small>Before: {t["capital_before"]:,.2f} • Stake: {t["amount"]:,.2f} • P/L: <b>{t["pnl"]:+,.2f}</b> • After: <b>{t["capital_after"]:,.2f}</b> • Cycle step: {t.get("cycle_step",1)}/{st.session_state.compounding_steps}</small></div>',unsafe_allow_html=True)

st.divider(); st.caption('Example: 100 capital, 5% base = 5. With 85% return, WIN gives 4.25 profit, so the next compounding stake is 9.25. If that next trade loses, the cycle resets and the new base is calculated from the updated capital.')
