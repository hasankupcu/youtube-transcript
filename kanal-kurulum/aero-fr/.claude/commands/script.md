Konu: $ARGUMENTS

CLAUDE.md'deki rol ve kuralları uygula. Sırayla:
1. KONULAR.md'de bu konuyu bul (yoksa kullanıcının verdiği konuyu kullan). DNA.md, ALTIN_ORNEKLER.md, KONSEPT.md, YASAKLAR.md, YAYIN_GUNLUGU.md dosyalarını oku.
2. Konu veya ana kaynak eksikse en fazla 3 soru sor ve dur.
3. PLAN.md yaz: hook türü (YAYIN_GUNLUGU'ndaki kullanılmışlardan farklı), açılış sahnesi (tarih + yer + nesne), makro loop ve sonda verilecek sayı, 3 mezo loop ve yüzdeleri, akt dilimleri, doruk (%88–94), en az 5 adlandırılmış tarihli kaynak, Fransa/Avrupa köprüsü paragrafı, rakip bölümü (ABD/Çin), risk bloğu 4–5 madde, CTA yüzdeleri, parça planı. Onay bekleme (kullanıcı "onaylı mod" demediyse).
4. SENARYO.md yaz: yalnızca seslendirmeye hazır Fransızca konuşma metni, paragraf arası boş satır, hedef karakter ±%5. Uzunsa parçalara böl; her parçadan önce PLAN.md'yi ve açık loopları yeniden oku.
5. Kalite kapısını CLAUDE.md'den uygula; `python3 -I hap.py olc SENARYO.md` çalıştır ve DNA.md ses ölçüleriyle karşılaştır; sapma varsa düzelt.
6. PROMPTLAR.md §1 ile BASLIK.md (5 başlık) ve ACIKLAMA.md yaz.
7. YAYIN_GUNLUGU.md'ye yeni satır ekle (video no, tarih, damar, hook türü, başlık formülü, makro loop sayısı, karakter sayısı, olc kr/dk alanı boş).
Çıktı: yalnızca dosya yolları ve olc özeti; senaryoyu sohbete yazma.
