# PROMPTLAR.md — yardımcı promptlar (§10.3). Her biri KONSEPT.md'yi üst blok alır.

## 1. Başlık + açıklama (BASLIK.md, ACIKLAMA.md)
Girdi: SENARYO.md. Çıktı 1 (BASLIK.md): 5 başlık, KONSEPT Paket Kartı kurallarıyla: 50–65 karakter, rakam yalnızca nesne adında, "vous" yok, soru işareti yok, yıkıcı fiil serbest, formül art arda tekrar etmez (YAYIN_GUNLUGU), ilk 45 karakter tek başına anlamlı; 2'si tireli iki parça, 3'ü tiresiz (A/B). Çıktı 2 (ACIKLAMA.md): 2 paragraf özet (hook'un vaadi, ne öğrenilecek, "le chiffre à la fin" ima), bölümler (zaman kodlu, 8–9 başlık), SOURCES listesi (senaryodaki her adlandırılmış kaynak, tarih ve yayın organı), görüntü kredileri satırı, tam 10 hashtag.

## 2. Sahne promptları (SRT → Flow)
Üst blok: KONSEPT görsel dil + karakter bloğu. Tempo: 0–30 sn her 3–4 sn, 30–60 sn her 5 sn, sonrası her 6–7 sn. Her sahne: fotogerçekçi, desatüre yüksek kontrast, hangar/gece ışığı, lacivert-çelik-turuncu; uçak dörtte üç profil alçak açı; **her uçak için tip adı + referans tarifi zorunlu** (ör. "B-21 Raider: aile B-2'ye benzer uçan kanat, daha küçük, iki motor girişi gömülü, açık gri alt yüzey"); tarih-konum damgası sol üst, kaynak atfı sağ alt. Yasak: talking-head, neon, meme font, bayrak patlaması, metin dolu ekran. Henri yalnızca sabit sahnelerde (masa, hangar kapısı), yüz konuşmaz.

## 3. Kapak (1 ana + 2 varyant)
Üst blok: KONSEPT Paket Kartı. Ana: makine dörtte üç profil sağ %60 + Henri yüzü sol alt omuz üstü şüpheci + 2–4 kelime beyaz/turuncu siyah kontur sol üst (mesaj: uyarı/kayıp/karşıtlık). A: yüz yok, iki makine (ABD + Çin/Avrupa) ikincisi kırmızı kontur. B: aynı düzen, yazı turuncu→sarı. Mobil 168 px ve TV okunurluk kontrolü; `hap.py poster bizim.jpg rakip1.jpg ...` kolajı yayın öncesi (Haskan'ın Mac'inde).

## 4. TTS formatlayıcı
SENARYO.md'yi al; cümle başına tek fikir; 17+ kelimelik cümleleri böl; sayıları harfle (uçak adları hariç, motor testine göre); kısaltmaları aç; parantez/yıldız/emoji temizle; paragraf arası boş satır; başka hiçbir şey ekleme.
