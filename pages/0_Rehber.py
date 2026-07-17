# -*- coding: utf-8 -*-
import streamlit as st

from lib.ui import page

page("Kullanım Rehberi", "📖")

st.markdown(
    """
Bu sayfa; her ekranın *ne gösterdiğini*, *nasıl okunması gerektiğini* ve
*tezin hangi bölümüne dayandığını* açıklar.

Model, geçmiş literatürdeki on binlerce perovskit güneş hücresi kaydından verim
(PCE) tahmin etmeyi öğrenir; tezin asıl katkısı ise bu tahminin **dürüstçe nasıl
ölçüleceğini** göstermektir.
"""
)

st.divider()
st.subheader("🗺️ Sayfa sayfa rehber")

REHBER = [
    ("🏠 Ana Sayfa", """
**Ne gösterir?** Tezin ana savı, başlık sonuçlar (41.485 kayıt, R² = 0,413) ve
uygulamanın haritası.

**Nasıl okunur?** Buradaki dört kutu tezin dört temel sayısıdır; diğer tüm
sayfalar bu sayıların nereden geldiğini açar.
"""),
    ("1️⃣ Veri Hattı — *tez Bölüm 3.4–3.6, 4.1*", """
**Ne gösterir?** 43.398 ham kaydın 41.485 temiz kayda nasıl dönüştüğünü:
hangi kayıtlar neden elendi, hangi eksik değerler nasıl dolduruldu, veri neye
benziyor.

**Nasıl okunur?** "Kayıt gezgini" sekmesinde herhangi bir kayda tıklayın —
uygulama o kayda ne yapıldığını tek tek söyler ("band gap medyanla dolduruldu",
"DOI grubu atandı"...). "Elenen kayıtlar" sekmesi ise hattın kimseyi sessizce
silmediğinin kanıtıdır: 1.913 kaydın her birinin eleme nedeni yazılıdır.

**Neden önemli?** Veri temizliği çoğu çalışmada kara kutudur; burada camdan bir
kutudur.
"""),
    ("2️⃣ Doğrulama Deneyleri — *tez Bölüm 3.13, 4.3* ⭐", """
**Ne gösterir?** Tezin merkez bulgusunu: aynı veri ve aynı modelle, yalnızca
**değerlendirme kararları** değiştirildiğinde skorun nasıl değiştiğini.

**Nasıl okunur?** Üstteki iki seçimi değiştirin ve R²'yi izleyin:
- *Rastgele bölme* seçince skor 0,481'e çıkar — ama bu bir ilerleme değil,
  aynı yayının kardeş cihazlarının teste sızmasından kaynaklanan **yapay şişme**dir.
- *+Voc, Jsc, FF* seçince skor 0,938 olur — model artık tahmin değil,
  cevabı içeren değişkenlerden **kopyalama** yapmaktadır.

**Neden önemli?** Literatürdeki 0,70+ skorlarla tezin 0,413'ü arasındaki farkın
büyük bölümü model kalitesi değil, **protokol** farkıdır.
"""),
    ("3️⃣ Model Karşılaştırma — *tez Bölüm 3.9, 4.2*", """
**Ne gösterir?** Altı algoritmanın (CatBoost, HistGBM, XGBoost, LightGBM,
Random Forest, Ridge) aynı kurallarla yarıştırılmasını.

**Nasıl okunur?** İlk dört çubuğun neredeyse eşit olması sayfanın asıl mesajıdır:
kazanan algoritma değil, **veri ve doğrulama tasarımıdır**. CatBoost'un farkı
istatistiksel gürültü düzeyindedir.
"""),
    ("4️⃣ Tahmin Aracı — *tez Bölüm 3.12, 4.10*", """
**Ne gösterir?** Kendi sanal hücre tarifinizi kurup modelden tahmin almanızı
sağlar.

**Nasıl okunur?** Üç şeye birden bakın:
1. **Tahmini PCE** — tek sayı, ama tek başına yanıltıcıdır;
2. **%90 aralık** — modelin dürüst belirsizliği (± ~6,4 puan geniştir; bu
   genişlik modelin değil, literatür verisindeki gürültünün eseridir);
3. **Eğitim-uzayına uzaklık** — tarifiniz modelin hiç görmediği bölgedeyse
   uygulama sizi kırmızı kutuyla uyarır.

Alttaki SHAP grafiği, *bu* tahmini hangi özelliklerin yükseltip düşürdüğünü
gösterir. **Hiçbir çıktı deneysel doğrulama yerine geçmez.**
"""),
    ("5️⃣ Gerçek vs Tahmin — *tez Bölüm 4.7*", """
**Ne gösterir?** Modelin eğitimde hiç görmediği 8.147 kayıtta (holdout)
tahminlerle gerçek ölçümlerin karşılaştırmasını.

**Nasıl okunur?** "En isabetli / tipik / en hatalı" sekmeleriyle gezin;
"Model nerede yanılıyor?" sekmesi hatanın hangi malzeme bölgelerinde
yoğunlaştığını gösterir (Sn'li hücreler, geniş band gap...). Model kanonik
FA-Pb-I bölgesinde güçlü, az örneklenmiş bölgelerde zayıftır — beklenen ve
tezde tartışılan bir örüntü.
"""),
    ("6️⃣ Aday Tarayıcı — *tez Bölüm 3.12, 4.5, 4.10*", """
**Ne gösterir?** Modelin taradığı 756 hipotetik kompozisyonu; her biri tahmin,
belirsizlik aralığı, eğitim-desteği ve veri-yoğunluğu bilgisiyle.

**Nasıl okunur?** En yüksek tahmin 17,78'dir ve eğitim maksimumunun (34,8)
çok altındadır — bu bir hata değil, ağaç tabanlı modellerin bilinen sınırıdır:
liste **yeni keşif değil, bilinen iyi bölgenin yeniden bulunmasıdır** ve
deneysel taramayı daraltma aracı olarak okunmalıdır.
"""),
    ("7️⃣ DOI Gezgini — *tez Bölüm 3.8, 5.7*", """
**Ne gösterir?** Verinin yayın (DOI) düzeyindeki yapısını ve tezin en kritik
kuralını: aynı DOI anahtarına sahip kayıtlar asla eğitim ile testin ikisine
birden düşmez (ayrım ham anahtar düzeyindedir; tez Bölüm 5.7 bu anahtarın
kendisini de denetler).

**Nasıl okunur?** Bir yayın seçin — uygulama o yayının eğitimde mi holdout'ta
mı olduğunu rozetle söyler. Alttaki genişletilebilir bölümde grup anahtarının
kendisinin nasıl denetlendiği (44 çift-varyantlı DOI bulgusu dahil) anlatılır.
"""),
    ("8️⃣ Pipeline & Provenans — *tez Bölüm 3.15*", """
**Ne gösterir?** Yazılım mühendisliği katmanını: her aşamanın kaydettiği
koşu-manifestleri (hangi seed, hangi paket sürümleri, hangi metrikler),
akış diyagramı ve bağımsız denetim özetleri.

**Nasıl okunur?** Bu sayfa "bu sayılar tekrar üretilebilir mi?" sorusunun
cevabıdır: 14 manifestin tamamı aynı ortamı gösterir ve uygulamadaki her veri
dosyası pipeline'dan deterministik olarak türetilir.
"""),
]

