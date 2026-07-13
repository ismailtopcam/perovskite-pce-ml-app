# -*- coding: utf-8 -*-
"""Giris noktasi: st.navigation ile tam Turkce kenar cubugu + IKCU logosu.

Sayfa dosya adlari (ve URL'ler) ASCII kalir; kenar cubugunda gorunen
basliklar burada tanimlanir.
"""
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="Perovskit PCE — İKÇÜ", page_icon="🔬", layout="wide",
                   initial_sidebar_state="expanded")
st.logo(str(ROOT / "assets" / "ikcu_logo.jpeg"), size="large")

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
