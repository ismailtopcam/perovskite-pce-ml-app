# -*- coding: utf-8 -*-
"""05 Gerçek – Tahmin — holdout kayıtlarında kayıt düzeyinde hata analizi."""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from lib import data, ui
from lib.ui import tr, ACC, N900

rec = data.records()
conf = data.js("conformal.json")
HW90 = float(conf["marginal"]["90"]["half_width"])
COV = 100 * float(conf["marginal"]["90"]["empirical_coverage"])
ho = rec[rec["bolme"] == "holdout-test"].copy()
ho["kapsandi"] = ho["mutlak_hata"] <= HW90
ssr = ((ho["PCE"] - ho["tahmin"]) ** 2).sum()
sst = ((ho["PCE"] - ho["PCE"].mean()) ** 2).sum()

ui.page_header(
    "05 — Gerçek Deney – Model Tahmini · Tez Bölüm 4.7",
    "Model nerede yanılıyor?",
    f"{tr(len(ho), 0)} holdout kaydında (eğitimden kanonik DOI anahtarı düzeyinde ayrık tutulan yayınlar) "
    "kayıt düzeyinde hata analizi.",
)

ui.stats([
    ("Holdout kayıt", tr(len(ho), 0), f"{tr(ho['DOI'].nunique(), 0)} yayın grubundan"),
    ("MAE", f"{tr(ho['mutlak_hata'].mean(), 2)} <small>puan</small>",
     f"medyan mutlak hata {tr(ho['mutlak_hata'].median(), 2)}"),
    ("Holdout R²", tr(1 - ssr / sst, 3), "grup-CV ile tutarlı", "blue"),
    ("%90 bandın kapsaması", f"%{tr(100 * ho['kapsandi'].mean(), 1)}",
     f"tüm holdout; conformal test alt kümesinde (n = {tr(conf['n_conformal_test'], 0)}) %{tr(COV, 1)}"),
])

tab1, tab2, tab3 = st.tabs(["Kayıt bazında", "Hata grupları", "Model nerede yanılıyor?"])

with tab1:
    grup = st.segmented_control("Göster", ["En isabetli 50", "Tipik 50 (medyan çevresi)", "En büyük hatalı 50"],
                                default="En isabetli 50", label_visibility="collapsed")
    grup = grup or "En isabetli 50"
    s = ho.sort_values("mutlak_hata")
    if grup.startswith("En isabetli"):
        sub = s.head(50)
    elif grup.startswith("Tipik"):
        mid = len(s) // 2
        sub = s.iloc[mid - 25: mid + 25]
    else:
        sub = s.tail(50)
    view = sub[["kompozisyon", "mimari", "HTL", "PCE", "tahmin", "mutlak_hata", "kapsandi", "DOI"]].rename(columns={
        "kompozisyon": "Kompozisyon", "mimari": "Mimari", "PCE": "Gerçek PCE",
        "tahmin": "Tahmin", "mutlak_hata": "Mutlak hata", "kapsandi": "%90 bant kapsıyor?"})
    st.dataframe(view, hide_index=True, width="stretch", height=330,
                 column_config={c: st.column_config.NumberColumn(c, format="%.2f")
                                for c in ["Gerçek PCE", "Tahmin", "Mutlak hata"]})
    r = sub.iloc[0]
    ui.text(f"<strong>Örnek okuma (ilk satır):</strong> gerçek PCE <strong>{tr(r['PCE'], 2)}</strong>, model "
            f"tahmini <strong>{tr(r['tahmin'], 2)}</strong>, mutlak hata <strong>{tr(r['mutlak_hata'], 2)}</strong>; "
            f"%90 aralık [{tr(r['tahmin'] - HW90, 1)}; {tr(r['tahmin'] + HW90, 1)}] gerçek değeri "
            f"<strong>{'kapsıyor' if r['kapsandi'] else 'kapsamıyor'}</strong>.", mute=True)

with tab2:
    l, rr = st.columns(2, gap="medium")
    with l, ui.card():
        ui.kicker("Hata büyüklüğü dağılımı", "mutlak hata, PCE puanı", tone="ink")
        bins = [0, 1, 2, 3, 5, 10, 40]
        labels = ["≤1", "1–2", "2–3", "3–5", "5–10", ">10"]
        tones = ["blue", "blue", "blue2", "mid", "soft", "acc"]
        d = pd.cut(ho["mutlak_hata"], bins, labels=labels).value_counts().reindex(labels)
        share = 100 * d.values / len(ho)
        ui.bar_rows([dict(name=f"{lab} puan", value=v, value_str=f"%{tr(v, 1)}", value_sub=f"({tr(int(n), 0)} kayıt)",
                          tone=t, bold=False) for lab, v, n, t in zip(labels, share, d.values, tones)],
                    vmax=float(max(share)), slim=True)
        ui.text(f"Kayıtların %{tr(100 * (ho['mutlak_hata'] <= 2).mean(), 0)}'ı ≤2 puan, "
                f"%{tr(100 * (ho['mutlak_hata'] <= 3).mean(), 0)}'i ≤3 puan hatayla tahmin ediliyor (tez Bölüm 4.7).",
                mute=True)
    with rr:
        err = ho["tahmin"] - ho["PCE"]
        fig = px.histogram(err, nbins=80, labels={"value": "İşaretli hata (tahmin − gerçek)"})
        fig.update_traces(marker_color=N900, showlegend=False)
        fig.add_vline(x=0, line_color=ACC)
        fig.update_layout(yaxis_title="Kayıt")
        ui.chart(fig, height=340, title=f"Yön: >+5 aşırı tahmin %{tr(100 * (err > 5).mean(), 1)} · "
                                        f"<−5 eksik tahmin %{tr(100 * (err < -5).mean(), 1)}")
        ui.text("Sağa çarpık kuyruk: model düşük verimli kayıtları zaman zaman olduğundan yüksek tahmin ediyor; bu, "
                "reçete-içi etiket gürültüsünün beklenen izidir (tez Bölüm 5.1, Tablo 5.1).", mute=True)

