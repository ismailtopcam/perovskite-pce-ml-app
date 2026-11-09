# -*- coding: utf-8 -*-
"""Genel Bakış — tezin savı, dört temel sayı, sayfa dizini, okuma kılavuzu, provenans."""
import streamlit as st

from lib import data, ui
from lib.ui import tr

meta = data.js("app_meta.json")
val = data.csv("validation_experiments.csv").set_index("ayar")
cv = data.csv("model_comparison_groupkfold.csv").set_index("model")
cand = data.candidates()

r2_grup = float(val.loc["DOI_grup_KFold", "R2_mean"])
r2_std = float(val.loc["DOI_grup_KFold", "R2_std"])
r2_rast = float(val.loc["rastgele_KFold", "R2_mean"])
n_destek = int(cand["uyumlu_N5"].sum())

# --- kahraman: sav + lede + iki buton
left, right = st.columns([7, 5], gap="large")
with left:
    st.html(
        '<div style="padding-top:26px"><div class="m-kicker" style="margin-bottom:14px">Tezin savı</div>'
        '<div class="m-hero">Raporlanan model başarımını algoritma kadar '
        '<span class="acc">doğrulama ve özellik kararları</span> belirler.</div></div>'
    )
with right:
    st.html(
        '<div class="hero-right" style="padding-top:26px">'
        f'<p class="m-lede" style="margin:0">Bu uygulama; {tr(meta["n_ham"], 0)} kayıtlık Perovskite Database '
        'anlık görüntüsünden başlayan veri hattını, doğrulama deneylerini ve bulguları etkileşimli ve '
        'denetlenebilir biçimde sunar. Her ekran bu savı veriyle görünür kılmak için tasarlandı.</p></div>'
    )
    b1, b2 = st.columns([1.3, 1])
    with b1:
        st.page_link("pages/2_Dogrulama_Deneyleri.py", label="Merkez deneyi çalıştır  →")
    with b2:
        st.page_link("pages/0_Rehber.py", label="Kullanım rehberi  →")

st.html('<div style="height:14px"></div>')

# --- dört temel sayı
ui.stats([
    ("Temiz kayıt", tr(meta["n_temiz"], 0),
     f"{tr(meta['n_ham'], 0)} ham kayıttan; {tr(meta['n_elenen'], 0)} eleme nedeniyle loglandı"),
    ("Grup-güvenli R²", tr(r2_grup, 3), f"± {tr(r2_std, 3)} · yayın-ayrık 5-kat CV — dürüst ölçüm"),
    ("Rastgele bölme iyimserliği", f"+{tr(r2_rast - r2_grup, 3)}",
     f"kardeş-cihaz sızıntısı skoru {tr(r2_rast, 3)}'e çıkarır", "acc"),
    ("Aday kompozisyon", tr(len(cand), 0), f"{tr(n_destek, 0)}'ü eğitimde ≥5 kayıtla destekli"),
], big=True)

st.html('<div style="height:10px"></div>')

# --- sayfa dizini + okuma kılavuzu + provenans
left, right = st.columns([7, 5], gap="large")
with left:
    ui.kicker("Sayfalar")
    ui.index_rows([
        ("R", "Kullanım Rehberi", "Her ekranın ne gösterdiği, nasıl okunacağı + küçük sözlük — buradan başlayın", "Rehber"),
        ("01", "Veri Hattı", "Ham→temiz dönüşüm, eleme nedenleri, kayıt gezgini", "Veri_Hatti"),
        ("02", "Doğrulama Deneyleri", "Merkez bulgu: bölme ve özellik kararlarının R²'ye etkisi", "Dogrulama_Deneyleri"),
        ("03", "Model Karşılaştırma", "6 modelin DOI-grup CV ve holdout başarımları", "Model_Karsilastirma"),
        ("04", "Tahmin Aracı", "Sanal cihaz tarifi → PCE + %90 aralık + yerel SHAP", "Tahmin_Araci"),
        ("05", "Gerçek – Tahmin", f"{tr(meta['n_holdout'], 0)} holdout kaydında hata analizi", "Gercek_vs_Tahmin"),
        ("06", "Aday Tarayıcı", "756 adayın aralıklı ve eğitim-uzayı bilgili keşfi", "Aday_Tarayici"),
        ("07", "DOI Gezgini", "Yayın-düzeyi izlenebilirlik; grup-güvenli ayrımın somut hâli", "DOI_Gezgini"),
        ("08", "Pipeline & Provenans", "Aşama manifestleri, sürümler, denetim özetleri", "Pipeline_Provenance"),
        ("09", "Sayıların Evrimi", "Bildiriden teze: ham ve kanonik DOI anahtarıyla ana sayılar", "Sayilarin_Evrimi"),
    ])
with right:
    ui.kicker("Nasıl okumalı")
    ui.steps([
        ("1", "Hiçbir çıktı <strong>deneysel doğrulama yerine geçmez</strong>; model, literatürden öğrenilen "
              "örüntülerle önceliklendirme yapar."),
        ("2", f"R² = {tr(r2_grup, 3)} <strong>bilinçli olarak muhafazakârdır</strong>: eğitimden kanonik DOI "
              f"anahtarı düzeyinde ayrık tutulan yayınlara genellemeyi ölçer. {tr(r2_rast, 3)} ve 0,937, iki "
              'gevşek kararın ürünüdür — <a href="Dogrulama_Deneyleri" target="_self">02\'de kendiniz deneyin</a>.'),
        ("3", "Belirsizlik aralıkları DOI-grup-güvenli <strong>conformal</strong> kalibrasyonla üretilmiştir "
              "(tez Bölüm 4.10)."),
    ])
    ui.box(
        f'<p>Pipeline commit <strong>{meta["pipeline_git_commit"][:12]}</strong> · veri hazırlama '
        f'<strong>{meta["hazirlama_zamani_utc"][:10]}</strong></p>'
        '<p>Veri: <a href="https://www.perovskitedatabase.com">Perovskite Database</a> (Jacobsson vd., 2022, '
        f'CC BY 4.0) — {tr(meta["n_ham"], 0)} kayıt anlık görüntüsü</p>'
        f'<p>Kod: <a href="{meta.get("github_pipeline", "#")}">pipeline deposu</a> · '
        f'<a href="{meta.get("github_app", "#")}">uygulama deposu</a> · '
        f'<a href="https://doi.org/{meta.get("zenodo_doi", "")}">DOI {meta.get("zenodo_doi", "")}</a></p>'
        '<p>Ölçüm-sonrası değişkenler (Voc / Jsc / FF…) modele <strong>dâhil değildir</strong> → '
        '<a href="Pipeline_Provenance" target="_self">08 Provenans</a></p>',
        k="Provenans")

ui.footer()
