# -*- coding: utf-8 -*-
"""06 Aday Tarayıcı — 756 aday kompozisyonun aralıklı ve eğitim-uzayı bilgili keşfi."""
import numpy as np
import plotly.express as px
import streamlit as st

from lib import data, ui
from lib.ui import tr, INK, ACC

cand = data.candidates()
conf = data.js("conformal.json")
scr = data.js("screening_metadata.json")
enr = data.csv("enrichment.csv")
thr = float(conf["applicability_domain"]["threshold"])
n_destek = int(cand["uyumlu_N5"].sum())
n_ici = int(cand["alan_ici"].sum())
top_all = cand.sort_values("Predicted_PCE", ascending=False).iloc[0]
prim = cand[cand["uyumlu_N5"]].sort_values("Predicted_PCE", ascending=False)
top = prim.iloc[0]
tc = conf["top_candidate"]
hw_top = float(conf["marginal"]["90"]["half_width"])
cand = cand.assign(destek=np.where(cand["uyumlu_N5"], "eğitimde destekli (≥5)", "destek < 5"))
zeng = enr[(enr["esik"] == scr.get("gains_threshold", 18)) & (enr["k_frac"] == 0.05)]
zeng = float(zeng["zenginlestirme"].iloc[0]) if len(zeng) else None

ui.page_header(
    "06 — Aday Kompozisyon Tarayıcı · Tez Bölüm 3.12, 4.5 ve 4.10",
    "756 aday, dürüst uyarılarla.",
    "756 aday = 7×2×3×2×3×3 kontrollü eksen çarpımı; her adaya nominal %90 belirsizlik aralığı, eğitim-verisi "
    "desteği ve eğitim-uzayına uzaklık bilgisi eşlik eder.",
)

ui.stats([
    ("Aday", tr(len(cand), 0)),
    ("Eğitimde destekli (≥5)", tr(n_destek, 0), "mimari–ETL–HTL üçlüsü eğitimde ≥5 kayıt"),
    ("En yüksek tahmin", tr(float(top["Predicted_PCE"]), 2),
     f"birincil (≥5 destek) liste; filtresiz {tr(float(top_all['Predicted_PCE']), 2)} — eğitim maksimumu 34,8'in çok altında"),
    ("Sıralama korelasyonu", f"ρ {tr(scr['spearman'], 3)}",
     f"holdout Spearman" + (f"; ilk %5'te {tr(zeng, 1)}× zenginleştirme" if zeng else "")),
])

left, right = st.columns(2, gap="large")
with left:
    ui.kicker("En yüksek tahminli aday", "(birincil liste: eğitim desteği ≥5)", tone="ink")
    st.html(
        '<div class="m-box" style="padding:0">'
        '<div style="display:flex; justify-content:space-between; align-items:baseline; padding:12px 16px; '
        'border-bottom:2px solid var(--ink)">'
        f'<span style="font-weight:800; font-size:17px">{ui.esc(top["A"])} · {ui.esc(top["B"])} · {ui.esc(top["X"])} · {ui.esc(top["arch"])}</span>'
        f'<span class="m-kicker" style="font-size:11px">sıra 01 / {len(prim)}</span></div>'
        '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; padding:14px 16px; gap:12px">'
        f'<div><div class="m-kicker mute" style="font-size:10.5px">Tahmini PCE</div><div style="font-weight:800; font-size:28px; color:var(--acc)">{tr(top["Predicted_PCE"], 2)}</div></div>'
        f'<div><div class="m-kicker mute" style="font-size:10.5px">Marjinal %90</div><div style="font-weight:800; font-size:20px; padding-top:5px">{tr(top["marginal90_low"], 1)} – {tr(top["marginal90_high"], 1)}</div></div>'
        f'<div><div class="m-kicker mute" style="font-size:10.5px">Eğitim desteği</div><div style="font-weight:800; font-size:20px; padding-top:5px">{tr(int(top["egitim_kayit_sayisi"]), 0)} kayıt</div></div>'
        '</div>'
        f'<div style="padding:0 16px 12px; font-size:12px; color:var(--n700)">ETL {ui.esc(top["ETL"])} · HTL {ui.esc(top["HTL"])} · '
        f'eğitim-uzayı uzaklığı {tr(top["knn_uzaklik"], 2)}. Filtresiz sıralamanın tepesi ({tr(float(top_all["Predicted_PCE"]), 2)}; '
        f'{ui.esc(top_all["arch"])}, {ui.esc(top_all["ETL"])}, {ui.esc(top_all["HTL"])}) eğitimde hiç görülmemiş bir üçlüye aittir (tez Bölüm 4.5).</div></div>'
    )

    ui.kicker("Filtreler", tone="ink")
    min_pce = st.slider("Min. tahmini PCE", 8.0, 18.0, 12.0, 0.5)
    sadece_uyumlu = st.checkbox(
        f"yalnızca eğitimde denenmiş kombinasyonlar ({len(cand)} → {n_destek})", value=True,
        help="Adayın mimari–ETL–HTL üçlüsü, modelin eğitim verisinde en az 5 kayıtta birlikte görülmüşse "
             "gösterilir (tez Bölüm 4.5). Model, hiç görmediği bir kombinasyonun katman etkileşimini öğrenmiş "
             "olamaz.")
    f3, f4, f5 = st.columns(3)
    a_sel = f3.multiselect("A-site", sorted(cand["A"].unique()), placeholder="Tümü")
    b_sel = f4.multiselect("B-site", sorted(cand["B"].unique()), placeholder="Tümü")
    arch_sel = f5.multiselect("Mimari", sorted(cand["arch"].unique()), placeholder="Tümü")

