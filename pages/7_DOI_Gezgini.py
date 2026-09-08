# -*- coding: utf-8 -*-
"""07 DOI Gezgini — yayın düzeyinde izlenebilirlik; grup-güvenli ayrımın somut hâli."""
import plotly.express as px
import streamlit as st

from lib import data, ui
from lib.ui import tr, INK

doi = data.doi_summary()
rec = data.records()
g = data.js("doi_grup_dogrulama.json")
k = data.js("kontamine_test_maesi.json")
cs = data.js("clean_summary.json")

ui.page_header(
    "07 — DOI Gezgini · Tez Bölüm 3.8, 4.1 ve 5.7",
    "Bölme kayıt değil, yayın düzeyinde.",
    "Aynı yayının kardeş cihazları çok benzerdir; bu yüzden aynı kanonik DOI anahtarını taşıyan kayıtlar asla "
    "eğitim ile testin ikisine birden düşmez. Bu sayfa o kuralı yayın yayın somutlaştırır.",
)

ui.stats([
    ("Yayın (grup)", tr(len(doi), 0), f"medyan {tr(int(doi['kayit'].median()), 0)} kayıt/yayın"),
    ("DOI'siz kayıt", tr(g["n_doi_missing"], 0), "tek yapay grupta — onlar da bölünmez"),
    ("Birleştirilen varyant", tr(cs.get("doi_variants_merged", 44), 0), "büyük/küçük harf çift kayıtları normalize edildi"),
    ("Sınır aşan çakışma", tr(g["n_collisions_split_holdout"] + g["n_collisions_split_cv"], 0),
     "normalizasyon sonrası, holdout + CV"),
])

left, right = st.columns([5, 7], gap="large")

with left:
    ui.kicker("Yayın ara", tone="ink")
    q = st.text_input("DOI ara", placeholder="örn. 10.1039 — adresin bir parçası yeterli",
                      label_visibility="collapsed")
    dsub = doi[doi["DOI"].str.contains(q, case=False, regex=False)] if q else doi.sort_values("kayit", ascending=False)
    ui.kicker(f"{tr(len(dsub), 0)} yayın", tone="mute")
    if dsub.empty:
        ui.box("Aramanızla eşleşen yayın bulunamadı — adresin farklı bir parçasını deneyin.", accent=True)
        st.stop()
    st.dataframe(dsub[["DOI", "kayit", "pce_medyan", "bolme"]].head(300), hide_index=True, height=280,
                 width="stretch",
                 column_config={"kayit": "Kayıt", "bolme": "Bölme",
                                "pce_medyan": st.column_config.NumberColumn("PCE medyan", format="%.1f")})
    secenekler = dsub["DOI"].head(300).tolist()
    ilk = 1 if (len(secenekler) > 1 and secenekler[0] == "(DOI yok)") else 0
    secim = st.selectbox("Yayın seç", secenekler, index=ilk)

with right:
    d = doi[doi["DOI"] == secim].iloc[0]
    kayitlar = rec[rec["DOI"] == secim]
    egitimde = d["bolme"] == "eğitim"
    ui.kicker("Seçili yayın", tone="ink")
    st.html(f'<div class="m-mono" style="display:inline-block; font-size:13px; margin-bottom:8px">{ui.esc(secim[:80])}</div>')
    if secim == "(DOI yok)":
        ui.box(f"<strong>Yapay grup:</strong> DOI'si raporlanmamış {tr(g['n_doi_missing'], 0)} kayıt tek grupta toplanır; "
               "böylece bunlar da asla eğitim+test'e bölünmez (tez Bölüm 3.8).", accent=True)
    ui.stats([
        ("Kayıt", tr(int(d["kayit"]), 0)),
        ("PCE aralığı", f"{tr(d['pce_min'], 1)} – {tr(d['pce_maks'], 1)}"),
        ("CV katı", f"{int(d['cv_fold'])}" if egitimde else "—", "" if egitimde else "holdout: CV dışında"),
    ], border=False, small=True)
    if egitimde:
        ui.box("Aynı DOI'nin hiçbir kaydı holdout test kümesine alınmamıştır — skor, bu yayının kardeş "
               "cihazlarından beslenemez.", chip="Eğitim kümesinde")
    else:
        ui.box("Model eğitilirken bu yayının hiçbir kaydı görülmedi. Yayın-içi ortalama mutlak hata: "
               f"<strong>{tr(d['test_mae'], 2)} puan</strong>.", chip="Holdout-test kümesinde", accent=True)

    fig = px.histogram(kayitlar, x="PCE", nbins=25, labels={"PCE": "PCE (%)"})
    fig.update_traces(marker_color=INK)
    fig.update_layout(yaxis_title="Kayıt")
    ui.chart(fig, height=220, title="Yayının PCE dağılımı")

    goster = kayitlar[["kompozisyon", "mimari", "ETL", "HTL", "PCE", "tahmin", "mutlak_hata"]].rename(columns={
        "kompozisyon": "Kompozisyon", "mimari": "Mimari", "PCE": "Gerçek PCE", "tahmin": "Tahmin", "mutlak_hata": "Hata"})
    st.dataframe(goster, hide_index=True, width="stretch", height=220,
                 column_config={c: st.column_config.NumberColumn(c, format="%.2f")
                                for c in ["Gerçek PCE", "Tahmin", "Hata"]})

ui.rule(thin=True)
ui.text(
    f"<strong>Grup anahtarının kendisi de denetlendi (tez Bölüm 5.7):</strong> {tr(cs.get('doi_variants_merged', 44), 0)} "
    "çift-varyantlı DOI (büyük/küçük harf yazımları) ana hatta normalizasyonla birleştirildi; sonrasında holdout veya "
    f"CV sınırını aşan çakışma <strong>{tr(g['n_collisions_split_holdout'] + g['n_collisions_split_cv'], 0)}</strong>, "
    f"kanonik anahtar düzeyinde sınırı aşan kayıt <strong>{tr(g['n_records_split_cv'], 0)}</strong>. Temiz test MAE'si "
    f"{tr(k['mae_clean'], 2)} puan. Ham-anahtar (v0.3.x) davranışı duyarlılık katmanında korunur; normalizasyonun "
    "skora etkisi kat gürültüsü içinde kalmıştır (08 Provenans). Bu kusur ölçüldü, belgelenmiş kalıntı risk olarak "
    "raporlandı.")

ui.footer()
