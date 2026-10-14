# DNA.md — Senaryo DNA'sı (F2'den; v1.0-FR, 2026-10-14)

## İskelet
"Soğuk açılış → sonda ödül → kanıt merdiveni → risk bloğu → ödeme → soru"

| Akt | % | İçerik |
|---|---|---|
| 1 Hook + makro loop | 0–4 | Tarih + yer + tek somut nesne (3 cümle) → herkesin sorusu → "yanlış soru" dönüşü → asıl soru + "un chiffre, à la fin" |
| 2 Kimlik + vaat + CTA | 4–9 | 1 paragraf Henri; "confirmé / rumeur / ce que tout le monde oublie"; abonelik: iki tür izleyici |
| 3 Kanıt merdiveni | 9–60 | Part 1–N: köprü ("Regardons le chiffre") → 2–4 kanıt paragrafı (kaynak + sayı + tarih) → tek cümle sonuç |
| 4 Rakip bölümü | 60–72 | "Et c'est là que la Chine entre dans l'histoire." İddia / kanıt / benim okumam |
| 5 Risk bloğu | 72–86 | "Maintenant, la partie que les autres ne montrent pas." Problème numéro un…cinq |
| 6 Köprü + hatırlatma | 84–90 | Son videoya gönderme (4. videodan itibaren); "retenez ce chiffre" |
| 7 Ödeme | 88–94 | "Je vous ai promis un chiffre. Le voici." + anlamı |
| 8 Soru + imza | 94–100 | A ou B, dites-le-moi; abonelik; "Un avion ne ment pas. Il vole, ou il ne vole pas." |

## Yapı Genomu motifleri (hitlerde tekrar)
1. `H L V P C` açılış bloğu ilk %9.
2. `L E E (E) K` kanıt basamağı, 3–8 kez.
3. `U U U U (U)` risk bloğu %72–88; 5'ten fazla U flop işareti (States Nuclear: 10 U).
4. `C R K C C P` kapanış.
5. Yasak: `B B B B` (4 ardışık bağlam) — yalnızca floplarda.
Kanıt payı (E) ≥ %40 paragraf; flop %21–30.

## Yapı Kalıbı (slot)
[tarih + yer + tek somut nesne, 3 cümle] → [herkesin sorduğu soru] → [mühendisin "yanlış soru" dönüşü] → [asıl soru + sonda açıklanacak sayı] → [1 paragraf kimlik] → [kanıtlı / söylenti / herkesin kaçırdığı] → [abonelik: iki tür izleyici, seçin] → N × ([köprü] → [adlandırılmış kaynak + sayı + tarih] × 2–4 → [tek cümle sonuç]) → [rakip: iddia / kanıt / okuma] → [risk bloğu 4–5 numaralı problem] → [son videoya köprü] → [hatırlatma] → [sayı + anlamı] → [tek soru, iki şık] → [imza]

## Hook türleri (hit dağılımı: sahne 4, kural kırma 3, gizli sebep 3, soru 0)
Sahne · Kural kırma · Sonuç önce · Çelişki (brochure/soufflerie). Soru hook yok, nostalji hook yok (flop). İlk 100 kelimede ≥ 10 özgül öğe.

## Ses DNA'sı (hedef) ve referans
| Ölçü | Hedef | Rakip hit bandı | Referans §2.2 |
|---|---|---|---|
| Karakter/dk | 850 (FR TTS, ölçülecek) | States 831–842; Mach Line ~1.000 (çok hızlı); Un Ciel EN dublaj parçası 926–1.036 (FR ölçülemedi) | 740–1.052 |
| Kelime/dk | 140–160 | 150–159 / 188–194 | 123–195 |
| Cümle medyanı | 10–12 kelime | 10–15 (Un Ciel 18–20, "trop long" şikâyeti) | — |
| ≤8 / 9–16 / 17+ % | 35–40 / 40–45 / ≤20 | 25–39 / 33–54 / 14–42 | — |
| Soru oranı | ≤ %3 | hit 0–5, flop 3–6 | 0–6, medyan 1 |
| Hitap/100k | 1–2 | 0,75–2,16 | 0,5–4,7 |
| Birinci şahıs/100k | 0,8–1,2 | Mach Line 0,7–1,05; States 0 | — |
| Somutluk/100k | ≥ 8 | hit 2,8–9,1 (Mach Line 8–9) | — |
| Somutluk son %20 / ilk %20 | ≥ 0,8 | hit 0,8–1,1; flop 0,3–0,7 | — |

## Süre Eşleme
Rakip medyan 23,6 dk (States), 26 dk (Mach Line). Ses hızı 850 kr/dk (tahmini) → format süresi ≈ 20.000 karakter. **Mevcut HEDEF_KARAKTER 12.000 ≈ 14 dk = %60 → Süre açığı.** Haskan ilk 3 videoda kendi sesini ölçer (`hap.py olc` + süre), SES_HIZI ve HEDEF_KARAKTER güncellenir.

## Hit–flop farkı (kurallara dönüşen)
- Başlıkta tek somut yeni makine + rakip; genel kategori ve yerel altyapı yok (Paket).
- İlk 15 sn tarih/yer/nesne; soru hook yok (Senaryo).
- Kanıt payı ≥ %40; 4 ardışık B yok; U 4–5 (Senaryo).
- Sonda ödül zorunlu; en güçlü kanıt sona (Senaryo).
- İlk CTA %4–9, orta video CTA yok (Senaryo).
- Son beşte bir somutluğu ≥ %80 (Senaryo).
- Ayırmayan (kural yok): hız, cümle uzunluğu, hype cümlesi sayısı, süre.

## FR doğrudan rakip (Un Ciel, Mille Histoires) ölçümleri
3 transkript (EN dublaj parçası): cümle medyanı 18–20 kelime, 17+ kelime %55–72; soru %1–3; hitap 0,17–0,28; birinci şahıs 0 (persona yok); açılış özgüllük 12–13 (tarihli sahne, iyi); somutluk son %20 çöküyor (10,4→4,4; 7,3→1,7); başlık iddiası 6–14 cümlede tekrar; ilk CTA %18–20 veya yok; sonda ödül yok; kapanış ikili soru. Kural çıkarımı: kısa cümle, tekrar ≤ 3, persona, sonda sayı, erken CTA, sonda kanıt yoğunluğu.

## Öğrenilmiş kurallar
(başta boş — §11.2 retention geri beslemesiyle dolar)
