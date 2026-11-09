# -*- coding: utf-8 -*-
"""02 Doğrulama Deneyleri — tezin merkez bulgusu: bölme yöntemi ve özellik kümesi kararlarının R²'ye etkisi."""
import numpy as np
import plotly.express as px
import streamlit as st

from lib import data, ui
from lib.ui import tr, INK, ACC

val = data.csv("validation_experiments.csv").set_index("ayar")
rec = data.records()
ho = rec[rec["bolme"] == "holdout-test"]
conf = data.js("conformal.json")
HW = float(conf["marginal"]["90"]["half_width"])

R = {k: (float(val.loc[k, "R2_mean"]), float(val.loc[k, "R2_std"])) for k in val.index}
grup_r2, grup_std = R["DOI_grup_KFold"]
rast_r2, rast_std = R["rastgele_KFold"]
leak_r2, leak_std = R["leakage_ON (+Voc,Jsc,FF)"]
c14, c57, c77 = R["kompozisyon (14 ozellik)"], R["+cihaz (57 ozellik)"], R["+surec_tam (77 ozellik)"]

ui.page_header(
    "02 — Doğrulama Deneyleri · Tez Bölüm 3.13 ve 4.3",
    "Kararları siz verin.",
    "Aynı veri, aynı model: yalnızca bölme yöntemi ve özellik kümesi değiştirildiğinde R² "
    f"<strong>{tr(c14[0], 3)} ile {tr(leak_r2, 3)}</strong> arasında değişir. Başarım, algoritmadan çok bu "
    "kararların ürünüdür.",
)

left, right = st.columns([5, 7], gap="large")

with left:
    ui.kicker("Bölme yöntemi", tone="ink")
    bolme = st.segmented_control("Bölme yöntemi", ["DOI-grup (yayın-ayrık)", "Rastgele KFold"],
                                 default="DOI-grup (yayın-ayrık)", label_visibility="collapsed")
    ui.text("Aynı yayının kardeş cihazları eğitim+test'e birlikte düşerse model \"görmediği\" veriyi dolaylı "
            "görmüş olur.", mute=True)
    ui.kicker("Özellik kümesi", tone="ink")
    ozellik = st.segmented_control("Özellik kümesi", ["Ölçüm-öncesi 77 özellik", "+ Voc, Jsc, FF"],
                                   default="Ölçüm-öncesi 77 özellik", label_visibility="collapsed")
    ui.text("Voc × Jsc × FF ≈ PCE: bu üçlü, hedefin kendisini dolaylı taşır — sentez öncesi bilinemez.",
            mute=True)

    grup = (bolme or "DOI").startswith("DOI")
    safe = (ozellik or "Ölçüm").startswith("Ölçüm")
    if grup and safe:
        r2, std, delta, dfg, r2fg = grup_r2, grup_std, "· taban değer", "var(--n700)", "var(--ink)"
        yb, y = "Tezin ana sonucu.", ("Eğitimden kanonik DOI anahtarı düzeyinde ayrık tutulan yayınlara "
                                     "genellemenin dürüst ölçüsü.")
    elif not grup and safe:
        r2, std = rast_r2, rast_std
        delta, dfg, r2fg = f"+{tr(r2 - grup_r2, 3)} taban değere göre", "var(--acc)", "var(--ink)"
        yb, y = f"+{tr(r2 - grup_r2, 3)} iyimserlik:", ("kardeş cihazlar test kümesine sızdı. Skor arttı, "
                                                          "genelleme gücü artmadı (tez Deney A).")
    elif grup and not safe:
        r2, std = leak_r2, leak_std
        delta, dfg, r2fg = f"+{tr(r2 - grup_r2, 3)} taban değere göre", "var(--acc)", "var(--acc)"
        yb, y = "Hedef sızıntısı.", ("Voc×Jsc×FF, PCE'yi neredeyse doğrudan verir: model artık tahmin değil, "
                                     "kopyalama yapıyor (tez Deney B). Sentez ÖNCESİ bu değerler bilinemez.")
    else:
        r2, std, delta, dfg, r2fg = None, None, "· tezde koşulmadı", "var(--n700)", "var(--ink)"
        yb, y = "Bu kombinasyon tezde koşulmadı:", ("iki gevşek kararı birleştirmek yalnızca daha da iyimser "
                                                    "(ve daha da anlamsız) bir skor üretir.")
    st.html(
        '<div style="border-top:1px solid var(--div); padding-top:18px; margin-top:8px">'
        f'<div class="m-kicker mute">Grup-CV R² <span style="color:{dfg}">{delta}</span></div>'
        '<div style="display:flex; align-items:baseline; gap:14px">'
        f'<div style="font-weight:800; font-size:clamp(52px,6vw,76px); line-height:1.05; color:{r2fg}">'
        f'{tr(r2, 3) if r2 is not None else "—"}</div>'
        f'<div style="font-size:13px; color:var(--n700)">{("± " + tr(std, 3) + " (5 kat)") if std is not None else ""}</div>'
        '</div>'
        f'<div class="m-text" style="margin-top:8px; max-width:52ch"><strong>{yb}</strong> {y}</div></div>'
    )

