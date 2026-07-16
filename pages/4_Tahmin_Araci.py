# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lib import data, encode
from lib.ui import page, tr, tez_notu, bilim_uyarisi, conformal_uyarisi, MAVI, KIRMIZI

page("Tahmin Aracı — Sanal Cihaz Tarifi", "4️⃣")
tez_notu("Bölüm 3.12 ve 4.10",
         "Tarif, modelin eğitimde gördüğü 77-özellik sözleşmesine kodlanır. Belirsizlik "
         "aralığı, eğitimden ham DOI anahtarı düzeyinde ayrık tutulan yayınlardaki gerçek "
         "hataların dağılımından türetilir (conformal kestirim). Aralıklar nominal %90 "
         "düzeyindedir; holdout'ta gözlenen kapsama %88,2'dir (tez Bölüm 4.10).")

maps = encode.categorical_options()
meta = data.js("features.json")

with st.form("tarif"):
    st.subheader("🧪 Kompozisyon (her site toplamı 1,00 olmalı)")
    c = st.columns(3)
    with c[0]:
        st.markdown("**A-site**")
        a = {i: st.number_input(f"A: {i}", 0.0, 1.0,
                                {"FA": 0.80, "MA": 0.10, "Cs": 0.10}.get(i, 0.0), 0.01)
             for i in ["FA", "MA", "Cs", "Rb", "K"]}
    with c[1]:
        st.markdown("**B-site**")
        b = {i: st.number_input(f"B: {i}", 0.0, 1.0, 1.0 if i == "Pb" else 0.0, 0.01)
             for i in ["Pb", "Sn", "Ge"]}
    with c[2]:
        st.markdown("**X-site**")
        x = {i: st.number_input(f"X: {i}", 0.0, 1.0,
                                {"I": 0.83, "Br": 0.17}.get(i, 0.0), 0.01)
             for i in ["I", "Br", "Cl"]}

    st.subheader("🏗️ Cihaz yığını ve süreç")
    d = st.columns(4)
    arch = d[0].selectbox("Mimari", list(maps["arch"].items()),
                          format_func=lambda kv: kv[1],
                          index=list(maps["arch"].values()).index("nip")
                          if "nip" in maps["arch"].values() else 0)
    etl = d[1].selectbox("ETL", list(maps["ETL"].items()), format_func=lambda kv: kv[1])
    htl = d[2].selectbox("HTL", list(maps["HTL"].items()), format_func=lambda kv: kv[1])
    solv = d[3].selectbox("Çözücü sistemi", list(maps["solv"].items()),
                          format_func=lambda kv: kv[1])
    e = st.columns(3)
    with e[0]:
        bg_unk = st.checkbox("Band gap bilinmiyor")
        bg = st.number_input("Band gap (eV)", 1.0, 3.6, 1.60, 0.01, disabled=bg_unk)
    with e[1]:
        at_unk = st.checkbox("Tavlama sıcaklığı bilinmiyor")
        at = st.number_input("Tavlama sıcaklığı (°C)", 20.0, 500.0, 100.0, 5.0,
                             disabled=at_unk)
    with e[2]:
        ati_unk = st.checkbox("Tavlama süresi bilinmiyor")
        ati = st.number_input("Tavlama süresi (dk)", 0.0, 600.0, 20.0, 5.0,
                              disabled=ati_unk)
    gonder = st.form_submit_button("🔮 PCE tahmini al", use_container_width=True)

