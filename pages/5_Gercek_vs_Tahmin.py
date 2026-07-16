# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from lib import data
from lib.ui import page, tr, tez_notu, MAVI, KIRMIZI

page("Gerçek Deney vs Model Tahmini", "5️⃣")
tez_notu("Bölüm 4.7", "8.147 holdout kaydında (eğitimden ham DOI anahtarı düzeyinde ayrık "
                      "tutulan yayınlar) kayıt düzeyinde hata analizi.")

rec = data.records()
ho = rec[rec["bolme"] == "holdout-test"].copy()
HW90 = 6.4186
ho["kapsandi"] = ho["mutlak_hata"] <= HW90

c1, c2, c3, c4 = st.columns(4)
c1.metric("Holdout kayıt", tr(len(ho), 0))
c2.metric("MAE", tr(ho["mutlak_hata"].mean(), 2) + " puan")
c3.metric("Medyan mutlak hata", tr(ho["mutlak_hata"].median(), 2) + " puan")
c4.metric("%90 bandın kapsaması", f"%{tr(100 * ho['kapsandi'].mean(), 1)}")

tab1, tab2, tab3 = st.tabs(["🎯 Kayıt bazında", "📉 Hata grupları", "🔬 Model nerede yanılıyor?"])

with tab1:
    grup = st.radio("Göster", ["En isabetli 50", "Tipik 50 (medyan çevresi)",
                               "En büyük hatalı 50"], horizontal=True)
    s = ho.sort_values("mutlak_hata")
    if grup.startswith("En isabetli"):
        sub = s.head(50)
    elif grup.startswith("Tipik"):
        mid = len(s) // 2
        sub = s.iloc[mid - 25: mid + 25]
    else:
        sub = s.tail(50)
    view = sub[["kompozisyon", "mimari", "HTL", "PCE", "tahmin", "mutlak_hata",
                "kapsandi", "DOI"]].rename(columns={
        "kompozisyon": "Kompozisyon", "mimari": "Mimari", "PCE": "Gerçek PCE",
        "tahmin": "Tahmin", "mutlak_hata": "Mutlak hata", "kapsandi": "%90 bant kapsıyor?"})
    st.dataframe(view, hide_index=True, width="stretch", height=330,
                 column_config={c: st.column_config.NumberColumn(c, format="%.2f")
                                for c in ["Gerçek PCE", "Tahmin", "Mutlak hata"]})
    r = sub.iloc[0]
    st.markdown(f"""
**Örnek okuma (ilk satır):** gerçek PCE **{tr(r['PCE'], 2)}**, model tahmini
**{tr(r['tahmin'], 2)}**, mutlak hata **{tr(r['mutlak_hata'], 2)}**; %90 aralık
[{tr(r['tahmin'] - HW90, 1)}; {tr(r['tahmin'] + HW90, 1)}] gerçek değeri
**{"kapsıyor ✅" if r['kapsandi'] else "kapsamıyor ❌"}**.
""")

with tab2:
    l, rr = st.columns(2)
    with l:
        bins = [0, 1, 2, 3, 5, 10, 40]
        labels = ["≤1", "1–2", "2–3", "3–5", "5–10", ">10"]
        d = pd.cut(ho["mutlak_hata"], bins, labels=labels).value_counts().reindex(labels)
        fig = px.bar(x=labels, y=100 * d.values / len(ho),
                     text=[f"%{tr(v, 1)}" for v in 100 * d.values / len(ho)],
                     labels={"x": "Mutlak hata (PCE puanı)", "y": "Kayıt %"})
        fig.update_traces(marker_color=MAVI, textposition="outside")
        fig.update_layout(height=340, title="Hata büyüklüğü dağılımı")
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Kayıtların %{tr(100 * (ho['mutlak_hata'] <= 2).mean(), 0)}'ı ≤2 puan, "
                   f"%{tr(100 * (ho['mutlak_hata'] <= 3).mean(), 0)}'i ≤3 puan hatayla "
                   "tahmin ediliyor (tez Bölüm 4.7).")
    with rr:
        err = ho["tahmin"] - ho["PCE"]
        fig = px.histogram(err, nbins=80,
                           labels={"value": "İşaretli hata (tahmin − gerçek)"})
        fig.update_traces(marker_color=MAVI, showlegend=False)
        fig.add_vline(x=0, line_color=KIRMIZI)
        fig.update_layout(height=340, title=f"Yön: >+5 aşırı tahmin %{tr(100 * (err > 5).mean(), 1)} · "
                                            f"<−5 eksik tahmin %{tr(100 * (err < -5).mean(), 1)}")
        st.plotly_chart(fig, width="stretch")
        st.caption("Sağa çarpık kuyruk: model düşük verimli kayıtları zaman zaman olduğundan "
                   "yüksek tahmin ediyor — reçete-içi etiket gürültüsünün beklenen izi "
                   "(tez Bölüm 5.1, Tablo 5.1).")

