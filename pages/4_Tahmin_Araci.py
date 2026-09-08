# -*- coding: utf-8 -*-
"""04 Tahmin Aracı — sanal cihaz tarifi → PCE tahmini, %90 aralık, eğitim-uzayına uzaklık, yerel SHAP."""
import numpy as np
import pandas as pd
import streamlit as st

from lib import data, encode, ui
from lib.ui import tr, pct

maps = encode.categorical_options()
fmeta = data.js("features.json")
conf = data.js("conformal.json")
HW = float(conf["marginal"]["90"]["half_width"])
THR = float(conf["applicability_domain"]["threshold"])
COV = 100 * float(conf["marginal"]["90"]["empirical_coverage"])

ui.page_header(
    "04 — Tahmin Aracı · Tez Bölüm 3.12 ve 4.10",
    "Sanal cihaz tarifi.",
    "Tarif, modelin eğitimde gördüğü 77-özellik sözleşmesine kodlanır. Belirsizlik aralığı, eğitimden kanonik "
    "DOI anahtarı düzeyinde ayrık tutulan yayınlardaki gerçek hataların dağılımından türetilir (conformal "
    f"kestirim; nominal %90, holdout kapsaması %{tr(COV, 1)}).",
)

left, right = st.columns([5, 7], gap="large")

# ---------------------------------------------------------------- tarif formu
with left:
    ui.kicker("Kompozisyon", "· her site toplamı 1,00 olmalı", tone="ink")
    c = st.columns(3)
    heads = []
    sites = {}
    for col, (site, ions, defaults) in zip(c, [
        ("A", ["FA", "MA", "Cs", "Rb", "K"], {"FA": 0.80, "MA": 0.10, "Cs": 0.10}),
        ("B", ["Pb", "Sn", "Ge"], {"Pb": 1.00}),
        ("X", ["I", "Br", "Cl"], {"I": 0.83, "Br": 0.17}),
    ]):
        with col:
            heads.append(st.empty())
            sites[site] = {i: st.number_input(i, 0.0, 1.0, defaults.get(i, 0.0), 0.01, key=f"p4_{site}_{i}")
                           for i in ions}
    a, b, x = sites["A"], sites["B"], sites["X"]
    sums = {s: sum(v.values()) for s, v in sites.items()}
    oks = {s: abs(v - 1.0) <= 0.011 for s, v in sums.items()}
    for h, s in zip(heads, ["A", "B", "X"]):
        h.html(f'<div style="display:flex; justify-content:space-between; align-items:baseline; '
               f'border-bottom:2px solid var(--ink); padding-bottom:4px; margin:6px 0 2px">'
               f'<span style="font-weight:800; font-size:13px">{s}-site</span>'
               f'<span style="font-size:11px; font-weight:700; color:{"var(--n700)" if oks[s] else "var(--acc)"}">'
               f'Σ {tr(sums[s], 2)}</span></div>')

    ui.kicker("Cihaz yığını ve süreç", tone="ink")
    d = st.columns(2)
    arch = d[0].selectbox("Mimari", list(maps["arch"].items()), format_func=lambda kv: kv[1],
                          index=list(maps["arch"].values()).index("nip") if "nip" in maps["arch"].values() else 0)
    etl = d[1].selectbox("ETL", list(maps["ETL"].items()), format_func=lambda kv: kv[1])
    htl = d[0].selectbox("HTL", list(maps["HTL"].items()), format_func=lambda kv: kv[1])
    solv = d[1].selectbox("Çözücü sistemi", list(maps["solv"].items()), format_func=lambda kv: kv[1])
    e = st.columns(3)
    with e[0]:
        ph = st.empty()
        bg_unk = st.checkbox("bilinmiyor", key="p4_bg_unk")
        bg = ph.number_input("Band gap (eV)", 1.0, 3.6, 1.60, 0.01, disabled=bg_unk)
    with e[1]:
        ph = st.empty()
        at_unk = st.checkbox("bilinmiyor", key="p4_at_unk")
        at = ph.number_input("Tavlama (°C)", 20.0, 500.0, 100.0, 5.0, disabled=at_unk)
    with e[2]:
        ph = st.empty()
        ati_unk = st.checkbox("bilinmiyor", key="p4_ati_unk")
        ati = ph.number_input("Tavlama (dk)", 0.0, 600.0, 20.0, 5.0, disabled=ati_unk)

    if st.button("PCE tahmini al  →", type="primary", width="stretch"):
        st.session_state["p4_submitted"] = True
    submitted = st.session_state.get("p4_submitted", False)
    if submitted and not all(oks.values()):
        hatalar = [s for s, ok in oks.items() if not ok]
        ui.box(f"<strong>Katsayı toplamı hatası:</strong> {', '.join(hatalar)}-site katsayı toplamı 1,00 olmalı "
               f"(şu an: {', '.join(tr(sums[h], 2) for h in hatalar)}).", accent=True)