for baslik, metin in REHBER:
    with st.expander(baslik):
        st.markdown(metin)

st.divider()
st.subheader("📚 Küçük sözlük")
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        """
- **PCE** — güç dönüşüm verimi: hücrenin ışığı elektriğe çevirme yüzdesi.
- **R²** — modelin, verimdeki farklılıkların ne kadarını açıkladığı (1 = mükemmel,
  0 = ortalamayı söylemekten farksız). 0,413 = farklılıkların ~%41'i.
- **MAE / RMSE** — ortalama tahmin hatası (PCE puanı cinsinden); RMSE büyük
  hataları daha çok cezalandırır.
- **Holdout** — eğitime alınmayan, yalnızca sınavda kullanılan kayıtlar (%20);
  ayrım ham DOI anahtarı düzeyinde yapılır.
- **Veri sızıntısı** — cevabın bir kopyasının soruya karışması; skoru gerçek
  dışı şişirir.
"""
    )
with c2:
    st.markdown(
        """
- **DOI-grup bölme** — aynı yayının tüm kayıtlarını aynı tarafta (ya eğitim ya
  test) tutan bölme; kardeş-cihaz sızıntısını engeller.
- **Conformal aralık** — tekrarlı kullanımda aralıkların gerçek değeri **nominal
  %90 sıklıkla** kapsamasını hedefleyen, dağılım-varsayımsız yöntem; tek bir
  tahmine "%90 olasılık" garantisi vermez. Tezde DOI-grup-güvenli kalibre edilmiştir.
- **SHAP** — bir tahmini, özelliklerin katkılarına adilce bölüştüren
  açıklanabilirlik yöntemi (nedensellik değil, ilişki gösterir).
- **Eğitim-uzayına uzaklık** — tarifin, modelin gördüğü veriye ne kadar
  benzediği; güven skoru değil, yoğunluk bilgisidir.
- **Koşu-manifesti** — her aşamanın seed + paket sürümü + metrik kaydı;
  tekrar üretilebilirliğin makbuzu.
"""
    )

st.divider()
st.subheader("❓ Sık sorulanlar")
with st.expander("R² = 0,413 düşük değil mi?"):
    st.markdown(
        "Tek başına bakıldığında mütevazı görünür; ama bu değer **eğitimden ham DOI "
        "anahtarı düzeyinde ayrık tutulan yayınlara genellemeyi** ölçer ve tez, literatür verisindeki reçete-içi "
        "gürültünün ulaşılabilir tavanı ~0,52'ye sınırladığını gösterir (Bölüm 5.1). "
        "Yani 0,413, 'kötü bir model' değil; 'dürüst ölçülmüş, tavana yakın bir "
        "model'dir. Daha yüksek görünen skorların nasıl üretildiğini 2. sayfada "
        "kendiniz deneyebilirsiniz."
    )
with st.expander("Tahmin Aracı'ndaki sonuca ne kadar güvenebilirim?"):
    st.markdown(
        "Üç göstergeyi birlikte okuyun: aralık genişliği, eğitim-uzayına uzaklık "
        "uyarısı ve SHAP açıklaması. Sonuç bir **önceliklendirme** çıktısıdır: "
        "hangi tarifin denenmeye değer olduğuna dair veri-destekli bir işaret; "
        "laboratuvar doğrulamasının yerine geçmez."
    )
with st.expander("Bu uygulamadaki sayılar tezle birebir aynı mı?"):
    st.markdown(
        "Evet. Uygulamanın tüm veri dosyaları, tezin kod deposundan "
        "(`perovskite-pce-ml-thesis`) deterministik olarak üretilir; üretim betiği "
        "bölmeleri yeniden kurup bilinen değerlerle doğrular, uyuşmazlıkta durur. "
        "Pipeline & Provenans sayfası hangi commit'ten üretildiğini gösterir."
    )