with tab3:
    st.markdown("Model hatası **segmentlere göre** — tezdeki 'giderilemeyen gürültü' savının "
                "kayıt-düzeyi görünümü:")
    seg = pd.DataFrame([
        ("Tümü", ho["mutlak_hata"].mean(), len(ho)),
        ("Sn içeren (B_Sn > 0)", ho.loc[ho["B_Sn"] > 0, "mutlak_hata"].mean(),
         int((ho["B_Sn"] > 0).sum())),
        ("HTL-free (HTL = none)", ho.loc[ho["HTL"] == "none", "mutlak_hata"].mean(),
         int((ho["HTL"] == "none").sum())),
        ("Yüksek band gap (>1,7 eV)", ho.loc[ho["band_gap"] > 1.7, "mutlak_hata"].mean(),
         int((ho["band_gap"] > 1.7).sum())),
        ("Band gap doldurulmuş", ho.loc[ho["band_gap_dolduruldu"], "mutlak_hata"].mean(),
         int(ho["band_gap_dolduruldu"].sum())),
        ("Br-ağırlıklı (X_Br ≥ 0,4)", ho.loc[ho["X_Br"] >= 0.4, "mutlak_hata"].mean(),
         int((ho["X_Br"] >= 0.4).sum())),
        ("Standart bölge (FA-Pb-I, n-i-p)",
         ho.loc[(ho["A_FA"] > 0.5) & (ho["B_Pb"] > 0.9) & (ho["X_I"] > 0.7) &
                (ho["mimari"] == "nip"), "mutlak_hata"].mean(),
         int(((ho["A_FA"] > 0.5) & (ho["B_Pb"] > 0.9) & (ho["X_I"] > 0.7) &
              (ho["mimari"] == "nip")).sum())),
    ], columns=["Segment", "MAE", "n"])
    fig = px.bar(seg.sort_values("MAE"), x="MAE", y="Segment", orientation="h",
                 text=[f"{tr(v, 2)}  (n={tr(n, 0)})" for v, n in
                       zip(seg.sort_values("MAE")["MAE"], seg.sort_values("MAE")["n"])])
    fig.update_traces(marker_color=[KIRMIZI if s_ != "Tümü" and v > seg.loc[0, 'MAE'] else MAVI
                                    for s_, v in zip(seg.sort_values("MAE")["Segment"],
                                                     seg.sort_values("MAE")["MAE"])],
                      textposition="outside")
    fig.update_layout(height=380, xaxis_title="MAE (PCE puanı)", margin=dict(t=20))
    st.plotly_chart(fig, width="stretch")
    st.info(
        "Beklenenin tersine, az temsil edilen bölgelerin çoğunda (Sn'li, geniş band gap, "
        "Br-ağırlıklı) MAE genel ortalamanın altındadır: bu alt kümelerde PCE değerleri dar ve "
        "görece düşük bir banda toplandığından mutlak hata küçülür; HTL-free kayıtlarda ise "
        "hata genel ortalamanın hafif üzerindedir. Düşük alt-grup MAE'si modelin o bölgede "
        "güvenilir olduğu anlamına gelmez — kayıt sayısı azdır ve tez, özellik-uzayı "
        "mesafesinin güvenilirliği ayırt etmediğini göstermiştir (Bölüm 4.10). Kanonik "
        "FA-Pb-I bölgesi, verinin büyük kısmını taşıdığı için genel hatayı belirler."
    )
