# -*- coding: utf-8 -*-
"""Giriş noktası: st.navigation ile sol ray (kenar çubuğu) ve Türkçe sayfa adları.

Sayfa dosya adları (ve URL'ler) ASCII kalır; rayda görünen başlıklar burada
tanımlanır. Ray düzeni "Kafes" tasarımından gelir: ABX₃ kafes logosu + kurum →
dört bölümlü numaralı sayfa listesi → tez sahibi ve provenans bloğu. Numaralar
URL yoluna göre CSS ile eklenir (lib/ui.py, _NAV_NUM).
"""
import streamlit as st

from lib import data, hatalar, ui

hatalar.baslat()

st.set_page_config(page_title="Perovskit PCE — İKÇÜ", page_icon="🔬", layout="wide",
                   initial_sidebar_state="auto")

ui.inject_css()

meta = data.js("app_meta.json")

# Perovskit ABX₃ kafesi: köşelerde A, yüzlerde X, merkezde B (turuncu). st.html satır içi SVG'yi
# temizlediği için logo statik dosyadan gelir (static/logo-kafes.svg).
_LOGO = ('<img src="app/static/logo-kafes.svg" width="42" height="42" alt="Perovskit ABX3 kafes simgesi" '
         'style="display:block; flex:none">')

# --- ray: üst kimlik bloğu (CSS ile navigasyonun üstüne taşınır)
st.sidebar.html(
    '<div class="rail-brand">'
    f'<a class="logo" href="./" target="_self">{_LOGO}'
    '<span><span class="marka">Perovskit PCE</span><span class="alt" style="display:block">ML ile verim tahmini</span></span></a>'
    '<div class="kurum">İzmir Kâtip Çelebi Üniversitesi<br>Fen Bilimleri Enstitüsü · Yazılım Mühendisliği</div>'
    '</div>'
)

# --- ray: alt blok (tez sahibi + provenans mikro bloğu; CSS ile en alta taşınır)
st.sidebar.html(
    '<div class="rail-foot">'
    '<div class="k">Yüksek lisans tezi</div>'
    '<div class="ad">İsmail Topçam</div>'
    f'<div class="m">R² 0,410 ± 0,016<br>{ui.tr(meta["n_temiz"], 0)} kayıt · seed {meta["seed"]}<br>'
    f'commit {meta["pipeline_git_commit"][:8]} · {meta["hazirlama_zamani_utc"][:10]}</div>'
    '</div>'
)

# Sayfa dosyaları bilinçli olarak `pages/` dışında (sayfalar/): Streamlit `pages/` klasörünü giriş betiği
# çalışmadan otomatik algılar; soğuk sunucuda doğrudan bir alt sayfa adresi bu betiği (CSS, ray) atlıyordu.
pages = {
    "Başlangıç": [
        st.Page("Ana_Sayfa.py", title="Genel Bakış", default=True),
        st.Page("sayfalar/0_Rehber.py", title="Rehber"),
    ],
    "Veri ve doğrulama": [
        st.Page("sayfalar/1_Veri_Hatti.py", title="Veri Hattı"),
        st.Page("sayfalar/2_Dogrulama_Deneyleri.py", title="Doğrulama"),
        st.Page("sayfalar/3_Model_Karsilastirma.py", title="Modeller"),
    ],
    "Model çıktıları": [
        st.Page("sayfalar/4_Tahmin_Araci.py", title="Tahmin Aracı"),
        st.Page("sayfalar/5_Gercek_vs_Tahmin.py", title="Gerçek – Tahmin"),
        st.Page("sayfalar/6_Aday_Tarayici.py", title="Aday Tarayıcı"),
    ],
    "İzlenebilirlik": [
        st.Page("sayfalar/7_DOI_Gezgini.py", title="DOI Gezgini"),
        st.Page("sayfalar/8_Pipeline_Provenance.py", title="Provenans"),
        st.Page("sayfalar/9_Sayilarin_Evrimi.py", title="Sayıların Evrimi"),
    ],
}

with hatalar.yakala():
    st.navigation(pages).run()