if gonder:
    hatalar = [s for s, v in (("A", a), ("B", b), ("X", x))
               if abs(sum(v.values()) - 1.0) > 0.011]
    if hatalar:
        st.error(f"{', '.join(hatalar)}-site katsayı toplamı 1,00 olmalı "
                 f"(şu an: {', '.join(tr(sum(dict(zip(['A','B','X'],[a,b,x]))[h].values()), 2) for h in hatalar)}).")
        st.stop()

    enc = encode.encode(a, b, x, arch[0], etl[0], htl[0], solv[0],
                        bg, at, ati, bg_unk, at_unk, ati_unk)
    pred = float(data.model().predict(enc)[0])
    m_lo, m_hi, q_lo, q_hi, quart = encode.conformal_interval(pred)
    dist, thr, inside, komsular = encode.ad_distance(enc)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Tahmini PCE", tr(pred, 2) + " %")
    r2.metric("Nominal %90 aralık (genel)", f"{tr(m_lo, 1)} – {tr(m_hi, 1)}",
              help="Eğitim dışı (DOI düzeyinde ayrık) yayınlardaki gerçek hataların %90'ını "
                   "kapsayan genişlik (marginal conformal): tüm kalibrasyon kayıtları birlikte. "
              "Holdout'ta gözlenen kapsama: %88,2 (tez Bölüm 4.10).")
    r3.metric(f"Nominal %90 aralık (bölgesel, {quart})", f"{tr(q_lo, 1)} – {tr(q_hi, 1)}",
              help="Aynı hesap, yalnızca bu tahmin düzeyindeki (çeyrekteki) kayıtların "
                   "hatalarıyla yapılır (Mondrian conformal) — aralık bölgeye duyarlı hâle gelir.")
    r4.metric("Eğitim-uzayına uzaklık", tr(dist, 2),
              f"eşik {tr(thr, 2)} — {'alan içi' if inside else 'alan DIŞI'}",
              delta_color="normal" if inside else "inverse")

    if not inside:
        st.error("🚧 Bu tarif, eğitim verisinin yoğun bölgesinin **dışında** "
                 f"(kNN uzaklığı {tr(dist, 2)} > eşik {tr(thr, 2)}). Model bu bölgeyi "
                 "çok az örnekten öğrenmiştir; tahmini "
                 "yalnızca kaba bir yönlendirme olarak okuyun.")
    if pred > meta["train_pce_max"] * 0.6:
        st.caption(f"Not: eğitimdeki en yüksek PCE {tr(meta['train_pce_max'], 1)} — ağaç "
                   "modeller gözlenmemiş bölgede güvenilir ekstrapolasyon yapamaz; "
                   "tahminler pratikte bu tavanın belirgin altında kalır (tez Bölüm 5.4).")

    # ---- Veri desteği: bu tarif eğitim verisinde ne kadar karşılık buluyor? ----
    st.subheader("📚 Veri desteği")
    rec = data.records()
    egitim = rec[rec["bolme"] == "eğitim"]
    uclu_n = int(((egitim["mimari"] == arch[1]) & (egitim["ETL"] == etl[1]) &
                  (egitim["HTL"] == htl[1])).sum())
    solv_n = int((egitim["cozucu"] == solv[1]).sum())
    d1, d2, d3 = st.columns(3)
    d1.metric("Mimari–ETL–HTL üçlüsü eğitimde", f"{tr(uclu_n, 0)} kayıt",
              "hiç görülmedi!" if uclu_n == 0 else
              ("seyrek (<5)" if uclu_n < 5 else "destekli"),
              delta_color="inverse" if uclu_n < 5 else "normal")
    d2.metric("Çözücü sistemi eğitimde", f"{tr(solv_n, 0)} kayıt")
    d3.metric("En yakın 5 komşuya uzaklık", tr(dist, 2))
    if uclu_n == 0:
        st.error("🚧 Seçtiğiniz mimari–ETL–HTL kombinasyonu eğitim verisinde **hiç "
                 "gözlenmemiş**. Model bu birleşimin etkileşimini öğrenmiş olamaz; "
                 "tahmin, bileşenlerin tekil örüntülerinin toplamıdır (tez Bölüm 4.5'teki "
                 "birlikte-görülme denetiminin birebir karşılığı).")
    elif uclu_n < 5:
        st.warning(f"⚠️ Bu üçlü eğitimde yalnızca {uclu_n} kez görüldü — tezin "
                   "eğitim-desteği eşiğinin (≥5) altında (Bölüm 4.5).")

    if komsular:
        with st.expander("🔍 Eğitimdeki en yakın 5 örnek (ölçekli özellik uzayında)"):
            kdf = rec.set_index("row_id").loc[[k for k in komsular if k in
                                               rec["row_id"].values]]
            st.dataframe(
                kdf[["kompozisyon", "mimari", "ETL", "HTL", "cozucu", "band_gap",
                     "PCE", "DOI"]].rename(columns={
                    "kompozisyon": "Kompozisyon", "cozucu": "Çözücü",
                    "PCE": "Gerçek PCE"}),
                hide_index=True, use_container_width=True,
                column_config={"Gerçek PCE": st.column_config.NumberColumn(format="%.2f"),
                               "band_gap": st.column_config.NumberColumn(format="%.2f")})
            st.caption("Bu komşular tahminin kaynağı değildir: CatBoost tahmini doğrudan "
                       "77-özellik vektöründen üretir; komşular yalnızca tarifin eğitim "
                       "verisindeki bağlamını gösterir (uygulanabilirlik-alanı teşhisi). "
                       "Komşuların gerçek PCE aralığı, tahmini tartmak için makul bir bağlamdır.")

    with st.expander("⚙️ Bu tahminde kullanılan varsayımların tam dökümü"):
        med = meta["medians"]
        satirlar = [
            f"- A/B/X oranları: girdiğiniz değerler (toplamlar doğrulandı)",
            f"- Mimari / ETL / HTL / çözücü: `{arch[1]}` / `{etl[1]}` / `{htl[1]}` / `{solv[1]}`",
            (f"- Band gap: **bilinmiyor işaretlendi → eğitim medyanı {tr(med['band_gap'], 2)} eV "
             f"kullanıldı + eksiklik bayrağı = 1**" if bg_unk
             else f"- Band gap: {tr(bg, 2)} eV (girdiğiniz değer)"),
            (f"- Tavlama sıcaklığı: **bilinmiyor → medyan {tr(med['anneal_temp'], 0)} °C + bayrak**"
             if at_unk else f"- Tavlama sıcaklığı: {tr(at, 0)} °C"),
            (f"- Tavlama süresi: **bilinmiyor → medyan {tr(med['anneal_time'], 0)} dk + bayrak**"
             if ati_unk else f"- Tavlama süresi: {tr(ati, 0)} dk"),
            "- Esnek/yarı-saydam: hayır (0) — tarif formunda sorulmaz, aday uzayıyla aynı varsayım",
            "- Ölçüm-sonrası hiçbir değişken (Voc, Jsc, FF...) modele girmez (sızıntı-güvenli sözleşme)",
        ]
        st.markdown("\n".join(satirlar))

    fig = go.Figure()
    fig.add_shape(type="rect", x0=m_lo, x1=m_hi, y0=-0.3, y1=0.3,
                  fillcolor=MAVI, opacity=0.25, line_width=0)
    fig.add_shape(type="rect", x0=q_lo, x1=q_hi, y0=-0.15, y1=0.15,
                  fillcolor=MAVI, opacity=0.45, line_width=0)
    fig.add_trace(go.Scatter(x=[pred], y=[0], mode="markers+text",
                             marker=dict(color=KIRMIZI, size=14, symbol="diamond"),
                             text=[tr(pred, 2)], textposition="top center",
                             showlegend=False))
    fig.update_layout(height=140, xaxis_title="PCE (%)", yaxis_visible=False,
                      xaxis_range=[max(0, m_lo - 2), m_hi + 2],
                      margin=dict(t=10, b=10),
                      title="Açık bant: marginal %90 · koyu bant: Mondrian %90")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧠 Bu tahmini ne belirledi? (yerel SHAP)")
    sv = data.explainer().shap_values(enc)[0]
    imp = pd.DataFrame({"özellik": enc.columns, "katkı": sv})
    imp = imp[imp["katkı"].abs() > 1e-4].sort_values("katkı")
    top = pd.concat([imp.head(8), imp.tail(8)]).drop_duplicates()
    fig = go.Figure(go.Bar(
        x=top["katkı"], y=top["özellik"], orientation="h",
        marker_color=[KIRMIZI if v < 0 else MAVI for v in top["katkı"]],
        text=[f"{v:+.2f}" for v in top["katkı"]], textposition="outside"))
    fig.update_layout(height=420, xaxis_title="PCE katkısı (puan)",
                      title="Yükselten (mavi) / düşüren (kırmızı) özellikler",
                      margin=dict(t=40))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🌍 Küresel önem sıralaması (model geneli, tez Tablo 4.6)"):
        g = data.csv("shap_top_features.csv").head(15)
        st.dataframe(g, hide_index=True, use_container_width=True,
                     column_config={"mean_abs_shap": st.column_config.NumberColumn(
                         "ort |SHAP|", format="%.4f")})

    bilim_uyarisi()
    conformal_uyarisi()
