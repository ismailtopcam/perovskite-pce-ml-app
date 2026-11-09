# -*- coding: utf-8 -*-
"""Genel Bakış — tezin savı, tek grafikte sav (dört R²), dört temel sayı, sayfa dizini, okuma kılavuzu, provenans."""
import streamlit as st

from lib import data, ui
from lib.ui import tr

meta = data.js("app_meta.json")
val = data.csv("validation_experiments.csv").set_index("ayar")
cand = data.candidates()

r2_grup = float(val.loc["DOI_grup_KFold", "R2_mean"])
r2_std = float(val.loc["DOI_grup_KFold", "R2_std"])
r2_rast = float(val.loc["rastgele_KFold", "R2_mean"])
r2_leak = float(val.loc["leakage_ON (+Voc,Jsc,FF)", "R2_mean"])
r2_komp = float(val.loc["kompozisyon (14 ozellik)", "R2_mean"])
n_destek = int(cand["uyumlu_N5"].sum())

# --- kahraman: sav + lede + düğmeler | tek grafikte sav
left, right = st.columns([7, 6], gap="large")
with left:
    st.html(
        '<div style="display:flex; flex-direction:column; gap:18px; padding-top:18px">'
        '<div class="m-kicker">Tezin savı</div>'
        '<div class="m-hero">Raporlanan model başarımını algoritma kadar '
        '<span class="acc">doğrulama ve özellik kararları</span> belirler.</div>'
        f'<p class="m-lede">Bu uygulama; {tr(meta["n_ham"], 0)} kayıtlık Perovskite Database anlık görüntüsünden '
        'başlayan veri hattını, doğrulama deneylerini ve bulguları etkileşimli ve denetlenebilir biçimde sunar. '
        'Her ekran bu savı veriyle görünür kılmak için tasarlandı.</p></div>'
    )
    b1, b2 = st.columns([1.25, 1])
    with b1:
        st.page_link("sayfalar/2_Dogrulama_Deneyleri.py", label="Merkez deneyi çalıştır  →")
    with b2:
        st.page_link("sayfalar/0_Rehber.py", label="Kullanım rehberi")
    ui.text("Veri: Perovskite Database (Jacobsson vd., 2022) · CC BY 4.0 · Model: CatBoost, "
            f"{meta['n_ozellik']} özellik", mute=True)
with right:
    with ui.card():
        ui.h2("Aynı veri, aynı model — dört farklı R²")
        ui.text("5-kat çapraz doğrulama; değişen yalnızca bölme ve özellik kararları.", mute=True)
        ui.bar_rows([
            dict(name="Yalnızca kompozisyon", sub="14 özellik · DOI-grup", value=r2_komp,
                 value_str=f'<span style="color:var(--n700)">{tr(r2_komp, 3)}</span>', tone="mid"),
            dict(name="Tezin ölçümü", sub=f"{meta['n_ozellik']} özellik · DOI-grup (yayın-ayrık)", value=r2_grup,
                 value_str=f'<span style="color:var(--blue)">{tr(r2_grup, 3)}</span>', tone="blue"),
            dict(name="Rastgele bölme", sub="kardeş-cihaz sızıntısı", value=r2_rast,
                 value_str=f'<span style="color:var(--acc700)">{tr(r2_rast, 3)}</span>',
                 value_sub=f"+{tr(r2_rast - r2_grup, 3)}", tone="soft"),
            dict(name="+ Voc, Jsc, FF", sub="hedef sızıntısı", value=r2_leak,
                 value_str=f'<span style="color:var(--acc700)">{tr(r2_leak, 3)}</span>',
                 value_sub=f"+{tr(r2_leak - r2_grup, 3)}", tone="acc"),
        ], vmax=1.0)
        st.html('<div class="m-axis num" style="border-top:1px solid var(--n200); padding-top:8px">'
                '<span>0</span><span>0,25</span><span>0,50</span><span>0,75</span><span>1,00</span></div>'
                '<div style="display:flex; flex-wrap:wrap; gap:8px 18px; font-size:12.5px; color:var(--n800); margin-top:10px">'
                '<span style="display:inline-flex; align-items:center; gap:7px"><span style="width:10px; height:10px; '
                'border-radius:3px; background:var(--blue)"></span>dürüst ölçüm</span>'
                '<span style="display:inline-flex; align-items:center; gap:7px"><span style="width:10px; height:10px; '
                'border-radius:3px; background:var(--acc)"></span>sızıntıyla şişen skor</span>'
                '<span style="display:inline-flex; align-items:center; gap:7px"><span style="width:10px; height:10px; '
                'border-radius:3px; background:var(--n500)"></span>eksik bilgi</span>'
                '<span style="margin-left:auto; color:var(--n700)">Tez Bölüm 4.3 · Deney A, B, C</span></div>')

st.html('<div style="height:6px"></div>')

