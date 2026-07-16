# -*- coding: utf-8 -*-
import plotly.graph_objects as go
import streamlit as st

from lib import data
from lib.ui import page, tr, tez_notu, MAVI

page("Model Karşılaştırma", "3️⃣")
tez_notu("Bölüm 3.9 ve 4.2",
         "Altı model aynı protokolle (aynı bölmeler, aynı 77 özellik, sabit hiperparametreler) "
         "karşılaştırıldı; hiçbir modele test verisine bakan ayar yapılmadı.")

cv = data.csv("model_comparison_groupkfold.csv").sort_values("R2_mean", ascending=False)
holdout = data.csv("model_comparison_holdout.csv").sort_values("R2", ascending=False)

l, r = st.columns([6, 5])
with l:
    st.subheader("DOI-grup 5-kat CV (ana ölçüt)")
    fig = go.Figure(go.Bar(
        x=cv["R2_mean"][::-1], y=cv["model"][::-1], orientation="h",
        error_x=dict(array=cv["R2_std"][::-1]),
        marker_color=[MAVI if m != "CatBoost" else "#2c5f8a" for m in cv["model"][::-1]],
        text=[tr(v, 3) for v in cv["R2_mean"][::-1]], textposition="outside"))
    fig.update_layout(height=340, xaxis_title="R² (ort ± std)", xaxis_range=[0, 0.5],
                      margin=dict(t=10))
    st.plotly_chart(fig, width="stretch")
    st.caption("İlk dört boosting modeli standart sapma mertebesinde iç içedir; CatBoost'un "
               "üstünlüğü **marjinaldir** (tez Bölüm 5.1). Salt-sklearn HistGBM'in dış "
               "kütüphanelerle at başı gitmesi, kurulum-hafif tekrar üretim için önemlidir.")

with r:
    st.subheader("Sayısal tablo")
    tab = cv.merge(holdout, on="model", suffixes=("_cv", "_holdout"))
    tab = tab[["model", "R2_mean", "R2_std", "MAE_mean", "RMSE_mean", "R2", "MAE", "RMSE"]]
    tab.columns = ["Model", "CV R²", "± std", "CV MAE", "CV RMSE",
                   "Holdout R²", "Holdout MAE", "Holdout RMSE"]
    st.dataframe(tab, hide_index=True, width="stretch",
                 column_config={c: st.column_config.NumberColumn(c, format="%.3f")
                                for c in tab.columns if c != "Model"})
    st.markdown(
        """
**Ayar duyarlılığı (tez Bölüm 4.8):** grup-güvenli ızgara aramaları hem HistGBM'de
(+0,0002) hem CatBoost'ta (fark 0,000) baştan kullanılan temel yapılandırmayı seçti —
başarım hiperparametreyle değil **veri yapısıyla** sınırlı.

**Fiziksel tanımlayıcı ablasyonu (Bölüm 4.9):** Goldschmidt *t* / oktahedral *μ* /
Bartel *τ* eklemek başarımı artırmadı (Δ = −0,003): ağaç modeller aynı bilgiyi ham
oranlardan zaten öğreniyor.
"""
    )

st.divider()
st.caption(
    "🔭 *Yol haritası:* eğitim süresi / tahmin süresi / model boyutu bu koşularda "
    "kaydedilmediği için operasyonel maliyet (Pareto) görünümü henüz verilemiyor; "
    "pipeline'a enstrümantasyon eklendiğinde bu sayfaya R²-vs-maliyet grafiği eklenecek."
)
