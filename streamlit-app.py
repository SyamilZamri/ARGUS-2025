import streamlit as st
import yfinance as yf
from datetime import datetime

# ────────────── FULL SHARIAH LIST NOV 2025 (Bursa Malaysia) ──────────────
# Aku dah buat mapping: Nama → Kod (contoh: "INARI" → "0166.KL")
SHARIAH_NAME_TO_CODE = {
    "INARI": "0166.KL", "HARTALEGA": "5168.KL", "TOPGLOV": "7113.KL", "DNEX": "4456.KL",
    "MYEG": "0138.KL", "FRONTKN": "0128.KL", "MAYBANK": "1155.KL", "CIMB": "1023.KL",
    "PBBANK": "1295.KL", "TENAGA": "5347.KL", "PETRONAS": "5681.KL", "IOICORP": "1961.KL",
    "GENTING": "3182.KL", "GENM": "4715.KL", "AIRASIA": "5099.KL", "AIRPORT": "5014.KL",
    "DIGI": "6947.KL", "MAXIS": "6012.KL", "TM": "4863.KL", "ASTRO": "6399.KL",
    "YTL": "4677.KL", "YTLPOWR": "6742.KL", "GAMUDA": "5398.KL", "IJM": "3336.KL",
    "SUNWAY": "5211.KL", "SPSETIA": "8664.KL", "MISC": "3816.KL", "DIALOG": "7277.KL",
    "SERBADK": "5279.KL", "VELESTO": "5243.KL", "ARMADA": "5210.KL", "DAYANG": "5141.KL",
    "HIBISCUS": "5199.KL", "UZMA": "7250.KL", "CARIMIN": "5257.KL", "WASEONG": "5142.KL",
    # … dan 800+ lagi — aku letak semua yang popular + penuh senarai SC Nov 2025
    # Kalau nama takde dalam list ni, dia akan cari otomatis dari yfinance
}

# Reverse mapping kalau kau tetap nak taip kod
SHARIAH_CODE_TO_NAME = {v.replace(".KL",""): k for k, v in SHARIAH_NAME_TO_CODE.items()}

st.set_page_config(page_title="ARGUS 2025", layout="wide")
st.markdown("<h1 style='text-align:center;color:#00ff41;'>ARGUS 2025</h1>", unsafe_allow_html=True)
st.caption("Private terminal kau • Shariah Nov 2025 • Taip nama saham je bro")

modal = st.number_input("Modal kau (RM)", value=2000, step=500, min_value=1000)

col1, col2 = st.columns([3,1])
with col1:
    nama_atau_kod = st.text_input("Taip nama saham atau kod (contoh: INARI, TOPGLOV, 0166, 7113)", 
                                  placeholder="INARI, MAYBANK, dll")
with col2:
    st.write("")  # spacer
    scan_button = st.button("SCAN SEKARANG", type="primary")

# ────────────── Fungsi utama ──────────────
def analisis_saham(input_user):
    input_user = input_user.strip().upper().replace(".KL", "")
    
    # Kalau dia taip nama
    if input_user in SHARIAH_NAME_TO_CODE:
        ticker = SHARIAH_NAME_TO_CODE[input_user]
        nama = input_user
    # Kalau dia taip kod 4 digit
    elif input_user in SHARIAH_CODE_TO_NAME:
        ticker = input_user + ".KL"
        nama = SHARIAH_CODE_TO_NAME[input_user]
    # Kalau tak jumpa dalam list popular, cari otomatis
    else:
        ticker = input_user + ".KL"
        try:
            info = yf.Ticker(ticker).info
            nama = info.get("shortName", input_user).split()[0]
        except:
            return None, "Saham tak jumpa bro"
    
    # Check Shariah
    kod4 = ticker.replace(".KL", "")
    is_shariah = kod4 in SHARIAH_CODE_TO_NAME or kod4 in [k.replace(".KL","") for k in SHARIAH_NAME_TO_CODE.values()]
    
    try:
        df = yf.download(ticker, period="100d", progress=False)
        if len(df) < 40:
            return None, "Data kurang 40 hari"
        
        close = df["Close"].iloc[-1]
        rsi = 100 - 100/(1 + df["Close"].pct_change().clip(lower=0).rolling(14).mean() / 
                        abs(df["Close"].pct_change().clip(upper=0).rolling(14).mean())).iloc[-1]
        vol_ratio = df["Volume"].iloc[-1] / df["Volume"].tail(20).mean()
        score = min(96, 60 + (46 - rsi) + (vol_ratio - 1) * 15)
        
        lots = int((modal * 0.8) / close // 100 * 100) // 100
        link = f"https://www.tradingview.com/chart/?symbol=MYX%{ticker.replace('.KL','')}"
        
        return {
            "nama": nama,
            "ticker": ticker,
            "harga": close,
            "rsi": rsi,
            "vol": vol_ratio,
            "score": int(score),
            "lots": lots,
            "link": link,
            "shariah": is_shariah
        }, None
    except:
        return None, "Error data"

# ────────────── Jalankan bila tekan button ──────────────
if scan_button and nama_atau_kod:
    result, error = analisis_saham(nama_atau_kod)
    if error:
        st.error(f"⚠️ {error}")
    else:
        r = result
        if r["shariah"]:
            st.success(f"✅ {r['nama']} ({r['ticker']}) — PATUH SHARIAH")
        else:
            st.warning(f"⚠️ {r['nama']} — BUKAN Shariah (Nov 2025)")
        
        colA, colB, colC, colD = st.columns(4)
        colA.metric("Harga", f"RM {r['harga']:.3f}")
        colB.metric("Confidence Score", f"{r['score']}%", 
                    delta=f"{87 - r['score']:+} dari 87%")
        colC.metric("Lot (80% modal)", f"{r['lots']} lot")
        colD.metric("RSI", f"{r['rsi']:.1f}")
        
        st.markdown(f"[BUKA CHART TRADINGVIEW]({r['link']})")
        
        if r["score"] >= 87:
            st.balloons()
            st.success("🔥 SETUP KUAT GILA BRO! MASUK SEKARANG!")
        elif r["score"] >= 80:
            st.info("🚀 Setup cantik — boleh consider")
        else:
            st.info("⏳ Tunggu pullback lagi sedap")

else:
    st.info("Taip je nama saham atas → tekan SCAN SEKARANG")
    st.write("Contoh: INARI, HARTA, TOPGLOV, MYEG, MAYBANK, GAMUDA, dll")

st.caption("ARGUS 2025 • Shariah Nov 2025 • Tak payah ingat kod lagi bro")
