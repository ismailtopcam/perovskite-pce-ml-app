# -*- coding: utf-8 -*-
"""Ortak arayüz katmanı — "Kafes" tasarım dili.

Kaynak tasarım: Claude Design kanvası "Tez Uygulaması Yeniden Tasarım" (2026-11, 11 ekran).
Lacivert ray, serin kâğıt zemin, beyaz kartlar; mavi = dürüst ölçüm / eğitimde destekli,
turuncu = sızıntı / iyimser skor / uyarı. Başlıklar Space Grotesk, metin Inter, sayılar
JetBrains Mono. Etkileşimli parçalar Streamlit bileşenleriyle kurulur ve aşağıdaki CSS ile
aynı dile çekilir.

Kullanım: her sayfa `ui.page_header(...)` ile başlar, `ui.footer()` ile biter. Kart içine
alınacak bölümler `with ui.card():` ile sarılır.
"""
from __future__ import annotations

import html as _html

import streamlit as st

# ---------------------------------------------------------------- jetonlar
INK = "#0E1A2B"          # lacivert mürekkep (metin, ray, ana işaretler)
BG = "#F4F5F7"           # zemin
SURFACE = "#FFFFFF"      # kart
BLUE = "#1F4FD1"         # dürüst ölçüm / destekli / seçili
BLUE700 = "#163BA0"
BLUE400 = "#7FA0F0"
BLUE200 = "#C4D2F7"
BLUE100 = "#E6ECFB"
BLUE50 = "#F5F7FD"
ACC = "#D9530F"          # turuncu: sızıntı / iyimserlik / uyarı (dolgu)
ACC600 = "#C2470B"
ACC700 = "#B84308"       # turuncu metin (4,5:1 üzeri)
ACC800 = "#8F3406"
ACC100 = "#FCEBDF"
ACC200 = "#F8D3BC"
ACC400 = "#F4A26B"
N100 = "#F7F8FA"
N200 = "#EEF1F5"
N300 = "#DCE0E6"
N400 = "#A3ACB9"
N500 = "#9AA5B4"
N600 = "#8C97A6"
N700 = "#5B6878"         # ikincil metin
N800 = "#33435A"
N900 = "#1E3150"
DIV = N300               # çizgiler
KURUM = "#9AA7B8"        # raydaki kurum satırı

# Eski adlar (sayfalar ve grafikler bunları kullanır)
MAVI = BLUE
KIRMIZI = ACC
GRI = N400
BORDO = ACC800

FONT = "Inter, system-ui, sans-serif"
HFONT = "'Space Grotesk', Inter, system-ui, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, Consolas, monospace"

# Raydaki sayfa numaraları (URL yolunun sonu → etiket); sıra streamlit_app.py ile aynıdır.
_NAV_NUM = [("Rehber", "R"), ("Veri_Hatti", "01"), ("Dogrulama_Deneyleri", "02"),
            ("Model_Karsilastirma", "03"), ("Tahmin_Araci", "04"), ("Gercek_vs_Tahmin", "05"),
            ("Aday_Tarayici", "06"), ("DOI_Gezgini", "07"), ("Pipeline_Provenance", "08"),
            ("Sayilarin_Evrimi", "09")]
_NAV_CSS = "\n".join(
    f'a[data-testid="stSidebarNavLink"][href$="/{p}"]::before {{ content: "{n}"; }}' for p, n in _NAV_NUM)

