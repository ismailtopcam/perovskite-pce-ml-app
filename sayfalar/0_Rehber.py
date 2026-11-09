# -*- coding: utf-8 -*-
"""Kullanım Rehberi — her ekranın ne gösterdiği, nasıl okunacağı; sözlük; sık sorulanlar."""
import streamlit as st

from lib import data, ui
from lib.ui import tr

meta = data.js("app_meta.json")

ui.page_header(
    "Kullanım Rehberi · Uzman olmayan ziyaretçiler için",
    "Her ekran ne gösterir, nasıl okunur?",
    "Model, geçmiş literatürdeki on binlerce perovskit güneş hücresi kaydından verim (PCE) tahmin "
    "etmeyi öğrenir; tezin asıl katkısı bu tahminin <strong>dürüstçe nasıl ölçüleceğini</strong> "
    "göstermektir. Bu sayfa; her ekranın <em>ne gösterdiğini</em>, <em>nasıl okunması gerektiğini</em> ve "
    "<em>tezin hangi bölümüne dayandığını</em> açıklar.",
)

left, right = st.columns([7, 5], gap="medium")

with left:
    ui.list_rows([
        ("—", "Genel Bakış", "",
         "Tezin ana savı ve dört temel sayı; diğer tüm sayfalar bu sayıların nereden geldiğini açar."),
        ("01", "Veri Hattı", "· Bölüm 3.4–3.6, 4.1",
         f"{tr(meta['n_ham'], 0)} ham kaydın {tr(meta['n_temiz'], 0)} temiz kayda dönüşümü. Kayıt gezgininde bir "
         "kayda tıklayın; uygulama o kayda ne yapıldığını tek tek söyler (\"band gap medyanla dolduruldu\", "
         "\"DOI grubu atandı\"…). Elenen kayıtlar sekmesi hattın kimseyi sessizce silmediğinin kanıtıdır: "
         f"{tr(meta['n_elenen'], 0)} kaydın her birinin eleme nedeni yazılıdır. Veri temizliği burada camdan bir kutudur."),
        ("02", "Doğrulama Deneyleri", "· Bölüm 3.13, 4.3",
         "Merkez bulgu: aynı veri ve aynı modelle yalnızca değerlendirme kararları değiştirildiğinde skor "
         "nasıl değişir? Rastgele bölme skoru 0,481'e çıkarır (kardeş-cihaz sızıntısından gelen iyimserlik); "
         "+Voc/Jsc/FF 0,937 yapar (cevabı içeren değişkenlerden kopyalama). Literatürdeki 0,70+ skorlarla "
         "tezin 0,410'u arasındaki farkın büyük bölümü model kalitesi değil, <strong>protokol</strong> farkıdır."),
        ("03", "Model Karşılaştırma", "· Bölüm 3.9, 4.2",
         "Altı algoritma (CatBoost, HistGBM, XGBoost, LightGBM, Random Forest, Ridge) aynı kurallarla yarışır. "
         "İlk dört çubuğun neredeyse eşit olması sayfanın asıl mesajıdır: yarışı algoritma kazandırmaz; "
         "belirleyici olan <strong>veri ve doğrulama tasarımıdır</strong>. CatBoost'un farkı istatistiksel "
         "gürültü düzeyindedir."),
        ("04", "Tahmin Aracı", "· Bölüm 3.12, 4.10",
         "Kendi sanal hücre tarifinizi kurup modelden tahmin alın. Üç şeye birden bakın: tahmini PCE (tek "
         "sayı, tek başına yanıltıcı); %90 aralık (± ~6,7 puan geniştir — bu genişlik modelin değil, literatür "
         "verisindeki gürültünün eseridir); eğitim-uzayına uzaklık uyarısı (tarif modelin hiç görmediği "
         "bölgedeyse uygulama sizi turuncu kutuyla uyarır). SHAP satırları bu tahmini neyin yükseltip "
         "düşürdüğünü gösterir. <strong>Hiçbir çıktı deneysel doğrulama yerine geçmez.</strong>"),
        ("05", "Gerçek – Tahmin", "· Bölüm 4.7",
         f"Modelin eğitimde hiç görmediği {tr(meta['n_holdout'], 0)} kayıtta (holdout) tahminlerle gerçek "
         "ölçümlerin karşılaştırması. En isabetli / tipik / en hatalı kayıtlarla gezin; \"Model nerede "
         "yanılıyor?\" hatanın hangi malzeme bölgelerinde yoğunlaştığını gösterir. Model kanonik FA-Pb-I "
         "bölgesinde güçlü, az örneklenmiş bölgelerde zayıftır — beklenen ve tezde tartışılan örüntü."),
        ("06", "Aday Tarayıcı", "· Bölüm 3.12, 4.5, 4.10",
         "Modelin taradığı 756 hipotetik kompozisyon; her biri tahmin, belirsizlik aralığı, eğitim desteği ve "
         "veri-yoğunluğu bilgisiyle. En yüksek tahmin 17,95 — eğitim maksimumunun (34,8) çok altında. Bu bir "
         "hata değil, ağaç tabanlı modellerin bilinen sınırıdır: liste <strong>bilinen iyi bölgenin yeniden "
         "bulunmasıdır</strong>; deneysel taramayı daraltma aracı olarak okunmalıdır."),
        ("07", "DOI Gezgini", "· Bölüm 3.8, 5.7",
         "Verinin yayın (DOI) düzeyindeki yapısı ve tezin en kritik kuralı: aynı kanonik DOI anahtarını taşıyan "
         "kayıtlar asla eğitim ile testin ikisine birden düşmez. Bir yayın seçin; uygulama eğitimde mi "
         "holdout'ta mı olduğunu rozetle söyler. Grup anahtarının kendisinin nasıl denetlendiği "
         "(44 çift-varyantlı DOI bulgusu dâhil) de burada anlatılır."),
        ("08", "Pipeline & Provenans", "· Bölüm 3.15",
         "Yazılım mühendisliği katmanı: her aşamanın kaydettiği koşu-manifestleri (hangi seed, hangi paket "
         "sürümleri, hangi metrikler), akış diyagramı ve bağımsız denetim özetleri. \"Bu sayılar tekrar "
         "üretilebilir mi?\" sorusunun cevabı: manifestlerin tamamı aynı ortamı gösterir ve uygulamadaki her "
         "veri dosyası pipeline'dan deterministik olarak türetilir."),
        ("09", "Sayıların Evrimi", "· Bölüm 3.15, 5.7, 5.8",
         "ICRAS 2026 bildirisindeki sayıların (ham DOI anahtarlı v0.3.x) tezdeki sayılarla (kanonik DOI anahtarlı "
         "v0.4.0) karşılaştırması. 44 DOI yazım varyantının birleştirilmesi kat sınırını aşan kayıtları sıfırladı; "
         "CV R² 0,413'ten 0,410'a indi. Farklar katlar arası standart sapmanın altında kalır ve nitel sonuçları "
         "değiştirmez."),
    ], numbered=True)

    with ui.card():
        ui.kicker("Sık sorulanlar", tone="ink")
        ui.text(
            "<p><strong>R² = 0,410 düşük değil mi?</strong> Tek başına bakıldığında mütevazı görünür; ama bu değer "
            "eğitimden kanonik DOI anahtarı düzeyinde ayrık tutulan yayınlara genellemeyi ölçer ve tez, literatür "
            "verisindeki reçete-içi gürültünün ulaşılabilir tavanı ~0,52'ye sınırladığını gösterir (Bölüm 5.1). "
            "0,410 \"kötü bir model\" değil; dürüst ölçülmüş, tavana yakın bir modeldir. Daha yüksek görünen "
            "skorların nasıl üretildiğini 02'de kendiniz deneyebilirsiniz.</p>"
            "<p><strong>Tahmin Aracı'ndaki sonuca ne kadar güvenebilirim?</strong> Üç göstergeyi birlikte okuyun: "
            "aralık genişliği, eğitim-uzayına uzaklık uyarısı ve SHAP açıklaması. Sonuç bir "
            "<strong>önceliklendirme</strong> çıktısıdır: hangi tarifin denenmeye değer olduğuna dair veri-destekli "
            "bir işaret; laboratuvar doğrulamasının yerine geçmez.</p>"
            "<p><strong>Sayılar tezle birebir aynı mı?</strong> Evet. Uygulamanın tüm veri dosyaları tezin kod "
            "deposundan (<span class='m-mono'>perovskite-pce-ml-thesis</span>) deterministik olarak üretilir; üretim "
            "betiği bölmeleri yeniden kurup bilinen değerlerle doğrular, uyuşmazlıkta durur. 08 Provenans hangi "
            "commit'ten üretildiğini gösterir.</p>"
        )