with right:
    ui.kicker("Deney A + B — bölme ve sızıntının etkisi", "(R², 5-kat CV, eksen 0–1)", tone="ink")
    ui.bar_rows([
        dict(name="DOI-grup", sub="— başlık sonuç", value=grup_r2, value_str=tr(grup_r2, 3),
             value_sub=f"±{tr(grup_std, 3)}", tone="ink", sel="şu anki seçiminiz" if (grup and safe) else ""),
        dict(name="Rastgele bölme", sub="— kardeş-cihaz sızıntısı", value=rast_r2, value_str=tr(rast_r2, 3),
             value_sub=f"±{tr(rast_std, 3)}", tone="mid", sel="şu anki seçiminiz" if (not grup and safe) else ""),
        dict(name="+ Voc / Jsc / FF", sub="— hedef sızıntısı", value=leak_r2,
             value_str=f'<span style="color:var(--acc)">{tr(leak_r2, 3)}</span>',
             value_sub=f"±{tr(leak_std, 3)}", tone="acc", sel="şu anki seçiminiz" if (grup and not safe) else ""),
    ], vmax=1.0)

    ui.kicker("Deney C — özellik kapsamı", "(R², DOI-grup CV, eksen 0–0,5)", tone="ink")
    ui.bar_rows([
        dict(name="Kompozisyon", sub="(14 özellik)", value=c14[0], value_str=tr(c14[0], 3), bold=False),
        dict(name="+ Cihaz", sub="(57 özellik)", value=c57[0], value_str=tr(c57[0], 3), bold=False),
        dict(name="+ Süreç", sub="(77 özellik)", value=c77[0], value_str=tr(c77[0], 3), bold=False),
    ], vmax=0.5)
    ui.text(f"PCE yalnızca kompozisyonla açıklanamıyor ({tr(c14[0], 3)}); cihaz ({tr(c57[0], 3)}) ve süreç "
            f"({tr(c77[0], 3)}) bilgisi anlamlı katkı veriyor (tez Bölüm 4.3).", mute=True)

    mae = float(ho["mutlak_hata"].mean())
    rmse = float(np.sqrt(((ho["tahmin"] - ho["PCE"]) ** 2).mean()))
    ssr = ((ho["PCE"] - ho["tahmin"]) ** 2).sum()
    sst = ((ho["PCE"] - ho["PCE"].mean()) ** 2).sum()
    st.html('<div style="border-top:1px solid var(--div); margin-top:6px"></div>')
    ui.kicker("Başlık kurulumun holdout görünümü", f"({tr(len(ho), 0)} kayıt)", tone="ink")
    ui.stats([
        ("Holdout R²", tr(1 - ssr / sst, 3)),
        ("MAE (puan)", tr(mae, 2)),
        ("RMSE (puan)", tr(rmse, 2)),
        ("%90 bandı", f"±{tr(HW, 2)}"),
    ], border=False)
    ui.text(f"Literatürdeki 0,70+ skorlarla tezin {tr(grup_r2, 3)}'u arasındaki farkın büyük bölümü model "
            "kalitesi değil, <strong>protokol</strong> farkıdır (tez Tablo 2.1; Kapoor ve Narayanan, 2023).",
            mute=True)

with st.expander("Holdout dağılımı — gerçek – tahmin serpmesi ve hata dağılımı"):
    l, r = st.columns(2, gap="large")
    with l:
        plot_df = ho.sample(min(4000, len(ho)), random_state=1)
        fig = px.scatter(plot_df, x="tahmin", y="PCE", opacity=0.25,
                         labels={"tahmin": "Model tahmini (PCE)", "PCE": "Gerçek PCE"})
        fig.update_traces(marker=dict(size=4, color=INK))
        fig.add_shape(type="line", x0=-4, y0=-4, x1=30, y1=30, line=dict(color=INK, width=1))
        fig.add_shape(type="line", x0=-4, y0=-4 + HW, x1=30, y1=30 + HW, line=dict(color=ACC, width=1, dash="dash"))
        fig.add_shape(type="line", x0=-4, y0=-4 - HW, x1=30, y1=30 - HW, line=dict(color=ACC, width=1, dash="dash"))
        n_neg = int((plot_df["tahmin"] < 0).sum())
        fig.update_layout(xaxis_range=[-4, 30], yaxis_range=[0, 32])
        ui.chart(fig, height=380, title=f"Gerçek – tahmin (kesikli: ±{tr(HW, 2)} = %90 bandı; negatif tahminler "
                                        f"dâhil, örneklemde {n_neg} adet)")
    with r:
        err = (ho["tahmin"] - ho["PCE"])
        fig = px.histogram(err, nbins=80, labels={"value": "İşaretli hata (tahmin − gerçek)"})
        fig.update_traces(marker_color=INK, showlegend=False)
        fig.add_vline(x=0, line_color=ACC)
        fig.update_layout(yaxis_title="Kayıt")
        ui.chart(fig, height=380, title=f"Hata dağılımı (medyan mutlak hata {tr(ho['mutlak_hata'].median(), 2)})")

ui.footer()
