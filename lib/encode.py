# -*- coding: utf-8 -*-
"""Kullanici tarifini modelin 77-ozellik formatina kodlar.

Sozlesme, pipeline'daki candidates/candidate_space.py ile birebir aynidir:
tum ozellikler 0'dan baslar; kompozisyon oranlari, sayisal degerler ve
secilen kategorilerin one-hot kolonlari doldurulur. Doldurma bayraklari
kullanici 'bilinmiyor' derse 1 olur ve deger egitim medyaniyla doldurulur
(feature_builder'in davranisiyla ayni).
"""
import numpy as np
import pandas as pd

from lib import data

ION_COLS = {
    "A": ["A_FA", "A_MA", "A_Cs", "A_Rb", "A_K"],
    "B": ["B_Pb", "B_Sn", "B_Ge"],
    "X": ["X_I", "X_Br", "X_Cl"],
}


def categorical_options():
    """{prefix: {kolon_adi: ham_etiket}} — arayuz secenekleri, siklik sirasinda."""
    return data.js("label_maps.json")


def encode(a: dict, b: dict, x: dict, arch_col: str, etl_col: str, htl_col: str,
           solv_col: str, band_gap, anneal_temp, anneal_time,
           bg_unknown=False, at_unknown=False, ati_unknown=False) -> pd.DataFrame:
    meta = data.js("features.json")
    feats = meta["features"]
    med = meta["medians"]
    row = {f: 0.0 for f in feats}

    for site, vals in (("A", a), ("B", b), ("X", x)):
        for ion, frac in vals.items():
            col = f"{site}_{ion}"
            if col in row and frac > 0:
                row[col] = float(frac)

    row["band_gap"] = med["band_gap"] if bg_unknown else float(band_gap)
    row["band_gap_missing"] = 1.0 if bg_unknown else 0.0
    row["anneal_temp"] = med["anneal_temp"] if at_unknown else float(anneal_temp)
    row["anneal_temp_missing"] = 1.0 if at_unknown else 0.0
    row["anneal_time"] = med["anneal_time"] if ati_unknown else float(anneal_time)
    row["anneal_time_missing"] = 1.0 if ati_unknown else 0.0

    for col in (arch_col, etl_col, htl_col, solv_col):
        if col in row:
            row[col] = 1.0

    return pd.DataFrame([row])[feats]


def ad_distance(enc: pd.DataFrame):
    """(knn_uzaklik, esik, alan_ici) — egitim-uzayina yakinlik (tez Bolum 4.10)."""
    nn, mean, scale, thr = data.ad_index()
    xs = ((enc.values - mean) / scale).astype(np.float32)
    d, _ = nn.kneighbors(xs)
    dist = float(d.mean())
    return dist, thr, dist <= thr


def conformal_interval(pred: float):
    """(m_lo, m_hi, q_lo, q_hi, ceyrek_adi) — marginal %90 + Mondrian ceyregi."""
    conf = data.js("conformal.json")
    hw = conf["marginal"]["90"]["half_width"]
    edges = conf["mondrian_90"]["quartile_edges"]
    qhw = conf["mondrian_90"]["per_quartile_half_width_list"]
    b = int(np.clip(np.digitize([pred], edges[1:-1])[0], 0, 3))
    return pred - hw, pred + hw, pred - qhw[b], pred + qhw[b], f"Q{b + 1}"
