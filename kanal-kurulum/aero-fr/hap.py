#!/usr/bin/env python3
"""HAP ölçüm betiği v3.1 — kanal-kurulum skill'inin sayısal motoru.

Alt komutlar:
  rontgen  <videolar.jsonl|csv> [...]   Kanal röntgeni: KME, hit bağımlılığı, kırılma, başlık kaldıraçları
  damar    <etiketli.csv>               Damar (alt niş) ölçümleri; 'damar' sütunu gerekir
  olc      <transkript.txt> [...]       Senaryo ses DNA'sı + konuşma hızı (#META satırında "sure" varsa)
  kapak    <x_kme.csv> [...]            Kapak grameri: en iyi %10 vs en zayıf %25 (OCR, yazı alanı, kontrast)
  poster   <bizim.jpg> <rakip.jpg> [...] Poster testi kolajı + birebir kopya kontrolü
  sahne    <video.mp4> [...]            Sahne kesim ritmi (scenedetect gerekir)
"""
import csv, json, re, sys, statistics as st
from datetime import date, datetime

BUGUN = date.today()
ALIAS = {
    "videoId": ["videoid", "id", "url"],
    "baslik": ["baslik", "başlık", "title", "videotitle"],
    "izlenme": ["izlenme", "views", "viewcount", "videoviewcount", "görüntüleme"],
    "yayin": ["yayin", "yayıntarihi", "publishdate", "publishedat", "published", "uploaddate", "videouploaddate", "date"],
    "yayin_metin": ["yayinmetin", "publishedtimetext"],
    "sure": ["sure", "süre", "lengthtext", "duration", "length"],
    "sira": ["sira", "index"],
    "kaynak": ["kaynak", "source"],
    "kanal": ["kanal", "channel"],
    "damar": ["damar", "vein", "altnis"],
}


def _norm(row):
    out = {k.strip(): v for k, v in row.items() if k}
    low = {re.sub(r"[\s_]", "", k.lower()): v for k, v in out.items()}
    for key, names in ALIAS.items():
        for n in names:
            if n in low and low[n] not in (None, ""):
                out[key] = low[n]
                break
    vid = str(out.get("videoId") or "")
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/live/)([\w-]{11})", vid)
    if m:
        out["videoId"] = m.group(1)
    return out


def oku(yol):
    rows = []
    with open(yol, encoding="utf-8") as f:
        if yol.endswith(".csv") or yol.endswith(".tsv"):
            rd = csv.DictReader(f, delimiter="\t" if yol.endswith(".tsv") else ",")
            rows = [_norm(r) for r in rd]
        else:
            rows = [_norm(json.loads(l)) for l in f if l.strip()]
    for r in rows:
        r["izlenme"] = sayi(r.get("izlenme"))
    return rows


def sayi(x):
    if x in (None, "", "null"):
        return None
    t = str(x).strip().upper().replace(" ", "").replace("VIEWS", "").replace("GÖRÜNTÜLEME", "")
    m = re.fullmatch(r"([\d.,]+)([KMB]?)", t)
    if not m:
        return None
    num, kat = m.groups()
    if kat:
        v = int(float(num.replace(",", ".")) * {"K": 1e3, "M": 1e6, "B": 1e9}[kat])
    else:
        v = int(num.replace(",", "").replace(".", ""))
    return v or None


def sn(sure):
    if not sure:
        return None
    p = [int(x) for x in re.findall(r"\d+", str(sure))]
    if not p:
        return None
    t = 0
    for x in p:
        t = t * 60 + x
    return t


YAS_BIRIM = {"second": 0, "minute": 0, "hour": 0, "day": 1, "week": 7, "month": 30, "year": 365,
             "saniye": 0, "dakika": 0, "saat": 0, "gün": 1, "hafta": 7, "ay": 30, "yıl": 365}
YAS_ORTA = {7: 3, 30: 15, 365: 182}


def yas_gun(r):
    m = re.search(r"(\d+)\s*([a-zçğıöşü]+)", str(r.get("yayin_metin") or "").lower())
    if m:
        for k, v in YAS_BIRIM.items():
            if m.group(2).startswith(k):
                return int(m.group(1)) * v + YAS_ORTA.get(v, 0)
    try:
        return (BUGUN - datetime.fromisoformat(str(r["yayin"])[:10]).date()).days
    except Exception:
        return None


