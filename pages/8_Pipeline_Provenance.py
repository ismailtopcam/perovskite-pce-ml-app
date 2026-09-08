# -*- coding: utf-8 -*-
"""08 Pipeline & Provenans — koşu-manifestleri, sürümler, bağımsız denetim özetleri, model ve veri kimliği."""
import pandas as pd
import streamlit as st

from lib import data, ui
from lib.ui import tr

meta = data.js("app_meta.json")
manifests = data.js("manifests.json")
p = data.js("pipeline_cv_results.json")
d = data.js("doi_normalizasyon_duyarlilik.json")
n_man = len(manifests)

ui.page_header(
    "08 — Pipeline & Provenans · Tez Bölüm 3.15",
    "Bu sayılar tekrar üretilebilir mi?",
    "Her aşama; parametre, seed ve paket sürümlerini bir koşu-manifestine yazar. Bu sayfa o manifestlerin canlı "
    "görünümüdür; uygulama bir ML denetim (audit) kaydı gibi okunabilir.",
)

ui.flow([
    ("Ham veri", f"{tr(meta['n_ham'], 0)} × 410"),
    ("Şema doğrulama", "sızıntı kolonu kontrolü"),
    ("Temizleme", f"{tr(meta['n_temiz'], 0)} (−{tr(meta['n_elenen'], 0)})"),
    ("Vektörizasyon", "A/B/X katsayıları"),
    ("77 özellik", "+ eksiklik bayrakları"),
    ("DOI-grup bölme", f"seed {meta['seed']}"),
    ("6 model", "CV + holdout"),
    ("SHAP", "küresel + yerel"),
    ("756 aday", "+ conformal"),
])

ui.stats([
    ("Pipeline commit", f'<span class="m-mono" style="font-size:0.55em">{meta["pipeline_git_commit"][:10]}</span>'),
    ("Seed", str(meta["seed"])),
    ("Aşama manifesti", str(n_man)),
    ("Veri hazırlama", meta["hazirlama_zamani_utc"][:10]),
])

vs = {tuple(sorted(m.get("versions", {}).items())) for m in manifests}
v0 = manifests[0].get("versions", {})
if len(vs) == 1:
    ui.box(f"<strong>{n_man} manifestin tamamı aynı ortamı kaydediyor</strong> (Python {v0.get('python')} · "
           f"scikit-learn {v0.get('scikit-learn')} · catboost {v0.get('catboost')} · "
           f"{ui.esc(str(v0.get('platform', '')).split('-')[0])}); sürüm karışması yoktur. Uygulamanın tüm veri "
           "dosyaları <span class='m-mono'>tools/prepare_app_data.py</span> ile pipeline reposundan deterministik "
           "üretilir; betik bölmeleri yeniden kurup bilinen değerlerle doğrular, uyuşmazlıkta durur.")
else:
    ui.box(f"Manifestler {len(vs)} farklı ortam kaydı içeriyor; ayrıntı için tabloya bakın.", accent=True)

ui.kicker("Koşu-manifestleri", tone="ink")
rows = []
for m in manifests:
    v = m.get("versions", {})
    rows.append({
        "Aşama": m.get("stage"), "Zaman (UTC)": m.get("timestamp_utc", "")[:19],
        "Seed": m.get("seed"), "Python": v.get("python"),
        "scikit-learn": v.get("scikit-learn"), "catboost": v.get("catboost"),
        "Metrikler": ", ".join(f"{k}={v_}" for k, v_ in list(m.get("metrics", {}).items())[:3]),
    })
st.dataframe(pd.DataFrame(rows).sort_values("Zaman (UTC)"), hide_index=True, width="stretch", height=380)

ui.kicker("Bağımsız denetim özetleri", tone="ink")
a, b, c = st.columns(3, gap="large")
with a:
    ui.text(f"<strong>Ön-işleme sızıntısı testi</strong> <span style='color:var(--n700)'>· Bölüm 3.7</span><br>"
            f"Global matris R² <strong>{tr(p['global_mean'], 4)}</strong> · kat-içi Pipeline R² "
            f"<strong>{tr(p['foldlocal_mean'], 4)}</strong> · fark <strong>{tr(abs(p['delta']), 4)}</strong> — "
            "ön-işleme sızıntısı ihmal edilebilir.")
with b:
    ui.text(f"<strong>DOI normalizasyon duyarlılığı</strong> <span style='color:var(--n700)'>· Bölüm 5.7</span><br>"
            f"GroupKFold <strong>{tr(d['raw_groups']['gkf5']['R2_mean'], 3)} → "
            f"{tr(d['normalized_groups']['gkf5']['R2_mean'], 3)}</strong> · holdout "
            f"<strong>{tr(d['raw_groups']['holdout']['R2'], 3)} → {tr(d['normalized_groups']['holdout']['R2'], 3)}</strong> "
            "(ham → normalize gruplar); fark kat gürültüsü içinde.")
with c:
    ui.text("<strong>CatBoost ızgara araması</strong> <span style='color:var(--n700)'>· Bölüm 4.8</span><br>"
            "Grup-güvenli arama temel yapılandırmayı seçti; 5-katta fark <strong>0,000</strong>. Sınırlayıcı etken "
            "hiperparametre değil veri yapısı.")

ui.kicker("Model ve veri kimliği", tone="ink")
gh_p = meta.get("github_pipeline", ""); gh_a = meta.get("github_app", ""); zdoi = meta.get("zenodo_doi", "10.5281/zenodo.20829027")
ui.table([], [
    ["Model", "CatBoost 1.2.10 — iterations 500 · depth 6 · lr 0,05 · seed 42"],
    ["model.cbm SHA-256", f"<span class='m-mono'>{meta.get('model_cbm_sha256', '—')[:32]}…</span>"],
    ["model_ready_dataset.csv SHA-256", f"<span class='m-mono'>{meta['model_ready_sha256'][:32]}…</span>"],
    ["Ham veri anlık görüntüsü", f"{tr(meta['n_ham'], 0)} kayıt × 410 kolon (SHA-256: pipeline README)"],
    ["Pipeline commit", f"<span class='m-mono'>{meta['pipeline_git_commit'][:12]}</span> (v0.4.0)"],
    ["Kod arşivi", f'<a href="https://doi.org/{zdoi}">Zenodo DOI {zdoi}</a> · <a href="{gh_p}">pipeline deposu</a> · '
                   f'<a href="{gh_a}">uygulama deposu</a>'],
    ["DOI-grup CV sonucu", "R² = 0,410 ± 0,016 · MAE 3,12 · RMSE 4,02 — <strong>ölçüm-sonrası hiçbir değişken "
                           "modele dâhil değildir</strong>; şema katmanı bunu her koşuda zorlar."],
], kv=True)
ui.text("Ölçüm-sonrası değişkenler (Voc, Jsc, FF, EQE, stabilite alanları) dâhil edilselerdi R² yapay olarak "
        "0,937'ye çıkardı (tez Deney B).", mute=True)

ui.footer()
