import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Saat Sipariş Paneli", 
    layout="centered", 
    page_icon="⌚"
)

# Arayüzü sadeleştiren ve linkleri gizleyen CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .price-text { color: #2ecc71; font-weight: bold; font-size: 1.1rem; }
    .model-header { font-size: 1.1rem; font-weight: bold; margin-bottom: 2px; }
    /* Görsellerin daha düzgün durması için */
    [data-testid="stImage"] img { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GOOGLE SHEETS VERİ BAĞLANTISI ---
URL = "https://script.google.com/macros/s/AKfycbwB8Qzgb9zO1OCjzBOl2JHoTjOvH_MWO_xyKWlVIQkksxeGnGqF7_CVppV9tTjL4zc7/exec"

@st.cache_data(ttl=30, show_spinner=False)
def verileri_yukle():
    try:
        res = requests.get(URL, timeout=10)
        res.raise_for_status()
        return pd.DataFrame(res.json())
    except Exception:
        return pd.DataFrame()

# --- 3. ANA UYGULAMA ---
st.title("⌚ Saat Sipariş Formu")
st.write("Lütfen sipariş bilgilerinizi doldurup ürün seçimi yapınız.")

df = verileri_yukle()

if df.empty:
    st.error("⚠️ Stok listesi şu an yüklenemiyor. Lütfen Google Sheets bağlantınızı kontrol edin.")
else:
    # Müşteri Bilgileri
    col_bilgi1, col_bilgi2 = st.columns(2)
    with col_bilgi1:
        musteri = st.text_input("👤 Adınız Soyadınız", placeholder="Zorunlu")
    with col_bilgi2:
        firma = st.text_input("🏢 Firma Adı", placeholder="Zorunlu")

    st.subheader("📦 Mevcut Modeller")
    siparisler = {}

    # Ürün Listeleme
    for i, row in df.iterrows():
        # Tablo sütun başlıklarınla birebir eşleşme
        model_kodu = row.get('Kodu', 'Bilinmiyor')
        stok_miktari = row.get('Miktar', 0)
        gorsel_linki = row.get('URL', '')
        fiyat = row.get('P.S.F.', '0')

        try:
            stok = int(float(stok_miktari))
        except:
            stok = 0

        # Sadece stokta olanları göster
        if stok > 0:
            with st.container():
                # Görsel | Bilgi | Adet Girişi
                c_img, c_info, c_input = st.columns([1, 2, 1])

                with c_img:
                    if gorsel_linki and str(gorsel_linki).startswith("http"):
                        # Sadece görseli gösteriyoruz, URL metni yazmıyor
                        st.image(gorsel_linki, use_container_width=True)
                    else:
                        st.write("🖼️")

                with c_info:
                    st.markdown(f"<p class='model-header'>{model_kodu}</p>", unsafe_allow_html=True)
                    st.markdown(f"Fiyat: <span class='price-text'>{fiyat} TL</span>", unsafe_allow_html=True)
                    st.caption(f"Stok Durumu: {stok}")

                with c_input:
                    adet = st.number_input(
                        "Adet", 
                        min_value=0, 
                        max_value=stok, 
                        key=f"item_{i}", 
                        step=1
                    )
                    if adet > 0:
                        siparisler[model_kodu] = adet
            st.divider()

    # Sipariş Gönderim Butonu
    if st.button("🚀 Siparişi Onayla ve Gönder", use_container_width=True):
        if musteri and firma and siparisler:
            # Google Sheets'e gönderilecek veri paketi
            veri_paketi = []
            for m, a in siparisler.items():
                veri_paketi.append({
                    "Tarih": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Müşteri": musteri,
                    "Firma": firma,
                    "Model": m,
                    "Adet": a
                })
            
            with st.spinner("Siparişiniz iletiliyor..."):
                try:
                    res = requests.post(URL, json=veri_paketi, timeout=15)
                    if res.status_code == 200:
                        st.success(f"✅ Teşekkürler {musteri}, siparişiniz iletildi!")
                        st.balloons()
                        st.cache_data.clear() # Stokları tazelemek için
                        time.sleep(3)
                        st.rerun()
                    else:
                        st.error("❌ Bir hata oluştu, lütfen tekrar deneyin.")
                except:
                    st.error("❌ Bağlantı hatası! İnternetinizi kontrol edin.")
        else:
            st.warning("⚠️ Lütfen bilgilerinizi doldurun ve en az bir adet seçin.")

st.caption("© 2026 Saat Sipariş Sistemi")