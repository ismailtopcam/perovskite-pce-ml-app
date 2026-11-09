# -*- coding: utf-8 -*-
"""Giriş noktası: st.navigation ile sol ray (kenar çubuğu) ve Türkçe sayfa adları.

Sayfa dosya adları (ve URL'ler) ASCII kalır; rayda görünen başlıklar burada
tanımlanır. Ray düzeni (İKÇÜ kimliği → numaralı sayfa listesi → tez sahibi ve
provenans bloğu) "Modernist" tasarımından gelir; numaralar CSS ile eklenir
(lib/ui.py, sıra bu listeyle aynıdır).
"""
import streamlit as st

from lib import data, hatalar, ui

hatalar.baslat()

st.set_page_config(page_title="Perovskit PCE — İKÇÜ", page_icon="🔬", layout="wide",
                   initial_sidebar_state="auto")

ui.inject_css()

meta = data.js("app_meta.json")

# --- ray: üst kimlik bloğu (CSS ile navigasyonun üstüne taşınır)
st.sidebar.html(
    '<div class="rail-brand">'
    '<div class="kurum">İzmir Kâtip Çelebi Üniversitesi</div>'
    '<div class="ens">Fen Bilimleri Enstitüsü · Yazılım Mühendisliği</div>'
    '<div class="marka">Perovskit<br>PCE</div>'
    '<div class="alt">Makine öğrenmesi tabanlı verim tahmini — DOI-grup-ayrık doğrulama hattı</div>'
    '</div>'
)

# --- ray: alt blok (tez sahibi + provenans mikro bloğu; CSS ile en alta taşınır)
st.sidebar.html(
    '<div class="rail-foot">'
    '<div class="k">Yüksek lisans tezi</div>'
    '<div class="ad">İsmail Topçam</div>'
    f'<div class="m">R² 0,410 ± 0,016 · {ui.tr(meta["n_temiz"], 0)} kayıt<br>'
    f'seed {meta["seed"]} · commit {meta["pipeline_git_commit"][:8]} · {meta["hazirlama_zamani_utc"][:10]}</div>'
    '</div>'
)

# Sayfa dosyaları bilinçli olarak `pages/` dışında (sayfalar/): Streamlit `pages/` klasörünü giriş betiği
# çalışmadan otomatik algılar; soğuk sunucuda doğrudan bir alt sayfa adresi bu betiği (CSS, ray) atlıyordu.
pages = [
    st.Page("Ana_Sayfa.py", title="Genel Bakış", default=True),
    st.Page("sayfalar/0_Rehber.py", title="Rehber"),
    st.Page("sayfalar/1_Veri_Hatti.py", title="Veri Hattı"),
    st.Page("sayfalar/2_Dogrulama_Deneyleri.py", title="Doğrulama"),
    st.Page("sayfalar/3_Model_Karsilastirma.py", title="Modeller"),
    st.Page("sayfalar/4_Tahmin_Araci.py", title="Tahmin Aracı"),
    st.Page("sayfalar/5_Gercek_vs_Tahmin.py", title="Gerçek – Tahmin"),
    st.Page("sayfalar/6_Aday_Tarayici.py", title="Aday Tarayıcı"),
    st.Page("sayfalar/7_DOI_Gezgini.py", title="DOI Gezgini"),
    st.Page("sayfalar/8_Pipeline_Provenance.py", title="Provenans"),
    st.Page("sayfalar/9_Sayilarin_Evrimi.py", title="Sayıların Evrimi"),
]

with hatalar.yakala():
    st.navigation(pages).run()
