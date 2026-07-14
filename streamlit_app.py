# -*- coding: utf-8 -*-
"""Giris noktasi: st.navigation ile tam Turkce kenar cubugu.

Sayfa dosya adlari (ve URL'ler) ASCII kalir; kenar cubugunda gorunen
basliklar burada tanimlanir.
"""
import streamlit as st

st.set_page_config(page_title="Perovskit PCE — İKÇÜ", page_icon="🔬", layout="wide",
                   initial_sidebar_state="auto")

# Universite kimligi: kenar cubugunun EN USTUNDE metin olarak (logo yerine).
# CSS, kullanici icerigini nav'in uzerine tasir; uyumsuz bir Streamlit
# surumunde blok zarifce nav'in altina duser.
st.sidebar.markdown(
    """
<style>
  [data-testid="stSidebarContent"] { display: flex; flex-direction: column; }
  [data-testid="stSidebarUserContent"] { order: -1; padding-bottom: 0; }
</style>
<div style="padding:0.1rem 0 0.3rem 0; line-height:1.35">
  <div style="color:#ab162c; font-weight:700; font-size:1.06rem">
    İzmir Kâtip Çelebi Üniversitesi</div>
  <div style="font-size:0.8rem; color:#666">
    Fen Bilimleri Enstitüsü · Yazılım Mühendisliği</div>
  <div style="font-size:0.8rem; color:#666">
    Yüksek Lisans Tezi — Etkileşimli Uygulama</div>
</div>
<hr style="margin:0.5rem 0 0 0; border:none; border-top:1px solid #e4d5d8">
""",
    unsafe_allow_html=True,
)

pages = [
    st.Page("Ana_Sayfa.py", title="Ana Sayfa", icon="🏠", default=True),
    st.Page("pages/0_Rehber.py", title="Kullanım Rehberi", icon="📖"),
    st.Page("pages/1_Veri_Hatti.py", title="Veri Hattı", icon="1️⃣"),
    st.Page("pages/2_Dogrulama_Deneyleri.py", title="Doğrulama Deneyleri", icon="2️⃣"),
    st.Page("pages/3_Model_Karsilastirma.py", title="Model Karşılaştırma", icon="3️⃣"),
    st.Page("pages/4_Tahmin_Araci.py", title="Tahmin Aracı", icon="4️⃣"),
    st.Page("pages/5_Gercek_vs_Tahmin.py", title="Gerçek vs Tahmin", icon="5️⃣"),
    st.Page("pages/6_Aday_Tarayici.py", title="Aday Tarayıcı", icon="6️⃣"),
    st.Page("pages/7_DOI_Gezgini.py", title="DOI Gezgini", icon="7️⃣"),
    st.Page("pages/8_Pipeline_Provenance.py", title="Pipeline & Provenans", icon="8️⃣"),
]

st.navigation(pages).run()
