# -*- coding: utf-8 -*-
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data
from lib.ui import page, tr, tez_notu, MAVI, KIRMIZI, GRI

page("Doğrulama Deneyleri — Tezin Merkez Bulgusu", "2️⃣")
tez_notu("Bölüm 3.13 ve 4.3",
         "Aynı veri, aynı model: yalnızca bölme yöntemi ve özellik seti değiştirildiğinde "
         "R² 0,263 ile 0,938 arasında değişir. Başarım, algoritmadan çok bu kararların ürünüdür.")

val = data.csv("validation_experiments.csv")
rec = data.records()
ho = rec[rec["bolme"] == "holdout-test"]

st.subheader("Kararları siz verin")
c1, c2 = st.columns(2)
with c1:
    bolme = st.radio("**Bölme yöntemi**",
                     ["DOI-grup (yayın-ayrık)", "Rastgele KFold"],
                     help="Aynı yayının kardeş cihazları eğitim+test'e birlikte düşerse "
                          "model 'görmediği' veriyi dolaylı görmüş olur.")
with c2:
    ozellik = st.radio("**Özellik seti**",
                       ["Ölçüm-öncesi 77 özellik", "+ Voc, Jsc, FF (ölçüm sonrası)"],
                       help="Voc×Jsc×FF ≈ PCE: bu üçlü, hedefin kendisini dolaylı taşır.")

grup = bolme.startswith("DOI")
safe = ozellik.startswith("Ölçüm-öncesi")

if grup and safe:
    r2, std, yorum, renk = 0.4129, 0.0065, \
        "**Tezin ana sonucu.** Eğitimden ham DOI anahtarı düzeyinde ayrık tutulan " \
        "yayınlara genellemenin dürüst ölçüsü.", "normal"
elif not grup and safe:
    r2, std, yorum, renk = 0.4812, 0.0089, \
        "**+0,068 iyimserlik:** kardeş cihazlar test kümesine sızdı. Skor arttı, " \
        "genelleme gücü artmadı (tez Deney A).", "inverse"
elif grup and not safe:
    r2, std, yorum, renk = 0.9380, 0.0040, \
        "**Hedef sızıntısı.** Voc×Jsc×FF, PCE'yi neredeyse doğrudan verir: model artık " \
        "tahmin değil, kopyalama yapıyor (tez Deney B). Sentez ÖNCESİ bu değerler bilinemez.", "inverse"
else:
    r2, std, yorum, renk = None, None, \
        "Bu kombinasyon tezde koşulmadı: iki gevşek kararı birleştirmek yalnızca daha da " \
        "iyimser (ve daha da anlamsız) bir skor üretir.", "off"

m1, m2, m3 = st.columns([1, 1, 2])
if r2 is not None:
    m1.metric("Grup-CV R²", tr(r2, 3), None if (grup and safe) else
              f"{'+' if r2 > 0.4129 else ''}{tr(r2 - 0.4129, 3)} taban değere göre",
              delta_color=renk)
    m2.metric("± std (5 kat)", tr(std, 3))
else:
    m1.metric("Grup-CV R²", "—")
m3.markdown(yorum)

st.divider()
l, r = st.columns(2)

