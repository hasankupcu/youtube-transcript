# Kurulum notu
1. Bu klasörü Claude Code'da proje kökü olarak aç (`cd kanal-kurulum/aero-fr && claude`). `CLAUDE.md` master prompt; bilgi dosyaları: DNA.md, ALTIN_ORNEKLER.md, KONSEPT.md, YASAKLAR.md, YAYIN_GUNLUGU.md, KONULAR.md.
2. Komutlar: `/script <konu>` (PLAN.md → SENARYO.md → BASLIK.md, ACIKLAMA.md, günlük satırı) · `/paket` (başlık, açıklama, kapak promptları) · `/sahne <srt>` (Flow sahne promptları + csv) · `/kontrol` (yayın öncesi denetim, hap.py olc dahil).
3. İlk 3 videodan sonra kendi ses hızını ölç (`python3 -I hap.py olc SENARYO.md` + süre) ve CLAUDE.md'de "Hedef uzunluk" satırını güncelle (12.000 vs 20.000 kararı). 4/8/12/15. videoda KANAL_DOSYASI.md §F5 KPI kapıları.
Tam analiz: KANAL_DOSYASI.md (F0–F5 + Pivot).
