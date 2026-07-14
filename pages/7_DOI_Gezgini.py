# -*- coding: utf-8 -*-
import plotly.express as px
import streamlit as st

from lib import data
from lib.ui import page, tr, tez_notu, MAVI

page("DOI Gezgini — Yayın Düzeyinde İzlenebilirlik", "7️⃣")
tez_notu("Bölüm 3.8, 4.1 ve 5.7",
         "Aynı yayının kardeş cihazları çok benzerdir; bu yüzden bölmeler kayıt değil "
         "YAYIN (DOI) düzeyinde yapılır. Bu sayfa o kuralı somutlaştırır.")

doi = data.doi_summary()
rec = data.records()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Yayın (grup)", tr(len(doi), 0))
c2.metric("Medyan kayıt/yayın", tr(int(doi["kayit"].median()), 0))
c3.metric("En büyük grup", tr(int(doi["kayit"].max()), 0),
          "DOI'siz kayıtların yapay grubu")
c4.metric("Holdout'a ayrılan yayın", tr(int((doi["bolme"] == "holdout-test").sum()), 0))

st.markdown("---")
l, r = st.columns([2, 3])

with l:
    q = st.text_input("DOI ara", placeholder="örn. 10.1039 — adresin bir parçasını yazmanız yeterli")
    dsub = doi[doi["DOI"].str.contains(q, case=False, regex=False)] if q else \
        doi.sort_values("kayit", ascending=False)
    st.caption(f"{tr(len(dsub), 0)} yayın")
    if dsub.empty:
        st.info("Aramanızla eşleşen yayın bulunamadı — adresin farklı bir parçasını deneyin.")
        st.stop()
    st.dataframe(dsub[["DOI", "kayit", "pce_medyan", "bolme"]].head(300),
                 hide_index=True, height=280, use_container_width=True,
                 column_config={"pce_medyan": st.column_config.NumberColumn(
                     "PCE medyan", format="%.1f")})
    secim = st.selectbox("Yayın seç", dsub["DOI"].head(300))

with r:
    d = doi[doi["DOI"] == secim].iloc[0]
    kayitlar = rec[rec["DOI"] == secim]
    egitimde = d["bolme"] == "eğitim"
    st.subheader(f"`{secim[:70]}`")
    if secim == "(DOI yok)":
        st.warning("**Yapay grup:** DOI'si raporlanmamış 201 kayıt tek grupta toplanır; "
                   "böylece bunlar da asla eğitim+test'e bölünmez (tez Bölüm 3.8).")
    b1, b2, b3 = st.columns(3)
    b1.metric("Kayıt", tr(int(d["kayit"]), 0))
    b2.metric("PCE aralığı", f"{tr(d['pce_min'], 1)} – {tr(d['pce_maks'], 1)}")
    b3.metric("CV katı", f"{int(d['cv_fold'])}")
    if egitimde:
        st.success("🔒 **Bu yayın EĞİTİM kümesinde.** Aynı DOI'nin hiçbir kaydı holdout "
                   "test kümesine alınmamıştır — skor, bu yayının kardeş cihazlarından "
                   "beslenemez.")
    else:
        st.info(f"🎯 **Bu yayın HOLDOUT-TEST kümesinde.** Modeli eğitirken bu yayının "
                f"hiçbir kaydı görülmedi. Yayın-içi ortalama mutlak hata: "
                f"**{tr(d['test_mae'], 2)} puan**.")

    fig = px.histogram(kayitlar, x="PCE", nbins=25, labels={"PCE": "PCE (%)"})
    fig.update_traces(marker_color=MAVI)
    fig.update_layout(height=230, title="Yayının PCE dağılımı", margin=dict(t=40))
    st.plotly_chart(fig, use_container_width=True)

    goster = kayitlar[["kompozisyon", "mimari", "ETL", "HTL", "PCE", "tahmin",
                       "mutlak_hata"]].rename(columns={
        "kompozisyon": "Kompozisyon", "PCE": "Gerçek PCE",
        "tahmin": "Tahmin", "mutlak_hata": "Hata"})
    st.dataframe(goster, hide_index=True, use_container_width=True, height=220,
                 column_config={c: st.column_config.NumberColumn(c, format="%.2f")
                                for c in ["Gerçek PCE", "Tahmin", "Hata"]})

with st.expander("🔍 Grup anahtarının kendisi de denetlendi (tez Bölüm 5.7)"):
    g = data.js("doi_grup_dogrulama.json")
    k = data.js("kontamine_test_maesi.json")
    st.markdown(f"""
Ham DOI dizgileri üzerinde denetim: **{g['n_collisions_normalized']} yayın** büyük/küçük
harf varyantıyla çift kayıtlı; bunlardan **{g['n_collisions_split_holdout']}**'u holdout
sınırını, **{g['n_collisions_split_cv']}**'si CV kat sınırını aşıyor
({tr(g['n_records_split_cv'], 0)} kayıt, %{tr(g['pct_records_split_cv'], 2)}).
Sınır aşan yayınların test kayıtlarında hata **düşük değil yüksek** çıktı
(MAE {tr(k['mae_contaminated'], 2)} vs {tr(k['mae_clean'], 2)}) ve DOI-normalizasyonlu
duyarlılık koşumunda skor değişimi kat gürültüsü içinde kaldı — yani bu kusur ölçüldü,
skor şişirmediği kayıt düzeyinde doğrulandı ve belgelenmiş kalıntı risk olarak raporlandı.
""")
