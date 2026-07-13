# -*- coding: utf-8 -*-
"""Ortak arayuz yardimcilari: sayfa kurulumu, Turkce sayi bicimi, standart uyarilar."""
import streamlit as st

MAVI = "#4878a8"
KIRMIZI = "#a85248"
GRI = "#b0b8c0"
BORDO = "#ab162c"   # IKCU kurumsal rengi (tez kapagi logosundan orneklendi)


def page(title: str, icon: str, wide: bool = True):
    # set_page_config girdi noktasinda (streamlit_app.py) bir kez cagrilir.
    st.title(f"{icon} {title}")


def tr(x, nd: int = 3) -> str:
    """Turkce sayi bicimi: ondalik virgul, binlik nokta."""
    if x is None:
        return "—"
    if isinstance(x, int) or (float(x).is_integer() and nd == 0):
        return f"{int(x):,}".replace(",", ".")
    s = f"{float(x):,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def tez_notu(bolum: str, metin: str):
    st.caption(f"📖 **Tez {bolum}** — {metin}")


def bilim_uyarisi():
    st.warning(
        "**Bu çıktı deneysel doğrulama yerine geçmez.** Model, geçmiş literatür "
        "kayıtlarından öğrenilen istatistiksel örüntülere dayalı bir **önceliklendirme** "
        "aracıdır; ağaç tabanlı modeller eğitim dağılımının dışına ekstrapolasyon yapamaz "
        "(tez Bölüm 5.4). Tahminler faz kararlılığı, film morfolojisi ve uzun dönem "
        "stabilite gibi ölçütlerle birlikte, uzman değerlendirmesiyle yorumlanmalıdır."
    )


def conformal_uyarisi():
    st.caption(
        "ℹ️ %90 aralıklar DOI-grup-güvenli kalibrasyonla (tez Bölüm 4.10) hesaplanmıştır. "
        "Elle girilen tarifler holdout dağılımından gelmediği için (değişebilirlik varsayımı "
        "sağlanmaz) bu aralıklar kesin bir %90 garantisi değil, **veriye dayalı belirsizlik "
        "göstergesi** olarak okunmalıdır."
    )
