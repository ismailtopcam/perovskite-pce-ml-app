# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data
from lib.ui import page, tr, tez_notu, MAVI, KIRMIZI

page("Veri Hattı: Ham → Temiz", "1️⃣")
tez_notu("Bölüm 3.4–3.6 ve 4.1",
         "43.398 ham kayıt; PCE/modül/iyon-katsayı kurallarıyla 1.913 kayıt elendi; "
         "41.485 kayıt 77 özelliğe dönüştürüldü.")

rec = data.records()
rem = data.removed()
reasons = data.csv("removed_reason_counts.csv")

NEDEN_TR = {
    "pce_not_numeric": "PCE sayısal değil / eksik",
    "pce_out_of_range": "PCE aralık dışı (0–35)",
    "module_record": "Modül kaydı (tek hücre değil)",
    "missing_ion_or_coef": "İyon/katsayı bilgisi eksik",
    "ion_coef_count_mismatch": "İyon ve katsayı sayısı uyuşmuyor",
    "coef_not_numeric": "Katsayı sayısal değil",
}
rem["neden_tr"] = rem["neden"].map(lambda r: NEDEN_TR.get(r, r))
reasons["neden_tr"] = reasons["reason"].map(lambda r: NEDEN_TR.get(r, r))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ham kayıt", tr(43398, 0))
c2.metric("Temiz kayıt", tr(len(rec), 0))
c3.metric("Elenen", tr(len(rem), 0), f"%{tr(100 * len(rem) / 43398, 1)}")
c4.metric("Özellik sayısı", "77")

tab_akis, tab_dagilim, tab_gezgin, tab_elenen = st.tabs(
    ["🔀 Dönüşüm ve eleme nedenleri", "📊 Dağılımlar", "🔎 Kayıt gezgini", "🗑️ Elenen kayıtlar"])

with tab_akis:
    left, right = st.columns([1, 1])
    with left:
        fig = px.bar(reasons.sort_values("count"), x="count", y="neden_tr",
                     orientation="h", text="count",
                     labels={"count": "Kayıt sayısı", "neden_tr": ""})
        fig.update_traces(marker_color=KIRMIZI)
        fig.update_layout(title="Eleme nedenleri (toplam 1.913)", height=340)
        st.plotly_chart(fig, width="stretch")
    with right:
        imp = pd.DataFrame({
            "Değişken": ["Band gap", "Tavlama süresi", "Tavlama sıcaklığı"],
            "Medyanla doldurulan %": [
                100 * rec["band_gap_dolduruldu"].mean(),
                100 * rec["tavlama_sure_dolduruldu"].mean(),
                100 * rec["tavlama_sicaklik_dolduruldu"].mean()],
        })
        fig = px.bar(imp, x="Medyanla doldurulan %", y="Değişken", orientation="h",
                     text=imp["Medyanla doldurulan %"].map(lambda v: f"%{tr(v, 1)}"))
        fig.update_traces(marker_color=MAVI)
        fig.update_layout(title="Eksik değer doldurma oranları (bayrakla izlenir)",
                          height=340, xaxis_range=[0, 30])
        st.plotly_chart(fig, width="stretch")
    st.info(
        "Elenen her kaydın **nedeni kayıt düzeyinde** loglanır "
        "(`outputs/logs/removed_records_log.csv`); doldurulan her değer modele ayrı bir "
        "**eksiklik bayrağı** olarak bildirilir. Böylece hattın hiçbir kararı görünmez değildir."
    )

