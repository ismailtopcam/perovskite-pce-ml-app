# -*- coding: utf-8 -*-
"""Ortak arayüz katmanı — "Modernist" tasarım sistemi.

Kaynak tasarım: Claude Design projesi "Website design work" →
"Tez Uygulamasi (Modernist).dc.html". Renk/tipografi jetonları ve bileşen
kalıpları (kicker, büyük başlık, 2 px çizgiler, sayı şeritleri, çubuk satırları,
mürekkep çerçeveli kutular) oradaki HTML'den birebir alınmıştır; etkileşimli
parçalar Streamlit bileşenleriyle kurulur ve aşağıdaki CSS ile aynı dile
çekilir.

Kullanım: her sayfa `ui.page_header(...)` ile başlar, `ui.footer()` ile biter.
"""
from __future__ import annotations

import html as _html

import streamlit as st

# ---------------------------------------------------------------- jetonlar
INK = "#201e1d"
BG = "#f3f2f2"
SURFACE = "#eae9e9"
ACC = "#ec3013"          # vurgu (Modernist kırmızısı)
ACC600 = "#dd2b0f"
ACC700 = "#ae1800"
ACC800 = "#7c1405"
ACC100 = "#fff2ef"
ACC200 = "#ffe0d9"
ACC400 = "#ff9783"
N200 = "#eae7e7"
N300 = "#d7d3d3"
N400 = "#bab6b6"
N600 = "#7d7979"
N700 = "#605d5d"
N800 = "#444141"
N900 = "#2d2b2b"
DIV = "#9f9d9d"          # color-mix(ink 40 %, zemin) — çizgiler
KURUM = ACC700           # İKÇÜ satırı (tasarımda "kurumsalBordo" kapalı)

# Eski adlar (grafiklerde anlamsal ayrım: yükselten = mürekkep, düşüren = vurgu)
MAVI = INK
KIRMIZI = ACC
GRI = N400
BORDO = "#ab162c"

FONT = "Archivo, system-ui, sans-serif"

