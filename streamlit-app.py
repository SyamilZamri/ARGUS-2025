import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="ARGUS 2025", layout="wide")
st.markdown("<h1 style='text-align:center;color:#00ff41;'>ARGUS 2025</h1>", unsafe_allow_html=True)
st.caption("Private terminal kau • Shariah • ICT • Modal smart")

modal = st.number_input("Modal kau (RM)", value=2000, step=500)

assets = {"INARI":"0166.KL","HARTA":"5168.KL","TOPGLOV":"7113.KL","DNEX":"4456.KL","MYEG":"0138.KL","FRONTKN":"0128.KL"}

@st.cache_data(ttl=300)
def scan():
    picks = []
    for name, code in assets.items():
        try:
            df = yf.download(code, period="100d", interval="1d", progress=False)
            if len(df)<40: continue
            close = df["Close"].iloc[-1]
            rsi = 100 - 100/(1 + df["Close"].pct_change().clip(lower=0).rolling(14).mean() / abs(df["Close"].pct_change().clip(upper=0).rolling(14).mean())).iloc[-1]
            vol = df["Volume"].iloc[-1] / df["Volume"].tail(20).mean()
            score = min(96, 60 + (46-rsi) + (vol-1)*15)
            if score >= 87:
                lots = int((modal*0.8)/close//100*100)//100
                link = f"https://www.tradingview.com/chart/?symbol=MYX%3A{code.replace('.KL','')}"
                picks.append((name, close, int(score), lots, link))
        except: pass
    return sorted(picks, key=lambda x: x[2], reverse=True)

picks = scan()
if picks:
    st.success(f"{len(picks)} SETUP KUAT • {datetime.now().strftime('%d %b %Y')}")
    for n,p,s,l,link in picks:
        st.markdown(f"**{n}** • RM {p:.3f} • **{s}%** • {l} lot → [BUKA CHART]({link})", unsafe_allow_html=True)
else:
    st.info("Tiada setup premium sekarang")

if st.button("REFRESH SCAN"):
    st.rerun()