with l:
    st.subheader("Deney A+B — bölme ve sızıntının etkisi")
    df = val.copy()
    df["etiket"] = ["Rastgele KFold", "DOI-grup KFold", "Ölçüm-öncesi (77)",
                    "+Voc/Jsc/FF", "Kompozisyon (14)", "+Cihaz (57)", "+Süreç (77)"]
    ab = df.iloc[[1, 0, 3]]
    fig = go.Figure(go.Bar(
        x=ab["R2_mean"], y=["DOI-grup\n(başlık sonuç)", "Rastgele bölme", "+Voc/Jsc/FF"],
        orientation="h", error_x=dict(array=ab["R2_std"]),
        marker_color=[MAVI, "#c9a26a", KIRMIZI],
        text=[tr(v, 3) for v in ab["R2_mean"]], textposition="outside"))
    fig.update_layout(xaxis_range=[0, 1.05], height=300, xaxis_title="R² (5-kat CV)",
                      margin=dict(t=10))
    st.plotly_chart(fig, width="stretch")

    st.subheader("Deney C — özellik kapsamı")
    cdf = df.iloc[[4, 5, 6]]
    fig = px.bar(cdf, x="etiket", y="R2_mean", error_y="R2_std",
                 text=[tr(v, 3) for v in cdf["R2_mean"]],
                 labels={"etiket": "", "R2_mean": "R² (DOI-grup CV)"})
    fig.update_traces(marker_color=MAVI, textposition="outside")
    fig.update_layout(height=300, yaxis_range=[0, 0.5], margin=dict(t=10))
    st.plotly_chart(fig, width="stretch")
    st.caption("PCE yalnızca kompozisyonla açıklanamıyor (0,263); cihaz (0,362) ve süreç "
               "(0,413) bilgisi anlamlı katkı veriyor (tez Bölüm 4.3).")

with r:
    st.subheader("Başlık kurulumun holdout görünümü")
    mae = ho["mutlak_hata"].mean()
    rmse = float(np.sqrt(((ho["tahmin"] - ho["PCE"]) ** 2).mean()))
    ssr = ((ho["PCE"] - ho["tahmin"]) ** 2).sum()
    sst = ((ho["PCE"] - ho["PCE"].mean()) ** 2).sum()
    h1, h2, h3 = st.columns(3)
    h1.metric("Holdout R²", tr(1 - ssr / sst, 3))
    h2.metric("MAE", tr(mae, 2) + " puan")
    h3.metric("RMSE", tr(rmse, 2) + " puan")

    plot_df = ho.sample(min(4000, len(ho)), random_state=1)
    fig = px.scatter(plot_df, x="tahmin", y="PCE", opacity=0.25,
                     labels={"tahmin": "Model tahmini (PCE)", "PCE": "Gerçek PCE"})
    fig.update_traces(marker=dict(size=4, color=MAVI))
    fig.add_shape(type="line", x0=-4, y0=-4, x1=30, y1=30, line=dict(color="#333", width=1))
    fig.add_shape(type="line", x0=-4, y0=2.42, x1=30, y1=36.42,
                  line=dict(color=KIRMIZI, width=1, dash="dash"))
    fig.add_shape(type="line", x0=-4, y0=-10.42, x1=30, y1=23.58,
                  line=dict(color=KIRMIZI, width=1, dash="dash"))
    n_neg = int((plot_df["tahmin"] < 0).sum())
    fig.update_layout(height=380,
                      title=f"Gerçek vs tahmin (kesikli: ±6,42 = %90 bandı; "
                            f"negatif tahminler dahil, örneklemde {n_neg} adet)",
                      xaxis_range=[-4, 30], yaxis_range=[0, 32], margin=dict(t=40))
    st.plotly_chart(fig, width="stretch")

    err = (ho["tahmin"] - ho["PCE"])
    fig = px.histogram(err, nbins=80, labels={"value": "İşaretli hata (tahmin − gerçek)"})
    fig.update_traces(marker_color=MAVI, showlegend=False)
    fig.add_vline(x=0, line_color=KIRMIZI)
    fig.update_layout(height=260, title=f"Hata dağılımı (medyan mutlak hata "
                                        f"{tr(ho['mutlak_hata'].median(), 2)})", margin=dict(t=40))
    st.plotly_chart(fig, width="stretch")

st.info(
    "**Neden önemli?** Literatürde Perovskite Database üzerinde rastgele bölmeyle 0,70–0,75 "
    "bandında R² raporlanır (tez Tablo 2.1). Bu sayfadaki deney, aynı veri ve modelde yalnızca "
    "protokol değişikliğinin skoru ne kadar iyimser gösterebildiğini nicel olarak ortaya koyar: raporlanan başarım, "
    "**doğrulama tasarımının** bir fonksiyonudur (Kapoor ve Narayanan, 2023)."
)
