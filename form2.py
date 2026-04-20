import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Saat Sipariş Paneli", layout="centered", page_icon="⌚")

# Görsel düzenleme ve sadeleştirme
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .price-text { color: #2ecc71; font-weight: bold; font-size: 1.1rem; }
    .model-header { font-size: 1.1rem; font-weight: bold; margin-bottom: 2px; }
    [data-testid="stImage"] img { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ BAĞLANTISI ---
URL = "https://script.google.com/macros/s/AKfycbzQeTffKkt07RZqE9Uk2WYL-qjhgco0aEXa4orenQgW8XkaGxyYUtLtWgxyJzUnLkEpBQ/exec"

@st.cache_data(ttl=10, show_spinner=False)
def verileri_yukle():
    try:
        res = requests.get(URL, timeout=10)
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

# --- 3. ANA UYGULAMA ---
st.title("⌚ Saat Sipariş Formu")

df = verileri_yukle()

if df.empty:
    st.error("⚠️ Liste şu an yüklenemiyor. Lütfen Google Sheets bağlantınızı kontrol edin.")
else:
    # Müşteri Bilgileri
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        musteri = st.text_input("👤 Adınız Soyadınız")
    with col_b2:
        firma = st.text_input("🏢 Firma Adı")

    st.subheader("📦 Mevcut Modeller")
    siparisler = {}

    for i, row in df.iterrows():
        model_kodu = row.get('Kodu', 'Bilinmiyor')
        stok_miktari = row.get('Miktar', 0)
        gorsel_linki = row.get('URL', '')
        fiyat = row.get('P.S.F.', '0')

        try:
            stok = int(float(stok_miktari))
        except:
            stok = 0

        if stok > 0:
            with st.container():
                c_img, c_info, c_input = st.columns([1, 2, 1])
                with c_img:
                    if gorsel_linki:
                        st.image(gorsel_linki, use_container_width=True)
                with c_info:
                    st.markdown(f"<p class='model-header'>{model_kodu}</p>", unsafe_allow_html=True)
                    st.markdown(f"Fiyat: <span class='price-text'>{fiyat} TL</span>", unsafe_allow_html=True)
                    st.caption(f"Stok: {stok}")
                with c_input:
                    adet = st.number_input("Adet", min_value=0, max_value=stok, key=f"it_{i}", step=1)
                    if adet > 0:
                        siparisler[model_kodu] = adet
            st.divider()

    # Sipariş Butonu
    if st.button("🚀 Siparişi Onayla ve Gönder", use_container_width=True):
        if musteri and firma and siparisler:
            veri_paketi = []
            for m, a in siparisler.items():
                veri_paketi.append({
                    "Tarih": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Müşteri": musteri,
                    "Firma": firma,
                    "Model": m,
                    "Adet": a
                })
            
            with st.spinner("Gönderiliyor..."):
                try:
                    res = requests.post(URL, json=veri_paketi, timeout=15)
                    if res.status_code == 200:
                        st.success(f"✅ Siparişiniz başarıyla iletildi!")
                        st.cache_data.clear()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Bir hata oluştu.")
                except:
                    st.error("❌ Gönderim sırasında bir sorun çıktı.")
        else:
            st.warning("⚠️ Lütfen formu eksiksiz doldurun.")

st.caption("© 2026 Has Saat")