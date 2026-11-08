# -*- coding: utf-8 -*-
"""Hata takibi: GlitchTip (Sentry uyumlu, kendi sunucumuzda).

DSN ``SENTRY_DSN`` ortam değişkeninden okunur; tanımlı değilse (yerelde) hiçbir şey
gönderilmez. Streamlit sayfadaki hataları kendisi yakalayıp ekrana bastığı için SDK
onları görmez: ``streamlit_app.py`` sayfayı ``yakala()`` içinde çalıştırır.

Kişisel veri gönderilmez: IP, çerez ve istek başlıkları SDK'ya hiç verilmez
(``send_default_pii=False``), performans izleme kapalıdır.
"""
import contextlib
import os

import sentry_sdk


def baslat() -> None:
    """SDK'yı bir kez başlatır. Streamlit betiği her etkileşimde yeniden çalıştırdığı için
    çağrı tekrarlanır; ikinci ve sonraki çağrılar bir şey yapmaz."""
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn or sentry_sdk.is_initialized():
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        send_default_pii=False,
        traces_sample_rate=0,
        max_breadcrumbs=30,
    )


@contextlib.contextmanager
def yakala():
    """İçerideki hatayı GlitchTip'e gönderir ve Streamlit göstersin diye yeniden fırlatır.

    Streamlit'in akış denetimi (st.stop, st.rerun, sayfa geçişi) ``BaseException``
    türündendir; ``Exception`` yakalandığı için onlar araya girmeden geçer.
    """
    try:
        yield
    except Exception as hata:
        sentry_sdk.capture_exception(hata)
        raise
