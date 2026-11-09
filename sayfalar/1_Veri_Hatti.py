# -*- coding: utf-8 -*-
"""01 Veri Hattı — ham → temiz dönüşüm, eleme nedenleri, dağılımlar, kayıt gezgini, elenen kayıtlar."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data, ui
from lib.ui import tr, INK, ACC, BLUE, N900

meta = data.js("app_meta.json")
rec = data.records()
rem = data.removed()
reasons = data.csv("removed_reason_counts.csv")

NEDEN_TR = {
    "pce_not_numeric": "PCE sayısal değil / eksik",
    "pce_out_of_range": "PCE aralık dışı (0–35)",
    "module_record": "Modül kaydı (tek hücre değil)",
    "missing_ion_or_coef": "İyon / katsayı bilgisi eksik",
    "ion_coef_count_mismatch": "İyon ve katsayı sayısı uyuşmuyor",
    "coef_not_numeric": "Katsayı sayısal değil",
}
rem["neden_tr"] = rem["neden"].map(lambda r: NEDEN_TR.get(r, r))
reasons["neden_tr"] = reasons["reason"].map(lambda r: NEDEN_TR.get(r, r))
n_ham, n_temiz, n_elenen = meta["n_ham"], len(rec), len(rem)

ui.page_header(
    "01 — Veri Hattı · Tez Bölüm 3.4–3.6 ve 4.1",
    "Ham → temiz: camdan kutu.",
    f"{tr(n_ham, 0)} ham kayıt; PCE / modül / iyon-katsayı kurallarıyla {tr(n_elenen, 0)} kayıt elendi; "
    f"{tr(n_temiz, 0)} kayıt 77 özelliğe dönüştürüldü. Hiçbir kayıt sessizce kaybolmaz: her eleme, kayıt "
    "düzeyinde nedeniyle loglanır.",
)

ui.stats([
    ("Ham kayıt", tr(n_ham, 0), "Perovskite Database anlık görüntüsü"),
    ("Temiz kayıt", tr(n_temiz, 0), f"{tr(rec['DOI'].nunique(), 0)} yayın grubu"),
    ("Elenen", f"−{tr(n_elenen, 0)}", f"%{tr(100 * n_elenen / n_ham, 1)} · her biri nedeniyle loglu", "acc"),
    ("Özellik", "77", "kompozisyon 14 · cihaz 43 · süreç 20"),
])

# ---------------------------------------------------------------- eleme nedenleri + doldurma oranları
left, right = st.columns(2, gap="medium")
with left, ui.card():
    ui.kicker("Eleme nedenleri", f"toplam {tr(n_elenen, 0)} kayıt", tone="ink")
    rs = reasons.sort_values("count", ascending=False)
    ui.bar_rows([
        dict(name=r.neden_tr, value=int(r["count"]),
             value_str=(f'<span style="color:var(--acc700)">{tr(int(r["count"]), 0)}</span>' if i == 0
                        else tr(int(r["count"]), 0)),
             tone="acc" if i == 0 else "ink", bold=False)
        for i, (_, r) in enumerate(rs.iterrows())
    ], vmax=float(rs["count"].max()), slim=True)
    ui.text("Elenen her kaydın <strong>nedeni kayıt düzeyinde</strong> loglanır "
            "(<span class='m-mono'>outputs/logs/removed_records_log.csv</span>); hattın açıklanabilirlik "
            "sözleşmesi: hiçbir kayıt sessizce kaybolmaz.", mute=True)
with right, ui.card():
    ui.kicker("Eksik değer doldurma oranları", "bayrakla izlenir · eksen 0–30", tone="ink")
    imp = [("Band gap", 100 * rec["band_gap_dolduruldu"].mean()),
           ("Tavlama süresi", 100 * rec["tavlama_sure_dolduruldu"].mean()),
           ("Tavlama sıcaklığı", 100 * rec["tavlama_sicaklik_dolduruldu"].mean())]
    ui.bar_rows([dict(name=n, value=v, value_str=f"%{tr(v, 1)}", tone="blue2", bold=False) for n, v in imp],
                vmax=30.0, slim=True)
    ui.text("Doldurulan her değer (band gap, tavlama sıcaklığı/süresi → eğitim medyanı) modele ayrı bir "
            "<strong>eksiklik bayrağı</strong> olarak bildirilir; hattın hiçbir kararı görünmez değildir.",
            mute=True)

# ---------------------------------------------------------------- modüller
tab_dagilim, tab_gezgin, tab_elenen = st.tabs(["Dağılımlar", "Kayıt gezgini", "Elenen kayıtlar"])

with tab_dagilim:
    l, r = st.columns(2, gap="large")
    with l:
        fig = px.histogram(rec, x="PCE", nbins=70, labels={"PCE": "PCE (%)"})
        fig.update_traces(marker_color=N900)
        fig.update_layout(yaxis_title="Kayıt")
        ui.chart(fig, height=320, title=f"PCE dağılımı (n = {tr(len(rec), 0)}; medyan {tr(rec['PCE'].median(), 2)})")

        doi_sizes = rec[rec["DOI"] != "(DOI yok)"].groupby("DOI").size()
        fig = go.Figure(go.Histogram(x=doi_sizes[doi_sizes <= 60], nbinsx=60, marker_color=N900))
        fig.add_vline(x=doi_sizes.median(), line_dash="dash", line_color=ACC,
                      annotation_text=f"medyan = {int(doi_sizes.median())}")
        fig.update_layout(yaxis_type="log", xaxis_title="Yayın başına kayıt", yaxis_title="Yayın sayısı (log)")
        ui.chart(fig, height=320, title=f"Yayın (DOI) başına kayıt sayısı ({tr(len(doi_sizes), 0)} yayın; eksen "
                                        f"60'ta kesildi; p95 = {int(doi_sizes.quantile(.95))}, maks = {doi_sizes.max()})")
    with r:
        site = st.segmented_control("Kompozisyon ekseni", ["A-site", "B-site", "X-site"], default="A-site")
        site = site or "A-site"
        cols = {"A-site": ["A_FA", "A_MA", "A_Cs"], "B-site": ["B_Pb", "B_Sn"],
                "X-site": ["X_I", "X_Br", "X_Cl"]}[site]
        melt = rec[cols].melt(var_name="iyon", value_name="oran")
        melt["iyon"] = melt["iyon"].str.split("_").str[1]
        fig = px.histogram(melt, x="oran", color="iyon", nbins=40, barmode="overlay", opacity=0.65,
                           color_discrete_sequence=[N900, BLUE, ACC])
        fig.update_layout(yaxis_type="log", xaxis_title="Oran", yaxis_title="Kayıt (log)",
                          legend_title_text="")
        ui.chart(fig, height=300, title=f"{site} iyon oranları")

        kat = st.selectbox("Kategori dağılımı", ["mimari", "ETL", "HTL", "cozucu"],
                           format_func=lambda s: {"mimari": "Hücre mimarisi", "ETL": "ETL",
                                                  "HTL": "HTL", "cozucu": "Çözücü"}[s])
        vc = rec[kat].value_counts().head(10)[::-1]
        fig = px.bar(x=vc.values, y=[v[:34] for v in vc.index], orientation="h")
        fig.update_traces(marker_color=N900)
        fig.update_layout(xaxis_title="Kayıt", yaxis_title="")
        ui.chart(fig, height=320, title=f"En sık 10 kategori — {kat}")

with tab_gezgin:
    ui.text("<strong>Filtreler</strong> — temiz veri kümesinde gezinin, bir kaydı seçip hattın o kayda ne "
            "yaptığını görün.", mute=True)
    f1, f2, f3, f4 = st.columns(4)
    pce_r = f1.slider("PCE aralığı", 0.0, 35.0, (0.0, 35.0), 0.5)
    bg_r = f2.slider("Band gap (eV)", 1.0, 3.6, (1.0, 3.6), 0.05)
    arch_sel = f3.multiselect("Mimari", rec["mimari"].value_counts().index.tolist()[:10], placeholder="Tümü")
    bolme_sel = f4.multiselect("Bölme", ["eğitim", "holdout-test"], placeholder="Tümü")
    f5, f6, f7, f8 = st.columns(4)
    etl_sel = f5.multiselect("ETL", rec["ETL"].value_counts().index.tolist()[:15], placeholder="Tümü")
    htl_sel = f6.multiselect("HTL", rec["HTL"].value_counts().index.tolist()[:15], placeholder="Tümü")
    solv_sel = f7.multiselect("Çözücü", rec["cozucu"].value_counts().index.tolist()[:15], placeholder="Tümü")
    doi_q = f8.text_input("DOI içinde ara", placeholder="örn. 10.1039")

    m = rec["PCE"].between(*pce_r) & rec["band_gap"].between(*bg_r)
    if arch_sel: m &= rec["mimari"].isin(arch_sel)
    if etl_sel: m &= rec["ETL"].isin(etl_sel)
    if htl_sel: m &= rec["HTL"].isin(htl_sel)
    if solv_sel: m &= rec["cozucu"].isin(solv_sel)
    if bolme_sel: m &= rec["bolme"].isin(bolme_sel)
    if doi_q: m &= rec["DOI"].str.contains(doi_q, case=False, regex=False)
    sub = rec[m]
    ui.kicker(f"{tr(len(sub), 0)} kayıt eşleşti", tone="mute")

    show = sub[["row_id", "DOI", "kompozisyon", "PCE", "mimari", "ETL", "HTL",
                "band_gap", "bolme", "tahmin"]].head(2000)
    st.dataframe(show, width="stretch", height=320, hide_index=True,
                 column_config={"row_id": "Kayıt No", "tahmin": st.column_config.NumberColumn(
                     "Model tahmini", format="%.2f")})

    if len(sub):
        etiket = dict(zip(sub["row_id"].head(2000), sub["kompozisyon"].head(2000)))
        rid = st.selectbox("Kayıt detayı", list(etiket),
                           format_func=lambda i: f"#{i} — {etiket[i][:40]}")
        r = sub[sub["row_id"] == rid].iloc[0]
        d1, d2 = st.columns(2, gap="medium")
        with d1:
            ui.box(
                f"<p><strong>Kompozisyon:</strong> {ui.esc(r['kompozisyon'])}</p>"
                f"<p><strong>Yığın:</strong> {ui.esc(r['mimari'])} / {ui.esc(r['ETL'][:30])} / {ui.esc(r['HTL'][:30])}</p>"
                f"<p><strong>Çözücü:</strong> {ui.esc(r['cozucu'][:30])} · <strong>Gerçek PCE:</strong> {tr(r['PCE'], 2)}</p>"
                f"<p><strong>DOI grubu:</strong> <span class='m-mono'>{ui.esc(r['DOI'][:50])}</span> → "
                f"<strong>{ui.esc(r['bolme'])}</strong> (CV kat {int(r['cv_fold'])})</p>",
                chip="Kayıt durumu: modellemeye alındı", tone="blue")
        with d2, ui.card():
            islemler = []
            for flag, ad, val in [("band_gap_dolduruldu", "Band gap", r["band_gap"]),
                                  ("tavlama_sicaklik_dolduruldu", "Tavlama sıcaklığı", r["tavlama_sicaklik"]),
                                  ("tavlama_sure_dolduruldu", "Tavlama süresi", r["tavlama_sure"])]:
                if r[flag]:
                    islemler.append(f"{ad} <strong>medyanla dolduruldu</strong> → {tr(val, 2)} (+ eksiklik bayrağı)")
                else:
                    islemler.append(f"{ad} raporlanmış: {tr(val, 2)}")
            islemler.append("A/B/X katsayıları sayısal vektöre dönüştürüldü")
            islemler.append("DOI grubu atandı → aynı kanonik DOI anahtarını taşıyan kayıtlar asla eğitim+test'e bölünmez")
            if r["bolme"] == "holdout-test" and not np.isnan(r["tahmin"]):
                islemler.append(f"Holdout tahmini: <strong>{tr(r['tahmin'], 2)}</strong> "
                                f"(mutlak hata {tr(r['mutlak_hata'], 2)})")
            ui.kicker("Uygulanan işlemler", tone="ink")
            ui.steps([(str(i + 1), s) for i, s in enumerate(islemler)])

with tab_elenen:
    ui.text(f"<strong>{tr(n_elenen, 0)} elenen kaydın tamamı, nedenleriyle.</strong> Hattın açıklanabilirlik "
            "sözleşmesi: hiçbir kayıt sessizce kaybolmaz.", mute=True)
    sec = st.multiselect("Nedene göre filtrele", reasons["neden_tr"].tolist(), placeholder="Tümü")
    subr = rem if not sec else rem[rem["neden_tr"].isin(sec)]
    ui.kicker(f"{tr(len(subr), 0)} kayıt", tone="mute")
    st.dataframe(
        subr[["row_id", "neden_tr", "DOI", "PCE_ham", "Modul",
             "A_iyonlar", "A_katsayilar", "B_iyonlar", "X_iyonlar"]].head(2000),
        width="stretch", height=340, hide_index=True,
        column_config={"row_id": "Ham kayıt no", "neden_tr": "Eleme nedeni", "PCE_ham": "Ham PCE"})
    if len(subr):
        rid = st.selectbox("Elenen kayıt detayı", subr["row_id"].head(2000))
        r = subr[subr["row_id"] == rid].iloc[0]
        ui.box(
            f"<p><strong>Ham PCE:</strong> <span class='m-mono'>{ui.esc(r['PCE_ham'])}</span> · "
            f"<strong>Modül:</strong> <span class='m-mono'>{ui.esc(r['Modul'])}</span> · "
            f"<strong>Mimari:</strong> {ui.esc(r['mimari'])}</p>"
            f"<p><strong>A:</strong> <span class='m-mono'>{ui.esc(r['A_iyonlar'])}</span> × "
            f"<span class='m-mono'>{ui.esc(r['A_katsayilar'])}</span></p>"
            f"<p><strong>B:</strong> <span class='m-mono'>{ui.esc(r['B_iyonlar'])}</span> × "
            f"<span class='m-mono'>{ui.esc(r['B_katsayilar'])}</span></p>"
            f"<p><strong>X:</strong> <span class='m-mono'>{ui.esc(r['X_iyonlar'])}</span> × "
            f"<span class='m-mono'>{ui.esc(r['X_katsayilar'])}</span></p>"
            f"<p><strong>DOI:</strong> <span class='m-mono'>{ui.esc(str(r['DOI'])[:60])}</span></p>",
            chip=f"Kayıt durumu: modellemeye alınmadı — {ui.esc(r['neden_tr'])}", accent=True)

ui.footer()
