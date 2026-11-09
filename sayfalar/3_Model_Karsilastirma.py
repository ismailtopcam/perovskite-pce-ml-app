# -*- coding: utf-8 -*-
"""03 Model Karşılaştırma — altı modelin DOI-grup CV ve holdout başarımları."""
import streamlit as st

from lib import data, ui
from lib.ui import tr

cv = data.csv("model_comparison_groupkfold.csv").sort_values("R2_mean", ascending=False)
holdout = data.csv("model_comparison_holdout.csv")
abl = data.js("descriptor_ablation.json")
tune = data.js("tuning_best_params.json")

ui.page_header(
    "03 — Model Karşılaştırma · Tez Bölüm 3.9 ve 4.2",
    "Yarışı algoritma kazandırmıyor.",
    "Altı model aynı protokolle (aynı bölmeler, aynı 77 özellik, sabit hiperparametreler) karşılaştırıldı; "
    "hiçbir modele test verisine bakan ayar yapılmadı.",
)

NOT = {"CatBoost": "— seçilen model", "HistGBM": "— salt scikit-learn", "Ridge": "— doğrusal taban"}
AD = {"RandomForest": "Random Forest"}

left, right = st.columns(2, gap="large")
with left:
    ui.kicker("DOI-grup 5-kat CV — ana ölçüt", "(R² ort ± std, eksen 0–0,5)", tone="ink")
    ui.bar_rows([
        dict(name=(f'<span style="color:var(--acc700)">{AD.get(r.model, r.model)}</span>' if r.model == "CatBoost"
                   else AD.get(r.model, r.model)),
             sub=NOT.get(r.model, ""), value=r.R2_mean, value_str=tr(r.R2_mean, 3),
             value_sub=f"±{tr(r.R2_std, 3)}", std=r.R2_std, tone="acc" if r.model == "CatBoost" else "ink",
             bold=(r.model == "CatBoost"))
        for r in cv.itertuples()
    ], vmax=0.5)
    top = cv.iloc[0]; second = cv.iloc[1]
    ui.text(f"İlk dört boosting modeli standart sapma mertebesinde iç içedir; CatBoost'un üstünlüğü "
            f"<strong>marjinaldir</strong>: eşleştirilmiş kat karşılaştırmasında CatBoost beş katın beşinde HistGBM'in "
            f"önündedir (ortalama fark ΔR² ≈ {tr(top.R2_mean - second.R2_mean, 4)}; eşleştirilmiş t p = 0,006, "
            "Wilcoxon p = 0,063) — yön tutarlı, büyüklük pratikte ihmal edilebilir (tez Bölüm 4.2). Salt-scikit-learn "
            "HistGBM'in dış kütüphanelerle at başı gitmesi, kurulum-hafif tekrar üretim için önemlidir. "
            "Sıfır-bilgi tabanı (eğitim ortalaması) aynı protokolde R² ≈ 0,00 / MAE 4,32 verir.", mute=True)

with right:
    ui.kicker("Sayısal tablo", tone="ink")
    tab = cv.merge(holdout, on="model", suffixes=("_cv", "_holdout"))
    rows = [[AD.get(r.model, r.model), tr(r.R2_mean, 3), tr(r.R2_std, 3), tr(r.MAE_mean, 3),
             tr(r.RMSE_mean, 3), tr(r.R2, 3), tr(r.MAE, 3)] for r in tab.itertuples()]
    ui.table(["Model", "CV R²", "± std", "CV MAE", "CV RMSE", "Hold. R²", "Hold. MAE"], rows,
             right_cols=(1, 2, 3, 4, 5, 6), hi_row=0)
    ui.text(
        "<p><strong>Ayar duyarlılığı (Bölüm 4.8):</strong> grup-güvenli ızgara aramaları hem HistGBM'de "
        f"(varsayılan {tr(tune['default_cv_r2'][0], 4)} → ayarlı {tr(tune['tuned_cv_r2'][0], 4)}; kazanım "
        f"{tr(tune['tuned_cv_r2'][0] - tune['default_cv_r2'][0], 4)}) hem CatBoost'ta (fark 0,000) baştan kullanılan temel yapılandırmayı seçti — başarım "
        "hiperparametreyle değil <strong>veri yapısıyla</strong> sınırlı.</p>"
        f"<p><strong>Fiziksel tanımlayıcı ablasyonu (Bölüm 4.9):</strong> Goldschmidt <em>t</em> / oktahedral "
        f"<em>μ</em> / Bartel <em>τ</em> eklemek başarımı artırmadı (Δ = +{tr(abl['delta_r2'], 4)}; "
        f"{tr(abl['descriptor_yok']['r2'], 4)} → {tr(abl['descriptor_var']['r2'], 4)}, kat gürültüsünün çok "
        "altında): ağaç modeller aynı bilgiyi ham oranlardan zaten öğreniyor.</p>")

ui.rule(thin=True)
ui.text("Yol haritası: eğitim süresi / tahmin süresi / model boyutu bu koşularda kaydedilmediği için "
        "operasyonel maliyet (Pareto) görünümü henüz verilemiyor; pipeline'a enstrümantasyon eklendiğinde bu "
        "sayfaya R²–maliyet grafiği eklenecek.", mute=True)

ui.footer()
