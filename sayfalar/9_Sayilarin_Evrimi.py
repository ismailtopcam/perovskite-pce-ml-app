# -*- coding: utf-8 -*-
"""09 Sayıların Evrimi — bildiriden (v0.3.x, ham DOI anahtarı) teze (v0.4.0, kanonik DOI anahtarı).

Tez (v0.4.0) değerleri uygulamanın veri dosyalarından okunur. v0.3.x değerleri iki kaynaktan gelir:
ham anahtarlı duyarlılık koşusu (doi_normalizasyon_duyarlilik.json: CV ve holdout) ve tez Bölüm 5.8'de
alıntılanan bildiri değerleri (iyimserlik, yalnızca kompozisyon R², aday tavanı). Ham anahtarın sınır aşımı
sayıları tez Bölüm 5.7'den; kanonik anahtardaki sıfır doi_grup_dogrulama.json'dan gelir.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib import data, ui
from lib.ui import tr

# Eski → yeni sıralı iki adım (tek ton). dataviz doğrulayıcısı (--ordinal, zemin #f3f2f2): tüm kontroller geçti.
ESKI = "#f0806b"   # v0.3.x · ham DOI anahtarı (açık adım; içi boş işaretle de ayrışır)
YENI = ui.ACC700   # v0.4.0 · kanonik DOI anahtarı = tez (koyu adım)

# Tez Bölüm 5.8: bildiride ve sunumunda yer alan v0.3.x değerleri
BILDIRI = {"iyimserlik": 0.068, "kompozisyon": 0.263, "tavan": 17.78}
# Tez Bölüm 5.7: ham anahtarla 44 yayın büyük/küçük harf farkıyla iki varyant; sınır aşımı
HAM = {"varyant": 44, "cv_kayit": 362, "cv_yayin": 37, "cv_oran": 0.87, "ho_kayit": 87, "ho_yayin": 10}

meta = data.js("app_meta.json")
d = data.js("doi_normalizasyon_duyarlilik.json")
g = data.js("doi_grup_dogrulama.json")
pcv = data.js("pipeline_cv_results.json")
tun = data.js("tuning_best_params.json")
val = data.csv("validation_experiments.csv")
cand = data.candidates()

ham, kan = d["raw_groups"], d["normalized_groups"]


def deney(ayar_bas: str) -> float:
    return float(val[val["ayar"].str.startswith(ayar_bas)].iloc[0]["R2_mean"])


def fark(a: float, b: float, nd: int = 3) -> str:
    v = round(b - a, nd)
    return ("+" if v > 0 else "−" if v < 0 else "±") + tr(abs(v), nd)


def doi_link(doi: str) -> str:
    return f'<a href="https://doi.org/{doi}">{doi}</a>'


cv0, s0 = ham["gkf5"]["R2_mean"], ham["gkf5"]["R2_std"]
# Kanonik koşu için tam hassasiyetli değerler (doi_normalizasyon dosyası 4 basamağa yuvarlıyor: 0,0165 → "0,017")
cv1, s1 = pcv["global_mean"], pcv["global_std"]
iyim1 = deney("rastgele") - cv1
komp1 = deney("kompozisyon")
tavan1 = float(cand["Predicted_PCE"].max())
asim1 = int(g["n_records_split_cv"]) + int(g["n_records_split_holdout"])
folds0, folds1 = ham["gkf5"]["R2_folds"], pcv["global_folds"]

ui.page_header(
    "09 — Sayıların Evrimi · Tez Bölüm 3.15, 5.7, 5.8",
    "Bildiriden teze: sayılar neden değişti?",
    "ICRAS 2026 bildirisi hattın <strong>ham DOI anahtarlı v0.3.x</strong> sürümüyle hazırlandı. Tez ise aynı "
    "yayının farklı yazılmış DOI'lerini tek anahtarda birleştiren <strong>kanonik DOI gruplamasını (v0.4.0)</strong> "
    "kullanır. Bu sayfa ana sayıların iki sürümdeki değerini, farkın nedenini ve katlar arası değişkenliğe göre "
    "büyüklüğünü gösterir.",
)

ui.stats([
    ("Birleşen DOI varyantı", str(HAM["varyant"]), f"{tr(ham['n_groups'], 0)} → {tr(kan['n_groups'], 0)} yayın grubu"),
    ("Ham anahtarda kat sınırını aşan", tr(HAM["cv_kayit"], 0),
     f"kayıt (%{tr(HAM['cv_oran'], 2)}) · {HAM['cv_yayin']} yayın"),
    ("Kanonik anahtarda", tr(asim1, 0), "sınırı aşan kayıt", "acc"),
    ("CV R² farkı", fark(cv0, cv1), f"katlar arası s.s. ({tr(s1, 3)}) altında"),
], big=True)

# ---------------------------------------------------------------- kat dağılımı
ui.kicker("Beş katın dağılımı", sub="5 katlı DOI-grup çapraz doğrulama · CatBoost")
OFS = [-0.14, -0.07, 0.0, 0.07, 0.14]   # aynı satırdaki noktalar üst üste binmesin
fig = go.Figure()
for y0, folds, col, ad, dolu, m, s in ((1.0, folds0, ESKI, "Ham anahtar · v0.3.x", False, cv0, s0),
                                       (0.0, folds1, YENI, "Kanonik anahtar · v0.4.0 (tez)", True, cv1, s1)):
    fig.add_trace(go.Scatter(x=[m - s, m + s], y=[y0, y0], mode="lines", line=dict(color=col, width=10),
                             opacity=0.22, hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=[m, m], y=[y0 - 0.24, y0 + 0.24], mode="lines", line=dict(color=col, width=2),
                             hovertemplate=f"{ad}<br>ortalama R² {tr(m, 4)} ± {tr(s, 4)}<extra></extra>",
                             showlegend=False))
    fig.add_trace(go.Scatter(
        x=folds, y=[y0 + o for o in OFS], mode="markers", name=ad,
        marker=dict(size=12, color=col if dolu else ui.BG, line=dict(color=ui.BG if dolu else col, width=2)),
        customdata=[[i + 1, tr(v, 4)] for i, v in enumerate(folds)],
        hovertemplate=f"{ad}<br>kat %{{customdata[0]}} · R² %{{customdata[1]}}<extra></extra>"))
    fig.add_annotation(x=m, y=y0 + 0.34, text=f"ortalama {tr(m, 3)} ± {tr(s, 3)}", showarrow=False,
                       font=dict(size=11, color=ui.INK))
i_min = min(range(len(folds1)), key=lambda i: folds1[i])
fig.add_annotation(x=folds1[i_min], y=OFS[i_min], text=f"zayıf kat · {tr(folds1[i_min], 3)}", showarrow=True,
                   arrowhead=0, arrowcolor=ui.N600, ax=0, ay=-34, font=dict(size=11, color=ui.N800))
fig.update_yaxes(tickvals=[1, 0], ticktext=["Ham anahtar<br>v0.3.x", "Kanonik anahtar<br>v0.4.0 · tez"],
                 range=[-0.55, 1.55], showgrid=False, zeroline=False)
fig.update_xaxes(range=[0.37, 0.43], dtick=0.01, tickformat=".2f", title_text="R²")
fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))  # ui.chart lejantı birleştirir
ui.chart(fig, height=320, separators=",.")
ui.text(f"Katlar iki koşuda aynı kayıtlardan oluşmaz: grup anahtarı değişince GroupKFold yayınları katlara farklı "
        f"dağıtır. Bu yüzden katlar eşleştirilmeden dağılımlar karşılaştırılır. Ortalama {fark(cv0, cv1)} değişti; "
        f"kanonik koşudaki standart sapma artışı tek bir zayıf kattan (R² ≈ {tr(folds1[i_min], 3)}) gelir, diğer dört "
        f"kat {tr(min(v for i, v in enumerate(folds1) if i != i_min), 2)}–"
        f"{tr(max(folds1), 2)} bandındadır.", mute=True)
with st.expander("Kat değerleri (tablo)"):
    st.dataframe(pd.DataFrame({"Kat": range(1, 6), "Ham anahtar · v0.3.x": folds0,
                               "Kanonik anahtar · v0.4.0": folds1}),
                 hide_index=True, width="stretch",
                 column_config={c: st.column_config.NumberColumn(format="%.4f")
                                for c in ("Ham anahtar · v0.3.x", "Kanonik anahtar · v0.4.0")})

# ---------------------------------------------------------------- bildiri ↔ tez
ui.kicker("Bildiri ve tez: ana sayılar")
ui.table(
    ["Sayı", "v0.3.x · ham anahtar", "v0.4.0 · kanonik (tez)", "Fark", "Tez bölümü"],
    [
        ["5 katlı DOI-grup CV R² (CatBoost)", f"{tr(cv0)} ± {tr(s0)}", f"<strong>{tr(cv1)} ± {tr(s1)}</strong>",
         fark(cv0, cv1), "4.2"],
        ["Holdout R²", f"{tr(ham['holdout']['R2'])} <small>({tr(ham['holdout']['n_test'], 0)} kayıt)</small>",
         f"<strong>{tr(kan['holdout']['R2'])}</strong> <small>({tr(kan['holdout']['n_test'], 0)} kayıt)</small>",
         fark(ham["holdout"]["R2"], kan["holdout"]["R2"]), "4.2"],
        ["Rastgele bölmenin iyimserliği (Deney A)", tr(BILDIRI["iyimserlik"]), f"<strong>{tr(iyim1)}</strong>",
         fark(BILDIRI["iyimserlik"], iyim1), "4.3"],
        ["Yalnızca kompozisyonla R² (Deney C)", tr(BILDIRI["kompozisyon"]), f"<strong>{tr(komp1)}</strong>",
         fark(BILDIRI["kompozisyon"], komp1), "4.3"],
        ["Aday tavanı (en yüksek tahmini PCE, %)", tr(BILDIRI["tavan"], 2), f"<strong>{tr(tavan1, 2)}</strong>",
         fark(BILDIRI["tavan"], tavan1, 2), "4.5"],
        ["Yayın (DOI) grubu", tr(ham["n_groups"], 0), f"<strong>{tr(kan['n_groups'], 0)}</strong>",
         f"−{HAM['varyant']} (birleşen varyant)", "3.8, 5.7"],
        ["Kat sınırını aşan kayıt",
         f"{HAM['cv_kayit']} <small>({HAM['cv_yayin']} yayın; holdout sınırında {HAM['ho_kayit']} kayıt)</small>",
         f"<strong>{asim1}</strong>", "sızıntı giderildi", "5.7"],
    ],
    right_cols=(1, 2, 3), hi_row=0,
)
ui.text("v0.3.x sütununda CV ve holdout değerleri ham anahtarlı duyarlılık koşusundan gelir. CV değeri bildirideki "
        "0,413 ± 0,006 ile aynıdır; holdout kümesi gruplama değiştiği için farklı büyüklüktedir. İyimserlik, yalnızca "
        "kompozisyon R² ve aday tavanı bildiride raporlanan değerlerdir (tez Bölüm 5.8). Ham anahtarın sınır aşımı "
        "tez Bölüm 5.7'den, kanonik anahtardaki sıfır denetim çıktısından (doi_grup_dogrulama.json) alınmıştır.",
        mute=True)

ui.box(
    f"<p><strong>Perovskite Database'de {HAM['varyant']} yayının DOI'si yalnızca büyük/küçük harf farkıyla iki ayrı "
    "biçimde kayıtlıdır.</strong> Ham anahtar bu iki biçimi ayrı yayın sayar; GroupKFold onları farklı katlara "
    "yerleştirebilir ve aynı yayının kardeş cihazları hem eğitimde hem testte bulunur. Ham anahtarla "
    f"{HAM['cv_yayin']} yayın ({HAM['cv_kayit']} kayıt, verinin %{tr(HAM['cv_oran'], 2)}'si) çapraz doğrulama kat "
    f"sınırını, {HAM['ho_yayin']} yayın ({HAM['ho_kayit']} kayıt) holdout sınırını aşıyordu. v0.4.0 DOI'yi kanonik "
    "biçime getirerek bu varyantları tek anahtarda birleştirir; denetim, kanonik anahtarda sınırı aşan kayıt "
    "kalmadığını doğrular.</p>"
    f"<p>Farkların yönü de beklenen yöndür: sızıntı kalkınca grup-güvenli CV skoru biraz düşer ({tr(cv0)} → "
    f"{tr(cv1)}), rastgele bölmenin iyimserliği biraz büyür ({tr(BILDIRI['iyimserlik'])} → {tr(iyim1)}). "
    "İki fark da katlar arası standart sapmanın altındadır; nitel sonuçların hiçbiri değişmez.</p>",
    k="Neden değişti?")

# ---------------------------------------------------------------- sürüm zinciri
ui.kicker("Sürüm zinciri", tone="ink")
ui.flow([
    ("v0.3.0 – v0.3.5", "17–30 Temmuz 2026 · ham DOI anahtarı · bildiri değerleri"),
    ("v0.4.0", f"10 Ağustos 2026 · kanonik DOI anahtarı · commit {meta['pipeline_git_commit'][:7]}"),
    ("Ana dal", "Ekim–Kasım 2026 · sonuçları değiştirmeyen ek denetimler"),
])
ui.table([], [
    ["v0.3.4 · 28 Temmuz 2026", doi_link("10.5281/zenodo.21639239")],
    ["v0.3.5 · 30 Temmuz 2026", doi_link("10.5281/zenodo.21704124")],
    ["v0.4.0 · 10 Ağustos 2026 (tezin atıf yaptığı sürüm)", doi_link("10.5281/zenodo.21870009")],
    ["Tüm sürümler (kavram DOI)", doi_link(meta.get("zenodo_doi", "10.5281/zenodo.20829027"))],
], kv=True)

# ---------------------------------------------------------------- sonradan eklenen denetimler
ui.kicker("v0.4.0 sonrası denetimler", sub="hiçbiri tezin nitel sonucunu değiştirmedi", tone="ink")
ui.list_rows([
    ("Kat içi ön işleme · Bölüm 3.7",
     f"Ön işleme her katta yalnızca eğitim kısmından öğrenildiğinde R² {tr(pcv['foldlocal_mean'], 4)}; global "
     f"ön işlemeyle {tr(pcv['global_mean'], 4)}. Fark {tr(abs(pcv['delta']), 4)}."),
    ("Model ailesi seçimi · Bölüm 4.2",
     "İç içe (nested) grup-CV, dış 5 / iç 3 kat: R² 0,408 ± 0,017; beş dış katın dördünde CatBoost seçildi."),
    ("Aydınlatma koşulu · Bölüm 4.2",
     "50 mW/cm²'nin altında ölçülen 114 kayıt dışlanınca R² 0,419 ± 0,015; 100 mW/cm² dışında ölçülen 394 kayıt "
     "dışlanınca 0,416 ± 0,015."),
    ("Hiperparametre araması · Bölüm 4.8",
     f"HistGBM'de ayarlı ve varsayılan yapılandırma {tr(tun['tuned_cv_r2'][0], 4)} ile aynı skoru verdi; CatBoost "
     "araması temel yapılandırmayı seçti."),
    ("Tarama belirsizliği · Bölüm 4.6",
     "Yayınlara göre kümeli bootstrap (1.000 tekrar): Spearman korelasyonu için %95 aralığı 0,57–0,65; ilk %5'te "
     "PCE ≥ 18 zenginleşmesi 3,2–5,0 kat."),
    ("Veri bağlamı · Bölüm 3.1, 5.7",
     "Temiz kümenin %98,4'ü 2020 ve öncesinde yayımlanmış kayıtlardan gelir; ters ve ileri taramanın birlikte "
     "raporlandığı 8.338 kayıtta ters tarama PCE'si medyanda 0,66 puan yüksektir."),
])

# ---------------------------------------------------------------- değişmeyenler
ui.kicker("Değişmeyenler", tone="mute")
ui.stats([
    ("Ham kayıt", tr(meta["n_ham"], 0)),
    ("Temiz kayıt", tr(meta["n_temiz"], 0)),
    ("Özellik", tr(meta["n_ozellik"], 0)),
    ("Aday", tr(len(cand), 0)),
    ("Holdout", tr(meta["n_holdout"], 0)),
], small=True)

ui.tez_notu("Bölüm 3.15, 5.7, 5.8",
            "Bildiri değerleri v0.3.x'e, tez değerleri v0.4.0'a aittir; iki sürüm arasındaki farklar kat gürültüsü "
            "içinde kalır ve nitel sonuçları değiştirmez.")
ui.footer()
