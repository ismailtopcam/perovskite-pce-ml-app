# -*- coding: utf-8 -*-
import streamlit as st

from lib import data
from lib.ui import page, tr

page("Perovskit PCE — Sızıntı-Güvenli ML Hattı", "🔬")

meta = data.js("app_meta.json")

st.markdown(
    """
Bu uygulama, **"Perovskit Güneş Hücrelerinde Makine Öğrenmesi Tabanlı PCE Tahmini ve
Yüksek Verim Potansiyelli Aday Kompozisyonların Belirlenmesi"** başlıklı yüksek lisans
tezinin (İzmir Kâtip Çelebi Üniversitesi, Yazılım Mühendisliği) veri hattını, deneylerini
ve bulgularını **etkileşimli** olarak sunar.

Tezin ana savı şudur: *raporlanan model başarımı yalnızca algoritmadan değil,
**doğrulama ve özellik kararlarından** etkilenir.* Bu uygulamadaki her ekran bu savı
veriyle görünür kılmak için tasarlandı.
"""
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temiz kayıt", tr(meta["n_temiz"], 0), f"ham: {tr(meta['n_ham'], 0)}")
c2.metric("Grup-güvenli R²", "0,413", "± 0,006 (5-kat CV)", delta_color="off")
c3.metric("Rastgele bölme şişmesi", "+0,068", "0,481'e çıkarır", delta_color="inverse")
c4.metric("Aday kompozisyon", "756", "504 eğitimde destekli")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("📑 Sayfalar")
    st.markdown(
        """
| Sayfa | İçerik |
|---|---|
| **📖 Kullanım Rehberi** | Her ekranın ne gösterdiği, nasıl okunacağı + küçük sözlük — buradan başlayın |
| **1 — Veri Hattı** | Ham→temiz dönüşüm, eleme nedenleri, kayıt gezgini ("bu kayıt neden elendi / hangi işlemler uygulandı?") |
| **2 — Doğrulama Deneyleri** | ⭐ Tezin merkez bulgusu: bölme yöntemi ve özellik seti seçiminin R²'ye etkisi |
| **3 — Model Karşılaştırma** | 6 modelin DOI-grup CV ve holdout başarımları |
| **4 — Tahmin Aracı** | Sanal cihaz tarifi → PCE + %90 belirsizlik aralığı + yerel SHAP |
| **5 — Gerçek vs Tahmin** | 8.147 holdout kaydında hata analizi; model nerede yanılıyor? |
| **6 — Aday Tarayıcı** | 756 adayın aralıklı ve eğitim-uzayı bilgili keşfi |
| **7 — DOI Gezgini** | Yayın-düzeyi izlenebilirlik; grup-güvenli ayrımın somut hali |
| **8 — Pipeline & Provenans** | Aşama manifestleri, sürümler, denetim özetleri |
"""
    )
with col2:
    st.subheader("⚠️ Nasıl okumalı?")
    st.markdown(
        """
- Buradaki hiçbir çıktı **deneysel doğrulama yerine geçmez**; model, geçmiş
  literatürden öğrenilen örüntülerle **önceliklendirme** yapar.
- Grup-güvenli R² = 0,413 **bilinçli olarak muhafazakârdır**: görülmemiş
  yayınlara genellemeyi ölçer. Daha yüksek görünen skorlar (0,481; 0,938)
  metodolojik gevşemenin ürünüdür — 2. sayfada kendiniz deneyin.
- Belirsizlik aralıkları DOI-grup-güvenli **conformal** kalibrasyonla üretilmiştir
  (tez Bölüm 4.10).
"""
    )
    st.subheader("🧾 Provenans")
    st.markdown(
        f"""
- Pipeline commit: `{meta['pipeline_git_commit'][:12]}` · Veri hazırlama: `{meta['hazirlama_zamani_utc'][:10]}`
- Kaynak veri: [Perovskite Database](https://www.perovskitedatabase.com)
  (Jacobsson vd., 2022, CC BY 4.0) — {tr(meta['n_ham'], 0)} kayıt anlık görüntüsü
- Kod: [pipeline deposu]({meta.get('github_pipeline', '#')}) ·
  [uygulama deposu]({meta.get('github_app', '#')}) ·
  arşiv: [DOI {meta.get('zenodo_doi', '')}](https://doi.org/{meta.get('zenodo_doi', '')})
- Ölçüm-sonrası değişkenler (Voc/Jsc/FF...) modele **dahil değildir**; ayrıntı:
  Pipeline & Provenans sayfası
"""
    )

st.divider()
st.caption(
    "© İsmail Topçam — İzmir Kâtip Çelebi Üniversitesi, Yazılım Mühendisliği YL tezi eşlik "
    "uygulaması. Veri: Perovskite Database (CC BY 4.0, atıfla). Uygulama çıktıları araştırma "
    "ve eğitim amaçlıdır."
)