# ---------------------------------------------------------------- CSS
_CSS = f"""
<style>
:root {{
  --ink:{INK}; --bg:{BG}; --surface:{SURFACE};
  --blue:{BLUE}; --blue700:{BLUE700}; --blue400:{BLUE400}; --blue200:{BLUE200}; --blue100:{BLUE100}; --blue50:{BLUE50};
  --acc:{ACC}; --acc600:{ACC600}; --acc700:{ACC700}; --acc800:{ACC800}; --acc100:{ACC100}; --acc200:{ACC200}; --acc400:{ACC400};
  --n100:{N100}; --n200:{N200}; --n300:{N300}; --n400:{N400}; --n500:{N500}; --n600:{N600}; --n700:{N700}; --n800:{N800}; --n900:{N900};
  --div:{DIV}; --kurum:{KURUM}; --font:{FONT}; --hfont:{HFONT}; --mono:{MONO};
  --shadow: 0 1px 2px rgba(14,26,43,.05), 0 10px 30px rgba(14,26,43,.06);
}}
html, body, [data-testid="stAppViewContainer"] {{ font-family: var(--font); }}
[data-testid="stAppViewContainer"] {{ background: var(--bg); }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMainBlockContainer"] {{ padding: 1.6rem clamp(1rem, 4vw, 3.5rem) 2.5rem; max-width: 1280px; }}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {{ gap: 1rem; }}
/* stil-yalnız html blokları yer kaplamasın */
[data-testid="stElementContainer"]:has(> [data-testid="stHtml"] > style:only-child) {{ display: none; }}
[data-testid="stHtml"] {{ font-family: var(--font); color: var(--ink); }}
.num, .m-mono {{ font-family: var(--mono); font-variant-numeric: tabular-nums; }}

/* ---------- sol ray (lacivert) ---------- */
[data-testid="stSidebar"] {{ background: var(--ink); border-right: 0; }}
[data-testid="stSidebar"] > div:first-child {{ height: 100%; }}
[data-testid="stSidebarContent"] {{ display: flex; flex-direction: column; min-height: 100%; padding-bottom: 0; }}
[data-testid="stSidebarHeader"] {{ order: -3; padding: 0.4rem 0.6rem 0 0; height: auto; min-height: 0; }}
[data-testid="stSidebarHeader"] [data-testid="stLogoSpacer"] {{ display: none; }}
[data-testid="stSidebarUserContent"], [data-testid="stSidebarUserContent"] > div,
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] {{ display: contents; }}
[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.rail-brand) {{ order: -2; }}
[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.rail-foot) {{ order: 10; margin-top: auto; }}
[data-testid="stSidebarNav"] {{ order: 0; padding: 10px 12px 6px; margin: 0; }}
[data-testid="stSidebarNavSeparator"] {{ display: none; }}
[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarHeader"] button {{ color: #C9D2DE; }}
.rail-brand {{ padding: 6px 22px 20px; border-bottom: 1px solid #22324A; display: flex; flex-direction: column; gap: 16px; }}
.rail-brand .logo {{ display: flex; align-items: center; gap: 12px; color: #FFFFFF; text-decoration: none; }}
.rail-brand .marka {{ font-family: var(--hfont); font-weight: 700; font-size: 20px; line-height: 1.05; letter-spacing: -0.01em; color: #FFFFFF; }}
.rail-brand .alt {{ font-size: 11.5px; color: #9AA7B8; margin-top: 3px; }}
.rail-brand .kurum {{ font-size: 11.5px; line-height: 1.55; color: var(--kurum); }}
.rail-foot {{ border-top: 1px solid #22324A; padding: 16px 22px 22px; }}
.rail-foot .k {{ font-size: 10.5px; font-weight: 600; letter-spacing: 0.09em; text-transform: uppercase; color: #7D8A9C; }}
.rail-foot .ad {{ font-size: 14px; font-weight: 600; margin-top: 4px; color: #FFFFFF; }}
.rail-foot .m {{ font-family: var(--mono); font-size: 11px; color: #9AA7B8; margin-top: 8px; line-height: 1.75; }}
ul[data-testid="stSidebarNavItems"] {{ padding: 0; margin: 0; max-height: none; }}
ul[data-testid="stSidebarNavItems"] li {{ margin: 0; }}
[data-testid="stNavSectionHeader"] {{ padding: 12px 10px 6px; margin: 0; font-size: 10.5px; font-weight: 600; letter-spacing: 0.09em;
  text-transform: uppercase; color: #7D8A9C; }}
[data-testid="stNavSectionHeader"] * {{ font-size: inherit; font-weight: inherit; letter-spacing: inherit; color: inherit; }}
[data-testid="stSidebarNavLinkContainer"] {{ padding: 0; margin: 0; }}
a[data-testid="stSidebarNavLink"] {{
  border-radius: 8px; margin: 1px 0; padding: 9px 10px; min-height: 40px; height: auto; box-sizing: border-box;
  display: grid; grid-template-columns: 28px minmax(0,1fr); gap: 8px; align-items: center;
  background: transparent; color: #C9D2DE;
}}
a[data-testid="stSidebarNavLink"] [data-testid="stIconEmoji"], a[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] {{ display: none; }}
a[data-testid="stSidebarNavLink"]::before {{
  content: "—"; font-family: var(--mono); font-weight: 600; font-size: 11.5px; color: #7D8A9C;
}}
{_NAV_CSS}
a[data-testid="stSidebarNavLink"] p, a[data-testid="stSidebarNavLink"] span {{ font-size: 13.5px; font-weight: 500; margin: 0; line-height: 1.3; color: inherit; }}
a[data-testid="stSidebarNavLink"]:hover {{ background: rgba(255,255,255,0.06); color: #FFFFFF; }}
a[data-testid="stSidebarNavLink"][aria-current="page"] {{ background: #1E3150; color: #FFFFFF; }}
a[data-testid="stSidebarNavLink"][aria-current="page"]::before {{ color: #FF9A5C; }}
a[data-testid="stSidebarNavLink"]:focus-visible {{ outline: 2px solid #7FA0F0; outline-offset: 1px; }}

/* ---------- sayfa başlığı ---------- */
.m-head {{ display: flex; flex-direction: column; gap: 12px; padding: 4px 0 10px; }}
.m-head .top {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; }}
.m-chip {{ font-size: 12px; padding: 5px 10px; border: 1px solid var(--div); border-radius: 999px; background: #FFFFFF; color: var(--n800); white-space: nowrap; }}
.m-kicker {{ font-size: 12px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--blue); }}
.m-kicker.ink {{ font-family: var(--hfont); color: var(--ink); text-transform: none; letter-spacing: -0.01em; font-size: 17.5px; }}
.m-kicker.ink .sub {{ font-family: var(--font); font-size: 12.5px; margin-left: 4px; }}
.m-kicker.mute {{ color: var(--n700); letter-spacing: 0.07em; font-size: 11.5px; }}
.m-kicker .sub {{ color: var(--n700); text-transform: none; letter-spacing: 0; font-weight: 400; }}
.m-h1 {{ font-family: var(--hfont); font-weight: 600; font-size: clamp(32px, 3.8vw, 50px); line-height: 1.04; letter-spacing: -0.02em; color: var(--ink); text-wrap: pretty; max-width: 22ch; }}
.m-h1 .acc {{ color: var(--blue); }}
.m-hero {{ font-family: var(--hfont); font-weight: 600; font-size: clamp(32px, 3.8vw, 52px); line-height: 1.04; letter-spacing: -0.02em; color: var(--ink); text-wrap: pretty; }}
.m-hero .acc {{ color: var(--blue); }}
.m-lede {{ margin: 0; font-size: 16px; color: var(--n800); max-width: 72ch; line-height: 1.6; }}
.m-lede strong {{ color: var(--ink); }}
.m-rule {{ border-top: 1px solid var(--div); margin: 6px 0 0; }}
.m-rule.thin {{ border-top-width: 1px; }}
.m-text {{ font-size: 14px; color: var(--n800); line-height: 1.6; }}
.m-text p {{ margin: 0 0 10px; }}
.m-text p:last-child {{ margin-bottom: 0; }}
.m-text strong {{ color: var(--ink); }}
.m-mute {{ font-size: 13px; color: var(--n700); line-height: 1.55; }}
.m-mute strong {{ color: var(--n800); }}
.m-text a, .m-mute a, .m-box a, .m-foot a, .m-steps a, .m-list a {{ color: var(--blue); text-decoration: none; }}
.m-text a:hover, .m-mute a:hover, .m-box a:hover, .m-steps a:hover {{ color: var(--blue700); text-decoration: underline; }}
.m-h2 {{ font-family: var(--hfont); font-weight: 600; font-size: 19px; letter-spacing: -0.01em; color: var(--ink); margin: 0; }}

/* ---------- sayı kartları ---------- */
.m-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }}
.m-stats > div {{ background: #FFFFFF; border: 1px solid var(--div); border-radius: 14px; padding: 18px 20px; min-width: 0;
  display: flex; flex-direction: column; gap: 6px; }}
.m-stats .l {{ font-size: 11.5px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: var(--n700); }}
.m-stats .v {{ font-family: var(--hfont); font-weight: 600; font-size: clamp(26px, 2.6vw, 38px); line-height: 1.05; letter-spacing: -0.02em; color: var(--ink); overflow-wrap: anywhere; }}
.m-stats .v.acc {{ color: var(--acc700); }}
.m-stats .v.blue {{ color: var(--blue); }}
.m-stats .v small {{ font-size: 0.45em; font-weight: 500; color: var(--n700); letter-spacing: 0; }}
.m-stats .s {{ font-size: 13px; color: var(--n700); line-height: 1.45; }}
.m-stats.big .v {{ font-size: clamp(30px, 3vw, 42px); }}
.m-stats.noborder {{ gap: 10px; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }}
.m-stats.noborder > div {{ background: var(--n100); border: 0; border-radius: 12px; padding: 12px 14px; gap: 3px; }}
.m-stats.noborder .l {{ letter-spacing: 0; text-transform: none; font-size: 12px; }}
.m-stats.noborder .v {{ font-size: clamp(20px, 1.8vw, 26px); }}
.m-stats.sm .v {{ font-size: clamp(18px, 1.6vw, 22px); white-space: nowrap; }}
.m-stats.sm .v.acc, .m-stats.sm .v.blue {{ font-size: clamp(30px, 3vw, 44px); }}

/* ---------- çubuk satırları ---------- */
.m-bars {{ display: flex; flex-direction: column; gap: 12px; }}
.m-bar {{ display: flex; flex-direction: column; gap: 6px; }}
.m-bar .t {{ display: flex; justify-content: space-between; align-items: baseline; gap: 12px; font-size: 13.5px; color: var(--ink); }}
.m-bar .t .n {{ font-weight: 600; white-space: nowrap; }}
.m-bar .t > span:last-child {{ font-family: var(--mono); font-size: 14px; }}
.m-bar .t .n small, .m-bar .t small {{ font-family: var(--font); font-weight: 400; color: var(--n700); font-size: 12.5px; }}
.m-bar .tr {{ height: 12px; background: var(--n200); position: relative; border-radius: 999px; }}
.m-bar .tr .f {{ height: 100%; background: var(--n800); border-radius: 999px; }}
.m-bar .tr .f.acc {{ background: var(--acc); }}
.m-bar .tr .f.mid {{ background: var(--n500); }}
.m-bar .tr .f.blue {{ background: var(--blue); }}
.m-bar .tr .f.soft {{ background: var(--acc400); }}
.m-bar .tr .f.blue2 {{ background: var(--blue400); }}
.m-bar .tr .w {{ position: absolute; top: 3px; height: 6px; border-left: 2px solid var(--ink); border-right: 2px solid var(--ink); background: rgba(14,26,43,0.28); }}
.m-bar .sel {{ font-size: 11px; font-weight: 600; letter-spacing: 0.03em; color: #FFFFFF; background: var(--ink); border-radius: 999px; padding: 2px 9px; width: fit-content; }}
.m-bars.slim .m-bar .tr {{ height: 10px; }}

/* ---------- kutular ---------- */
.m-box {{ background: #FFFFFF; border: 1px solid var(--div); border-radius: 14px; padding: 16px 18px; font-size: 13.5px; color: var(--n800); line-height: 1.6; }}
.m-box.acc {{ background: #FEF6F0; border-color: #F6C9AC; }}
.m-box.blue {{ background: var(--blue50); border-color: var(--blue200); }}
.m-box .chip {{ font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; background: var(--ink); color: #FFFFFF;
  display: block; width: fit-content; padding: 3px 9px; border-radius: 6px; margin-bottom: 10px; }}
.m-box.acc .chip {{ background: var(--acc700); }}
.m-box.blue .chip {{ background: var(--blue); }}
.m-box .k {{ font-family: var(--hfont); font-size: 17px; font-weight: 600; margin-bottom: 10px; color: var(--ink); }}
.m-box p {{ margin: 0 0 6px; }}
.m-box p:last-child {{ margin-bottom: 0; }}
.m-box strong {{ color: var(--ink); }}

/* ---------- sayfa dizini (kartlar) ---------- */
.m-index {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 14px; }}
.m-index a.row {{ display: flex; flex-direction: column; gap: 10px; padding: 18px; min-height: 136px; box-sizing: border-box;
  background: #FFFFFF; border: 1px solid var(--div); border-radius: 14px; color: var(--ink); text-decoration: none; }}
.m-index a.row:hover {{ border-color: var(--blue); box-shadow: 0 6px 20px rgba(31,79,209,.10); text-decoration: none; }}
.m-index a.row .h {{ display: flex; justify-content: space-between; align-items: center; color: var(--n700); }}
.m-index a.row .ar {{ font-size: 17px; line-height: 1; }}
.m-index a.row .n {{ font-family: var(--mono); font-weight: 600; font-size: 12px; color: var(--blue); background: var(--blue100); padding: 3px 8px; border-radius: 6px; }}
.m-index a.row .l {{ font-family: var(--hfont); font-weight: 600; font-size: 17.5px; }}
.m-index a.row .d {{ font-size: 13px; color: var(--n700); line-height: 1.5; }}
.m-index a.row.featured {{ background: var(--ink); border-color: var(--ink); color: #FFFFFF; }}
.m-index a.row.featured .h {{ color: #FFFFFF; }}
.m-index a.row.featured .n {{ background: #FF9A5C; color: var(--ink); }}
.m-index a.row.featured .d {{ color: #C9D2DE; }}
.m-index .end {{ display: none; }}

/* ---------- liste satırları ---------- */
.m-list {{ background: #FFFFFF; border: 1px solid var(--div); border-radius: 16px; padding: 4px 20px; }}
.m-list > div {{ border-top: 1px solid var(--n200); padding: 13px 0; }}
.m-list > div:first-child {{ border-top: 0; }}
.m-list .t {{ font-weight: 600; font-size: 14.5px; color: var(--ink); }}
.m-list .t small {{ font-weight: 400; font-size: 12px; color: var(--n700); margin-left: 4px; }}
.m-list .d {{ font-size: 13.5px; color: var(--n800); margin-top: 4px; line-height: 1.55; }}
.m-list .d strong {{ color: var(--ink); }}
.m-list.num > div {{ display: grid; grid-template-columns: 44px minmax(0,1fr); gap: 12px; }}
.m-list.num .n {{ font-family: var(--mono); font-weight: 600; font-size: 13px; color: var(--blue); padding-top: 2px; }}
.m-list.num .t {{ font-family: var(--hfont); font-size: 16.5px; }}
.m-steps {{ display: flex; flex-direction: column; gap: 12px; }}
.m-steps > div {{ display: grid; grid-template-columns: 28px minmax(0,1fr); gap: 12px; font-size: 14px; color: var(--n800); line-height: 1.6; }}
.m-steps > div > b {{ width: 26px; height: 26px; border-radius: 999px; background: var(--blue100); color: var(--blue);
  font-family: var(--mono); font-weight: 600; font-size: 12.5px; display: flex; align-items: center; justify-content: center; }}
.m-steps strong {{ color: var(--ink); }}

/* ---------- tablo ---------- */
table.m-table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; color: var(--ink); font-variant-numeric: tabular-nums; }}
table.m-table th {{ text-align: left; padding: 0 10px 8px; border-bottom: 1px solid var(--n400); font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600; color: var(--n700); }}
table.m-table th.r, table.m-table td.r {{ text-align: right; }}
table.m-table td {{ padding: 9px 10px; border-bottom: 1px solid var(--n200); vertical-align: top; }}
table.m-table td.r {{ font-family: var(--mono); font-size: 13px; }}
table.m-table th:first-child, table.m-table td:first-child {{ padding-left: 6px; }}
table.m-table th:last-child, table.m-table td:last-child {{ padding-right: 6px; }}
table.m-table tr.hi {{ background: var(--blue50); }}
table.m-table tr.hi td {{ font-weight: 600; }}
table.m-table tr.hi td:first-child {{ color: var(--blue); }}
table.m-table.kv td:first-child {{ color: var(--n700); width: 34%; min-width: 120px; }}
table.m-table.kv tr:last-child td {{ border-bottom: 0; }}
table.m-table a {{ color: var(--blue); text-decoration: none; }}
table.m-table a:hover {{ text-decoration: underline; }}
table.m-table code, .m-mono {{ font-family: var(--mono); font-size: 12.5px; background: var(--n200); padding: 1px 5px; border-radius: 4px; }}
.m-table-wrap {{ overflow-x: auto; background: #FFFFFF; border: 1px solid var(--div); border-radius: 14px; padding: 14px 14px 6px; }}
[data-testid="stVerticalBlockBorderWrapper"] .m-table-wrap {{ background: none; border: 0; border-radius: 0; padding: 0; }}

/* ---------- akış ---------- */
.m-flow {{ display: flex; align-items: stretch; flex-wrap: wrap; gap: 8px; padding: 4px 0; }}
.m-flow .st {{ display: flex; align-items: center; gap: 8px; flex: 1 1 120px; min-width: 0; }}
.m-flow .bx {{ flex: 1 1 auto; background: #FFFFFF; border: 1px solid var(--div); border-radius: 10px; padding: 10px 12px; min-width: 0; }}
.m-flow .bx .t {{ font-weight: 600; font-size: 13.5px; color: var(--ink); }}
.m-flow .bx .d {{ font-size: 12px; color: var(--n700); margin-top: 2px; }}
.m-flow .ar {{ color: var(--n400); font-weight: 600; }}

/* ---------- bant / aralık görselleştirme ---------- */
.m-band {{ position: relative; height: 72px; background: var(--n100); border-radius: 12px; }}
.m-band .mb {{ position: absolute; top: 18px; bottom: 18px; background: #DCE5FB; border-radius: 8px; }}
.m-band .qb {{ position: absolute; top: 27px; bottom: 27px; background: var(--blue400); border-radius: 6px; }}
.m-band .pt {{ position: absolute; top: 50%; width: 18px; height: 18px; background: var(--ink); border: 3px solid #FFFFFF; border-radius: 999px;
  transform: translate(-50%,-50%); box-shadow: 0 0 0 1px var(--ink); box-sizing: border-box; }}
.m-band .pl {{ position: absolute; top: 2px; transform: translateX(-50%); font-family: var(--mono); font-size: 12px; font-weight: 600; color: var(--ink); }}
.m-axis {{ display: flex; justify-content: space-between; gap: 12px; font-size: 11.5px; color: var(--n700); margin-top: 6px; }}

/* ---------- SHAP satırları ---------- */
.m-shap {{ display: flex; flex-direction: column; gap: 7px; margin-top: 8px; }}
.m-shap > div {{ display: grid; grid-template-columns: minmax(120px, 210px) minmax(0,1fr) 58px; gap: 12px; align-items: center; }}
.m-shap .nm {{ font-size: 12.5px; text-align: right; color: var(--n800); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.m-shap .tr {{ position: relative; height: 16px; background: var(--bg); border-radius: 4px; }}
.m-shap .tr .z {{ position: absolute; top: -3px; bottom: -3px; left: 50%; width: 1px; background: var(--n400); }}
.m-shap .tr .b {{ position: absolute; top: 0; bottom: 0; border-radius: 3px; }}
.m-shap .vl {{ font-family: var(--mono); font-size: 12.5px; font-weight: 600; }}

/* ---------- alt bilgi ---------- */
.m-foot {{ display: flex; justify-content: space-between; gap: 8px 24px; flex-wrap: wrap; padding: 18px 0 6px; font-size: 12.5px; line-height: 1.55;
  color: var(--n700); border-top: 1px solid var(--div); margin-top: 20px; }}
.m-foot .kurum {{ color: var(--n800); font-weight: 600; }}

/* ---------- kart (st.container(border=True)) ---------- */
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]),
[data-testid="stMainBlockContainer"] .st-key-kart, [data-testid="stMainBlockContainer"] [class*="st-key-kart"] {{
  background: #FFFFFF; border: 1px solid var(--div) !important; border-radius: 16px !important; box-shadow: none;
}}

/* ---------- Streamlit bileşenlerini tasarım diline çekme ---------- */
[data-testid="stMainBlockContainer"] h1, [data-testid="stMainBlockContainer"] h2, [data-testid="stMainBlockContainer"] h3 {{ font-family: var(--hfont); font-weight: 600; letter-spacing: -0.01em; }}
[data-testid="stMainBlockContainer"] h3 {{ font-size: 1.15rem; }}
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{ font-size: 12.5px; font-weight: 600; color: var(--n700); }}
[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p {{ font-weight: 400; font-size: 13px; color: var(--n800); }}
[data-testid="stButtonGroup"] [role="radiogroup"] {{ background: var(--n200); border: 0; padding: 4px; gap: 4px; width: fit-content; border-radius: 12px; flex-wrap: wrap; }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"] {{ border: 0 !important; border-radius: 9px !important; padding: 8px 16px; min-height: 40px;
  font-weight: 600; font-size: 14px; color: var(--n700); background: transparent; }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"]:hover {{ color: var(--ink); background: rgba(255,255,255,0.6); }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"][aria-checked="true"] {{ background: #FFFFFF; color: var(--ink); box-shadow: 0 1px 3px rgba(14,26,43,0.14); }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"] p {{ font-weight: 600; font-size: 14px; color: inherit; }}
[data-testid="stBaseButton-primary"] {{ background: var(--ink); border: 0; border-radius: 12px; color: #FFFFFF; font-weight: 600; font-size: 15px; min-height: 48px; padding: 12px 20px; }}
[data-testid="stBaseButton-primary"]:hover {{ background: var(--n900); color: #FFFFFF; }}
[data-testid="stBaseButton-primary"] p {{ font-weight: 600; font-size: 15px; }}
[data-testid="stBaseButton-secondary"] {{ border: 1px solid var(--n400); border-radius: 10px; background: #FFFFFF; color: var(--n800); font-weight: 600; }}
[data-testid="stBaseButton-secondary"]:hover {{ border-color: var(--ink); background: #FFFFFF; color: var(--ink); }}
[data-testid="stTabs"] [role="tablist"] {{ gap: 4px; border-bottom: 1px solid var(--div); }}
[data-testid="stTabs"] [data-testid="stTab"] {{ padding: 10px 14px 12px; margin: 0; background: transparent; border-radius: 0; position: relative; }}
[data-testid="stTabs"] [data-testid="stTab"] p {{ font-size: 14px; font-weight: 600; color: var(--n700); }}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p {{ color: var(--ink); }}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"]::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: -1px; height: 3px; background: var(--blue); }}
[data-testid="stTabs"] [data-baseweb="tab-highlight"], [data-testid="stTabs"] [data-baseweb="tab-border"] {{ display: none; }}
[data-testid="stTabs"] [data-testid="stTab"]:hover p {{ color: var(--blue); }}
[data-testid="stExpander"] details {{ border: 1px solid var(--div); border-radius: 14px; background: #FFFFFF; }}
[data-testid="stExpander"] summary {{ font-size: 14px; font-weight: 600; color: var(--ink); min-height: 48px; }}
[data-testid="stExpander"] summary:hover {{ color: var(--blue); }}
[data-testid="stDataFrame"] {{ border: 1px solid var(--div); border-radius: 12px; overflow: hidden; background: #FFFFFF; }}
[data-testid="stAlert"] {{ border-radius: 12px; }}
[data-testid="stPlotlyChart"] {{ background: #FFFFFF; border: 1px solid var(--div); border-radius: 14px; padding: 6px 8px 2px; }}
/* sayfa bağlantıları = tasarımın düğmeleri (ana: lacivert dolu; ikincil: beyaz, ince çerçeve) */
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"] {{
  border-radius: 10px; border: 1px solid var(--n400); background: #FFFFFF; color: var(--n800);
  padding: 12px 18px; min-height: 46px; width: 100%; justify-content: space-between; margin: 0; box-sizing: border-box;
}}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"] p, [data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"] span {{ font-weight: 600; font-size: 15px; color: inherit; white-space: normal; line-height: 1.25; }}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"] > span {{ width: 100%; }}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"]:hover {{ border-color: var(--ink); color: var(--ink); background: #FFFFFF; }}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"][href$="Dogrulama_Deneyleri"] {{ background: var(--ink); border-color: var(--ink); color: #FFFFFF; }}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"][href$="Dogrulama_Deneyleri"]:hover {{ background: var(--n900); border-color: var(--n900); color: #FFFFFF; }}
[data-testid="stCaptionContainer"] {{ color: var(--n700); }}
hr {{ border-top: 1px solid var(--div); margin: 14px 0; }}
[data-testid="stMetricLabel"] p {{ font-size: 11.5px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: var(--n700); }}
[data-testid="stMetricValue"] {{ font-family: var(--hfont); font-weight: 600; }}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {{ font-variant-numeric: tabular-nums; }}
[data-testid="stNumberInput"] input {{ font-family: var(--mono); }}
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] {{ font-family: var(--mono); font-weight: 600; color: var(--blue); }}
@media (max-width: 900px) {{
  [data-testid="stMainBlockContainer"] {{ padding: 1rem 1rem 2rem; }}
  .m-h1 {{ max-width: none; }}
}}
</style>
"""