with tab_dagilim:
    l, r = st.columns(2)
    with l:
        fig = px.histogram(rec, x="PCE", nbins=70,
                           labels={"PCE": "PCE (%)"})
        fig.update_traces(marker_color=MAVI)
        fig.update_layout(title=f"PCE dağılımı (n = {tr(len(rec), 0)}; "
                                f"medyan {tr(rec['PCE'].median(), 2)})", height=330)
        st.plotly_chart(fig, width="stretch")

        doi_sizes = rec[rec["DOI"] != "(DOI yok)"].groupby("DOI").size()
        fig = go.Figure(go.Histogram(x=doi_sizes[doi_sizes <= 60], nbinsx=60,
                                     marker_color=MAVI))
        fig.add_vline(x=doi_sizes.median(), line_dash="dash", line_color=KIRMIZI,
                      annotation_text=f"medyan = {int(doi_sizes.median())}")
        fig.update_layout(title=f"Yayın (DOI) başına kayıt sayısı "
                                f"({tr(len(doi_sizes), 0)} yayın; eksen 60'ta kesildi; "
                                f"p95={int(doi_sizes.quantile(.95))}, maks={doi_sizes.max()})",
                          yaxis_type="log", height=330,
                          xaxis_title="Yayın başına kayıt", yaxis_title="Yayın sayısı (log)")
        st.plotly_chart(fig, width="stretch")
    with r:
        site = st.radio("Kompozisyon ekseni", ["A-site", "B-site", "X-site"], horizontal=True)
        cols = {"A-site": ["A_FA", "A_MA", "A_Cs"], "B-site": ["B_Pb", "B_Sn"],
                "X-site": ["X_I", "X_Br", "X_Cl"]}[site]
        melt = rec[cols].melt(var_name="iyon", value_name="oran")
        melt["iyon"] = melt["iyon"].str.split("_").str[1]
        fig = px.histogram(melt, x="oran", color="iyon", nbins=40, barmode="overlay",
                           opacity=0.6)
        fig.update_layout(title=f"{site} iyon oranları", yaxis_type="log", height=330)
        st.plotly_chart(fig, width="stretch")

        kat = st.selectbox("Kategori dağılımı", ["mimari", "ETL", "HTL", "cozucu"],
                           format_func=lambda s: {"mimari": "Hücre mimarisi", "ETL": "ETL",
                                                  "HTL": "HTL", "cozucu": "Çözücü"}[s])
        vc = rec[kat].value_counts().head(10)[::-1]
        fig = px.bar(x=vc.values, y=[v[:34] for v in vc.index], orientation="h")
        fig.update_traces(marker_color=MAVI)
        fig.update_layout(title=f"En sık 10 kategori — {kat}", height=330,
                          xaxis_title="Kayıt", yaxis_title="")
        st.plotly_chart(fig, width="stretch")

