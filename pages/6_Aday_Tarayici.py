# -*- coding: utf-8 -*-
import plotly.express as px
import streamlit as st

from lib import data
from lib.ui import page, tr, tez_notu, bilim_uyarisi, MAVI, KIRMIZI

page("Aday Kompozisyon Tarayıcı", "6️⃣")
tez_notu("Bölüm 3.12, 4.5 ve 4.10",
         "756 aday = 7×2×3×2×3×3 kontrollü eksen çarpımı; her adaya conformal aralık, "
         "eğitim-desteği ve eğitim-uzayına uzaklık eşlik eder.")

cand = data.candidates()

f1, f2, f3, f4, f5 = st.columns(5)
min_pce = f1.slider("Min. tahmini PCE", 8.0, 18.0, 12.0, 0.5)
a_sel = f2.multiselect("A-site", sorted(cand["A"].unique()))
b_sel = f3.multiselect("B-site", sorted(cand["B"].unique()))
arch_sel = f4.multiselect("Mimari", sorted(cand["arch"].unique()))
sadece_uyumlu = f5.checkbox("Yalnız eğitimde destekli (≥5 kayıt)", value=True)

m = cand["Predicted_PCE"] >= min_pce
if a_sel: m &= cand["A"].isin(a_sel)
if b_sel: m &= cand["B"].isin(b_sel)
if arch_sel: m &= cand["arch"].isin(arch_sel)
if sadece_uyumlu: m &= cand["uyumlu_N5"]
sub = cand[m].sort_values("Predicted_PCE", ascending=False)

st.caption(f"**{tr(len(sub), 0)} / 756** aday eşleşti "
           f"(eğitim destekli: {tr(int(cand['uyumlu_N5'].sum()), 0)}; "
           f"eğitim-uzayı eşiği içinde: {tr(int(cand['alan_ici'].sum()), 0)}).")

view = sub[["A", "B", "X", "arch", "ETL", "HTL", "Predicted_PCE",
            "marginal90_low", "marginal90_high", "egitim_kayit_sayisi",
            "knn_uzaklik", "alan_ici"]].rename(columns={
    "Predicted_PCE": "Tahmini PCE", "marginal90_low": "%90 alt",
    "marginal90_high": "%90 üst", "egitim_kayit_sayisi": "Eğitim desteği (üçlü)",
    "knn_uzaklik": "Eğitim-uzayı uzaklığı", "alan_ici": "Eşik içi?"})
st.dataframe(view.head(200), hide_index=True, use_container_width=True, height=380,
             column_config={c: st.column_config.NumberColumn(c, format="%.2f")
                            for c in ["Tahmini PCE", "%90 alt", "%90 üst",
                                      "Eğitim-uzayı uzaklığı"]})

l, r = st.columns(2)
with l:
    fig = px.scatter(cand, x="knn_uzaklik", y="Predicted_PCE", color="uyumlu_N5",
                     color_discrete_map={True: MAVI, False: KIRMIZI},
                     labels={"knn_uzaklik": "Eğitim-uzayına kNN uzaklığı",
                             "Predicted_PCE": "Tahmini PCE",
                             "uyumlu_N5": "Eğitim destekli"},
                     hover_data=["A", "B", "X", "arch", "ETL", "HTL"])
    thr = data.js("conformal.json")["applicability_domain"]["threshold"]
    fig.add_vline(x=thr, line_dash="dash", line_color="#333",
                  annotation_text=f"AD eşiği {tr(thr, 2)}")
    fig.update_layout(height=380, title="Tahmin vs eğitim-uzayına yakınlık (756 aday)")
    st.plotly_chart(fig, use_container_width=True)
with r:
    st.markdown(f"""
### Bu sayfayı dürüst okumak

- **Tavan 17,78:** hiçbir aday eğitim maksimumuna (34,8) yaklaşamaz — ağaç modeller
  ekstrapolasyon yapamaz; liste **yeni keşif değil, bilinen yüksek-verim bölgesinin
  yeniden bulunmasıdır** (tez Bölüm 5.4).
- **Eğitim desteği:** ham ilk-30'a hâkim bazı (mimari, ETL, HTL) üçlüleri eğitimde hiç
  görülmemiştir; ≥5 kayıt filtresi 756 adayı 546'ya indirir ve tavanı değiştirmez
  (tez Bölüm 4.5).
- **Uzaklık ≠ güven:** adayların yalnızca {tr(int(cand['alan_ici'].sum()), 0)} tanesi
  eğitim-uzayı eşiğinin içindedir (sabit medyan varsayımları yüzünden beklenen bir durum).
  Üstelik tez, bu mesafenin holdout'ta hata düzeyini **ayırt etmediğini** göstermiştir
  (MAE 3,28 vs 3,19; Bölüm 4.10) — bu sütunu bir güven skoru değil, adayın veri
  yoğunluğu bilgisi olarak okuyun.
- Adaylar holdout dağılımından gelmediği için aralıklar kesin %90 garantisi değildir.
""")

bilim_uyarisi()