with right:
    ui.kicker("Küçük sözlük", tone="ink")
    ui.list_rows([
        ("PCE", "Güç dönüşüm verimi: hücrenin ışığı elektriğe çevirme yüzdesi."),
        ("R²", "Modelin, verimdeki farklılıkların ne kadarını açıkladığı (1 = mükemmel, 0 = ortalamayı "
               "söylemekten farksız). 0,410 ≈ farklılıkların %41'i."),
        ("MAE / RMSE", "Ortalama tahmin hatası (PCE puanı); RMSE büyük hataları daha çok cezalandırır."),
        ("Holdout", "Eğitime alınmayan, yalnızca sınavda kullanılan kayıtlar (%20); ayrım kanonik DOI "
                    "anahtarı düzeyinde."),
        ("Veri sızıntısı", "Cevabın bir kopyasının soruya karışması; skoru gerçek dışı şişirir."),
        ("DOI-grup bölme", "Aynı kanonik DOI anahtarını taşıyan tüm kayıtları aynı tarafta (ya eğitim ya "
                           "test) tutan bölme; kardeş-cihaz sızıntısını büyük ölçüde azaltır."),
        ("Conformal aralık", "Tekrarlı kullanımda gerçek değeri nominal %90 sıklıkla kapsamayı hedefleyen, "
                             "dağılım-varsayımsız yöntem; tek tahmine olasılık garantisi vermez. Tezde "
                             "DOI-grup-güvenli kalibre edilmiştir."),
        ("SHAP", "Bir tahmini, özelliklerin katkılarına adilce bölüştüren açıklanabilirlik yöntemi "
                 "(nedensellik değil, ilişki)."),
        ("Eğitim-uzayına uzaklık", "Tarifin, modelin gördüğü veriye benzerliği; güven skoru değil, yoğunluk "
                                   "bilgisi."),
        ("Koşu-manifesti", "Her aşamanın seed + paket sürümü + metrik kaydı; tekrar üretilebilirliğin makbuzu."),
    ])

ui.footer()