def inject_css():
    """Küresel stil; giriş betiğinde (her sayfa çalışmasında) bir kez çağrılır."""
    st.html(_CSS)


# ---------------------------------------------------------------- yardımcılar
def esc(s) -> str:
    return _html.escape(str(s), quote=True)


def tr(x, nd: int = 3) -> str:
    """Türkçe sayı biçimi: ondalık virgül, binlik nokta."""
    if x is None:
        return "—"
    try:
        if isinstance(x, bool):
            return str(x)
        if isinstance(x, int) or (float(x).is_integer() and nd == 0):
            return f"{int(x):,}".replace(",", ".")
        s = f"{float(x):,.{nd}f}"
    except (TypeError, ValueError):
        return str(x)
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v, lo=0.0, hi=30.0) -> float:
    """[lo, hi] aralığını %0–100'e taşır (bant görselleştirmesi)."""
    return max(0.0, min(100.0, (v - lo) / (hi - lo) * 100.0))


# st.html satır içi SVG'yi temizler; ok işareti metin olarak verilir.
_ARROW = '<span class="ar" aria-hidden="true">→</span>'


# ---------------------------------------------------------------- bileşenler
def card(key: str | None = None):
    """Beyaz kart (kenarlıklı Streamlit kapsayıcısı). Kullanım: ``with ui.card(): ...``"""
    return st.container(border=True, key=key)