# ---------------------------------------------------------------- sonuç
with right:
    if not submitted:
        st.html('<div style="padding:26px 0 0"></div>')
        ui.box("<p>Sol taraftaki tarifi kurun ve <strong>PCE tahmini al</strong> düğmesine basın. Sonuç, tahmini "
               "PCE ile birlikte %90 belirsizlik aralığını, tarifin eğitim verisine yakınlığını ve tahmini "
               "belirleyen özellik katkılarını (yerel SHAP) gösterir.</p>"
               "<p>Tahmin değerleri canlı CatBoost modelinden (v0.4.0 eğitim bölmesi) üretilir; aralık matematiği "
               f"tezin gerçek kalibrasyonudur (±{tr(HW, 2)} marjinal / Mondrian çeyrekleri).</p>",
               k="Nasıl çalışır")
    elif all(oks.values()):
        enc = encode.encode(a, b, x, arch[0], etl[0], htl[0], solv[0], bg, at, ati, bg_unk, at_unk, ati_unk)
        pred = float(data.model().predict(enc)[0])
        m_lo, m_hi, q_lo, q_hi, quart = encode.conformal_interval(pred)
        dist, thr, inside, komsular = encode.ad_distance(enc)
        fg = "var(--ink)" if inside else "var(--acc)"

        ui.stats([
            ("Tahmini PCE", f"{tr(pred, 2)}<small>%</small>", "", "acc"),
            ("%90 aralık — genel", f"{tr(m_lo, 1)} – {tr(m_hi, 1)}", f"marjinal conformal · ±{tr(HW, 2)}"),
            (f"%90 aralık — bölgesel {quart}", f"{tr(q_lo, 1)} – {tr(q_hi, 1)}", "Mondrian conformal · çeyreğe duyarlı"),
            ("Eğitim-uzayına uzaklık", f'<span style="color:{fg}">{tr(dist, 2)}</span>',
             f'eşik {tr(thr, 2)} — <strong style="color:{fg}">{"alan içi" if inside else "alan DIŞI"}</strong>'),
        ], border=False, small=True)

        st.html(
            '<div class="m-band">'
            f'<div class="mb" style="left:{pct(m_lo):.2f}%; width:{pct(m_hi) - pct(m_lo):.2f}%"></div>'
            f'<div class="qb" style="left:{pct(q_lo):.2f}%; width:{pct(q_hi) - pct(q_lo):.2f}%"></div>'
            f'<div class="pt" style="left:{pct(pred):.2f}%"></div>'
            f'<div class="pl" style="left:{pct(pred):.2f}%">{tr(pred, 2)}</div></div>'
            '<div class="m-axis"><span>0</span><span>PCE (%) — açık bant: marjinal %90 · koyu bant: Mondrian %90</span>'
            '<span>30</span></div>'
        )

        if not inside:
            ui.box(f"Bu tarif, eğitim verisinin yoğun bölgesinin <strong>dışında</strong> (kNN uzaklığı "
                   f"{tr(dist, 2)} &gt; eşik {tr(thr, 2)}). Model bu bölgeyi çok az örnekten öğrenmiştir; tahmini "
                   "yalnızca kaba bir yönlendirme olarak okuyun.", chip="Alan dışı", accent=True)
        if pred > fmeta["train_pce_max"] * 0.6:
            ui.text(f"Not: eğitimdeki en yüksek PCE {tr(fmeta['train_pce_max'], 1)}. Ağaç modeller gözlenmemiş "
                    "bölgede güvenilir ekstrapolasyon yapamaz; tahminler pratikte bu tavanın belirgin altında kalır "
                    "(tez Bölüm 5.4).", mute=True)

        # --- veri desteği
        rec = data.records()
        egitim = rec[rec["bolme"] == "eğitim"]
        uclu_n = int(((egitim["kova_arch"] == arch[1]) & (egitim["kova_ETL"] == etl[1]) &
                      (egitim["kova_HTL"] == htl[1])).sum())
        solv_n = int((egitim["kova_solv"] == solv[1]).sum())
        st.html('<div style="border-top:1px solid var(--div); margin-top:8px"></div>')
        ui.kicker("Veri desteği", tone="ink")
        u_fg = "var(--acc)" if uclu_n == 0 else ("var(--acc700)" if uclu_n < 5 else "var(--ink)")
        ui.stats([
            ("Mimari–ETL–HTL üçlüsü eğitimde", f'<span style="color:{u_fg}">{tr(uclu_n, 0)}<small> kayıt</small></span>',
             "hiç gözlenmedi" if uclu_n == 0 else ("seyrek (&lt;5)" if uclu_n < 5 else "≥ 5 · destekli (Bölüm 4.5)")),
            ("Çözücü sistemi eğitimde", f"{tr(solv_n, 0)}<small> kayıt</small>", "çözücü sisteminin eğitimdeki sıklığı"),
            ("En yakın 5 komşuya uzaklık", tr(dist, 2), "ölçekli özellik uzayında"),
        ], border=False, small=True)
        if any(s.startswith("Diğer (") or s in ("unknown", "Unknown") for s in (arch[1], etl[1], htl[1], solv[1])):
            ui.text("Not: \"Diğer (…)\" ve \"unknown\" seçenekleri tek bir malzemeyi değil, modelin aynı kovada "
                    "topladığı tüm seyrek/bilinmeyen etiketleri temsil eder; yukarıdaki sayımlar bu kovanın "
                    "toplamıdır.", mute=True)
        if uclu_n == 0:
            ui.box("<strong>Bu üçlü eğitimde hiç gözlenmemiş.</strong> Model bu birleşimin etkileşimini öğrenmiş "
                   "olamaz; tahmin, bileşenlerin tekil örüntülerinin toplamıdır (tez Bölüm 4.5'teki birlikte-görülme "
                   "denetiminin birebir karşılığı).", accent=True)
        elif uclu_n < 5:
            ui.box(f"Bu üçlü eğitimde yalnızca {uclu_n} kez görüldü; tezin eğitim-desteği eşiğinin (≥5) altında "
                   "(Bölüm 4.5).", accent=True)

        # --- yerel SHAP
        st.html('<div style="border-top:1px solid var(--div); margin-top:8px"></div>')
        ui.kicker("Bu tahmini ne belirledi? — yerel katkılar", "(SHAP, PCE puanı)", tone="ink")
        sv = data.explainer().shap_values(enc)[0]
        imp = pd.DataFrame({"özellik": enc.columns, "katkı": sv})
        imp = imp[imp["katkı"].abs() > 1e-4].sort_values("katkı")
        top = pd.concat([imp.head(8), imp.tail(8)]).drop_duplicates().sort_values("katkı")
        mx = max(0.01, float(top["katkı"].abs().max()))
        rows = []
        for r in top.itertuples():
            w = abs(r.katkı) / mx * 50
            left_ = f"{50 - w:.2f}%" if r.katkı < 0 else "50%"
            col = "var(--acc)" if r.katkı < 0 else "var(--ink)"
            fgc = "var(--acc700)" if r.katkı < 0 else "var(--ink)"
            sign = "−" if r.katkı < 0 else "+"
            rows.append(f'<div><div class="nm" title="{ui.esc(r.özellik)}">{ui.esc(r.özellik)}</div>'
                        f'<div class="tr"><div class="z"></div><div class="b" style="left:{left_}; width:{w:.2f}%; '
                        f'background:{col}"></div></div><div class="vl" style="color:{fgc}">{sign}{tr(abs(r.katkı), 2)}</div></div>')
        st.html(f'<div class="m-shap">{"".join(rows)}</div>')
        g = data.csv("shap_top_features.csv")
        ui.text("Sola uzanan (kırmızı) katkılar tahmini düşürür, sağa uzananlar (mürekkep) yükseltir. Küresel "
                f"önem sıralaması (model geneli): {' · '.join(ui.esc(f) for f in g['feature'].head(5))} "
                "(tez Tablo 4.6).", mute=True)
        with st.expander("Küresel önem sıralaması (model geneli, tez Tablo 4.6)"):
            st.dataframe(g.head(15), hide_index=True, width="stretch",
                         column_config={"feature": "Özellik", "mean_abs_shap": st.column_config.NumberColumn(
                             "ort |SHAP|", format="%.4f")})

        if komsular:
            with st.expander("Eğitimdeki en yakın 5 örnek (ölçekli özellik uzayında)"):
                kdf = rec.set_index("row_id").loc[[k for k in komsular if k in rec["row_id"].values]]
                st.dataframe(
                    kdf[["kompozisyon", "mimari", "ETL", "HTL", "cozucu", "band_gap", "PCE", "DOI"]].rename(
                        columns={"kompozisyon": "Kompozisyon", "cozucu": "Çözücü", "PCE": "Gerçek PCE"}),
                    hide_index=True, width="stretch",
                    column_config={"Gerçek PCE": st.column_config.NumberColumn(format="%.2f"),
                                   "band_gap": st.column_config.NumberColumn(format="%.2f")})
                ui.text("Bu komşular tahminin kaynağı değildir: CatBoost tahmini doğrudan 77-özellik vektöründen "
                        "üretir; komşular yalnızca tarifin eğitim verisindeki bağlamını gösterir "
                        "(uygulanabilirlik-alanı teşhisi). Komşuların gerçek PCE aralığı, tahmini tartmak için makul "
                        "bir bağlamdır.", mute=True)

        with st.expander("Bu tahminde kullanılan varsayımların tam dökümü"):
            med = fmeta["medians"]
            satirlar = [
                "A/B/X oranları: girdiğiniz değerler (toplamlar doğrulandı)",
                f"Mimari / ETL / HTL / çözücü: <span class='m-mono'>{ui.esc(arch[1])}</span> / "
                f"<span class='m-mono'>{ui.esc(etl[1])}</span> / <span class='m-mono'>{ui.esc(htl[1])}</span> / "
                f"<span class='m-mono'>{ui.esc(solv[1])}</span>",
                (f"Band gap: <strong>bilinmiyor işaretlendi → eğitim medyanı {tr(med['band_gap'], 2)} eV kullanıldı "
                 f"+ eksiklik bayrağı = 1</strong>" if bg_unk else f"Band gap: {tr(bg, 2)} eV (girdiğiniz değer)"),
                (f"Tavlama sıcaklığı: <strong>bilinmiyor → medyan {tr(med['anneal_temp'], 0)} °C + bayrak</strong>"
                 if at_unk else f"Tavlama sıcaklığı: {tr(at, 0)} °C"),
                (f"Tavlama süresi: <strong>bilinmiyor → medyan {tr(med['anneal_time'], 0)} dk + bayrak</strong>"
                 if ati_unk else f"Tavlama süresi: {tr(ati, 0)} dk"),
                "Esnek / yarı saydam: hayır (0) — tarif formunda sorulmaz, aday uzayıyla aynı varsayım",
                "Ölçüm-sonrası hiçbir değişken (Voc, Jsc, FF…) modele girmez (hedef sızıntısı denetimli sözleşme)",
            ]
            ui.steps([(str(i + 1), s) for i, s in enumerate(satirlar)])

        ui.sci_limit_box()

ui.footer()
