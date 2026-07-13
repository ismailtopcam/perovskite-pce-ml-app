# -*- coding: utf-8 -*-
"""data_app/ altindaki hazir dosyalar icin onbellekli yukleyiciler."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parents[1] / "data_app"


@st.cache_data(show_spinner=False)
def records() -> pd.DataFrame:
    return pd.read_parquet(DATA / "records_clean.parquet")


@st.cache_data(show_spinner=False)
def removed() -> pd.DataFrame:
    return pd.read_parquet(DATA / "records_removed.parquet")


@st.cache_data(show_spinner=False)
def doi_summary() -> pd.DataFrame:
    return pd.read_parquet(DATA / "doi_summary.parquet")


@st.cache_data(show_spinner=False)
def candidates() -> pd.DataFrame:
    return pd.read_parquet(DATA / "candidates.parquet")


@st.cache_data(show_spinner=False)
def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


@st.cache_data(show_spinner=False)
def js(name: str):
    return json.load(open(DATA / name, encoding="utf-8"))


@st.cache_resource(show_spinner="Model yükleniyor...")
def model():
    from catboost import CatBoostRegressor
    m = CatBoostRegressor()
    m.load_model(str(DATA / "model.cbm"))
    return m


@st.cache_resource(show_spinner="Eğitim-uzayı indeksi kuruluyor...")
def ad_index():
    """(NearestNeighbors, scaler_mean, scaler_scale, esik, train_row_ids)."""
    from sklearn.neighbors import NearestNeighbors
    z = np.load(DATA / "ad_reference.npz")
    nn = NearestNeighbors(n_neighbors=5).fit(z["X_train_scaled"])
    row_ids = z["train_row_ids"] if "train_row_ids" in z.files else None
    return nn, z["scaler_mean"], z["scaler_scale"], float(z["threshold"][0]), row_ids


@st.cache_resource(show_spinner="SHAP açıklayıcısı hazırlanıyor...")
def explainer():
    import shap
    return shap.TreeExplainer(model())