# --- dört temel sayı
ui.stats([
    ("Temiz kayıt", tr(meta["n_temiz"], 0),
     f"{tr(meta['n_ham'], 0)} ham kayıttan; {tr(meta['n_elenen'], 0)}'ü nedeniyle loglanarak elendi"),
    ("Grup-güvenli R²", f"{tr(r2_grup, 3)} <small>± {tr(r2_std, 3)}</small>",
     "yayın-ayrık 5-kat CV — dürüst ölçüm", "blue"),
    ("Rastgele bölme iyimserliği", f"+{tr(r2_rast - r2_grup, 3)}",
     f"kardeş-cihaz sızıntısı skoru {tr(r2_rast, 3)}'e çıkarır", "acc"),
    ("Aday kompozisyon", tr(len(cand), 0), f"{tr(n_destek, 0)}'ü eğitimde ≥5 kayıtla destekli"),
], big=True)

st.html('<div style="height:6px"></div>')

# --- sayfa dizini
ui.h2("Sayfalar", "Uzman değilseniz Rehber'den başlayın")
ui.index_rows([
    ("02", "Doğrulama Deneyleri", "Bölme ve özellik kararlarının R²'ye etkisi — kararları siz verin", "Dogrulama_Deneyleri"),
    ("R", "Kullanım Rehberi", "Her ekranın ne gösterdiği, nasıl okunacağı ve küçük bir sözlük", "Rehber"),
    ("01", "Veri Hattı", "Ham → temiz dönüşüm, eleme nedenleri, kayıt gezgini", "Veri_Hatti"),
    ("03", "Model Karşılaştırma", "6 modelin DOI-grup CV ve holdout başarımları", "Model_Karsilastirma"),
    ("04", "Tahmin Aracı", "Sanal cihaz tarifi → PCE + %90 aralık + yerel SHAP", "Tahmin_Araci"),
    ("05", "Gerçek – Tahmin", f"{tr(meta['n_holdout'], 0)} holdout kaydında hata analizi; model nerede yanılıyor",
     "Gercek_vs_Tahmin"),
    ("06", "Aday Tarayıcı", f"{tr(len(cand), 0)} adayın aralıklı ve eğitim-uzayı bilgili keşfi", "Aday_Tarayici"),
    ("07", "DOI Gezgini", "Yayın-düzeyi izlenebilirlik; grup-güvenli ayrımın somut hâli", "DOI_Gezgini"),
    ("08", "Pipeline & Provenans", "Aşama manifestleri, sürümler, denetim özetleri", "Pipeline_Provenance"),
    ("09", "Sayıların Evrimi", "Bildiriden teze: ham ve kanonik DOI anahtarıyla ana sayılar", "Sayilarin_Evrimi"),
])

st.html('<div style="height:6px"></div>')

# --- okuma kılavuzu + provenans
left, right = st.columns([7, 5], gap="medium")
with left:
    with ui.card():
        ui.h2("Nasıl okumalı")
        ui.steps([
            ("1", "Hiçbir çıktı <strong>deneysel doğrulama yerine geçmez</strong>; model, literatürden öğrenilen "
                  "örüntülerle önceliklendirme yapar."),
            ("2", f"R² = {tr(r2_grup, 3)} <strong>bilinçli olarak muhafazakârdır</strong>: eğitimden kanonik DOI "
                  f"anahtarı düzeyinde ayrık tutulan yayınlara genellemeyi ölçer. {tr(r2_rast, 3)} ve "
                  f"{tr(r2_leak, 3)}, iki gevşek kararın ürünüdür — "
                  '<a href="Dogrulama_Deneyleri" target="_self">02\'de kendiniz deneyin</a>.'),
            ("3", "Belirsizlik aralıkları DOI-grup-güvenli <strong>conformal</strong> kalibrasyonla üretilmiştir "
                  "(tez Bölüm 4.10)."),
        ])
with right:
    with ui.card():
        ui.h2("Provenans")
        ui.table([], [
            ["Pipeline commit", f'<span class="m-mono">{meta["pipeline_git_commit"][:12]}</span>'],
            ["Veri hazırlama", meta["hazirlama_zamani_utc"][:10]],
            ["Veri", f'<a href="https://www.perovskitedatabase.com">Perovskite Database</a> · '
                     f'{tr(meta["n_ham"], 0)} kayıt (CC BY 4.0)'],
            ["Kod", f'<a href="{meta.get("github_pipeline", "#")}">pipeline</a> · '
                    f'<a href="{meta.get("github_app", "#")}">uygulama</a>'],
            ["Arşiv", f'<a href="https://doi.org/{meta.get("zenodo_doi", "")}">{meta.get("zenodo_doi", "")}</a>'],
        ], kv=True)
        ui.text('Ölçüm-sonrası değişkenler (Voc / Jsc / FF…) modele <strong>dâhil değildir</strong> → '
                '<a href="Pipeline_Provenance" target="_self">08 Provenans</a>', mute=True)

ui.footer()
