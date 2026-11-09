# Perovskit PCE ML — Etkileşimli Tez Uygulaması

**"Perovskit Güneş Hücrelerinde Makine Öğrenmesi Tabanlı PCE Tahmini ve Yüksek Verim
Potansiyelli Aday Kompozisyonların Belirlenmesi"** yüksek lisans tezinin
(İzmir Kâtip Çelebi Üniversitesi, Yazılım Mühendisliği) veri hattını, doğrulama
deneylerini ve bulgularını etkileşimli sunan Streamlit uygulaması.

Ana pipeline deposu: <https://github.com/ismailtopcam/perovskite-pce-ml-thesis>

## Sayfalar

| # | Sayfa | İçerik |
|---|---|---|
| — | Genel Bakış | Tezin savı, dört temel sayı, sayfa dizini, provenans |
| R | Rehber | Her ekranın açıklaması, küçük sözlük, SSS (uzman olmayan ziyaretçiler için) |
| 01 | Veri Hattı | Ham→temiz dönüşüm, eleme nedenleri, **kayıt-düzeyi açıklama** ("bu kayıt neden elendi / hangi işlemler uygulandı") |
| 02 | Doğrulama | Merkez ekran: bölme yöntemi ve özellik kümesi seçiminin R²'ye etkisi (0,261 ↔ 0,937) |
| 03 | Modeller | 6 modelin DOI-grup CV / holdout başarımları |
| 04 | Tahmin Aracı | Sanal cihaz tarifi → PCE + conformal %90 aralık + eğitim-uzayına uzaklık + **yerel SHAP** |
| 05 | Gerçek – Tahmin | 8.355 holdout kaydında hata analizi; segment bazlı "model nerede yanılıyor" |
| 06 | Aday Tarayıcı | 756 adayın aralıklı, eğitim-destekli ve dürüst-uyarılı keşfi |
| 07 | DOI Gezgini | Yayın-düzeyi izlenebilirlik; grup-güvenli bölmenin somut görünümü |
| 08 | Provenans | Koşu-manifestleri, sürüm/seed kaydı, bağımsız denetim özetleri, model ve veri kimliği |

Sayfa dosya adları ve URL'ler (`/Veri_Hatti`, `/Dogrulama_Deneyleri`, …) değişmez; rayda görünen
başlıklar `streamlit_app.py` içinde tanımlanır.

## Tasarım

Arayüz, Claude Design'da hazırlanan **"Kafes"** tasarım dilini uygular (kanvas: "Tez Uygulaması
Yeniden Tasarım", 2026-11): lacivert sol ray (ABX₃ kafes logosu + İKÇÜ kimliği → dört bölümlü numaralı
sayfa listesi → tez sahibi/provenans bloğu), serin zemin `#F4F5F7` üzerinde beyaz kartlar, mürekkep
`#0E1A2B`. Renklerin anlamı her ekranda aynıdır: **mavi `#1F4FD1` = dürüst ölçüm / eğitimde destekli**,
**turuncu `#D9530F` (metin `#B84308`) = sızıntı / iyimser skor / uyarı**. Başlıklar Space Grotesk,
metin Inter, sayılar JetBrains Mono.

- Tema jetonları: `.streamlit/config.toml` (`[theme]`, `[theme.sidebar]`, `[[theme.fontFaces]]`).
- Bileşen CSS'i ve HTML yardımcıları (`page_header`, `card`, `stats`, `bar_rows`, `box`, `table`,
  `flow`, `chart` …): `lib/ui.py`. Her sayfa `ui.page_header(...)` ile başlar, `ui.footer()` ile biter;
  kart içine alınacak bölümler `with ui.card():` ile sarılır. `bar_rows` tonları: `blue` (dürüst),
  `acc` / `soft` (sızıntı), `ink`, `mid`, `blue2`; `stats` ve `box` için `blue` / `acc` tonları.
- Raydaki sayfa numaraları URL yoluna göre CSS ile eklenir (`lib/ui.py` → `_NAV_NUM`); yeni sayfa
  eklenirse oraya da yazılmalıdır.
- Yazı tipleri uygulamayla birlikte sunulur, dış istek yapılmaz: `static/fonts/` (Inter, Space Grotesk,
  JetBrains Mono — Fontsource 5.3.0 değişken sürümleri, latin + latin-ext; üçü de SIL OFL 1.1, lisans
  dosyaları aynı klasörde). Logo: `static/logo-kafes.svg` (`st.html` satır içi SVG'yi temizlediği için
  dosyadan yüklenir). `server.enableStaticServing = true` gerektirir.
- Etkileşimli parçalar (segmentli seçim, sayı girişleri, tablolar, Plotly grafikleri) Streamlit
  bileşenleridir; `lib/ui.py` içindeki CSS onları aynı dile çeker.

## Yerel çalıştırma

```bash
python -m venv .venv && .venv\Scripts\activate   # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Uygulama `data_app/` altındaki **önceden üretilmiş** kompakt dosyalarla çalışır
(bu depoya dâhildir); ham 83 MB'lık Perovskite Database CSV'sine ihtiyaç duymaz.

## Docker ile dağıtım (kendi sunucunuz)

```bash
docker build -t perovskite-pce-app .
docker run -d --name pce-app -p 8501:8501 --restart unless-stopped perovskite-pce-app
# -> http://SUNUCU:8501  (ters proxy arkasına alacaksaniz 8501'i localhost'a bağlayın)
```

Ters proxy (nginx) örneği: `location / { proxy_pass http://127.0.0.1:8501; }` +
WebSocket başlıkları (`proxy_set_header Upgrade $http_upgrade; Connection "upgrade";`).

## Veriyi yeniden üretme

`data_app/` içeriği, pipeline reposundan deterministik olarak üretilir:

```bash
python tools/prepare_app_data.py ../perovskite-pce-ml
```

Betik; bölmeleri (seed 42 holdout, 5-kat GroupKFold, conformal kalibrasyon) pipeline
ile birebir yeniden kurar ve bilinen değerlerle **assert** eder; hizasızlık durumunda
üretim durur. Pipeline'da yeni bir koşu yapıldığında bu betiği yeniden çalıştırmak yeterlidir.

## Bilimsel çerçeve ve sınırlar

- Uygulama çıktıları **deneysel doğrulama yerine geçmez**; model tabanlı
  önceliklendirme amacı taşır (tez Bölüm 5.4).
- %90 aralıklar DOI-grup-güvenli conformal kalibrasyondandır (Bölüm 4.10); elle girilen
  tarifler için kesin garanti değil, veriye dayalı belirsizlik göstergesidir.
- "Eğitim-uzayına uzaklık" bir güven skoru değildir: tez, bu mesafenin holdout hatasını
  ayırt etmediğini göstermiştir (Bölüm 4.10); sütun, veri yoğunluğu bilgisi olarak sunulur.

## Veri kaynağı ve atıf

Veri: **Perovskite Database** (Jacobsson vd., 2022, *Nature Energy*,
DOI: 10.1038/s41560-021-00941-3) — CC BY 4.0. Uygulamadaki tüm türetilmiş sayılar,
tezde raporlanan 43.398 kayıtlık anlık görüntüden üretilmiştir.

> **Not:** Kayıt-düzeyi ham alanların (Sayfa 1 ve 7) herkese açık sunumu, kaynak
> veri tabanının CC BY lisansı kapsamında atıf gerektirir. Bu atıf tüm sayfa
> altbilgilerinde ve /hakkinda sayfasında yer almaktadır; gelecekteki düzenlemelerde
> korunmalıdır.
