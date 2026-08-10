# -*- coding: utf-8 -*-
"""Pipeline reposundan web uygulamasinin kompakt veri dosyalarini uretir.

Kullanim (uygulama kokunden):
    python tools/prepare_app_data.py [PIPELINE_REPO_YOLU]

Varsayilan pipeline yolu: ../perovskite-pce-ml
Ciktilar: data_app/  (uygulama bu klasorden calisir; deploy'a dahil edilir)

Tum bolmeler pipeline ile BIREBIR ayni tohum/mantikla yeniden kurulur ve
bilinen degerlerle assert edilir (yanlis hizalama sessizce gecemez).
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

APP = Path(__file__).resolve().parents[1]
PIPE = Path(sys.argv[1]) if len(sys.argv) > 1 else APP.parent / "perovskite-pce-ml"
OUT = APP / "data_app"
OUT.mkdir(exist_ok=True)

sys.path.insert(0, str(PIPE / "src"))
from perovskite_ml.config import load_config                      # noqa: E402
from perovskite_ml.candidates.candidate_space import enumerate_candidates  # noqa: E402

SEED, CAL_SEED, N_BINS = 42, 7, 4


def sanitize(s: str) -> str:
    return re.sub(r"[^0-9A-Za-z_]", "_", s)


def conformal_quantile(scores, coverage):
    n = len(scores)
    k = min(int(np.ceil((n + 1) * coverage)), n)
    return float(np.sort(scores)[k - 1])


def sha256(path, limit=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


print(f"[prep] pipeline: {PIPE}")
cfg = load_config(str(PIPE / "config.yaml"))
proc = PIPE / "data" / "processed"
outs = PIPE / "outputs"

# ---------------- 1) Veri + bolmelerin birebir yeniden kurulmasi ----------------
M = pd.read_csv(proc / "model_ready_dataset.csv", low_memory=False)
C = pd.read_csv(proc / "cleaned_dataset.csv", low_memory=False)
assert len(M) == len(C) == 41485, f"beklenmeyen satir sayisi: {len(M)}/{len(C)}"

y = M[cfg["target"]].values
groups = M[cfg["group_col"]].fillna("unknown_doi").astype(str).values
X = M.drop(columns=[cfg["target"], cfg["group_col"]])
feat_names = list(X.columns)
assert len(feat_names) == 77

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
tr, ho = next(gss.split(X, y, groups))
assert set(groups[tr]).isdisjoint(set(groups[ho]))
assert len(ho) == 8355, f"holdout {len(ho)}"

fold_of = np.full(len(M), -1)
for f_i, (_, vai) in enumerate(GroupKFold(n_splits=5).split(X, y, groups)):
    fold_of[vai] = f_i

pred = pd.read_csv(outs / "v4" / "best_model_holdout_predictions.csv")
avp = pd.read_csv(outs / "v4" / "actual_vs_predicted.csv")
assert len(pred) == len(ho) == len(avp)
assert np.allclose(y[ho], pred["y_true"].values, atol=1e-6), "holdout hizasiz!"

# ---------------- 2) Kategori etiket haritalari (one-hot kolon <-> ham etiket) ----------------
feat_set = set(feat_names)
CAT_COLS = [("arch", "Cell_architecture"), ("ETL", "ETL_stack_sequence"),
            ("HTL", "HTL_stack_sequence"), ("solv", cfg["features"]["solvent_col"])]
label_maps = {}
for prefix, col in CAT_COLS:
    vc = C[col].fillna("unknown").astype(str).value_counts()
    m = {}
    for raw in vc.index:
        cname = sanitize(f"{prefix}_{raw}")
        if cname in feat_set and cname not in m:
            m[cname] = raw
    other = f"{prefix}_{prefix}_other"
    if other in feat_set:
        m[other] = f"Diğer ({prefix})"
    label_maps[prefix] = m
json.dump(label_maps, open(OUT / "label_maps.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ---------------- 3) Kayit gezgini tablolari ----------------
FRAC = ["A_FA", "A_MA", "A_Cs", "A_Rb", "A_K", "A_other",
        "B_Pb", "B_Sn", "B_Ge", "B_other", "X_I", "X_Br", "X_Cl", "X_other"]


def _oran(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s != "0" else f"{v:.3g}"  # 0,005 altindaki oranlar "0" diye gorunmesin


def comp_label(row):
    parts = []
    for pre, keys in [("", ["A_FA", "A_MA", "A_Cs", "A_Rb", "A_K", "A_other"]),
                      (" | ", ["B_Pb", "B_Sn", "B_Ge", "B_other"]),
                      (" | ", ["X_I", "X_Br", "X_Cl", "X_other"])]:
        seg = " ".join(k.split("_")[1] + _oran(row[k])
                       for k in keys if row[k] > 1e-9)
        parts.append(pre + seg)
    return "".join(parts)


rec = pd.DataFrame({
    "row_id": C.index.values,
    "DOI": C["Ref_DOI_number"].fillna("(DOI yok)").astype(str).values,
    "PCE": y,
    "mimari": C["Cell_architecture"].fillna("(boş)").astype(str).values,
    "ETL": C["ETL_stack_sequence"].fillna("(boş)").astype(str).values,
    "HTL": C["HTL_stack_sequence"].fillna("(boş)").astype(str).values,
    "cozucu": C[cfg["features"]["solvent_col"]].fillna("(boş)").astype(str).values,
    "band_gap": M["band_gap"].values,
    "band_gap_dolduruldu": M["band_gap_missing"].astype(bool).values,
    "tavlama_sicaklik": M["anneal_temp"].values,
    "tavlama_sicaklik_dolduruldu": M["anneal_temp_missing"].astype(bool).values,
    "tavlama_sure": M["anneal_time"].values,
    "tavlama_sure_dolduruldu": M["anneal_time_missing"].astype(bool).values,
    "cv_fold": fold_of,
})
for c in FRAC:
    rec[c] = M[c].values
rec["kompozisyon"] = M[FRAC].apply(comp_label, axis=1)
rec["bolme"] = "eğitim"
rec.loc[ho, "bolme"] = "holdout-test"
rec["tahmin"] = np.nan
rec.loc[ho, "tahmin"] = pred["y_pred"].values
rec["mutlak_hata"] = (rec["tahmin"] - rec["PCE"]).abs()
# Her kaydin one-hot kovasi: "Veri destegi" sayimlari ham etiketle degil, modelin
# gercekte gordugu kovayla (_other ve NaN kovalari dahil) yapilabilsin diye
# label_maps gorunum etiketleriyle yazilir.
for prefix, _col in CAT_COLS:
    cols = list(label_maps[prefix])
    onehot = M[cols].to_numpy()
    assert onehot.sum(axis=1).max() <= 1, f"{prefix}: coklu kova"
    labels = np.array([label_maps[prefix][c] for c in cols], dtype=object)
    rec[f"kova_{prefix}"] = np.where(onehot.sum(axis=1) == 1,
                                     labels[onehot.argmax(axis=1)], "(kova yok)")
rec.to_parquet(OUT / "records_clean.parquet", index=False)
print(f"[prep] records_clean: {rec.shape}")

# elenen kayitlar + ham baglamlari
rem = pd.read_csv(outs / "logs" / "removed_records_log.csv")
assert len(rem) == 1913
raw_cols = ["Ref_DOI_number", "JV_default_PCE", "Module", "Cell_architecture",
            "Perovskite_composition_a_ions", "Perovskite_composition_a_ions_coefficients",
            "Perovskite_composition_b_ions", "Perovskite_composition_b_ions_coefficients",
            "Perovskite_composition_c_ions", "Perovskite_composition_c_ions_coefficients"]
raw = pd.read_csv(PIPE / cfg["paths"]["raw_csv"], encoding="utf-8-sig",
                  usecols=raw_cols, low_memory=False)[raw_cols]  # usecols dosya sirasini korur; asagidaki konumsal adlandirma icin siraya getir
ctx = raw.loc[rem["row_index"].values].reset_index(drop=True)
rem_full = pd.concat([rem.reset_index(drop=True), ctx], axis=1)
rem_full.columns = ["row_id", "neden", "DOI", "PCE_ham", "Modul", "mimari",
                    "A_iyonlar", "A_katsayilar", "B_iyonlar", "B_katsayilar",
                    "X_iyonlar", "X_katsayilar"]
rem_full.to_parquet(OUT / "records_removed.parquet", index=False)
print(f"[prep] records_removed: {rem_full.shape}")

# ---------------- 4) DOI ozeti ----------------
doi = rec.groupby("DOI").agg(
    kayit=("PCE", "size"), pce_medyan=("PCE", "median"), pce_min=("PCE", "min"),
    pce_maks=("PCE", "max"), bolme=("bolme", "first"), cv_fold=("cv_fold", "first"),
    test_mae=("mutlak_hata", "mean"),
).reset_index()
doi.to_parquet(OUT / "doi_summary.parquet", index=False)
print(f"[prep] doi_summary: {doi.shape} (7.353 grup bekleniyor)")
assert len(doi) == 7353

# ---------------- 5) Conformal (kalibrasyon ceyrek sinirlari dahil) ----------------
conf = json.load(open(outs / "conformal" / "conformal_results.json"))
g_ho = groups[ho]
cal_rel, cte_rel = next(GroupShuffleSplit(n_splits=1, test_size=0.5,
                                          random_state=CAL_SEED).split(X.iloc[ho], y[ho], g_ho))
yhat_ho, ytrue_ho = pred["y_pred"].values, y[ho]
yhat_cal, ytrue_cal = yhat_ho[cal_rel], ytrue_ho[cal_rel]
res = np.abs(ytrue_cal - yhat_cal)
assert len(res) == conf["n_calibration"] == 4144, "kalibrasyon bolmesi hizasiz"
q90 = conformal_quantile(res, 0.90)
assert abs(q90 - conf["marginal"]["90"]["half_width"]) < 1e-3, f"q90={q90}"
edges = np.quantile(yhat_cal, np.linspace(0, 1, N_BINS + 1))
bin_cal = np.clip(np.digitize(yhat_cal, edges[1:-1]), 0, N_BINS - 1)
q_bin = [conformal_quantile(res[bin_cal == b], 0.90) for b in range(N_BINS)]
for b in range(N_BINS):
    ref = conf["mondrian_90"]["per_quartile_half_width"][f"Q{b + 1}"]
    assert abs(q_bin[b] - ref) < 1e-3, f"Q{b + 1}: {q_bin[b]} != {ref}"
conf["mondrian_90"]["quartile_edges"] = [float(e) for e in edges]
conf["mondrian_90"]["per_quartile_half_width_list"] = q_bin
json.dump(conf, open(OUT / "conformal.json", "w"), indent=1)
print("[prep] conformal: ceyrek sinirlari eklendi", [round(e, 2) for e in edges])

# ---------------- 6) Adaylar (aralik + uyumluluk + egitim-uzayina yakinlik) ----------------
cand = pd.read_csv(outs / "candidates_full" / "candidate_predictions.csv")
ints = pd.read_csv(outs / "conformal" / "candidate_intervals.csv")
tri = pd.read_csv(outs / "candidates_full" / "triple_cooccurrence.csv")
KEY = ["A", "B", "X", "arch", "ETL", "HTL"]
cand = cand.merge(ints.drop(columns=["Predicted_PCE"]), on=KEY, how="left")
cand = cand.merge(tri, on=["arch", "ETL", "HTL"], how="left")
cand["egitim_kayit_sayisi"] = cand["egitim_kayit_sayisi"].fillna(0).astype(int)
cand["uyumlu_N5"] = cand["egitim_kayit_sayisi"] >= 5
# marginal yarı-genişlik tahminden bağımsızdır -> her adaya nominal %90 aralık yazılabilir
hw90 = float(conf["marginal"]["90"]["half_width"])
cand["marginal90_low"] = cand["marginal90_low"].fillna((cand["Predicted_PCE"] - hw90).round(2))
cand["marginal90_high"] = cand["marginal90_high"].fillna((cand["Predicted_PCE"] + hw90).round(2))
# uyumluluk sayıları YALNIZ eğitim bölmesinden gelir (pipeline: aday_uyumluluk_filtresi.py)
assert len(cand) == 756 and cand["uyumlu_N5"].sum() == 504

bundle = joblib.load(outs / "v4" / "best_model.joblib")
model, bfeats = bundle["model"], bundle["features"]
assert bfeats == feat_names
bg_med = float(M["band_gap"].median())
at_med = float(M["anneal_temp"].median())
ati_med = float(M["anneal_time"].median())
recipes, enc = enumerate_candidates(feat_names, bg_med, at_med, ati_med)
enc_key = recipes[KEY].astype(str).agg("|".join, axis=1)
cand_key = cand[KEY].astype(str).agg("|".join, axis=1)
assert sorted(enc_key) == sorted(cand_key) and enc_key.is_unique, \
    "aday anahtar kumeleri uyusmuyor (enumerate ile CSV farkli uzaylar)"
order = pd.Series(range(len(enc_key)), index=enc_key)[cand_key].values
enc_aligned = enc.iloc[order].reset_index(drop=True)

scaler = StandardScaler().fit(X.iloc[tr])
Xtr_s = scaler.transform(X.iloc[tr]).astype(np.float32)
nn = NearestNeighbors(n_neighbors=5).fit(Xtr_s)
d_cand, _ = nn.kneighbors(scaler.transform(enc_aligned[feat_names]).astype(np.float32))
cand["knn_uzaklik"] = d_cand.mean(axis=1).round(4)
ad_thr = conf["applicability_domain"]["threshold"]
cand["alan_ici"] = cand["knn_uzaklik"] <= ad_thr
cand.to_parquet(OUT / "candidates.parquet", index=False)
print(f"[prep] candidates: {cand.shape}; alan ici: {int(cand['alan_ici'].sum())}/756")

# ---------------- 7) Canli tahmin varliklar: model + ozellikler + AD referansi ----------------
model.save_model(str(OUT / "model.cbm"))
json.dump({"features": feat_names,
           "medians": {"band_gap": bg_med, "anneal_temp": at_med, "anneal_time": ati_med},
           "train_pce_max": float(y[tr].max()), "n_train": int(len(tr))},
          open(OUT / "features.json", "w"), indent=1)
np.savez_compressed(OUT / "ad_reference.npz",
                    X_train_scaled=Xtr_s,
                    scaler_mean=scaler.mean_, scaler_scale=scaler.scale_,
                    threshold=np.array([ad_thr]),
                    train_row_ids=rec.loc[tr, "row_id"].values.astype(np.int64))
print(f"[prep] model.cbm + ad_reference ({Xtr_s.shape}, row_ids dahil)")

# ---------------- 8) Kucuk dosyalarin kopyalari ----------------
import shutil
COPY = [
    ("outputs/v4/validation_experiments.csv", "validation_experiments.csv"),
    ("outputs/v4/model_comparison_holdout.csv", "model_comparison_holdout.csv"),
    ("outputs/v4/model_comparison_groupkfold.csv", "model_comparison_groupkfold.csv"),
    ("outputs/shap_full/shap_top_features.csv", "shap_top_features.csv"),
    ("outputs/conformal/conformal_summary.csv", "conformal_summary.csv"),
    ("outputs/logs/clean_summary.json", "clean_summary.json"),
    ("outputs/logs/removed_reason_counts.csv", "removed_reason_counts.csv"),
    ("outputs/robustness/doi_grup_dogrulama.json", "doi_grup_dogrulama.json"),
    ("outputs/robustness/doi_normalizasyon_duyarlilik.json", "doi_normalizasyon_duyarlilik.json"),
    ("outputs/robustness/kontamine_test_maesi.json", "kontamine_test_maesi.json"),
    ("outputs/pipeline_cv/results.json", "pipeline_cv_results.json"),
    ("outputs/ablation/descriptor_ablation.json", "descriptor_ablation.json"),
    ("outputs/screening/enrichment.csv", "enrichment.csv"),
    ("outputs/screening/metadata.json", "screening_metadata.json"),
    ("outputs/tuning/best_params.json", "tuning_best_params.json"),
    ("outputs/tuning_catboost/best_params.json", "tuning_catboost_best_params.json"),
]
for src, dst in COPY:
    shutil.copy2(PIPE / src, OUT / dst)

manifests = []
for p in sorted((outs / "manifests").glob("manifest_*.json")):
    manifests.append(json.load(open(p, encoding="utf-8")))
manifests.append(json.load(open(outs / "pipeline_cv" / "manifest_14_pipeline_cv.json",
                                encoding="utf-8")))
json.dump(manifests, open(OUT / "manifests.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"[prep] {len(COPY)} kopya + {len(manifests)} manifest")

# ---------------- 9) Meta / provenans ----------------
try:
    git_hash = subprocess.run(["git", "-C", str(PIPE), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
except Exception:
    git_hash = "bilinmiyor"
meta = {
    "hazirlama_zamani_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "pipeline_git_commit": git_hash,
    "model_ready_sha256": sha256(proc / "model_ready_dataset.csv"),
    "model_cbm_sha256": sha256(OUT / "model.cbm"),
    "n_ham": 43398, "n_temiz": int(len(M)), "n_elenen": int(len(rem_full)),
    "n_egitim": int(len(tr)), "n_holdout": int(len(ho)),
    "n_ozellik": len(feat_names), "seed": SEED,
    "zenodo_doi": "10.5281/zenodo.20829027",  # concept DOI: tum surumler, daima en yeniye cozunur
    "github_pipeline": "https://github.com/ismailtopcam/perovskite-pce-ml-thesis",
    "github_app": "https://github.com/ismailtopcam/perovskite-pce-ml-app",
}
json.dump(meta, open(OUT / "app_meta.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"[prep] TAMAM -> {OUT} | pipeline commit {git_hash[:8]}")