with right:
    ui.kicker("Bu sayfayı dürüst okumak", tone="ink")
    ad = conf["applicability_domain"]
    ui.text(
        f"<p><strong>Tavan {tr(float(top_all['Predicted_PCE']), 2)} (birincil filtreli listede {tr(float(top['Predicted_PCE']), 2)}):</strong> hiçbir aday eğitim maksimumuna "
        "(34,8) yaklaşamaz — ağaç tabanlı modelin eğitim aralığı dışına çıkamaması, 756 adaylık kısıtlı eksen "
        "uzayı ve band gap/tavlama gibi bağlam değişkenlerinin eğitim medyanlarına sabitlenmesi birlikte çalışır. "
        "Liste <strong>bilinen yüksek-verim bölgesinin yeniden bulunmasıdır</strong>; yeni bir keşif vaat etmez "
        "(tez Bölüm 5.4).</p>"
        f"<p><strong>Eğitim desteği:</strong> ham ilk-30'a hâkim bazı (mimari, ETL, HTL) üçlüleri eğitimde hiç "
        f"görülmemiştir; ≥5 kayıt filtresi {len(cand)} adayı {n_destek}'e indirir ve tavanı değiştirmez (tez Bölüm 4.5).</p>"
        f"<p><strong>Uzaklık ≠ güven:</strong> adayların yalnızca {tr(n_ici, 0)} tanesi eğitim-uzayı eşiğinin "
        "içindedir (sabit medyan varsayımları yüzünden beklenen bir durum). Üstelik tez, bu mesafenin holdout'ta "
        f"hata düzeyini <strong>ayırt etmediğini</strong> göstermiştir (MAE {tr(ad['mae_inside'], 2)}'e karşı "
        f"{tr(ad['mae_outside'], 2)}; Bölüm 4.10). Bu sütunu adayın veri yoğunluğu bilgisi olarak okuyun; güven "
        "skoru sayılmaz.</p>"
        "<p>Adaylar holdout dağılımından gelmediği için aralıklar kesin %90 garantisi değildir.</p>")

m = cand["Predicted_PCE"] >= min_pce
if a_sel: m &= cand["A"].isin(a_sel)
if b_sel: m &= cand["B"].isin(b_sel)
if arch_sel: m &= cand["arch"].isin(arch_sel)
if sadece_uyumlu: m &= cand["uyumlu_N5"]
sub = cand[m].sort_values("Predicted_PCE", ascending=False)

ui.rule()
ui.kicker(f"{tr(len(sub), 0)} / {len(cand)} aday eşleşti",
          f"(eğitimde ≥5 kez görülmüş kombinasyon: {tr(n_destek, 0)}; eğitim-uzayı eşiği içinde: {tr(n_ici, 0)})",
          tone="ink")
view = sub[["A", "B", "X", "arch", "ETL", "HTL", "Predicted_PCE", "marginal90_low", "marginal90_high",
            "egitim_kayit_sayisi", "knn_uzaklik", "alan_ici"]].rename(columns={
    "arch": "Mimari", "Predicted_PCE": "Tahmini PCE", "marginal90_low": "%90 alt", "marginal90_high": "%90 üst",
    "egitim_kayit_sayisi": "Eğitim desteği (üçlü)", "knn_uzaklik": "Eğitim-uzayı uzaklığı", "alan_ici": "Eşik içi?"})
st.dataframe(view.head(200), hide_index=True, width="stretch", height=380,
             column_config={c: st.column_config.NumberColumn(c, format="%.2f")
                            for c in ["Tahmini PCE", "%90 alt", "%90 üst", "Eğitim-uzayı uzaklığı"]})

fig = px.scatter(cand, x="knn_uzaklik", y="Predicted_PCE", color="destek",
                 color_discrete_map={"eğitimde destekli (≥5)": INK, "destek < 5": ACC},
                 labels={"knn_uzaklik": "Eğitim-uzayına kNN uzaklığı", "Predicted_PCE": "Tahmini PCE",
                         "destek": ""},
                 hover_data=["A", "B", "X", "arch", "ETL", "HTL"])
fig.add_vline(x=thr, line_dash="dash", line_color=INK, annotation_text=f"AD eşiği {tr(thr, 2)}")
fig.update_layout(legend=dict(orientation="h", y=1.08, x=0))
ui.chart(fig, height=380, title=f"Tahmin – eğitim-uzayına yakınlık ({len(cand)} aday)")

ui.sci_limit_box()
ui.footer()