def page_header(kicker: str, title_html: str, lede_html: str = "", rule: bool = False):
    """Sayfa başlığı. ``kicker`` "02 — Doğrulama Deneyleri · Tez Bölüm 3.13" biçimindeyse
    " · " sonrası sağ üstte çip olarak gösterilir."""
    chip = ""
    if " · " in kicker:
        kicker, chip = kicker.split(" · ", 1)
    top = f'<div class="top"><div class="m-kicker">{kicker}</div>' + (
        f'<span class="m-chip">{chip}</span>' if chip else "") + "</div>"
    h = f'<div class="m-head">{top}<div class="m-h1">{title_html}</div>'
    if lede_html:
        h += f'<p class="m-lede">{lede_html}</p>'
    h += "</div>"
    if rule:
        h += '<div class="m-rule"></div>'
    st.html(h)


def kicker(text: str, sub: str = "", tone: str = "acc"):
    cls = {"acc": "m-kicker", "ink": "m-kicker ink", "mute": "m-kicker mute"}[tone]
    s = f' <span class="sub">{sub}</span>' if sub else ""
    st.html(f'<div class="{cls}" style="margin:2px 0 4px">{text}{s}</div>')


def h2(text: str, sub: str = ""):
    """Kart başlığı (Space Grotesk) + isteğe bağlı sağda açıklama."""
    s = f'<span class="m-mute" style="font-size:12.5px">{sub}</span>' if sub else ""
    st.html(f'<div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:baseline; '
            f'gap:4px 12px; margin-bottom:2px"><h2 class="m-h2">{text}</h2>{s}</div>')