with tab3:
    l, rr = st.columns([7, 5], gap="medium")
    seg = pd.DataFrame([
        ("Tümü", ho["mutlak_hata"].mean(), len(ho)),
        ("Sn içeren (B_Sn > 0)", ho.loc[ho["B_Sn"] > 0, "mutlak_hata"].mean(), int((ho["B_Sn"] > 0).sum())),
        ("HTL-free (HTL = none)", ho.loc[ho["HTL"] == "none", "mutlak_hata"].mean(), int((ho["HTL"] == "none").sum())),
        ("Yüksek band gap (>1,7 eV)", ho.loc[ho["band_gap"] > 1.7, "mutlak_hata"].mean(), int((ho["band_gap"] > 1.7).sum())),
        ("Band gap doldurulmuş", ho.loc[ho["band_gap_dolduruldu"], "mutlak_hata"].mean(), int(ho["band_gap_dolduruldu"].sum())),
        ("Br-ağırlıklı (X_Br ≥ 0,4)", ho.loc[ho["X_Br"] >= 0.4, "mutlak_hata"].mean(), int((ho["X_Br"] >= 0.4).sum())),
        ("Standart bölge (FA-Pb-I, n-i-p)",
         ho.loc[(ho["A_FA"] > 0.5) & (ho["B_Pb"] > 0.9) & (ho["X_I"] > 0.7) & (ho["mimari"] == "nip"), "mutlak_hata"].mean(),
         int(((ho["A_FA"] > 0.5) & (ho["B_Pb"] > 0.9) & (ho["X_I"] > 0.7) & (ho["mimari"] == "nip")).sum())),
    ], columns=["Segment", "MAE", "n"])
    tum = float(seg.loc[0, "MAE"])
    with l, ui.card():
        ui.kicker("Segmentlere göre MAE", "tezdeki 'giderilemeyen gürültü' savının kayıt-düzeyi görünümü", tone="ink")
        ss = seg.sort_values("MAE")
        ui.bar_rows([dict(name=r.Segment, value=r.MAE, value_str=tr(r.MAE, 2), value_sub=f"(n = {tr(int(r.n), 0)})",
                          tone="acc" if (r.Segment != "Tümü" and r.MAE > tum) else ("ink" if r.Segment == "Tümü" else "blue"),
                          bold=(r.Segment == "Tümü")) for r in ss.itertuples()],
                    vmax=float(ss["MAE"].max()) * 1.05, slim=True)
        ui.text("Turuncu: genel ortalamanın üzerinde; mavi: altında; koyu: tüm holdout.", mute=True)
    with rr, ui.card():
        ui.kicker("Tezin kayıt-düzeyi bulgusu", tone="ink")
        ad = conf["applicability_domain"]
        ustte = [r.Segment for r in seg.itertuples() if r.Segment != "Tümü" and r.MAE > tum]
        ust_txt = (f"{', '.join(ustte)} kayıtlarında ise hata genel ortalamanın üzerindedir" if ustte
                   else "bu kesitte hiçbir segment genel ortalamayı aşmaz")
        ui.text(
            "<p>Model kanonik <strong>FA-Pb-I bölgesinde güçlü</strong>, az örneklenmiş bölgelerde zayıftır — "
            "beklenen ve tezde tartışılan örüntü.</p>"
            "<p>Beklenenin tersine, az temsil edilen alt kümelerin çoğunda (Sn'li, geniş band gap, Br-ağırlıklı) "
            "MAE <strong>genel ortalamanın altındadır</strong>: bu bölgelerde PCE dar ve görece düşük bir banda "
            f"toplandığından mutlak hata küçülür; {ust_txt}. "
            "Düşük alt-grup MAE'si güvenilirlik anlamına gelmez: kayıt sayısı azdır (Bölüm 4.10).</p>"
            f"<p>Uygulanabilirlik alanı içi / dışı MAE: <strong>{tr(ad['mae_inside'], 2)} / {tr(ad['mae_outside'], 2)}</strong> "
            "— özellik-uzayı mesafesi hata düzeyini ayırt etmiyor; \"uzaklık ≠ güven\". Kanonik FA-Pb-I bölgesi, "
            "verinin büyük kısmını taşıdığı için genel hatayı belirler.</p>")

ui.footer()