def med(x):
    x = [v for v in x if v is not None]
    return st.median(x) if x else None


def yuzde(a, b):
    return round(100 * a / b) if b else None


AYLAR = r"\b(january|february|march|april|june|july|august|september|october|november|december|jan|feb|apr|jun|jul|aug|sept?|oct|nov|dec|janvier|février|avril|juin|juillet|août|septembre|octobre|novembre|décembre|januar|februar|märz|juni|juli|oktober|dezember|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|gennaio|febbraio|aprile|maggio|giugno|luglio|settembre|ottobre|dicembre|ocak|şubat|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\b\.?"
KISALTMA = {"USA", "DIY", "JBL", "CEO", "FBI", "CIA", "NASA", "BBC", "CNN", "NFL", "NBA", "UFO", "WWII", "LED", "USB",
            "IRS", "ATV", "LLC", "PBS", "ABC", "NBC", "CBS", "HBO", "MGM", "RCA", "NHS", "SUV", "GPS", "DNA", "WWI", "BMW", "IKEA"}
OZELLIK = {
    "rakam_var": lambda t: bool(re.search(r"\d", t)),
    "rakamla_baslar": lambda t: bool(re.match(r"\s*\d", t)),
    "parantez": lambda t: "(" in t or "[" in t,
    "BUYUK_kelime": lambda t: any(w not in KISALTMA for w in re.findall(r"\b[A-ZÇĞİÖŞÜÉÈÀÄÖÜ]{3,}\b", t)) and not t.isupper(),
    "soru_isareti": lambda t: "?" in t,
    "iki_nokta_tire": lambda t: bool(re.search(r":|\s[-–—|]\s|[–—]", t)),
    "hitap_sen_siz": lambda t: bool(re.search(r"\b(you|your|you'll|you're|vous|votre|vos|ihnen|usted|ustedes|tu|tus|siz|sizin|size)\b", t, re.I)),
    "birinci_sahis": lambda t: bool(re.search(r"\bI\b|\b(?i:i'm|i've|i'd|my|we|our|je|j'ai|mon|mes|ich|mein|meine|yo|mis|io|mio|mia|ben|benim)\b", t)),
    "uyari_negatif": lambda t: bool(re.search(r"\b(never|stop|don't|dont|mistake|regret|avoid|wrong|worst|dangerous|killing|ruin|jamais|erreur|nie|niemals|fehler|nunca|error|mai|errore|asla|hata)\b", t, re.I)),
    "zaman_baskisi": lambda t: bool(re.search(AYLAR + r"|\b(before|now|today|tonight|last chance|asap|this (fall|winter|spring|summer|week|year)|avant|maintenant|vor|jetzt|antes|ahora|prima|ora|önce|şimdi)\b", t, re.I)),
    "gizem_kayip": lambda t: bool(re.search(r"\b(secret|hidden|forgotten|nobody|no one|lost|truth|real reason|why|what happened|mystery|secret|oublié|caché|vergessen|geheim|olvidad|secreto|dimenticat|segreto|unutulan|gizli|neden)\b", t, re.I)),
    "nostalji_eski": lambda t: bool(re.search(r"\b(old|old-school|grandma|grandpa|grandparents|1[89]\d0s|19\d\d|back then|used to|vintage|classic|autrefois|grand-mère|früher|oma|opa|abuela|antes|nonna|eskiden|babaanne|anneanne)\b", t, re.I)),
}


def iskelet(t):
    s = re.sub(r"\b(1[89]\d\d|20\d\d)\b", "[YIL]", t)
    s = re.sub(r"\d+[\d.,]*", "[N]", s)
    s = re.sub(AYLAR, "[AY]", s, flags=re.I)
    return s