def rule(thin: bool = False):
    st.html(f'<div class="m-rule{" thin" if thin else ""}"></div>')


def stats(items, big: bool = False, border: bool = True, small: bool = False):
    """items: [(etiket, değer_html, alt_metin, 'acc'|'blue'|'')]"""
    cells = []
    for it in items:
        label, value, sub = it[0], it[1], (it[2] if len(it) > 2 else "")
        tone = it[3] if len(it) > 3 else ""
        cells.append(
            f'<div><div class="l">{label}</div><div class="v {tone}">{value}</div>'
            + (f'<div class="s">{sub}</div>' if sub else "") + "</div>")
    cls = "m-stats" + (" big" if big else "") + (" sm" if small else "") + ("" if border else " noborder")
    st.html(f'<div class="{cls}">{"".join(cells)}</div>')


_FILL = {"ink": "f", "acc": "f acc", "mid": "f mid", "blue": "f blue", "soft": "f soft", "blue2": "f blue2"}


def bar_rows(rows, vmax: float = 1.0, slim: bool = False):
    """rows: [dict(name, value, value_str, tone('ink'|'acc'|'mid'|'blue'|'soft'|'blue2'), sub, std, sel)]"""
    out = []
    for r in rows:
        v = float(r["value"])
        w = max(0.0, min(100.0, v / vmax * 100.0))
        fcls = _FILL[r.get("tone", "ink")]
        sub = f' <small>{r["sub"]}</small>' if r.get("sub") else ""
        vs = r.get("value_str", tr(v, 3))
        vsub = f' <small>{r["value_sub"]}</small>' if r.get("value_sub") else ""
        whisk = ""
        if r.get("std"):
            s = float(r["std"]) / vmax * 100.0
            whisk = f'<div class="w" style="left:{w - s:.2f}%;width:{2 * s:.2f}%"></div>'
        sel = f'<div class="sel">{r["sel"]}</div>' if r.get("sel") else ""
        ncls = "n" if r.get("bold", True) else ""
        out.append(
            f'<div class="m-bar"><div class="t"><span class="{ncls}">{r["name"]}{sub}</span>'
            f'<span class="n">{vs}{vsub}</span></div>'
            f'<div class="tr"><div class="{fcls}" style="width:{w:.2f}%"></div>{whisk}</div>{sel}</div>')
    st.html(f'<div class="m-bars{" slim" if slim else ""}">{"".join(out)}</div>')


