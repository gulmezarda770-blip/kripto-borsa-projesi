import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Arda Finans Paneli", layout="wide")
st.title("🚀 Arda'nın Finans & Borsa Paneli")

# --- SANAL CÜZDAN ---
if 'bakiye' not in st.session_state:
    st.session_state.bakiye = 10000.0  # 10.000 Dolar Nakit
if 'varlik' not in st.session_state:
    st.session_state.varlik = 0.0

# --- VARLIK LİSTESİ ---
semboller = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "Dolar / TL": "TRY=X",
    "Euro / TL": "EURTRY=X",
    "Altın (Ons)": "GC=F"
}

# --- YAN MENÜ ---
st.sidebar.header("Ayarlar")
secilen_isim = st.sidebar.selectbox("Yatırım Aracı Seç:", list(semboller.keys()))
sembol_kodu = semboller[secilen_isim]

aralik = st.sidebar.selectbox("Zaman Aralığı:", ("1d", "5d", "1mo", "6mo", "1y"))

# --- AKILLI ARALIK (INTERVAL) AYARI ---
# İşte hatayı çözen kısım burası:
if aralik == '1d':
    aralik_detay = '15m' # 1 günse 15 dk'lık veri getir
elif aralik == '5d':
    aralik_detay = '1h'  # 5 günse saatlik veri getir
else:
    aralik_detay = '1d'  # Diğerlerinde günlük veri yeter

# --- VERİ ÇEKME ---
try:
    data = yf.Ticker(sembol_kodu)
    df = data.history(period=aralik, interval=aralik_detay)
    
    if df.empty:
        st.error("Veri alınamadı. Borsa kapalı olabilir veya sembol hatalı.")
        st.stop()

    # Son fiyatı ve değişimi al
    guncel_fiyat = df['Close'].iloc[-1]
    onceki_fiyat = df['Close'].iloc[-2] # Bir önceki kapanış
    fark = guncel_fiyat - onceki_fiyat
    yuzde_degisim = (fark / onceki_fiyat) * 100

except Exception as e:
    st.error(f"Bir hata oluştu: {e}")
    st.stop()

# --- ÜST BİLGİ KARTLARI ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label=f"{secilen_isim} Fiyatı", 
              value=f"{guncel_fiyat:.2f}", 
              delta=f"{fark:.2f} (%{yuzde_degisim:.2f})")

with col2:
    st.metric(label="Nakit Bakiye (USD)", value=f"${st.session_state.bakiye:.2f}")

with col3:
    st.metric(label="Elimdeki Varlık Miktarı", value=f"{st.session_state.varlik:.4f}")

# --- GRAFİK ---
st.subheader(f"📈 {secilen_isim} Fiyat Grafiği ({aralik})")

fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

fig.update_layout(height=500, margin=dict(l=20, r=20, t=20, b=20))
st.plotly_chart(fig, use_container_width=True)

# --- AL / SAT SİMÜLASYONU ---
st.markdown("---")
st.header("⚡ Hızlı İşlem Yap")

col_al, col_sat = st.columns(2)

with col_al:
    if st.button(f"🟢 1000$ Değerinde {secilen_isim} AL", use_container_width=True):
        if st.session_state.bakiye >= 1000:
            miktar = 1000 / guncel_fiyat
            st.session_state.varlik += miktar
            st.session_state.bakiye -= 1000
            st.success(f"İşlem Başarılı! {miktar:.4f} adet alındı.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Yetersiz Bakiye!")

with col_sat:
    if st.button(f"🔴 Tüm {secilen_isim} Varlığını SAT", use_container_width=True):
        if st.session_state.varlik > 0:
            tutar = st.session_state.varlik * guncel_fiyat
            st.session_state.bakiye += tutar
            st.session_state.varlik = 0
            st.success(f"Satış Başarılı! Kasaya {tutar:.2f}$ eklendi.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Satacak varlığın yok!")