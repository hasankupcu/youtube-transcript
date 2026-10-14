# Gunluk Otomatik Video Zinciri

Cok dilli faceless kanallar icin: konu -> script (Claude) -> seslendirme (ElevenLabs / Fish Audio)
-> sahne gorselleri (Pexels) -> montaj (FFmpeg, Ken Burns) -> kapak (Pillow)
-> YouTube'a private yukleme + `publishAt` ile zamanlama.

Zincir "onay kapili" calisir: video uretilir, Telegram'a kapak ve baslik gelir, sen tek komutla
yuklersin. `auto` modu onayi atlar. Tam otomatik yayin, YouTube'un seri uretim (inauthentic content)
politikasi ve CTR kaybi yuzunden tavsiye edilmez.

## 1. Kurulum

```bash
cd youtube-transcript
python -m venv .venv && source .venv/bin/activate
pip install -r pipeline/requirements.txt
sudo apt install ffmpeg          # ffmpeg ve ffprobe PATH'te olmali
cp pipeline/.env.example pipeline/.env   # anahtarlari doldur
```

`pipeline/channels.yaml` icinde her kanal icin `voice_id`, `publish_hour_utc` ve `tts_provider` ayarla.
`pipeline/assets/music/calm.mp3` koyarsan alcak sesle altta calar, yoksa muziksiz uretir.

## 2. YouTube yetkisi (kanal basina bir kez)

1. Google Cloud Console'da proje ac, **YouTube Data API v3** etkinlestir.
2. OAuth istemci olustur (tur: Masaustu), JSON'u `pipeline/secrets/client_secret.json` olarak kaydet.
3. OAuth onay ekranina kendi Google hesabini test kullanicisi olarak ekle.
4. Her kanal icin: `python -m pipeline.auth_youtube fr` -> tarayici acilir, kanali sec.

Onemli: Google uygulaman YouTube API uyumluluk denetiminden gecene kadar API ile yuklenen videolar
**private'ta kilitli kalir**, `publishAt` calismaz. Denetim basvurusunu ilk gun yap. Denetim bitene
kadar videoyu API ile yukle, yayin saatini YouTube Studio'dan elle ver.

Kota: gunde 10.000 birim, bir yukleme 1.600 birim. Kanal basina ayri Cloud projesi ac.

## 3. Calistirma

```bash
# Kuyruga konu ekle: pipeline/queue.csv (id, channel, topic, angle, status=pending)
python -m pipeline.run_daily render --channel fr    # uret, Telegram'a onaya gonder
python -m pipeline.run_daily upload --job 1         # onayladiysan yukle + zamanla
python -m pipeline.run_daily auto --all             # onay kapisiz, butun kanallar
```

Her is `pipeline/output/job_<id>/` altinda. Bir adim bittiyse tekrar calistirmada atlanir;
scripti begenmediysen `script.json` sil ve tekrar calistir.

## 4. Gunluk tetikleme

Uc secenek, en guvenilirden en kolaya:

1. **Kendi VPS'in + cron.** `pipeline/crontab.example` dosyasina bak. En saglam yol, cunku FFmpeg
   ve tokenlar kalici diskte durur.
2. **Claude Code Routine (bulut).** Claude Code web'de bu depo icin bir ortam ac, `.env`
   degerlerini ortam sirlari olarak gir, FFmpeg'i kurulum betigine ekle. Sonra gunluk bir Routine
   olustur: "`python -m pipeline.run_daily render --all` calistir, ciktiyi ozetle". Tokenlar ve
   output klasoru her oturumda sifirlanir; bu yuzden tokenlari sir olarak, ciktiyi da yukleme
   bittikten sonra silinebilir kabul ederek kullan.
3. **GitHub Actions.** Gunluk `schedule` ile calisan bir workflow. Sirlari repo secrets'a koy.
   6 saat limiti ve ffmpeg kurulumu var, kucuk hacimler icin yeterli.

## 5. Dosyalar

| Dosya | Is |
|---|---|
| `run_daily.py` | Orkestrator, onay kapisi, hata yakalama |
| `steps/script.py` | Claude ile sahnelere bolunmus script, JSON semasi zorunlu |
| `steps/tts.py` | ElevenLabs ve Fish Audio |
| `steps/visuals.py` | Pexels gorselleri, AI gorsel icin degistirilecek tek fonksiyon |
| `steps/assemble.py` | FFmpeg zoompan + concat + ses + muzik |
| `steps/thumbnail.py` | 1280x720, sari/beyaz dev yazi, siyah kontur |
| `steps/upload.py` | YouTube Data API, private + publishAt, kapak set |
| `steps/notify.py` | Telegram bildirim |
| `auth_youtube.py` | Kanal basina OAuth token |

## 6. Neyi otomatiklestirme

- Baslik ve kapak metnini model yazar ama sen onaylarsin. CTR burada kazanilir ya da kaybedilir.
- Konu secimini otomatiklestirme. Kuyruk, outlier aramalarindan elle doldurulur.
- Ilk 20 videonun AVD ve CTR verisini `steps/script.py` icindeki prompt'a geri besle.