def box(body_html: str, chip: str = "", accent: bool = False, k: str = "", tone: str = ""):
    """Kart kutu. ``accent=True`` (veya tone="acc") turuncu uyarı, tone="blue" mavi bilgi kutusu."""
    tone = "acc" if accent else tone
    head = f'<div class="chip">{chip}</div>' if chip else (f'<div class="k">{k}</div>' if k else "")
    st.html(f'<div class="m-box{" " + tone if tone else ""}">{head}{body_html}</div>')


def text(html_: str, mute: bool = False):
    st.html(f'<div class="{"m-mute" if mute else "m-text"}">{html_}</div>')


def index_rows(rows, featured: str = "Dogrulama_Deneyleri"):
    """rows: [(numara, etiket, açıklama, href)] — bağlantılı sayfa kartları."""
    out = ['<div class="m-index">']
    for n, l, d, href in rows:
        f = " featured" if href == featured else ""
        nn = f"{n} · merkez deney" if f else n
        out.append(f'<a class="row{f}" href="{href}" target="_self"><span class="h"><span class="n">{nn}</span>{_ARROW}</span>'
                   f'<span class="l">{l}</span><span class="d">{d}</span></a>')
    out.append("</div>")
    st.html("".join(out))


def list_rows(rows, numbered: bool = False):
    """rows: [(başlık, açıklama)] veya numbered ise [(no, başlık, küçük, açıklama)]"""
    out = [f'<div class="m-list{" num" if numbered else ""}">']
    for r in rows:
        if numbered:
            n, t, s, d = r
            out.append(f'<div><div class="n">{n}</div><div><div class="t">{t} <small>{s}</small></div>'
                       f'<div class="d">{d}</div></div></div>')
        else:
            t, d = r
            out.append(f'<div><div class="t">{t}</div><div class="d">{d}</div></div>')
    out.append("</div>")
    st.html("".join(out))