# ---------------------------------------------------------------- CSS
_CSS = f"""
<style>
:root {{
  --ink:{INK}; --bg:{BG}; --acc:{ACC}; --acc600:{ACC600}; --acc700:{ACC700}; --acc800:{ACC800};
  --acc100:{ACC100}; --acc200:{ACC200}; --acc400:{ACC400};
  --n200:{N200}; --n300:{N300}; --n400:{N400}; --n600:{N600}; --n700:{N700}; --n800:{N800}; --n900:{N900};
  --div:{DIV}; --kurum:{KURUM}; --font:{FONT};
}}
html, body, [data-testid="stAppViewContainer"] {{ font-family: var(--font); }}
[data-testid="stAppViewContainer"] {{ background: var(--bg); }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMainBlockContainer"] {{ padding: 1.4rem 3rem 2.5rem; max-width: 1560px; }}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {{ gap: 0.75rem; }}
/* stil-yalnız html blokları yer kaplamasın */
[data-testid="stElementContainer"]:has(> [data-testid="stHtml"] > style:only-child) {{ display: none; }}
[data-testid="stHtml"] {{ font-family: var(--font); color: var(--ink); }}

/* ---------- sol ray (kenar çubuğu) ---------- */
[data-testid="stSidebar"] {{ background: var(--bg); border-right: 2px solid var(--div); }}
[data-testid="stSidebar"] > div:first-child {{ height: 100%; }}
[data-testid="stSidebarContent"] {{ display: flex; flex-direction: column; min-height: 100%; padding-bottom: 0; }}
[data-testid="stSidebarHeader"] {{ order: -3; padding: 0.4rem 0.6rem 0 0; height: auto; min-height: 0; }}
[data-testid="stSidebarHeader"] [data-testid="stLogoSpacer"] {{ display: none; }}
[data-testid="stSidebarUserContent"], [data-testid="stSidebarUserContent"] > div,
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] {{ display: contents; }}
[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.rail-brand) {{ order: -2; }}
[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.rail-foot) {{ order: 10; margin-top: auto; }}
[data-testid="stSidebarNav"] {{ order: 0; padding: 0; margin: 0; }}
[data-testid="stSidebarNavSeparator"] {{ display: none; }}
.rail-brand {{ padding: 0.2rem 1.25rem 1rem; border-bottom: 2px solid var(--div); }}
.rail-brand .kurum {{ font-size: 10.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--kurum); line-height: 1.5; }}
.rail-brand .ens {{ font-size: 10.5px; color: var(--n700); letter-spacing: 0.04em; margin-top: 2px; }}
.rail-brand .marka {{ font-family: var(--font); font-weight: 800; font-size: 30px; line-height: 1.0; letter-spacing: -0.01em; margin-top: 16px; color: var(--ink); }}
.rail-brand .alt {{ font-size: 12px; color: var(--n700); margin-top: 8px; text-wrap: pretty; }}
.rail-foot {{ border-top: 2px solid var(--div); padding: 14px 1.25rem 18px; }}
.rail-foot .k {{ font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--n700); }}
.rail-foot .ad {{ font-size: 12px; font-weight: 700; margin-top: 3px; color: var(--ink); }}
.rail-foot .m {{ font-size: 10.5px; color: var(--n700); margin-top: 6px; line-height: 1.6; }}
ul[data-testid="stSidebarNavItems"] {{ padding: 0; margin: 0; max-height: none; }}
ul[data-testid="stSidebarNavItems"] li {{ margin: 0; }}
[data-testid="stSidebarNavLinkContainer"] {{ padding: 0; margin: 0; }}
a[data-testid="stSidebarNavLink"] {{
  border-radius: 0; margin: 0; padding: 11px 14px 11px 1.25rem; height: auto;
  border-bottom: 1px solid var(--div); display: grid; grid-template-columns: 34px minmax(0,1fr);
  gap: 10px; align-items: baseline; background: transparent; color: var(--ink);
}}
a[data-testid="stSidebarNavLink"] [data-testid="stIconEmoji"], a[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] {{ display: none; }}
a[data-testid="stSidebarNavLink"]::before {{
  content: ""; font-weight: 800; font-size: 11px; letter-spacing: 0.06em; color: var(--acc700);
}}
a[data-testid="stSidebarNavLink"] p {{ font-size: 13.5px; font-weight: 600; margin: 0; line-height: 1.3; }}
a[data-testid="stSidebarNavLink"]:hover {{ background: var(--acc100); }}
a[data-testid="stSidebarNavLink"][aria-current="page"] {{ background: var(--ink); color: var(--bg); }}
a[data-testid="stSidebarNavLink"][aria-current="page"] p {{ color: var(--bg); }}
a[data-testid="stSidebarNavLink"][aria-current="page"]::before {{ color: var(--acc400); }}
ul[data-testid="stSidebarNavItems"] li:nth-child(1) a::before {{ content: "—"; }}
ul[data-testid="stSidebarNavItems"] li:nth-child(2) a::before {{ content: "R"; }}
ul[data-testid="stSidebarNavItems"] li:nth-child(3) a::before {{ content: "01"; }}
ul[data-testid="stSidebarNavItems"] li:nth-child(4) a::before {{ content: "02"; }}
ul[data-testid="stSidebarNavItems"] li:nth-child(5) a::before {{ content: "03"; }}
ul[data-testid="stSidebarNavItems"] li:nth-child(6) a::before {{ content: "04"; }}
ul[data-testid="stSidebarNavItems"] li:nth-child(7) a::before {{ content: "05"; }}
ul[data-testid="stSidebarNavItems"] li:nth-child(8) a::before {{ content: "06"; }}
ul[data-testid="stSidebarNavItems"] li:nth-child(9) a::before {{ content: "07"; }}
ul[data-testid="stSidebarNavItems"] li:nth-child(10) a::before {{ content: "08"; }}

/* ---------- tipografi kalıpları ---------- */
.m-kicker {{ font-size: 11px; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--acc700); }}
.m-kicker.ink {{ color: var(--ink); }}
.m-kicker.mute {{ color: var(--n700); }}
.m-kicker .sub {{ color: var(--n700); text-transform: none; letter-spacing: 0; font-weight: 400; }}
.m-h1 {{ font-weight: 800; font-size: clamp(26px, 2.8vw, 38px); line-height: 1.08; letter-spacing: -0.01em; margin-top: 10px; color: var(--ink); text-wrap: pretty; }}
.m-h1 .acc {{ color: var(--acc); }}
.m-hero {{ font-weight: 800; font-size: clamp(28px, 3.2vw, 44px); line-height: 1.06; letter-spacing: -0.01em; color: var(--ink); text-wrap: pretty; }}
.m-lede {{ margin: 12px 0 0; font-size: 14px; color: var(--n800); max-width: 78ch; line-height: 1.55; }}
.m-head {{ padding: 8px 0 6px; }}
.m-rule {{ border-top: 2px solid var(--div); margin: 14px 0 0; }}
.m-rule.thin {{ border-top-width: 1px; }}
.m-text {{ font-size: 13.5px; color: var(--n800); line-height: 1.55; }}
.m-text strong {{ color: var(--ink); }}
.m-mute {{ font-size: 12.5px; color: var(--n700); line-height: 1.5; }}
.m-text a, .m-mute a, .m-box a, .m-foot a {{ color: var(--acc700); text-decoration: none; }}
.m-text a:hover, .m-mute a:hover, .m-box a:hover {{ color: var(--acc600); text-decoration: underline; }}

/* ---------- sayı şeridi ---------- */
.m-stats {{ display: grid; grid-template-columns: repeat(var(--n, 4), minmax(0, 1fr)); border-top: 2px solid var(--div); border-bottom: 2px solid var(--div); }}
.m-stats.noborder {{ border: 0; }}
.m-stats > div {{ padding: 18px 20px 20px; border-left: 1px solid var(--div); min-width: 0; }}
.m-stats > div:first-child {{ border-left: 0; padding-left: 0; }}
.m-stats > div:last-child {{ padding-right: 0; }}
.m-stats .l {{ font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--n700); }}
.m-stats .v {{ font-weight: 800; font-size: clamp(26px, 2.4vw, 40px); line-height: 1.1; color: var(--ink); margin-top: 2px; overflow-wrap: anywhere; }}
.m-stats .v.acc {{ color: var(--acc); }}
.m-stats .v small {{ font-size: 0.42em; font-weight: 600; }}
.m-stats .s {{ font-size: 12px; color: var(--n700); margin-top: 2px; }}
.m-stats.big .v {{ font-size: clamp(30px, 3vw, 44px); }}
.m-stats.sm {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
.m-stats.sm > div {{ padding: 14px 14px 16px; }}
.m-stats.sm .v {{ font-size: clamp(18px, 1.5vw, 24px); margin-top: 8px; white-space: nowrap; }}
.m-stats.sm .v.acc {{ font-size: clamp(30px, 3vw, 44px); margin-top: 0; }}

/* ---------- çubuk satırları ---------- */
.m-bars {{ display: flex; flex-direction: column; gap: 12px; }}
.m-bar .t {{ display: flex; justify-content: space-between; gap: 12px; font-size: 12.5px; margin-bottom: 4px; color: var(--ink); }}
.m-bar .t .n {{ font-weight: 700; white-space: nowrap; }}
.m-bar .t .n small, .m-bar .t small {{ font-weight: 400; color: var(--n700); font-size: 12px; }}
.m-bar .tr {{ height: 22px; background: var(--n200); position: relative; }}
.m-bar .tr .f {{ height: 100%; background: var(--ink); }}
.m-bar .tr .f.acc {{ background: var(--acc); }}
.m-bar .tr .f.mid {{ background: var(--n600); }}
.m-bar .tr .w {{ position: absolute; top: 8px; height: 6px; border-left: 2px solid var(--ink); border-right: 2px solid var(--ink); background: rgba(32,30,29,0.35); }}
.m-bar .sel {{ font-size: 11px; font-weight: 700; color: var(--acc700); margin-top: 3px; }}
.m-bars.slim .m-bar .tr {{ height: 18px; }}

/* ---------- kutular ---------- */
.m-box {{ border: 2px solid var(--ink); padding: 14px 16px; font-size: 13px; color: var(--n900); line-height: 1.55; }}
.m-box.acc {{ border-color: var(--acc); }}
.m-box .chip {{ font-size: 10px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; background: var(--ink); color: var(--bg); display: block; width: fit-content; padding: 2px 8px; margin-bottom: 8px; }}
.m-box.acc .chip {{ background: var(--acc); color: #fff; }}
.m-box .k {{ font-size: 11px; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; margin-bottom: 10px; color: var(--ink); }}
.m-box p {{ margin: 0 0 6px; }}
.m-box p:last-child {{ margin-bottom: 0; }}

/* ---------- dizin / liste satırları ---------- */
.m-index a.row {{ display: grid; grid-template-columns: 56px 200px minmax(0,1fr); gap: 16px; align-items: baseline; padding: 12px 4px; border-top: 1px solid var(--div); color: var(--ink); text-decoration: none; }}
.m-index a.row:hover {{ background: var(--acc100); text-decoration: none; }}
.m-index a.row .n {{ font-weight: 800; font-size: 15px; color: var(--acc); }}
.m-index a.row .l {{ font-weight: 700; font-size: 14px; }}
.m-index a.row .d {{ font-size: 13px; color: var(--n700); }}
.m-index .end {{ border-top: 1px solid var(--div); }}
.m-list > div {{ border-top: 1px solid var(--div); padding: 12px 4px; }}
.m-list > div:last-child {{ border-bottom: 1px solid var(--div); }}
.m-list .t {{ font-weight: 700; font-size: 14px; color: var(--ink); }}
.m-list .t small {{ font-weight: 400; font-size: 12px; color: var(--n700); }}
.m-list .d {{ font-size: 13px; color: var(--n800); margin-top: 3px; line-height: 1.5; }}
.m-list.num > div {{ display: grid; grid-template-columns: 56px minmax(0,1fr); gap: 16px; padding: 14px 4px; }}
.m-list.num .n {{ font-weight: 800; font-size: 15px; color: var(--acc); }}
.m-steps > div {{ display: flex; gap: 10px; font-size: 13.5px; color: var(--n800); margin-bottom: 10px; line-height: 1.5; }}
.m-steps > div > b {{ font-weight: 800; color: var(--ink); flex: none; }}
.m-steps strong {{ color: var(--ink); }}
.m-steps a, .m-list a, .m-index a.row .d a {{ color: var(--acc700); text-decoration: none; }}
.m-steps a:hover {{ text-decoration: underline; }}

/* ---------- tablo ---------- */
table.m-table {{ border-collapse: collapse; width: 100%; font-size: 12.5px; color: var(--ink); }}
table.m-table th {{ text-align: left; padding: 8px 10px; border-bottom: 2px solid var(--ink); font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; font-weight: 700; }}
table.m-table th.r, table.m-table td.r {{ text-align: right; }}
table.m-table td {{ padding: 7px 10px; border-bottom: 1px solid var(--div); vertical-align: top; }}
table.m-table th:first-child, table.m-table td:first-child {{ padding-left: 0; }}
table.m-table th:last-child, table.m-table td:last-child {{ padding-right: 0; }}
table.m-table tr.hi {{ background: var(--acc100); }}
table.m-table tr.hi td {{ font-weight: 700; }}
table.m-table.kv td:first-child {{ font-weight: 700; width: 280px; }}
table.m-table.kv tr:first-child td {{ border-top: 2px solid var(--ink); }}
table.m-table.kv tr:last-child td {{ border-bottom: 2px solid var(--ink); }}
table.m-table a {{ color: var(--acc700); text-decoration: none; }}
table.m-table a:hover {{ text-decoration: underline; }}
table.m-table code, .m-mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; background: var(--n200); padding: 1px 5px; }}

/* ---------- akış ---------- */
.m-flow {{ display: flex; align-items: stretch; flex-wrap: wrap; padding: 16px 0 12px; gap: 10px 0; }}
.m-flow .st {{ display: flex; align-items: center; flex: 0 0 auto; }}
.m-flow .bx {{ border: 2px solid var(--ink); padding: 10px 14px; min-width: 118px; }}
.m-flow .bx .t {{ font-weight: 800; font-size: 13px; color: var(--ink); }}
.m-flow .bx .d {{ font-size: 11px; color: var(--n700); margin-top: 2px; }}
.m-flow .ar {{ padding: 0 8px; font-weight: 800; color: var(--acc); }}

/* ---------- bant / aralık görselleştirme ---------- */
.m-band {{ position: relative; height: 64px; background: var(--n200); }}
.m-band .mb {{ position: absolute; top: 14px; bottom: 14px; background: var(--acc200); }}
.m-band .qb {{ position: absolute; top: 22px; bottom: 22px; background: var(--acc400); }}
.m-band .pt {{ position: absolute; top: 50%; width: 14px; height: 14px; background: var(--ink); transform: translate(-50%,-50%) rotate(45deg); }}
.m-band .pl {{ position: absolute; top: 50%; transform: translate(-50%,-260%); font-size: 12px; font-weight: 800; color: var(--ink); }}
.m-axis {{ display: flex; justify-content: space-between; gap: 12px; font-size: 10.5px; color: var(--n700); margin-top: 4px; }}

/* ---------- SHAP satırları ---------- */
.m-shap {{ display: flex; flex-direction: column; gap: 6px; margin-top: 12px; }}
.m-shap > div {{ display: grid; grid-template-columns: 190px minmax(0,1fr) 62px; gap: 10px; align-items: center; }}
.m-shap .nm {{ font-size: 12px; text-align: right; color: var(--n800); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.m-shap .tr {{ position: relative; height: 16px; background: var(--n200); }}
.m-shap .tr .z {{ position: absolute; top: 0; bottom: 0; left: 50%; width: 1px; background: var(--n600); }}
.m-shap .tr .b {{ position: absolute; top: 0; bottom: 0; }}
.m-shap .vl {{ font-size: 12px; font-weight: 700; }}

/* ---------- alt bilgi ---------- */
.m-foot {{ display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap; padding: 16px 0 8px; font-size: 11.5px; color: var(--n700); border-top: 2px solid var(--div); margin-top: 28px; }}
.m-foot .kurum {{ color: var(--kurum); font-weight: 700; }}

/* ---------- Streamlit bileşenlerini tasarım diline çekme ---------- */
[data-testid="stMainBlockContainer"] h1, [data-testid="stMainBlockContainer"] h2, [data-testid="stMainBlockContainer"] h3 {{ font-weight: 800; letter-spacing: -0.01em; }}
[data-testid="stMainBlockContainer"] h3 {{ font-size: 1.15rem; }}
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{ font-size: 11.5px; font-weight: 700; letter-spacing: 0.03em; color: var(--n700); }}
[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p {{ text-transform: none; letter-spacing: 0; font-weight: 400; font-size: 12.5px; color: var(--n700); }}
[data-testid="stButtonGroup"] [role="radiogroup"] {{ border: 2px solid var(--ink); gap: 0; width: fit-content; border-radius: 0; flex-wrap: wrap; }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"] {{ border: 0; border-radius: 0; border-left: 2px solid var(--ink); padding: 8px 16px; font-weight: 700; font-size: 13px; color: var(--ink); background: transparent; min-height: 0; }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"]:first-child {{ border-left: 0; }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"]:hover {{ background: var(--acc100); color: var(--ink); }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"][aria-checked="true"] {{ background: var(--ink); color: var(--bg); }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"][aria-checked="true"]:hover {{ background: var(--ink); color: var(--bg); }}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"] p {{ font-weight: 700; font-size: 13px; color: inherit; }}
[data-testid="stBaseButton-primary"] {{ background: var(--acc); border: 0; border-radius: 0; color: #fff; font-weight: 700; font-size: 14px; padding: 12px 18px; }}
[data-testid="stBaseButton-primary"]:hover {{ background: var(--acc600); color: #fff; }}
[data-testid="stBaseButton-secondary"] {{ border: 2px solid var(--ink); border-radius: 0; background: transparent; color: var(--ink); font-weight: 700; }}
[data-testid="stBaseButton-secondary"]:hover {{ background: var(--acc100); border-color: var(--ink); color: var(--ink); }}
[data-testid="stTabs"] [role="tablist"] {{ gap: 0; border-bottom: 2px solid var(--div); }}
[data-testid="stTabs"] [data-testid="stTab"] {{ padding: 8px 0 10px; margin-right: 26px; background: transparent; border-radius: 0; position: relative; }}
[data-testid="stTabs"] [data-testid="stTab"] p {{ font-size: 11px; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--n700); }}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] p {{ color: var(--ink); }}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"]::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: -2px; height: 3px; background: var(--ink); }}
[data-testid="stTabs"] [data-testid="stTab"] > div[data-rac]:last-child {{ display: none; }}
[data-testid="stTabs"] [data-testid="stTab"]:hover p {{ color: var(--acc700); }}
[data-testid="stExpander"] details {{ border: 0; border-top: 1px solid var(--div); border-bottom: 1px solid var(--div); border-radius: 0; background: transparent; }}
[data-testid="stExpander"] summary {{ font-size: 12px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink); }}
[data-testid="stExpander"] summary:hover {{ color: var(--acc700); }}
[data-testid="stDataFrame"] {{ border: 1px solid var(--div); }}
[data-testid="stAlert"] {{ border-radius: 0; border: 2px solid var(--ink); background: transparent; }}
[data-testid="stAlertContainer"] {{ border-radius: 0; }}
/* sayfa bağlantıları = tasarımın düğmeleri (ana: dolu vurgu; ikincil: 2 px mürekkep çerçeve) */
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"] {{
  border-radius: 0; border: 2px solid var(--ink); background: transparent; color: var(--ink);
  padding: 10px 16px; width: 100%; justify-content: space-between; margin: 0;
}}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"] p {{ font-weight: 700; font-size: 13px; color: inherit; white-space: normal; line-height: 1.25; }}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"] > span {{ width: 100%; }}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"]:hover {{ background: var(--acc100); }}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"][href$="Dogrulama_Deneyleri"] {{ background: var(--acc); border-color: var(--acc); color: #fff; }}
[data-testid="stMainBlockContainer"] a[data-testid="stPageLink-NavLink"][href$="Dogrulama_Deneyleri"]:hover {{ background: var(--acc600); border-color: var(--acc600); }}
[data-testid="stColumn"]:has(.hero-right) {{ border-left: 1px solid var(--div); padding-left: 32px; }}
[data-testid="stCaptionContainer"] {{ color: var(--n700); }}
hr {{ border-top: 2px solid var(--div); margin: 14px 0; }}
[data-testid="stMetricLabel"] p {{ font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--n700); }}
[data-testid="stMetricValue"] {{ font-weight: 800; }}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-baseweb="select"] > div {{ background: #ffffff; border-radius: 0; }}
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] {{ font-weight: 700; color: var(--acc700); }}
@media (max-width: 900px) {{
  [data-testid="stMainBlockContainer"] {{ padding: 1rem 1.2rem 2rem; }}
  .m-stats {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
  .m-stats > div:nth-child(2n+1) {{ border-left: 0; padding-left: 0; }}
  .m-index a.row {{ grid-template-columns: 44px minmax(0,1fr); }}
  .m-index a.row .d {{ grid-column: 2; }}
  [data-testid="stColumn"]:has(.hero-right) {{ border-left: 0; padding-left: 0; }}
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


# ---------------------------------------------------------------- bileşenler
def page_header(kicker: str, title_html: str, lede_html: str = "", rule: bool = True):
    """Sayfa başlığı: kicker (vurgu), büyük başlık, lede; altında 2 px çizgi."""
    h = f'<div class="m-head"><div class="m-kicker">{kicker}</div><div class="m-h1">{title_html}</div>'
    if lede_html:
        h += f'<p class="m-lede">{lede_html}</p>'
    h += "</div>"
    if rule:
        h += '<div class="m-rule"></div>'
    st.html(h)


def kicker(text: str, sub: str = "", tone: str = "acc"):
    cls = {"acc": "m-kicker", "ink": "m-kicker ink", "mute": "m-kicker mute"}[tone]
    s = f' <span class="sub">{sub}</span>' if sub else ""
    st.html(f'<div class="{cls}" style="margin:6px 0 10px">{text}{s}</div>')


def rule(thin: bool = False):
    st.html(f'<div class="m-rule{" thin" if thin else ""}"></div>')


def stats(items, big: bool = False, border: bool = True, small: bool = False):
    """items: [(etiket, değer_html, alt_metin, 'acc'|'')]"""
    cells = []
    for it in items:
        label, value, sub = it[0], it[1], (it[2] if len(it) > 2 else "")
        tone = it[3] if len(it) > 3 else ""
        cells.append(
            f'<div><div class="l">{label}</div><div class="v {tone}">{value}</div>'
            + (f'<div class="s">{sub}</div>' if sub else "") + "</div>")
    cls = "m-stats" + (" big" if big else "") + (" sm" if small else "") + ("" if border else " noborder")
    st.html(f'<div class="{cls}" style="--n:{len(items)}">{"".join(cells)}</div>')


def bar_rows(rows, vmax: float = 1.0, slim: bool = False):
    """rows: [dict(name, value, value_str, tone('ink'|'acc'|'mid'), sub, std, sel)]"""
    out = []
    for r in rows:
        v = float(r["value"])
        w = max(0.0, min(100.0, v / vmax * 100.0))
        tone = r.get("tone", "ink")
        fcls = {"ink": "f", "acc": "f acc", "mid": "f mid"}[tone]
        sub = f' <small>{r["sub"]}</small>' if r.get("sub") else ""
        vs = r.get("value_str", tr(v, 3))
        vsub = f' <small>{r["value_sub"]}</small>' if r.get("value_sub") else ""
        whisk = ""
        if r.get("std"):
            s = float(r["std"]) / vmax * 100.0
            whisk = f'<div class="w" style="left:{w - s:.2f}%;width:{2 * s:.2f}%"></div>'
        sel = f'<div class="sel">▲ {r["sel"]}</div>' if r.get("sel") else ""
        ncls = "n" if r.get("bold", True) else ""
        out.append(
            f'<div class="m-bar"><div class="t"><span class="{ncls}">{r["name"]}{sub}</span>'
            f'<span class="n">{vs}{vsub}</span></div>'
            f'<div class="tr"><div class="{fcls}" style="width:{w:.2f}%"></div>{whisk}</div>{sel}</div>')
    st.html(f'<div class="m-bars{" slim" if slim else ""}">{"".join(out)}</div>')


def box(body_html: str, chip: str = "", accent: bool = False, k: str = ""):
    """Mürekkep (veya vurgu) çerçeveli kutu; opsiyonel etiket çipi ya da kicker."""
    head = f'<div class="chip">{chip}</div>' if chip else (f'<div class="k">{k}</div>' if k else "")
    st.html(f'<div class="m-box{" acc" if accent else ""}">{head}{body_html}</div>')


def text(html_: str, mute: bool = False):
    st.html(f'<div class="{"m-mute" if mute else "m-text"}">{html_}</div>')


def index_rows(rows):
    """rows: [(numara, etiket, açıklama, href)] — bağlantılı dizin satırları."""
    out = ['<div class="m-index">']
    for n, l, d, href in rows:
        out.append(f'<a class="row" href="{href}" target="_self"><span class="n">{n}</span>'
                   f'<span class="l">{l}</span><span class="d">{d}</span></a>')
    out.append('<div class="end"></div></div>')
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
    h = [f'<table class="{cls}">']
    if header:
        h.append("<thead><tr>" + "".join(
            f'<th class="{"r" if i in right_cols else ""}">{c}</th>' for i, c in enumerate(header)) + "</tr></thead>")
    h.append("<tbody>")
    for ri, r in enumerate(rows):
        tr_cls = ' class="hi"' if hi_row is not None and ri == hi_row else ""
        h.append(f"<tr{tr_cls}>" + "".join(
            f'<td class="{"r" if i in right_cols else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>")
    h.append("</tbody></table>")
    st.html("".join(h))


def flow(stages):
    """stages: [(başlık, açıklama)] → ok işaretli akış."""
    out = ['<div class="m-flow">']
    for i, (t, d) in enumerate(stages):
        out.append(f'<div class="st"><div class="bx"><div class="t">{t}</div><div class="d">{d}</div></div>'
                   + ('<div class="ar">→</div>' if i < len(stages) - 1 else "") + "</div>")
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
    """Grafikleri tasarım diline çeker: Archivo, saydam zemin, ince nötr ızgara."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, color=INK, size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=44 if (title or fig.layout.title.text) else 16, b=10),
        colorway=[INK, ACC, N600, ACC400, N400],
        title=dict(text=title if title is not None else fig.layout.title.text,
                   font=dict(size=13, family=FONT, color=INK), x=0, xanchor="left"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        hoverlabel=dict(font=dict(family=FONT)),
        **kw,
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(gridcolor=N300, zerolinecolor=DIV, linecolor=DIV, tickfont=dict(size=11),
                     title_font=dict(size=11, color=N700))
    fig.update_yaxes(gridcolor=N300, zerolinecolor=DIV, linecolor=DIV, tickfont=dict(size=11),
                     title_font=dict(size=11, color=N700))
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
