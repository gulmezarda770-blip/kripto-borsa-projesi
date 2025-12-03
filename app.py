import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time

# Sayfa Ayarları
st.set_page_config(page_title="Arda Kripto Paneli", layout="wide")
st.title("🚀 Arda'nın Kripto Borsası & Simülasyonu")

# Sanal Cüzdan (Hafıza)
if 'bakiye' not in st.session_state:
    st.session_state.bakiye = 10000.0  # 10.000 Dolar Başlangıç
if 'varlik' not in st.session_state:
    st.session_state.varlik = 0.0

# Yan Menü
kripto = st.sidebar.selectbox("Kripto Para Seç:", ("BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD"))
aralik = st.sidebar.selectbox("Zaman:", ("1d", "1mo", "1y"))

# Veri Çekme (Yahoo Finance)
try:
    data = yf.Ticker(kripto)
    df = data.history(period=aralik)
    fiyat = df['Close'].iloc[-1]
    fark = fiyat - df['Close'].iloc[-2]
except:
    st.error("Veri çekilemedi! İnternetini kontrol et.")
    st.stop()

# Üst Bilgi Kartları
col1, col2, col3 = st.columns(3)
col1.metric(f"{kripto} Fiyatı", f"${fiyat:.2f}", f"{fark:.2f}")
col2.metric("Nakit Bakiye", f"${st.session_state.bakiye:.2f}")
col3.metric("Elimdeki Varlık", f"{st.session_state.varlik:.4f} Adet")

# Grafik (Mum Grafiği)
fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
fig.update_layout(height=400, title=f"{kripto} Fiyat Grafiği")
st.plotly_chart(fig, use_container_width=True)

# Al-Sat Butonları
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    if st.button("🟢 1000$ AL", use_container_width=True):
        if st.session_state.bakiye >= 1000:
            miktar = 1000 / fiyat
            st.session_state.varlik += miktar
            st.session_state.bakiye -= 1000
            st.success(f"İşlem Başarılı! {miktar:.4f} adet alındı.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Yetersiz Bakiye!")

with c2:
    if st.button("🔴 Hepsini SAT", use_container_width=True):
        if st.session_state.varlik > 0:
            tutar = st.session_state.varlik * fiyat
            st.session_state.bakiye += tutar
            st.session_state.varlik = 0
            st.success(f"Satıldı! Kasaya {tutar:.2f}$ girdi.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Satacak varlığın yok!")