def steps(items):
    """items: [(no, html)] — numaralı kısa maddeler."""
    out = ['<div class="m-steps">'] + [f"<div><b>{n}</b><span>{h}</span></div>" for n, h in items] + ["</div>"]
    st.html("".join(out))


def table(header, rows, right_cols=(), hi_row: int | None = None, kv: bool = False):
    """Basit HTML tablo. header: [str]; rows: [[html,...]]."""
    cls = "m-table kv" if kv else "m-table"
    h = [f'<div class="m-table-wrap"><table class="{cls}">']
    if header:
        h.append("<thead><tr>" + "".join(
            f'<th class="{"r" if i in right_cols else ""}">{c}</th>' for i, c in enumerate(header)) + "</tr></thead>")
    h.append("<tbody>")
    for ri, r in enumerate(rows):
        tr_cls = ' class="hi"' if hi_row is not None and ri == hi_row else ""
        h.append(f"<tr{tr_cls}>" + "".join(
            f'<td class="{"r" if i in right_cols else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>")
    h.append("</tbody></table></div>")
    st.html("".join(h))


def flow(stages):
    """stages: [(başlık, açıklama)] → oklu aşama şeridi."""
    out = ['<div class="m-flow">']
    for i, (t, d) in enumerate(stages):
        out.append(f'<div class="st"><div class="bx"><div class="t">{t}</div><div class="d">{d}</div></div>'
                   + ('<div class="ar" aria-hidden="true">→</div>' if i < len(stages) - 1 else "") + "</div>")
    out.append("</div>")
    st.html("".join(out))


def footer():
    st.html(
        '<div class="m-foot"><div>© 2026 İsmail Topçam — <span class="kurum">İzmir Kâtip Çelebi '
        'Üniversitesi</span>, Yazılım Mühendisliği YL tezi eşlik uygulaması.</div>'
        '<div>Veri: <a href="https://www.perovskitedatabase.com">Perovskite Database</a> '
        '(Jacobsson vd., 2022 — CC BY 4.0, atıfla). Çıktılar araştırma ve eğitim amaçlıdır.</div></div>')


def sci_limit_box():
    box('<p><strong>Bu çıktı deneysel doğrulama yerine geçmez.</strong> Model, literatür kayıtlarından '
        'öğrenilen istatistiksel örüntülere dayalı bir önceliklendirme aracıdır; ağaç tabanlı modeller '
        'eğitim dağılımının dışına ekstrapolasyon yapamaz (tez Bölüm 5.4). Tahminler faz kararlılığı, film '
        'morfolojisi ve uzun dönem stabilite gibi ölçütlerle birlikte, uzman değerlendirmesiyle '
        'yorumlanmalıdır. %90 aralıklar DOI-grup-güvenli conformal kalibrasyonla hesaplanmıştır (tez '
        'Bölüm 4.10); elle girilen tarifler için kesin garanti değil, veriye dayalı belirsizlik '
        'göstergesidir.</p>', chip="Bilimsel sınır")


# ---------------------------------------------------------------- plotly
def plotly_layout(fig, height: int | None = None, title: str | None = None, **kw):
    """Grafikleri tasarım diline çeker: Inter, saydam zemin, ince nötr ızgara."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, color=INK, size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=44 if (title or fig.layout.title.text) else 16, b=10),
        colorway=[N900, BLUE, ACC, N600, BLUE400],
        title=dict(text=title if title is not None else fig.layout.title.text,
                   font=dict(size=14, family=HFONT, color=INK), x=0, xanchor="left"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        hoverlabel=dict(font=dict(family=FONT), bgcolor="#FFFFFF", bordercolor=N300),
        **kw,
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(gridcolor=N200, zerolinecolor=N300, linecolor=N300, tickfont=dict(size=11, color=N700),
                     title_font=dict(size=11.5, color=N700))
    fig.update_yaxes(gridcolor=N200, zerolinecolor=N300, linecolor=N300, tickfont=dict(size=11, color=N700),
                     title_font=dict(size=11.5, color=N700))
    return fig


def chart(fig, height: int | None = None, title: str | None = None, **kw):
    plotly_layout(fig, height=height, title=title, **kw)
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})


# ---------------------------------------------------------------- eski API (geriye dönük)
def page(title: str, icon: str = "", wide: bool = True):
    st.title(title)


def tez_notu(bolum: str, metin: str):
    st.caption(f"**Tez {bolum}** · {metin}")


def bilim_uyarisi():
    sci_limit_box()


def conformal_uyarisi():
    text("%90 aralıklar DOI-grup-güvenli kalibrasyonla (tez Bölüm 4.10) hesaplanmıştır. Elle girilen "
         "tarifler holdout dağılımından gelmediği için (değişebilirlik varsayımı sağlanmaz) bu aralıklar "
         "<strong>veriye dayalı belirsizlik göstergesi</strong> olarak okunmalıdır; kesin bir %90 garantisi "
         "sunmaz.", mute=True)
