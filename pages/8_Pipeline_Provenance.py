# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from lib import data
from lib.ui import page, tr, tez_notu

page("Pipeline ve Provenans", "8️⃣")
tez_notu("Bölüm 3.15",
         "Her aşama; parametre, seed ve paket sürümlerini bir koşu-manifestine yazar. "
         "Bu sayfa o manifestlerin canlı görünümüdür — uygulama bir ML denetim (audit) "
         "kaydı gibi okunabilir.")

meta = data.js("app_meta.json")
manifests = data.js("manifests.json")

st.graphviz_chart("""
digraph {
  rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#eef3f8",
                    fontname="Arial", fontsize=11];
  ham [label="Ham veri\\n43.398 × 410"];
  sema [label="Şema doğrulama\\n(sızıntı kolonu kontrolü)"];
  temiz [label="Temizleme\\n41.485 (−1.913)"];
  vek [label="Kompozisyon\\nvektörizasyonu"];
  oz [label="77 özellik\\n(+eksiklik bayrakları)"];
  bolme [label="DOI-grup bölme\\n(seed 42)"];
  model [label="6 model\\nCV + holdout"];
  shap [label="SHAP"];
  aday [label="756 aday\\n+ conformal"];
  ham -> sema -> temiz -> vek -> oz -> bolme -> model -> shap -> aday;
}
""")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Pipeline commit", meta["pipeline_git_commit"][:10])
c2.metric("Seed", str(meta["seed"]))
c3.metric("Aşama manifesti", str(len(manifests)))
c4.metric("Veri hazırlama", meta["hazirlama_zamani_utc"][:10])

st.subheader("📜 Koşu manifestleri")
rows = []
for m in manifests:
    v = m.get("versions", {})
    rows.append({
        "Aşama": m.get("stage"), "Zaman (UTC)": m.get("timestamp_utc", "")[:19],
        "Seed": m.get("seed"), "Python": v.get("python"),
        "sklearn": v.get("scikit-learn"), "catboost": v.get("catboost"),
        "Metrikler": ", ".join(f"{k}={v_}" for k, v_ in list(m.get("metrics", {}).items())[:3]),
    })
st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=380)

vs = {tuple(sorted(m.get("versions", {}).items())) for m in manifests}
if len(vs) == 1:
    st.success("✅ 14 manifestin tamamı **aynı ortamı** kaydediyor (Python "
               f"{manifests[0]['versions']['python']}, scikit-learn "
               f"{manifests[0]['versions']['scikit-learn']}, catboost "
               f"{manifests[0]['versions']['catboost']}) — sürüm karışması yok.")

st.subheader("🔎 Bağımsız denetim özetleri")
a, b, c = st.columns(3)
with a:
    p = data.js("pipeline_cv_results.json")
    st.markdown(f"""**Ön-işleme sızıntısı testi** (Bölüm 3.7)
Global matris: R² {tr(p['global_mean'], 4)}
Kat-içi Pipeline: R² {tr(p['foldlocal_mean'], 4)}
Fark: **{tr(abs(p['delta']), 4)}** → önişleme sızıntısı ihmal edilebilir.""")
with b:
    d = data.js("doi_normalizasyon_duyarlilik.json")
    st.markdown(f"""**DOI normalizasyon duyarlılığı** (Bölüm 5.7)
GroupKFold: {tr(d['raw_groups']['gkf5']['R2_mean'], 3)} → {tr(d['normalized_groups']['gkf5']['R2_mean'], 3)}
Holdout: {tr(d['raw_groups']['holdout']['R2'], 3)} → {tr(d['normalized_groups']['holdout']['R2'], 3)}
Fark kat gürültüsü içinde.""")
with c:
    t = data.js("tuning_catboost_best_params.json")
    st.markdown(f"""**CatBoost ızgara araması** (Bölüm 4.8)
Grup-güvenli arama, temel yapılandırmayı seçti;
5-katta fark **0,000** → başarım veri yapısıyla sınırlı,
ayarla değil.""")

st.subheader("🧾 Model ve veri kimliği")
st.markdown(f"""
| Alan | Değer |
|---|---|
| Model | CatBoost 1.2.10 (iterations=500, depth=6, lr=0.05, seed=42) |
| Model artefaktı (`model.cbm`) SHA-256 | `{meta.get('model_cbm_sha256', '—')[:32]}…` |
| `model_ready_dataset.csv` SHA-256 | `{meta['model_ready_sha256'][:32]}…` |
| Ham veri anlık görüntüsü | {tr(meta['n_ham'], 0)} kayıt × 410 kolon (SHA-256: pipeline README) |
| Pipeline commit | `{meta['pipeline_git_commit'][:12]}` |
| Kod arşivi | [Zenodo DOI {meta.get('zenodo_doi', '10.5281/zenodo.20829027')}](https://doi.org/{meta.get('zenodo_doi', '10.5281/zenodo.20829027')}) |
| Pipeline deposu | [{meta.get('github_pipeline', '').replace('https://', '')}]({meta.get('github_pipeline', '')}) |
| Uygulama deposu | [{meta.get('github_app', '').replace('https://', '')}]({meta.get('github_app', '')}) |
| DOI-grup CV sonucu | R² = 0,413 ± 0,006 (MAE 3,12 / RMSE 4,02) |

⚠️ **Ölçüm-sonrası hiçbir değişken (Voc, Jsc, FF, EQE, stabilite alanları) modele dahil
değildir** — şema katmanı bunu her koşuda zorlar; dahil edilselerdi R² yapay olarak
0,938'e çıkardı (tez Deney B).

Bu uygulamanın tüm dosyaları `tools/prepare_app_data.py` ile pipeline reposundan
**deterministik** üretilir; betik, bölmeleri yeniden kurup bilinen değerlerle doğrular
(assert), uyuşmazlıkta üretim durur.
""")