with tab_gezgin:
    st.markdown("**Filtreler** — temiz veri kümesinde gezinin, bir kayda tıklayıp "
                "hattın o kayda ne yaptığını görün.")
    f1, f2, f3, f4 = st.columns(4)
    pce_r = f1.slider("PCE aralığı", 0.0, 35.0, (0.0, 35.0), 0.5)
    bg_r = f2.slider("Band gap (eV)", 1.0, 3.6, (1.0, 3.6), 0.05)
    arch_sel = f3.multiselect("Mimari", rec["mimari"].value_counts().index.tolist()[:10])
    bolme_sel = f4.multiselect("Bölme", ["eğitim", "holdout-test"])
    f5, f6, f7, f8 = st.columns(4)
    etl_sel = f5.multiselect("ETL", rec["ETL"].value_counts().index.tolist()[:15])
    htl_sel = f6.multiselect("HTL", rec["HTL"].value_counts().index.tolist()[:15])
    solv_sel = f7.multiselect("Çözücü", rec["cozucu"].value_counts().index.tolist()[:15])
    doi_q = f8.text_input("DOI içinde ara")

    m = rec["PCE"].between(*pce_r) & rec["band_gap"].between(*bg_r)
    if arch_sel: m &= rec["mimari"].isin(arch_sel)
    if etl_sel: m &= rec["ETL"].isin(etl_sel)
    if htl_sel: m &= rec["HTL"].isin(htl_sel)
    if solv_sel: m &= rec["cozucu"].isin(solv_sel)
    if bolme_sel: m &= rec["bolme"].isin(bolme_sel)
    if doi_q: m &= rec["DOI"].str.contains(doi_q, case=False, regex=False)
    sub = rec[m]
    st.caption(f"**{tr(len(sub), 0)}** kayıt eşleşti.")

    show = sub[["row_id", "DOI", "kompozisyon", "PCE", "mimari", "ETL", "HTL",
                "band_gap", "bolme", "tahmin"]].head(2000)
    st.dataframe(show, width="stretch", height=320, hide_index=True,
                 column_config={"row_id": "Kayıt No", "tahmin": st.column_config.NumberColumn(
                     "Model tahmini", format="%.2f")})

    if len(sub):
        rid = st.selectbox("Kayıt detayı", sub["row_id"].head(2000),
                           format_func=lambda i: f"#{i} — {sub.loc[sub.row_id == i, 'kompozisyon'].iloc[0][:40]}")
        r = sub[sub["row_id"] == rid].iloc[0]
        st.success("**Kayıt durumu: Modellemeye alındı** ✅")
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"""
- **Kompozisyon:** {r['kompozisyon']}
- **Yığın:** {r['mimari']} / {r['ETL'][:30]} / {r['HTL'][:30]}
- **Çözücü:** {r['cozucu'][:30]} | **Gerçek PCE:** {tr(r['PCE'], 2)}
- **DOI grubu:** `{r['DOI'][:50]}` → **{r['bolme']}** (CV kat {int(r['cv_fold'])})
""")
        with d2:
            islemler = []
            for flag, ad, val in [("band_gap_dolduruldu", "Band gap", r["band_gap"]),
                                  ("tavlama_sicaklik_dolduruldu", "Tavlama sıcaklığı", r["tavlama_sicaklik"]),
                                  ("tavlama_sure_dolduruldu", "Tavlama süresi", r["tavlama_sure"])]:
                if r[flag]:
                    islemler.append(f"🔧 {ad} **medyanla dolduruldu** → {tr(val, 2)} (+ eksiklik bayrağı)")
                else:
                    islemler.append(f"✓ {ad} raporlanmış: {tr(val, 2)}")
            islemler.append("✓ A/B/X katsayıları sayısal vektöre dönüştürüldü")
            islemler.append(f"✓ DOI grubu atandı → aynı ham DOI anahtarını taşıyan kayıtlar asla eğitim+test'e bölünmez")
            if r["bolme"] == "holdout-test" and not np.isnan(r["tahmin"]):
                islemler.append(f"🎯 Holdout tahmini: **{tr(r['tahmin'], 2)}** "
                                f"(mutlak hata {tr(r['mutlak_hata'], 2)})")
            st.markdown("**Uygulanan işlemler:**\n" + "\n".join(f"- {i}" for i in islemler))

with tab_elenen:
    st.markdown("**1.913 elenen kaydın tamamı, nedenleriyle.** Hattın açıklanabilirlik "
                "sözleşmesi: hiçbir kayıt sessizce kaybolmaz.")
    sec = st.multiselect("Nedene göre filtrele", reasons["neden_tr"].tolist())
    sub = rem if not sec else rem[rem["neden_tr"].isin(sec)]
    st.caption(f"**{tr(len(sub), 0)}** kayıt.")
    st.dataframe(
        sub[["row_id", "neden_tr", "DOI", "PCE_ham", "Modul",
             "A_iyonlar", "A_katsayilar", "B_iyonlar", "X_iyonlar"]].head(2000),
        width="stretch", height=340, hide_index=True,
        column_config={"row_id": "Ham kayıt no", "neden_tr": "Eleme nedeni",
                       "PCE_ham": "Ham PCE"})
    if len(sub):
        rid = st.selectbox("Elenen kayıt detayı", sub["row_id"].head(2000))
        r = sub[sub["row_id"] == rid].iloc[0]
        st.error(f"**Kayıt durumu: Modellemeye alınmadı** — {r['neden_tr']}")
        st.markdown(f"""
- **Ham PCE:** `{r['PCE_ham']}` | **Modül:** `{r['Modul']}` | **Mimari:** {r['mimari']}
- **A:** `{r['A_iyonlar']}` × `{r['A_katsayilar']}`
- **B:** `{r['B_iyonlar']}` × `{r['B_katsayilar']}`
- **X:** `{r['X_iyonlar']}` × `{r['X_katsayilar']}`
- **DOI:** `{str(r['DOI'])[:60]}`
""")