def ngramlar(t, n):
    w = re.findall(r"[\w'\[\]]+", iskelet(t).lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def kme_hesapla(seri, pencere=10):
    out = []
    for i, r in enumerate(seri):
        komsu = [x["izlenme"] for x in seri[max(0, i - pencere):i] + seri[i + 1:i + 1 + pencere]]
        m = med(komsu)
        out.append(round(r["izlenme"] / m, 2) if m else None)
    return out


def kirilma(seri, kat=3.0, devam=2.0, w=10):
    v = [r["izlenme"] for r in seri]
    for i in range(w, len(v) - w):
        m1 = med(v[i - w:i]); m2 = med(v[i + 1:i + 1 + w])
        if m1 and v[i] >= kat * m1 and m2 >= devam * m1:
            return i, round(v[i] / m1, 1), round(m2 / m1, 1)
    return None


def rontgen(yol, taze_gun=7, cikti=None):
    rows = oku(yol)
    kanal = rows[0].get("kanal") if rows else yol
    ilk = [r for r in rows if r.get("kaynak") == "oldest"]
    rows = [r for r in rows if r.get("kaynak") != "oldest" and r.get("izlenme") is not None]
    for r in rows:
        r["yas"] = yas_gun(r); r["sn"] = sn(r.get("sure"))
    if rows and "sira" in rows[0]:
        rows.sort(key=lambda r: int(r["sira"]), reverse=True)
    elif rows and all(r["yas"] is not None for r in rows):
        rows.reverse()
        rows.sort(key=lambda r: -r["yas"])
    else:
        rows.reverse()
    taze = [r for r in rows if r["yas"] is not None and r["yas"] < taze_gun]
    seri = [r for r in rows if r not in taze]
    n = len(seri)
    if n < 12:
        return {"kanal": kanal, "hata": f"olgun video sayısı {n} (<12); röntgen güvenilmez", "taze": len(taze)}
    v = [r["izlenme"] for r in seri]
    for r, k in zip(seri, kme_hesapla(seri)):
        r["kme"] = k
    seri = [r for r in seri if r["kme"] is not None]
    v = [r["izlenme"] for r in seri]; n = len(seri)
    kme = [r["kme"] for r in seri]
    srt = sorted(v, reverse=True)
    top = max(1, round(n * 0.1))
    k = kirilma(seri)
    sure = [r["sn"] for r in seri if r["sn"]]
    yaslar = [r["yas"] for r in seri if r["yas"] is not None]
    hafta = (max(yaslar) - min(yaslar)) / 7 if yaslar and max(yaslar) > min(yaslar) else None
    evg = [r for r in seri if r["yas"] and r["yas"] >= 180]
    rapor = {
        "kanal": kanal,
        "olgun_video": n, "taze_haric": len(taze),
        "medyan": med(v), "ortalama": round(st.mean(v)), "ort_medyan_orani": round(st.mean(v) / med(v), 1),
        "ilk10_payi_%": yuzde(sum(srt[:top]), sum(v)),
        "kme_p50_p75_p90": [round(x, 2) for x in (med(kme), st.quantiles(kme, n=4)[2], st.quantiles(kme, n=10)[8])],
        "hit_tipi": None,
        "kirilma": None,
        "sure_dk_medyan": round(med(sure) / 60, 1) if sure else None,
        "sure_dk_p25_p75": [round(x / 60, 1) for x in st.quantiles(sure, n=4)[::2]] if len(sure) >= 4 else None,
        "haftalik_yukleme_yaklasik": round(len(seri) / hafta, 1) if hafta and hafta >= 2 else None,
        "evergreen_180g+": (f"{sum(1 for r in evg if r['izlenme'] > med(v))}/{len(evg)}" if evg else "veri yok (180 günden eski video yok)"),
        "ilk_yukleme_medyani": med([r["izlenme"] for r in ilk if r.get("izlenme") is not None]) if ilk else None,
    }
    t10 = rapor["ilk10_payi_%"]
    rapor["hit_tipi"] = "format-bağımlı (iskelet kazandırıyor)" if t10 <= 50 else ("hit-bağımlı (konu/paket kazandırıyor)" if t10 >= 65 else "karma")
    p90, p25 = st.quantiles(kme, n=10)[8], st.quantiles(kme, n=4)[0]
    olgun14 = [r for r in seri if r["yas"] is None or r["yas"] >= 14]
    sirali = sorted(olgun14, key=lambda r: -r["kme"])
    rapor["outlier_P90"] = [{"videoId": r.get("videoId"), "baslik": r.get("baslik"), "izlenme": r["izlenme"], "kme": r["kme"], "sure": r.get("sure"),
                             "p90_ustu": r["kme"] >= p90}
                            for i, r in enumerate(sirali) if r["kme"] >= p90 or i < 5]
    rapor["flop_P25"] = [{"videoId": r.get("videoId"), "baslik": r.get("baslik"), "izlenme": r["izlenme"], "kme": r["kme"], "sure": r.get("sure")}
                        for r in sorted(olgun14, key=lambda r: r["kme"]) if r["kme"] <= p25][:8]
    if k:
        i, kat, devam = k
        rapor["kirilma"] = {"video": seri[i].get("baslik"), "videoId": seri[i].get("videoId"), "sira_kronolojik": i + 1,
                            "onceki10_kati": kat, "sonraki10_kati": devam,
                            "sure": seri[i].get("sure"),
                            "once5": [{"baslik": x.get("baslik"), "sure": x.get("sure"), "videoId": x.get("videoId"), "kme": x["kme"]} for x in seri[max(0, i - 5):i]],
                            "sonra5": [{"baslik": x.get("baslik"), "sure": x.get("sure"), "videoId": x.get("videoId"), "kme": x["kme"]} for x in seri[i + 1:i + 6]],
                            "not": "kapak karşılaştırması için: poster <kırılma.jpg> <önce...> ; süre değişimi 'sure' alanlarından"}
    kald = {}
    for ad, f in OZELLIK.items():
        evet = [r["kme"] for r in seri if r["kme"] and f(r.get("baslik") or "")]
        hayir = [r["kme"] for r in seri if r["kme"] and not f(r.get("baslik") or "")]
        if len(evet) >= 5 and len(hayir) >= 5:
            kald[ad] = {"kaldirac": round(med(evet) / med(hayir), 2), "n_evet": len(evet), "n_hayir": len(hayir)}
        else:
            kald[ad] = {"kaldirac": None, "n_evet": len(evet), "n_hayir": len(hayir)}
    rapor["baslik_kaldiraclari"] = kald
    bl = [r.get("baslik") or "" for r in seri]
    rapor["baslik_uzunluk_medyan"] = med([len(t) for t in bl])
    rapor["baslik_kelime_medyan"] = med([len(t.split()) for t in bl])
    out = [r for r in seri if r["kme"] and r["kme"] >= p90]
    kal = []
    for nn in (2, 3):
        say_all, say_out = {}, {}
        for r in seri:
            for g in ngramlar(r.get("baslik") or "", nn):
                say_all[g] = say_all.get(g, 0) + 1
                if r in out:
                    say_out[g] = say_out.get(g, 0) + 1
        for g, c in say_all.items():
            if c >= 4:
                ks = [r["kme"] for r in seri if r["kme"] and g in ngramlar(r.get("baslik") or "", nn)]
                kal.append((g, c, say_out.get(g, 0), round(med(ks), 2)))
    kal.sort(key=lambda x: (-x[3], -x[1], x[0]))
    rapor["kalip_kme_ilk8"] = [{"kalip": g, "n": c, "p90_icinde": o, "medyan_kme": m} for g, c, o, m in kal[:8]]
    rapor["kalip_kme_son4"] = [{"kalip": g, "n": c, "medyan_kme": m} for g, c, o, m in kal[-4:]] if len(kal) > 8 else []
    if cikti:
        with open(cikti, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["kronolojik_sira", "videoId", "baslik", "izlenme", "yas_gun", "sure_sn", "kme", "damar"])
            for i, r in enumerate(seri):
                w.writerow([i + 1, r.get("videoId"), r.get("baslik"), r["izlenme"], r["yas"], r["sn"], r["kme"], ""])
    return rapor


def damar(yol):
    rows = oku(yol)
    for r in rows:
        r["kme"] = float(r["kme"]) if r.get("kme") not in (None, "") else None
    rows = [r for r in rows if r.get("kme") is not None]
    if not rows or "damar" not in rows[0]:
        sys.exit("damar: CSV'de 'damar' ve 'kme' sütunu olmalı (önce rontgen --csv ile üret, damar sütununu doldur)")
    n = len(rows); kanal_med = med([r["izlenme"] for r in rows])
    p75 = st.quantiles([r["kme"] for r in rows], n=4)[2]
    gruplar = {}
    for r in rows:
        gruplar.setdefault(r["damar"].strip() or "etiketsiz", []).append(r)
    ort_pay = 100 / len(gruplar)
    tablo = []
    for ad, g in gruplar.items():
        endeks = round(med([r["kme"] for r in g]), 2)
        pay = round(100 * len(g) / n, 1)
        son = [r for r in g if int(r.get("kronolojik_sira") or r.get("sira") or 0) > n * 0.7]
        once = [r for r in g if r not in son]
        ivme = round(med([r["kme"] for r in son]) / med([r["kme"] for r in once]), 2) if len(son) >= 2 and len(once) >= 2 and med([r["kme"] for r in once]) else "veri yok"
        hucre = ("Yetim Damar" if pay < ort_pay else "Ana Damar") if endeks >= 1.3 else ("Deneme" if pay < ort_pay else "Ölü Yük")
        if len(g) < 3:
            hucre = "tekil (3'ten az video, karar yok)"
        tablo.append({"damar": ad, "video": len(g), "pay_%": pay, "medyan_izlenme": med([r["izlenme"] for r in g]),
                      "endeks_kme": endeks, "ust_ceyrek_orani_%": yuzde(sum(1 for r in g if r["kme"] >= p75), len(g)),
                      "guven": "düşük (n<5)" if len(g) < 5 else "normal",
                      "son_%30_video": len(son), "ivme_son%30/onceki": ivme, "hucre": hucre})
    tablo.sort(key=lambda x: -x["endeks_kme"])
    return {"kanal_medyani": kanal_med, "ortalama_pay_%": round(ort_pay, 1), "ust_ceyrek_taban_%": 25,
            "not": "ust_ceyrek_orani taban %25'tir; üstü damarın kanaldan iyi gittiğini gösterir", "damarlar": tablo}


HITAP = r"\b(?i:you|your|yours|vous|votre|vos|usted|ustedes|siz|sizin|size|sizi)\b|\b(Sie|Ihnen|Ihr|Ihre|Ihrem|Ihren|Lei|Suo|Sua|Suoi)\b"
BUYUK = r"(?<=[a-zçğıöşüéèàäöü,;:] )[A-ZÇĞİÖŞÜÉÀÄÖÜ][\wçğıöşüéèàäöü'-]+"
BIRINCI = r"\b(I|I'm|I've|I'd|my|me|je|j'ai|moi|mon|ich|mich|mir|mein|meine|yo|mi|io|mio|mia|ben|benim|bana)\b"


def olc(yol):
    ham = open(yol, encoding="utf-8").read()
    meta = {}
    if ham.startswith("#META"):
        bas, _, ham = ham.partition("\n")
        try:
            meta = json.loads(bas[5:].strip())
        except Exception:
            pass
    t = ham.strip()
    par = [p for p in re.split(r"\n\s*\n", t) if p.strip()]
    sen = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", t) if s.strip()]
    wc = [len(s.split()) for s in sen]; n = sum(wc) or 1
    k = sum(w <= 8 for w in wc); o = sum(9 <= w <= 16 for w in wc); u = sum(w >= 17 for w in wc)
    say = lambda x: len(re.findall(r"\b\d[\d.,]*\b", x)) + len(re.findall(BUYUK, x))
    kel = t.split()
    dilim = max(1, len(kel) // 5)
    ilk20 = " ".join(kel[:dilim]); son20 = " ".join(kel[-dilim:])
    r = {"dosya": yol.split("/")[-1], "karakter_bosluklu": len(t), "kelime": n, "cumle": len(sen),
         "ort_cumle_kelime": round(n / len(sen), 1) if sen else 0, "medyan_cumle": st.median(wc) if wc else 0,
         "dagilim_<=8/9-16/17+_%": [round(100 * x / len(sen)) for x in (k, o, u)] if sen else [],
         "paragraf_basina_cumle": round(len(sen) / len(par), 1) if len(par) > 1 else "paragraf yok",
         "soru_orani_%": round(100 * sum(s.endswith("?") for s in sen) / len(sen)) if sen else 0,
         "hitap_100k": round(100 * len(re.findall(HITAP, t)) / n, 2),
         "birinci_sahis_100k": round(100 * len(re.findall(BIRINCI, t)) / n, 2),
         "acilis_ozgulluk_ilk100": say(" ".join(kel[:100])),
         "somutluk_100k_yaklasik": round(100 * say(t) / n, 2),
         "somutluk_ilk%20/son%20": [round(100 * say(ilk20) / dilim, 1), round(100 * say(son20) / dilim, 1)]}
    s = sn(meta.get("sure"))
    if s:
        r["sure_dk"] = round(s / 60, 1)
        r["karakter_dk"] = round(len(t) / (s / 60))
        r["kelime_dk"] = round(n / (s / 60))
    return r


def _shingle(s):
    s = re.sub(r"[^a-z0-9çğıöşüéèàäöüñ]", "", s.lower())
    return {s[i:i + 4] for i in range(len(s) - 3)}


def kapak_olc(img_yol, baslik, ocr):
    from PIL import Image, ImageStat
    im = Image.open(img_yol).convert("RGB")
    W, H = im.size
    if abs(W / H - 4 / 3) < 0.01:
        bant = int((H - W * 9 / 16) / 2)
        im = im.crop((0, bant, W, H - bant)); W, H = im.size
    import numpy as np
    sonuc, _ = ocr(np.asarray(im)) if callable(ocr) else (None, None)
    kutular = sonuc or []
    metin = " ".join(k[1] for k in kutular)
    alan = 0
    for k in kutular:
        xs = [p[0] for p in k[0]]; ys = [p[1] for p in k[0]]
        alan += (max(xs) - min(xs)) * (max(ys) - min(ys))
    L = im.convert("L"); S = im.convert("HSV").split()[1]
    tb, bb = _shingle(metin), _shingle(baslik or "")
    return {"metin": metin, "metin_karakter": len(re.sub(r"\s", "", metin)),
            "kelime_yaklasik": len(metin.split()), "metin_alan_%": round(100 * alan / (W * H), 1),
            "baslik_tekrar_%": round(100 * len(tb & bb) / len(tb)) if tb else None,
            "kontrast_rms": round(ImageStat.Stat(L).stddev[0], 1), "parlaklik": round(ImageStat.Stat(L).mean[0]),
            "doygunluk": round(ImageStat.Stat(S).mean[0])}


def kapak(kme_csv, klasor=None, ust_yuzde=10, alt_yuzde=25, min_yas=14):
    import os, urllib.request
    try:
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR()
    except ImportError:
        sys.exit("kapak: pip install rapidocr-onnxruntime pillow")
    rows = [r for r in csv.DictReader(open(kme_csv, encoding="utf-8")) if r.get("kme")]
    if not rows or not all(r.get("videoId") for r in rows):
        sys.exit("kapak: videoId sütunu boş. Video listesi URL veya ID içermeli (NexLev JSONL veya 'url' sütunlu CSV).")
    rows = [r for r in rows if not r.get("yas_gun") or float(r["yas_gun"]) >= min_yas]
    rows.sort(key=lambda r: -float(r["kme"]))
    n = len(rows)
    ust = rows[:max(3, round(n * ust_yuzde / 100))]
    alt = rows[-max(3, round(n * alt_yuzde / 100)):]
    klasor = klasor or kme_csv.rsplit(".", 1)[0] + "_kapak"
    os.makedirs(klasor, exist_ok=True)
    def grup(liste):
        out = []
        for r in liste:
            y = os.path.join(klasor, r["videoId"] + ".jpg")
            if not os.path.exists(y):
                try:
                    urllib.request.urlretrieve(f"https://i.ytimg.com/vi/{r['videoId']}/hqdefault.jpg", y)
                except Exception:
                    continue
            m = kapak_olc(y, r["baslik"], ocr); m["kme"] = float(r["kme"]); m["baslik"] = r["baslik"]
            out.append(m)
        return out
    U, A = grup(ust), grup(alt)
    ozet = lambda g, k: med([x[k] for x in g if x[k] is not None])
    alanlar = ["metin_karakter", "kelime_yaklasik", "metin_alan_%", "baslik_tekrar_%", "kontrast_rms", "parlaklik", "doygunluk"]
    return {"kaynak": kme_csv, "ust_n": len(U), "alt_n": len(A),
            "medyan_ust_vs_alt": {k: [ozet(U, k), ozet(A, k)] for k in alanlar},
            "metinsiz_kapak_%_ust_alt": [yuzde(sum(1 for x in U if x["metin_karakter"] == 0), len(U)), yuzde(sum(1 for x in A if x["metin_karakter"] == 0), len(A))],
            "ust_ornek": [{"kapak_yazisi": x["metin"], "baslik": x["baslik"], "kme": x["kme"]} for x in U[:5]],
            "klasor": klasor}


def poster(bizim, rakipler, cikti="poster_testi.jpg"):
    from PIL import Image
    def ac(p):
        im = Image.open(p).convert("RGB"); W, H = im.size
        if abs(W / H - 4 / 3) < 0.01:
            b = int((H - W * 9 / 16) / 2); im = im.crop((0, b, W, H - b))
        return im.resize((480, 270))
    ims = [ac(p) for p in [bizim] + list(rakipler)]
    kol = 2; sat = (len(ims) + 1) // 2
    tuval = Image.new("RGB", (480 * kol, 270 * sat), "white")
    for i, im in enumerate(ims):
        tuval.paste(im, ((i % kol) * 480, (i // kol) * 270))
    tuval.save(cikti, quality=88)
    out = {"kolaj": cikti, "sol_ust": "bizim kapak", "piksel_kopya": []}
    try:
        import imagehash
        hb = imagehash.phash(ims[0])
        for p, im in zip(rakipler, ims[1:]):
            out["piksel_kopya"].append({"rakip": p, "phash_mesafe": int(hb - imagehash.phash(im)),
                                        "birebir_kopya": int(hb - imagehash.phash(im)) <= 8})
    except ImportError:
        out["piksel_kopya"] = "kontrol yapılmadı (pip install imagehash); birebir kopya kararını kolajdan ver"
    return out


def sahne(yol):
    try:
        from scenedetect import detect, ContentDetector
    except ImportError:
        sys.exit("sahne: pip install 'scenedetect[opencv]'")
    sc = detect(yol, ContentDetector(threshold=27.0))
    zs = lambda t: t.seconds if hasattr(t, "seconds") and not callable(t.seconds) else t.get_seconds()
    kes = [zs(s[0]) for s in sc[1:]]
    bolum = lambda a, b: [x for x in kes if a <= x < b]
    son = zs(sc[-1][1]) if sc else 0
    def ort(a, b):
        k = bolum(a, b)
        return round((min(b, son) - a) / (len(k) + 1), 1) if son > a else None
    return {"dosya": yol, "sure_sn": round(son), "toplam_kesim": len(kes),
            "ort_sahne_sn_0-30": ort(0, 30), "ort_sahne_sn_30-60": ort(30, 60),
            "ort_sahne_sn_60-300": ort(60, 300), "ort_sahne_sn_300+": ort(300, son + 1)}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    kom, args = sys.argv[1], sys.argv[2:]
    if kom == "rontgen":
        csv_cikti = "--csv" in args
        args = [a for a in args if a != "--csv"]
        sonuc = [rontgen(a, cikti=(a.rsplit(".", 1)[0] + "_kme.csv") if csv_cikti else None) for a in args]
    elif kom == "damar":
        sonuc = damar(args[0])
    elif kom == "olc":
        sonuc = [olc(a) for a in args]
    elif kom == "kapak":
        sonuc = [kapak(a) for a in args]
    elif kom == "poster":
        sonuc = poster(args[0], args[1:])
    elif kom == "sahne":
        sonuc = [sahne(a) for a in args]
    else:
        sys.exit(__doc__)
    print(json.dumps(sonuc, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
