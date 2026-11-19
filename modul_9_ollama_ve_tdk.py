# -*- coding: utf-8 -*-
"""
==============================================================================
AR AI STUDIO v4.3 — MODÜL 9: OLLAMA YEREL YAPAY ZEKA & TDK (TÜRK DİL KURUMU)
SÖZLÜK ENTEGRASYONU VE AÇ/KAPAT KONTROL MERKEZİ (modul_9_ollama_ve_tdk.py)
Ana Kontrol: main.py tarafından otomatik import edilir.
==============================================================================
"""
import importlib.util
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, as_completed, wait
from datetime import datetime
import json
import time
import os
import re
import sys
import urllib.parse
import urllib.request
import streamlit as st

_MODUL_DIZINI = os.path.dirname(os.path.abspath(__file__))
if _MODUL_DIZINI not in sys.path:
    sys.path.insert(0, _MODUL_DIZINI)


def _guvenli_modul_yukle(modul_adi: str):
    if modul_adi in sys.modules and getattr(sys.modules[modul_adi], "__file__", None):
        return sys.modules[modul_adi]
    yol = os.path.join(_MODUL_DIZINI, f"{modul_adi}.py")
    if os.path.exists(yol):
        spec = importlib.util.spec_from_file_location(modul_adi, yol)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[modul_adi] = mod
            spec.loader.exec_module(mod)
            return mod
    return __import__(modul_adi)


_m1 = _guvenli_modul_yukle("modul_1_arayuz_ve_tema")
bilgi_karti_olustur = _m1.bilgi_karti_olustur


def _guncel_tarih_etiketi() -> str:
    """Tüm yapay zeka istemlerine canlı güncel tarih ve saat bilgisini verir."""
    _aylar = [
        "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
    ]
    _gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    simdi = datetime.now()
    return f"{simdi.day} {_aylar[simdi.month]} {simdi.year} {_gunler[simdi.weekday()]}, saat {simdi.strftime('%H:%M')}"

OLLAMA_VARSAYILAN_URL = "http://127.0.0.1:11434"
_OLLAMA_YEREL_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

# Çevrimdışı / Hızlı Yedek TDK Sözlük Tabanı (İnternet kesikse bile anında anlam verir)
YEDEK_TDK_SOZLUK = {
    "mühendislik": {
        "anlamlar": [
            "1. (isim) İnsanların her türlü ihtiyacını karşılamaya dayalı yol, köprü, bina, makine, elektrik, elektronik, yazılım ve havacılık gibi teknik işleri matematik ve fen bilimleri ilkeleriyle tasarlama ve uygulama mesleği.",
        ],
        "atasozu_deyim": ["Mühendislik harikası", "Tersine mühendislik"],
        "birlesikler": ["yazılım mühendisliği", "uçak mühendisliği", "mekatronik mühendisliği", "bilgisayar mühendisliği"],
    },
    "yazılım": {
        "anlamlar": [
            "1. (isim, bilişim) Bir bilgisayarda donanıma hayat veren ve bilgi işlemde kullanılan programlar, yordamlar, programlama dilleri ve belgelerin tümü.",
        ],
        "atasozu_deyim": ["Açık kaynak yazılım", "Gömülü yazılım"],
        "birlesikler": ["yazılım mühendisi", "yazılım geliştirici", "sistem yazılımı"],
    },
    "algoritma": {
        "anlamlar": [
            "1. (isim, matematik ve bilişim) Belli bir problemi çözmek veya belirli bir amaca ulaşmak için tasarlanan sıralı ve mantıksal işlem basamakları (Adını İslam âlimi El-Hârizmî'den alır).",
        ],
        "atasozu_deyim": ["Algoritma kurmak", "Arama algoritması"],
        "birlesikler": ["yapay zeka algoritması", "sıralama algoritması"],
    },
    "akıl": {
        "anlamlar": [
            "1. (isim) Düşünme, anlama ve kavrama gücü, us, خرد (hıred).",
            "2. (isim) Hafıza, bellek, zihin.",
            "3. (isim) Öğüt, salık, tavsiye.",
        ],
        "atasozu_deyim": ["Akıl akıldan üstündür", "Aklı başına gelmek", "Akıl yürütmek", "Aklına yatmak"],
        "birlesikler": ["akılcı", "akıl sağlığı", "akıl oyunu", "sağduyu"],
    },
    "bilim": {
        "anlamlar": [
            "1. (isim) Evrenin veya olayların bir bölümünü konu olarak seçen, deneye dayanan yöntemler ve gerçeklikten yararlanarak sonuç çıkarmaya çalışan düzenli bilgi, ilim.",
            "2. (isim) Belli bir konuyu bilme isteğinden yola çıkan, belli bir amaca yönelen bilgi edinme ve yöntemli araştırma süreci.",
        ],
        "atasozu_deyim": ["Bilim adamı", "Bilim dalı", "Bilim kurgu"],
        "birlesikler": ["bilim insanı", "bilgisayar bilimi", "doğa bilimleri", "fen bilimleri"],
    },
    "otonom": {
        "anlamlar": [
            "1. (sıfat, Fransızca autonome) Özerk; kendi kendini yöneten veya dışarıdan müdahale olmadan kendi kararlarını verebilen sistem.",
        ],
        "atasozu_deyim": ["Otonom sürüş", "Otonom uçuş", "Otonom sistem"],
        "birlesikler": ["otonom İHA", "otonom araç", "otonom sinir sistemi"],
    },
    "tork": {
        "anlamlar": [
            "1. (isim, fizik) Bir kuvvetin bir nesneyi bir eksen etrafında döndürme eğiliminin ölçüsü; döndürme momenti (N·m).",
        ],
        "atasozu_deyim": ["Motor torku", "Tork üretmek"],
        "birlesikler": ["tork anahtarı", "tork konvertörü"],
    },
    "irfan": {
        "anlamlar": [
            "1. (isim, Arapça) Bilme, anlama, sezme, kültür ve manevi derinlik.",
            "2. (isim, tasavvuf) Evrenin sırlarını bilme gücü.",
        ],
        "atasozu_deyim": ["İrfan sahibi", "İlim ve irfan"],
        "birlesikler": ["irfan meclisi"],
    },
}


# ==============================================================================
# 1. OLLAMA YEREL YAPAY ZEKA ENTEGRASYONU (v7.7 — PROXY-FREE, IPv4, THREAD-SAFE)
# ==============================================================================
_OLLAMA_DURUM_ONBELLEK = {"zaman": 0.0, "url": "", "aktif": False, "modeller": [], "hata": ""}
_OLLAMA_EMBED_ANAHTARLARI = ("embed", "bge-", "minilm", "snowflake-arctic-embed", "mxbai", "nomic-embed")
_OLLAMA_TURKCE_MODEL_ONCELIK = (
    "qwen2.5",
    "qwen3",
    "gemma3",
    "gemma2",
    "llama3.3",
    "llama3.1",
    "llama3.2",
    "mistral",
    "deepseek-r1",
    "phi4",
    "phi3",
)


def _ollama_url_normallestir(base_url: str = None) -> str:
    """
    Ollama adresini temizler; Windows'ta IPv6 (::1) beklemesini önlemek için
    'localhost' adresini doğrudan hızlı IPv4 '127.0.0.1'e çevirir.
    """
    ham = (base_url or OLLAMA_VARSAYILAN_URL).strip()
    if not ham:
        return OLLAMA_VARSAYILAN_URL
    if not ham.startswith(("http://", "https://")):
        ham = "http://" + ham
    ham = ham.rstrip("/")
    ham = re.sub(r"^(https?://)localhost(?=[:/]|$)", r"\g<1>127.0.0.1", ham, flags=re.IGNORECASE)
    return ham


def _ollama_http_istek(url: str, veri_dict: dict = None, timeout: float = 2.0) -> dict:
    """Sistem proxy'sini baypas ederek yerel Ollama'ya doğrudan HTTP isteği gönderir."""
    if veri_dict is not None:
        req = urllib.request.Request(
            url,
            data=json.dumps(veri_dict).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
    else:
        req = urllib.request.Request(url, method="GET")
    with _OLLAMA_YEREL_OPENER.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ollama_sohbet_modellerini_filtrele(modeller: list) -> list:
    """Embedding (vektör) modellerini ayıklar, yalnızca sohbet yetenekli modelleri döndürür."""
    uygun = []
    for m in modeller or []:
        ad = str(m).strip()
        if not ad:
            continue
        ad_kucuk = ad.lower()
        if any(emb in ad_kucuk for emb in _OLLAMA_EMBED_ANAHTARLARI):
            continue
        uygun.append(ad)
    return uygun


def ollama_hizli_durum_kontrol(base_url: str = OLLAMA_VARSAYILAN_URL, zorla: bool = False) -> tuple:
    """
    Ollama sunucusunun canlı olup olmadığını proxy baypaslı IPv4 127.0.0.1 üzerinden
    1.0 sn zaman aşımı ve akıllı önbellek ile kontrol eder.
    """
    temiz_url = _ollama_url_normallestir(base_url)
    simdi = time.time()
    _onbellek_suresi = 20.0 if _OLLAMA_DURUM_ONBELLEK["aktif"] else 45.0
    if (
        not zorla
        and _OLLAMA_DURUM_ONBELLEK["url"] == temiz_url
        and (simdi - _OLLAMA_DURUM_ONBELLEK["zaman"]) < _onbellek_suresi
    ):
        return _OLLAMA_DURUM_ONBELLEK["aktif"], list(_OLLAMA_DURUM_ONBELLEK["modeller"])

    try:
        veri = _ollama_http_istek(f"{temiz_url}/api/tags", timeout=1.0)
        ham_modeller = [m.get("name") for m in veri.get("models", []) if m.get("name")]
        sohbet_modelleri = _ollama_sohbet_modellerini_filtrele(ham_modeller)
        _OLLAMA_DURUM_ONBELLEK.update(
            {"zaman": simdi, "url": temiz_url, "aktif": True, "modeller": sohbet_modelleri, "hata": ""}
        )
        return True, sohbet_modelleri
    except Exception as e:
        _OLLAMA_DURUM_ONBELLEK.update(
            {"zaman": simdi, "url": temiz_url, "aktif": False, "modeller": [], "hata": str(e)}
        )
        return False, []


def ollama_en_iyi_modeli_sec(base_url: str = OLLAMA_VARSAYILAN_URL, tercih_edilen: str = None) -> str:
    """Yüklü Ollama sohbet modelleri arasından en uygun Türkçe sohbet modelini seçer."""
    aktif, yuklu_modeller = ollama_hizli_durum_kontrol(base_url)
    tercih = (tercih_edilen or "").strip()
    if not aktif or not yuklu_modeller:
        return tercih or "llama3.2"

    if tercih and not any(emb in tercih.lower() for emb in _OLLAMA_EMBED_ANAHTARLARI):
        for m in yuklu_modeller:
            if m == tercih or m.split(":")[0].lower() == tercih.split(":")[0].lower():
                return m

    for oncelik in _OLLAMA_TURKCE_MODEL_ONCELIK:
        for m in yuklu_modeller:
            if oncelik in m.lower():
                return m

    return yuklu_modeller[0]


def _ollama_yanit_temizle(ham_metin: str) -> str:
    """Ollama/AI yanıtlarındaki <think>...</think> bloklarını ve rol öneklerini temizler."""
    if not ham_metin:
        return ""
    temiz = str(ham_metin).strip()
    temiz = re.sub(r"<think>.*?</think>", "", temiz, flags=re.IGNORECASE | re.DOTALL).strip()
    if "<think>" in temiz.lower():
        temiz = re.sub(r"<think>.*$", "", temiz, flags=re.IGNORECASE | re.DOTALL).strip()
    temiz = re.sub(r"^(?:Asistan|Assistant|Ollama|Ar\s*AI)\s*:\s*", "", temiz, flags=re.IGNORECASE).strip()
    temiz = re.sub(r"\n{3,}", "\n\n", temiz).strip()

    if len(temiz) < 4:
        return ""
    cjk_sayisi = len(re.findall(r"[\u4e00-\u9fff\u3040-\u30ff]", temiz))
    if cjk_sayisi > 12 and cjk_sayisi > len(temiz) * 0.25:
        return ""
    return temiz


def ollama_modelleri_getir(base_url: str = OLLAMA_VARSAYILAN_URL) -> list:
    """Bilgisayarda çalışan Ollama servisindeki yüklü sohbet modellerini listeler."""
    aktif, modeller = ollama_hizli_durum_kontrol(base_url, zorla=True)
    if aktif and modeller:
        return modeller
    return ["qwen2.5", "llama3.2", "llama3.1", "gemma2", "mistral", "deepseek-r1"]


def ollama_baglanti_kontrol(base_url: str = OLLAMA_VARSAYILAN_URL) -> tuple:
    """Ollama servisinin açık olup olmadığını ve yüklü sohbet modellerini proxy baypaslı kontrol eder."""
    temiz_url = _ollama_url_normallestir(base_url)
    try:
        veri = _ollama_http_istek(f"{temiz_url}/api/tags", timeout=2.0)
        ham_modeller = [m.get("name") for m in veri.get("models", []) if m.get("name")]
        modeller = _ollama_sohbet_modellerini_filtrele(ham_modeller) or ham_modeller
        _OLLAMA_DURUM_ONBELLEK.update(
            {"zaman": time.time(), "url": temiz_url, "aktif": True, "modeller": modeller, "hata": ""}
        )
        return True, modeller
    except Exception as e:
        _OLLAMA_DURUM_ONBELLEK.update(
            {"zaman": time.time(), "url": temiz_url, "aktif": False, "modeller": [], "hata": str(e)}
        )
        return False, str(e)


def ollama_soru_sor(
    soru: str,
    model_adi: str = None,
    base_url: str = None,
    sicaklik: float = None,
    ek_baglam: str = "",
    gecmis_mesajlar: list = None,
    sistem_prompt_ozel: str = None,
) -> tuple:
    """
    v7.7 — Thread-safe, proxy-free, IPv4 öncelikli Ollama motoru.
    İş parçacığı (ThreadPoolExecutor) içinde çağrıldığında st.session_state'e dokunmaz.
    """
    try:
        ss_url = st.session_state.get("ollama_url", OLLAMA_VARSAYILAN_URL)
        ss_model = st.session_state.get("ollama_secili_model", "llama3.2")
        ss_mesajlar = st.session_state.get("messages") or []
    except Exception:
        ss_url, ss_model, ss_mesajlar = OLLAMA_VARSAYILAN_URL, "llama3.2", []

    hedef_url = _ollama_url_normallestir(base_url or ss_url)
    tercih_model = model_adi or ss_model
    secili_model = ollama_en_iyi_modeli_sec(hedef_url, tercih_model)

    baglam_var = bool(ek_baglam and ek_baglam.strip())
    aktif_sicaklik = float(sicaklik) if sicaklik is not None else (0.35 if baglam_var else 0.45)

    if sistem_prompt_ozel and sistem_prompt_ozel.strip():
        sistem_mesaji = sistem_prompt_ozel.strip()
    else:
        sistem_mesaji = (
            "Sen Ahmet tarafından geliştirilen 'Ar AI Studio' adlı Türkçe yapay zeka asistanısın. "
            "Ahmet İstanbul Fatih'te Fen ve Sosyal Bilimler Proje Okulu 9. sınıf öğrencisi; "
            f"TEKNOFEST İHA ve TÜBİTAK akıllı bebek arabası projeleri geliştiriyor. BUGÜNÜN GERÇEK TARİHİ: {_guncel_tarih_etiketi()}. Güncel açık kaynak verilerini her zaman esas al.\n"
            "KESİN KURALLAR:\n"
            "1. YALNIZCA akıcı, doğal, düzgün ve anlaşılır Türkçe yaz; rastgele İngilizce kelime, garip sembol veya iç düşünce (<think>) metni yazma.\n"
            "2. Bilmediğin veya emin olmadığın bir sayıyı, tarihi ya da kulüp/fiyat bilgisini ASLA uydurma; dürüstçe belirt.\n"
            "3. Kısa, düzenli paragraflar veya temiz madde işaretleriyle doğrudan soruya odaklan."
        )

    if baglam_var:
        sistem_mesaji += (
            "\n\nAŞAĞIDA AÇIK KAYNAKLARDAN (Wikipedia, TDK, Hava Durumu, Yemek Tarifleri, "
            "81 İl & 195+ Ülke, Harita, Piyasa/Kur) TOPLANMIŞ DOĞRULANMIŞ VERİLER VAR. "
            "Bu gerçek verileri asla çarpıtmadan ve uydurma eklemeden, Ahmet'e akıcı ve samimi tek bir Türkçe yanıt olarak sentezle:\n"
            f"{ek_baglam.strip()[:6500]}"
        )

    mesaj_listesi = [{"role": "system", "content": sistem_mesaji}]
    kaynak_gecmis = gecmis_mesajlar if gecmis_mesajlar is not None else ss_mesajlar
    for m in kaynak_gecmis[-10:]:
        rol = m.get("role", "")
        icerik = str(m.get("content", "")).strip()
        if rol in ("user", "assistant") and icerik:
            if rol == "user" and icerik == soru.strip():
                continue
            mesaj_listesi.append({"role": rol, "content": icerik[:1200]})
    mesaj_listesi.append({"role": "user", "content": soru.strip()})

    ollama_secenekleri = {
        "temperature": aktif_sicaklik,
        "top_p": 0.85,
        "top_k": 40,
        "repeat_penalty": 1.18,
        "num_ctx": 8192,
        "num_predict": 2048,
    }

    son_hata = ""
    # 1. /api/chat uç noktası (proxy-free + 45 sn cold-start toleransı + keep_alive 10m)
    try:
        sonuc = _ollama_http_istek(
            f"{hedef_url}/api/chat",
            veri_dict={
                "model": secili_model,
                "messages": mesaj_listesi,
                "stream": False,
                "keep_alive": "10m",
                "options": ollama_secenekleri,
            },
            timeout=45,
        )
        yanit_metni = _ollama_yanit_temizle(sonuc.get("message", {}).get("content", ""))
        if yanit_metni:
            return f"🦙 **Ollama ({secili_model}):**\n\n{yanit_metni}", f"Ollama ({secili_model})"
    except Exception as e:
        son_hata = str(e)

    # 2. /api/generate yedek uç noktası
    try:
        sonuc = _ollama_http_istek(
            f"{hedef_url}/api/generate",
            veri_dict={
                "model": secili_model,
                "system": sistem_mesaji,
                "prompt": soru.strip(),
                "stream": False,
                "keep_alive": "10m",
                "options": ollama_secenekleri,
            },
            timeout=45,
        )
        yanit_metni = _ollama_yanit_temizle(sonuc.get("response", ""))
        if yanit_metni:
            return f"🦙 **Ollama ({secili_model}):**\n\n{yanit_metni}", f"Ollama ({secili_model})"
    except Exception as e:
        son_hata = str(e)

    return (
        None,
        f"Ollama bağlantısı kurulamadı (`{hedef_url}` — Model: `{secili_model}`). "
        f"Ollama uygulamasının açık olduğundan ve en az bir sohbet modelinin (`ollama pull qwen2.5:3b`) yüklü olduğundan emin ol. ({son_hata})",
    )


# ==============================================================================
# 2. TDK (TÜRK DİL KURUMU) GÜNCEL TÜRKÇE SÖZLÜK ENTEGRASYONU (sozluk.gov.tr)
# ==============================================================================
def tdk_kelime_cikar(kullanici_girdisi: str) -> str:
    """
    Kullanıcının cümlesinden TDK'da aranacak kelimeyi ayıklar.
    Örn: 'tdk: mühendislik', 'mütefekkir ne demek?', 'irfan kelimesinin anlamı nedir' -> 'mütefekkir', 'irfan'
    """
    temiz = kullanici_girdisi.strip()
    # Başındaki 'tdk:', 'tdk', 'sözlük:' öneklerini temizle
    temiz = re.sub(r"^(?:tdk|sozluk|sözlük)\s*[:\-]?\s*", "", temiz, flags=re.IGNORECASE).strip()
    # Sonundaki 'ne demek', 'anlamı nedir', 'tdk anlamı' vb. ekleri temizle
    temiz = re.sub(
        r"\s+(?:kelimesinin\s+anlamı\s+nedir|kelimesinin\s+anlamı|kelimesi\s+ne\s+demek|tdk\s+anlamı\s+nedir|tdk\s+anlamı|anlamı\s+nedir|anlamı\s+ne|ne\s+demektir|ne\s+demek|nedir)\s*\??$",
        "",
        temiz,
        flags=re.IGNORECASE,
    ).strip()
    temiz = temiz.strip("?!.,;:\"' ")
    return temiz.replace("İ", "i").replace("I", "ı").lower()


def tdk_sozluk_sorgula(kelime: str) -> dict:
    """
    Resmi Türk Dil Kurumu (https://sozluk.gov.tr/gts?ara=...) API'sinden kelimenin
    anlamlarını, örnek cümlelerini, atasözü/deyimlerini ve birleşik kelimelerini çeker.
    """
    aranan = tdk_kelime_cikar(kelime)
    if not aranan:
        return {"basarili": False, "kelime": kelime, "hata": "Lütfen aranacak bir kelime girin."}

    try:
        kodlu_kelime = urllib.parse.quote(aranan)
        url = f"https://sozluk.gov.tr/gts?ara={kodlu_kelime}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
            },
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            veri = json.loads(resp.read().decode("utf-8"))

        if isinstance(veri, list) and len(veri) > 0 and isinstance(veri[0], dict):
            madde = veri[0]
            anlamlar = []
            ornekler = []
            for idx, a_obj in enumerate(madde.get("anlamlarListe", []), 1):
                anlam_metin = a_obj.get("anlam", "").strip()
                ozellikler = [
                    oz.get("tam_adi", "")
                    for oz in a_obj.get("ozelliklerListe", [])
                    if oz.get("tam_adi")
                ]
                oz_str = f" *({', '.join(ozellikler)})*" if ozellikler else ""
                if anlam_metin:
                    anlamlar.append(f"{idx}. {oz_str} {anlam_metin}".strip())
                for orn in a_obj.get("orneklerListe", [])[:2]:
                    orn_metin = orn.get("ornek", "").strip()
                    yazar_liste = orn.get("yazar", [])
                    yazar_adi = yazar_liste[0].get("tam_adi", "") if isinstance(yazar_liste, list) and yazar_liste else ""
                    if orn_metin:
                        ornekler.append(f'"{orn_metin}"' + (f" — *{yazar_adi}*" if yazar_adi else ""))

            atasozleri = [a.get("madde", "") for a in madde.get("atasozu", []) if a.get("madde")][:8]
            birlesikler = (
                [b.strip() for b in madde.get("birlesikler", "").split(",") if b.strip()][:10]
                if madde.get("birlesikler")
                else []
            )
            lisan = madde.get("lisan", "").strip()

            if anlamlar:
                return {
                    "basarili": True,
                    "kelime": madde.get("madde", aranan),
                    "koken": lisan or "Türkçe",
                    "anlamlar": anlamlar,
                    "ornekler": ornekler,
                    "atasozu_deyim": atasozleri,
                    "birlesikler": birlesikler,
                    "kaynak": "TDK Güncel Türkçe Sözlük (Canlı)",
                }
    except Exception:
        pass

    # Çevrimdışı Yedek Sözlük Kontrolü
    if aranan in YEDEK_TDK_SOZLUK:
        y_veri = YEDEK_TDK_SOZLUK[aranan]
        return {
            "basarili": True,
            "kelime": aranan,
            "koken": "Türkçe / Köken Bilgisi",
            "anlamlar": y_veri["anlamlar"],
            "ornekler": [],
            "atasozu_deyim": y_veri["atasozu_deyim"],
            "birlesikler": y_veri["birlesikler"],
            "kaynak": "TDK Yerleşik Yedek Sözlük",
        }

    return {
        "basarili": False,
        "kelime": aranan,
        "hata": f"TDK Güncel Türkçe Sözlük'te '{aranan}' maddesi bulunamadı veya yazımı farklı olabilir.",
    }


def tdk_sonucunu_metne_formatla(sonuc: dict) -> str:
    """TDK sözlük sonucunu şık bir Markdown metnine dönüştürür."""
    if not sonuc.get("basarili"):
        return f"📕 **TDK Sözlük:** {sonuc.get('hata', 'Kelime bulunamadı.')}"

    satirlar = [
        f"### 📕 TDK Güncel Türkçe Sözlük: **{sonuc['kelime'].upper()}**",
        f"**Köken / Dil Bilgisi:** `{sonuc.get('koken', 'Türkçe')}` | **Kaynak:** `{sonuc.get('kaynak', 'TDK')}`\n",
        "**📌 Anlamları:**",
    ]
    for a in sonuc.get("anlamlar", []):
        satirlar.append(f"- {a}")

    if sonuc.get("ornekler"):
        satirlar.append("\n**📝 Edebiyatımızdan Örnek Cümleler:**")
        for o in sonuc["ornekler"]:
            satirlar.append(f"> {o}")

    if sonuc.get("atasozu_deyim"):
        satirlar.append("\n**🗣️ Atasözleri ve Deyimler:** " + " • ".join(f"`{x}`" for x in sonuc["atasozu_deyim"]))

    if sonuc.get("birlesikler"):
        satirlar.append("\n**🔗 Birleşik Kelimeler:** " + ", ".join(sonuc["birlesikler"]))

    return "\n".join(satirlar)


# ==============================================================================
# 3. OLLAMA & TDK BÖLÜMÜ ARAYÜZ STÜDYOSU (main.py Tarafından Çağrılır)
# ==============================================================================
def ollama_ve_tdk_studyosu_goster(sesli_soyle_fn):
    st.subheader("🦙 Ollama Yerel Yapay Zeka & 📕 TDK Güncel Türkçe Sözlük Merkezi")

    # Üst Aç / Kapat Kontrol Çubuğu
    ust1, ust2, ust3 = st.columns([1.2, 1.2, 1.2])
    with ust1:
        st.session_state.ollama_aktif = st.toggle(
            "🦙 Ollama Modu (Aç / Kapat)",
            value=st.session_state.get("ollama_aktif", False),
            key="studio_ollama_toggle",
        )
    with ust2:
        st.session_state.tdk_aktif = st.toggle(
            "📕 TDK Sözlük Modu (Aç / Kapat)",
            value=st.session_state.get("tdk_aktif", True),
            key="studio_tdk_toggle",
        )
    with ust3:
        bagli_mi, modeller_veya_hata = ollama_baglanti_kontrol(st.session_state.get("ollama_url", OLLAMA_VARSAYILAN_URL))
        if bagli_mi:
            st.markdown('<span class="live-badge">🦙 OLLAMA SERVİSİ AÇIK</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="silent-badge">🦙 OLLAMA BEKLEMEDE (localhost:11434)</span>', unsafe_allow_html=True)

    tab_ollama, tab_tdk = st.tabs([
        "🦙 Ollama Yapay Zeka Bölümü",
        "📕 TDK (Türk Dil Kurumu) Sözlük Bölümü",
    ])

    # --- BÖLÜM 1: OLLAMA YAPAY ZEKA BÖLÜMÜ ---
    with tab_ollama:
        col_o1, col_o2 = st.columns([1.05, 1.65], gap="large")
        with col_o1:
            st.markdown("#### ⚙️ Ollama Bağlantı & Model Merkezi")
            girilen_url = st.text_input(
                "Ollama Sunucu Adresi (IPv4 Önerilir):",
                value=st.session_state.get("ollama_url", OLLAMA_VARSAYILAN_URL),
                help="Windows'ta en hızlı bağlantı için http://127.0.0.1:11434 kullanılır (localhost otomatik çevrilir).",
            )
            st.session_state.ollama_url = _ollama_url_normallestir(girilen_url)

            mevcut_modeller = ollama_modelleri_getir(st.session_state.ollama_url)
            varsayilan_m = st.session_state.get("ollama_secili_model", mevcut_modeller[0])
            if varsayilan_m not in mevcut_modeller:
                mevcut_modeller.insert(0, varsayilan_m)
            st.session_state.ollama_secili_model = st.selectbox(
                "Aktif Sohbet Modeli:",
                options=mevcut_modeller,
                index=mevcut_modeller.index(varsayilan_m),
            )
            ozel_model = st.text_input("Veya Model Adını Elle Yaz:", placeholder="Örn: qwen2.5:3b, gemma2, llama3.2", value="")
            if ozel_model.strip():
                st.session_state.ollama_secili_model = ozel_model.strip()

            sicaklik_val = st.slider("Tutarlılık / Yaratıcılık (Temperature):", 0.1, 0.9, 0.4, 0.05)

            if st.button("🔄 Bağlantıyı Yenile ve Test Et", use_container_width=True):
                ok_mu, m_list = ollama_baglanti_kontrol(st.session_state.ollama_url)
                if ok_mu:
                    if m_list:
                        st.success(f"✅ Bağlantı aktif (`{st.session_state.ollama_url}`) — Modeller: {', '.join(m_list)}")
                    else:
                        st.warning("✅ Ollama servisi açık ancak hiç sohbet modeli yüklü değil. Terminalde `ollama pull qwen2.5:3b` çalıştır.")
                else:
                    st.error(
                        f"⚠️ Ollama'ya ulaşılamadı (`{st.session_state.ollama_url}`). "
                        f"Ollama uygulamasını aç veya terminalde `ollama serve` komutunu çalıştır. (Detay: {m_list})"
                    )

        with col_o2:
            st.markdown(f"#### 💬 Doğrudan Ollama'ya Sor (`{st.session_state.ollama_secili_model}`)")
            ollama_soru_input = st.text_area(
                "Ollama'ya sormak istediğin soru veya yazdırmak istediğin kod:",
                height=130,
                placeholder="Örn: Akıllı bebek arabasında yokuş aşağı inerken otomatik frenleme algoritmasını nasıl kurmalıyım?",
            )
            ob1, ob2 = st.columns(2)
            btn_ollama_sor = ob1.button("🦙 Ollama'dan Cevap Al", use_container_width=True)
            btn_ollama_sesli = ob2.button("🔊 Ollama'dan Cevap Al ve Sesli Oku", use_container_width=True)

            if btn_ollama_sor or btn_ollama_sesli:
                if ollama_soru_input.strip():
                    with st.spinner(f"🦙 Ollama ({st.session_state.ollama_secili_model}) düşünüyor..."):
                        o_yanit, o_bilgi = ollama_soru_sor(
                            ollama_soru_input.strip(),
                            model_adi=st.session_state.ollama_secili_model,
                            base_url=st.session_state.ollama_url,
                            sicaklik=sicaklik_val,
                        )
                    if o_yanit:
                        st.session_state["son_ollama_yaniti"] = o_yanit
                        if btn_ollama_sesli:
                            sesli_soyle_fn(o_yanit, dil="tr")
                    else:
                        st.warning(o_bilgi)
                else:
                    st.warning("Lütfen Ollama'ya sormak için bir soru yaz Ahmet.")

            if st.session_state.get("son_ollama_yaniti"):
                st.markdown(
                    bilgi_karti_olustur(
                        f"🦙 Ollama Yanıtı ({st.session_state.ollama_secili_model})",
                        "Yerel Yapay Zeka Motoru",
                        st.session_state["son_ollama_yaniti"].replace("\n", "<br>"),
                    ),
                    unsafe_allow_html=True,
                )

    # --- BÖLÜM 2: TDK (TÜRK DİL KURUMU) SÖZLÜK BÖLÜMÜ ---
    with tab_tdk:
        st.markdown("#### 📕 Türk Dil Kurumu (TDK) Güncel Türkçe Sözlük, Atasözleri & Deyimler")
        # Hızlı Türkçe Karakter Ekleme ve Örnek Kelimeler
        hk1, hk2, hk3, hk4, hk5 = st.columns(5)
        hizli_kelime = None
        if hk1.button("📕 bilim", use_container_width=True):
            hizli_kelime = "bilim"
        if hk2.button("📕 akıl", use_container_width=True):
            hizli_kelime = "akıl"
        if hk3.button("📕 otonom", use_container_width=True):
            hizli_kelime = "otonom"
        if hk4.button("📕 irfan", use_container_width=True):
            hizli_kelime = "irfan"
        if hk5.button("📕 mühendislik", use_container_width=True):
            hizli_kelime = "mühendislik"

        tdk_aranan = st.text_input(
            "TDK Sözlük'te Aranacak Kelimeyi Yaz:",
            value=hizli_kelime or st.session_state.get("son_tdk_kelime", "bilim"),
            placeholder="Örn: merhamet, adalet, yazılım, özerk, tefekkür...",
        )
        tb1, tb2 = st.columns(2)
        btn_tdk_ara = tb1.button("🔍 TDK Sözlük'te Ara", use_container_width=True)
        btn_tdk_ses = tb2.button("🔊 Anlamını Bul ve Sesli Oku", use_container_width=True)

        if btn_tdk_ara or btn_tdk_ses or hizli_kelime:
            secilen_k = hizli_kelime or tdk_aranan
            st.session_state["son_tdk_kelime"] = secilen_k
            sonuc = tdk_sozluk_sorgula(secilen_k)
            st.session_state["son_tdk_sonuc"] = sonuc
            if btn_tdk_ses and sonuc.get("basarili"):
                ses_metin = f"{sonuc['kelime']} kelimesinin TDK anlamı: " + " ".join(sonuc["anlamlar"])
                sesli_soyle_fn(ses_metin, dil="tr")

        aktif_tdk = st.session_state.get("son_tdk_sonuc") or tdk_sozluk_sorgula("bilim")
        if aktif_tdk.get("basarili"):
            anlam_html = "<br>".join(aktif_tdk["anlamlar"])
            ornek_html = ("<br><br><strong>📝 Örnek Cümleler:</strong><br>" + "<br>".join(aktif_tdk["ornekler"])) if aktif_tdk.get("ornekler") else ""
            atasozu_html = ("<br><br><strong>🗣️ Atasözleri & Deyimler:</strong> " + " • ".join(aktif_tdk["atasozu_deyim"])) if aktif_tdk.get("atasozu_deyim") else ""
            birlesik_html = ("<br><br><strong>🔗 Birleşik Kelimeler:</strong> " + ", ".join(aktif_tdk["birlesikler"])) if aktif_tdk.get("birlesikler") else ""
            st.markdown(
                bilgi_karti_olustur(
                    f"📕 {aktif_tdk['kelime'].upper()} — TDK Sözlük Maddesi",
                    f"Köken: {aktif_tdk.get('koken', 'Türkçe')} | {aktif_tdk.get('kaynak', 'TDK')}",
                    f"<strong>📌 Anlamları:</strong><br>{anlam_html}{ornek_html}{atasozu_html}{birlesik_html}",
                ),
                unsafe_allow_html=True,
            )
        else:
            st.warning(aktif_tdk.get("hata", "Kelime bulunamadı."))


# ==============================================================================
# 4. AÇIK KAYNAKLI YAPAY ZEKA SİTELERİ KÖPRÜSÜ (ANAHTARSIZ POLLINATIONS, GROQ,
#    HUGGING FACE, OPENROUTER VE YEREL OLLAMA TEK MERKEZDE)
# ==============================================================================
ACIK_KAYNAK_AI_SAGLAYICILARI = {
    "pollinations_free": {
        "ad": "🌐 Pollinations Açık Kaynak AI (Ücretsiz & API Anahtarsız!)",
        "url": "https://text.pollinations.ai/openai",
        "model": "openai",
        "anahtar_gerekli": False,
        "aciklama": "Hiçbir üyelik veya API anahtarı gerektirmeden internete bağlıyken doğrudan açık kaynak dil modelleriyle Türkçe sohbet üretir.",
    },
    "groq_cloud": {
        "ad": "⚡ Groq Cloud — Meta Llama 3.3 70B (Ücretsiz Hızlı API)",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "anahtar_gerekli": True,
        "site": "https://console.groq.com/keys",
        "aciklama": "Açık kaynaklı Meta Llama 3.3 70B ve Qwen 2.5 modellerini saniyede 300 kelime hızla ücretsiz çalıştıran en popüler geliştirici sitesidir.",
    },
    "huggingface": {
        "ad": "🤗 Hugging Face — Qwen 2.5 72B / Llama 3 (Açık Kaynak Merkezi)",
        "url": "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-72B-Instruct/v1/chat/completions",
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "anahtar_gerekli": True,
        "site": "https://huggingface.co/settings/tokens",
        "aciklama": "Dünyanın en büyük açık kaynak yapay zeka sitesidir. Ücretsiz 'hf_...' token alarak yüz binlerce modeli kullanabilirsin.",
    },
    "openrouter": {
        "ad": "🔀 OpenRouter — DeepSeek R1 & Llama 3.3 (:free Modeller)",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "anahtar_gerekli": True,
        "site": "https://openrouter.ai/keys",
        "aciklama": "Sonunda ':free' yazan tüm açık kaynak modelleri (DeepSeek-R1, Llama 3.3, Qwen) tek anahtarla ücretsiz sunar.",
    },
    "ollama_local": {
        "ad": "🦙 Ollama Yerel AI (Bilgisayarında İnternetsiz Çalışır)",
        "url": "http://localhost:11434",
        "model": "llama3.2",
        "anahtar_gerekli": False,
        "site": "https://ollama.com",
        "aciklama": "Bilgisayarına indirdiğin açık kaynak modelleri (llama3.2, qwen2.5, gemma2, deepseek-r1) tamamen çevrimdışı çalıştırır.",
    },
}


def _aday_yanit_puanla(metin: str, ek_baglam: str = "") -> float:
    """
    Hakem sentezi zaman aşımına uğrarsa aday yanıtlar arasından en mantıklı,
    akıcı ve açık kaynak verisiyle en uyumlu Türkçe cevabı puanlayarak seçer.
    """
    if not metin or len(metin.strip()) < 10:
        return -10.0
    m = metin.strip()
    puan = min(len(m) / 40.0, 12.0)

    # Türkçe karakter ve doğal dil yoğunluğu bonusu
    tr_karakterler = sum(1 for c in m if c in "çğıöşüÇĞİÖŞÜ")
    if tr_karakterler >= 3:
        puan += 4.0

    # Hata/sızıntı cezaları
    if "<think>" in m.lower() or "sorry, i cannot" in m.lower() or "as an ai language model" in m.lower():
        puan -= 15.0

    # Doğrulanmış açık kaynak verisiyle (ek_baglam) kelime örtüşmesi bonusu
    if ek_baglam and ek_baglam.strip():
        baglam_kelimeler = {
            k.lower() for k in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]{4,}", ek_baglam)
        }
        if baglam_kelimeler:
            metin_kelimeler = {
                k.lower() for k in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]{4,}", m)
            }
            ortak = len(baglam_kelimeler & metin_kelimeler)
            puan += min(ortak * 0.8, 14.0)

    return puan


def _bulut_anahtarli_ai_cagir(
    soru: str,
    secili: str,
    anahtar: str,
    sistem_prompt: str,
    gecmis_mesajlar: list,
    ek_baglam: str = "",
) -> tuple:
    """Seçili anahtarlı açık kaynak bulut AI sağlayıcısını (Groq / HuggingFace / OpenRouter) çağırır."""
    if secili not in ("groq_cloud", "huggingface", "openrouter") or not anahtar:
        return None, None
    bilgi = ACIK_KAYNAK_AI_SAGLAYICILARI[secili]
    try:
        payload = {
            "model": bilgi["model"],
            "messages": (
                [{"role": "system", "content": sistem_prompt}]
                + [
                    {"role": m.get("role", "user"), "content": str(m.get("content", ""))[:1400]}
                    for m in gecmis_mesajlar[-12:]
                    if m.get("role") in ("user", "assistant") and m.get("content")
                ]
                + [{"role": "user", "content": soru}]
            ),
            "temperature": 0.45 if not ek_baglam else 0.35,
            "max_tokens": 4096,
        }
        req = urllib.request.Request(
            bilgi["url"],
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {anahtar}",
                "User-Agent": "ArAIStudio/7.3",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8.5) as resp:
            veri = json.loads(resp.read().decode("utf-8"))
            cevap = _ollama_yanit_temizle(veri["choices"][0]["message"]["content"])
            if cevap:
                return cevap, f"{bilgi['model']}"
    except Exception:
        pass
    return None, None


def _pollinations_ai_cagir(
    soru: str,
    sistem_prompt: str,
    gecmis_mesajlar: list,
    ek_baglam: str = "",
    endpoint_url: str = "https://text.pollinations.ai/openai",
) -> tuple:
    """Anahtarsız ücretsiz Pollinations açık kaynak AI köprüsünü çağırır."""
    try:
        payload = {
            "model": "openai",
            "messages": (
                [{"role": "system", "content": sistem_prompt}]
                + [
                    {"role": m.get("role", "user"), "content": str(m.get("content", ""))[:1400]}
                    for m in gecmis_mesajlar[-12:]
                    if m.get("role") in ("user", "assistant") and m.get("content")
                ]
                + [{"role": "user", "content": soru}]
            ),
            "temperature": 0.45 if not ek_baglam else 0.35,
        }
        req = urllib.request.Request(
            endpoint_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ArAIStudio/7.3",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=6.5) as resp:
            ham = resp.read().decode("utf-8").strip()
            if ham.startswith("{"):
                veri = json.loads(ham)
                cevap = _ollama_yanit_temizle(veri.get("choices", [{}])[0].get("message", {}).get("content", ""))
            else:
                cevap = _ollama_yanit_temizle(ham)
            if cevap and len(cevap) > 10:
                return cevap, "Pollinations AI"
    except Exception:
        pass
    return None, None


def _ollama_ham_cagir(
    soru: str,
    ollama_url: str,
    ek_baglam: str = "",
    gecmis_mesajlar: list = None,
    sistem_prompt_ozel: str = None,
    model_adi: str = None,
) -> tuple:
    """Ollama'dan başlık öneki olmadan saf, temizlenmiş Türkçe yanıt ve etiket döndürür (thread-safe)."""
    o_yanit, o_etiket = ollama_soru_sor(
        soru,
        model_adi=model_adi,
        base_url=ollama_url,
        ek_baglam=ek_baglam,
        gecmis_mesajlar=gecmis_mesajlar,
        sistem_prompt_ozel=sistem_prompt_ozel,
    )
    if not o_yanit:
        return None, None
    saf = re.sub(r"^🦙\s*\*\*Ollama\s*\([^)]+\):\*\*\s*", "", o_yanit).strip()
    return (saf if saf else o_yanit), o_etiket


def coklu_ai_ortak_akil_sor(
    soru: str,
    saglayici_kodu: str = None,
    api_key: str = "",
    ek_baglam: str = "",
) -> tuple:
    """
    v7.4 — MANTIK ÖNCELİKLİ ÇOKLU AI & OLLAMA ORTAK AKIL KONSEYİ:
      • Hiçbir model (Ollama dahil) körü körüne ön planda tutulmaz.
      • Erişilebilir tüm kaynaklardan (Bulut Açık Kaynak AI'lar + canlıysa Yerel Ollama)
        paralel yanıt alınır ve her yanıt objektif kalite puanına tabi tutulur.
      • Bir yanıt diğerinden bariz şekilde daha mantıklı ve doğruysa (puan farkı >= 8),
        zayıf/değişik yanıtın sonucu bozmasına izin vermeden en mantıklı yanıt öne çıkar.
      • Birden fazla güçlü ve dengeli yanıt varsa Baş Hakem hepsindeki en doğru bilgileri
        tek bir akıcı, temiz Türkçe cevapta birleştirir.
    """
    secili = saglayici_kodu or st.session_state.get("acik_kaynak_saglayici", "pollinations_free")
    anahtar = (api_key or st.session_state.get("acik_kaynak_api_key", "")).strip()
    ollama_url = _ollama_url_normallestir(st.session_state.get("ollama_url", OLLAMA_VARSAYILAN_URL))
    ollama_model = st.session_state.get("ollama_secili_model", "llama3.2")
    pollinations_url = st.session_state.get("pollinations_url_ozel", "https://text.pollinations.ai/openai")
    gecmis_mesajlar = st.session_state.get("messages") or []

    sistem_prompt = (
        "Sen Ahmet tarafından geliştirilen 'Ar AI Studio' adlı Türkçe yapay zeka asistanısın. "
        "Ahmet İstanbul Fatih'te Fen ve Sosyal Bilimler Proje Okulu 9. sınıf öğrencisi; "
        f"TEKNOFEST İHA ve TÜBİTAK akıllı bebek arabası projeleri geliştiriyor. BUGÜNÜN GERÇEK TARİHİ: {_guncel_tarih_etiketi()}. Güncel açık kaynak verilerini her zaman esas al. "
        "Ahmet ile candan, samimi ve anlaşılır ama bilgi verirken son derece net, düzenli ve bozuksuz Türkçeyle konuş. "
        "Bilmediğin bir veriyi asla uydurma; <think> gibi iç düşünce etiketleri yazma."
    )
    if ek_baglam and ek_baglam.strip():
        sistem_prompt += (
            "\n\nAşağıda açık kaynaklardan (Wikipedia, TDK, Hava Durumu, Yemek Tarifleri, "
            "81 İl & 195+ Ülke, Harita, Piyasa/Kur veya Fiyat) toplanmış doğrulanmış gerçek veriler var. "
            "Bu verileri çarpıtmadan ve uydurma eklemeden kullan:\n"
            f"{ek_baglam.strip()[:6500]}"
        )

    gorevler = {}
    if secili in ("groq_cloud", "huggingface", "openrouter") and anahtar:
        gorevler["bulut_anahtarli"] = lambda: _bulut_anahtarli_ai_cagir(
            soru, secili, anahtar, sistem_prompt, gecmis_mesajlar, ek_baglam=ek_baglam
        )

    if st.session_state.get("acik_kaynak_ai_aktif", True):
        gorevler["pollinations"] = lambda: _pollinations_ai_cagir(
            soru, sistem_prompt, gecmis_mesajlar, ek_baglam=ek_baglam, endpoint_url=pollinations_url
        )

    o_canli, _ = ollama_hizli_durum_kontrol(ollama_url)
    if o_canli:
        gorevler["ollama"] = lambda: _ollama_ham_cagir(
            soru, ollama_url, ek_baglam=ek_baglam, gecmis_mesajlar=gecmis_mesajlar, model_adi=ollama_model
        )

    if not gorevler:
        return None, None

    adaylar = []
    baslangic_t = time.time()
    ilk_yanit_t = None
    havuz = ThreadPoolExecutor(max_workers=len(gorevler))
    gelecekler = {havuz.submit(fn): ad for ad, fn in gorevler.items()}
    bekleyen = set(gelecekler.keys())
    try:
        while bekleyen:
            simdi = time.time()
            if ilk_yanit_t is not None:
                en_yuksek_puan = max((a[0] for a in adaylar), default=0.0)
                ek_bekleme = 2.0 if en_yuksek_puan >= 14.0 else 3.5
                kalan = min(ek_bekleme - (simdi - ilk_yanit_t), 7.0 - (simdi - baslangic_t))
            else:
                kalan = 7.0 - (simdi - baslangic_t)
            if kalan <= 0.05:
                break
            bitenler, bekleyen = wait(bekleyen, timeout=kalan, return_when=FIRST_COMPLETED)
            if not bitenler:
                break
            for fut in bitenler:
                try:
                    metin, etiket = fut.result(timeout=0.1)
                    if metin and etiket:
                        puan = _aday_yanit_puanla(metin, ek_baglam)
                        if puan > 0:
                            adaylar.append((puan, etiket, metin))
                            if ilk_yanit_t is None:
                                ilk_yanit_t = time.time()
                except Exception:
                    pass
    except Exception:
        pass
    finally:
        havuz.shutdown(wait=False, cancel_futures=True)

    if not adaylar:
        return None, None

    # En mantıklı ve tutarlı yanıt her zaman listenin en başında!
    adaylar.sort(key=lambda x: x[0], reverse=True)

    # Tek geçerli kaynak varsa doğrudan temiz sunumla döndür
    if len(adaylar) == 1:
        _, tek_etiket, tek_metin = adaylar[0]
        return f"🤖 **Ar AI:**\n\n{tek_metin}", tek_etiket

    # En iyi aday ile ikinci aday arasında büyük kalite farkı varsa zayıf adayı karıştırma!
    en_iyi_puan, en_iyi_etiket, en_iyi_metin = adaylar[0]
    ikinci_puan = adaylar[1][0]
    if (en_iyi_puan - ikinci_puan) >= 6.5:
        return (
            f"🧠 **Ar AI (En Mantıklı Seçim — {en_iyi_etiket}):**\n\n{en_iyi_metin}",
            f"Ortak Akıl (Öncelikli: {en_iyi_etiket})",
        )

    # Birden fazla güçlü ve dengeli yanıt -> Baş Hakem Sentezi
    guclu_adaylar = [a for a in adaylar if (en_iyi_puan - a[0]) < 6.5]
    katilanlar = [e for _, e, _ in guclu_adaylar]
    aday_bloklari = []
    for idx, (_, etiket, metin) in enumerate(guclu_adaylar, 1):
        aday_bloklari.append(f"### Kaynak {idx} ({etiket}):\n{metin[:2200]}")
    aday_metni = "\n\n".join(aday_bloklari)

    hakem_sistem = (
        "Sen Ar AI Studio'nun Baş Hakem (Ortak Akıl) Sentez Motorusun. "
        "Görevin: Farklı açık kaynak yapay zekalardan gelen yanıtları ve varsa doğrulanmış "
        "açık kaynak verilerini karşılaştırmak; çelişkili, uydurma veya garip kısımları tamamen elemek "
        "ve her kaynaktaki en doğru, en mantıklı bilgileri tek bir akıcı, samimi Türkçe cevapta birleştirmek.\n"
        "KESİN KURALLAR:\n"
        "1. 'Kaynak 1 şöyle dedi' gibi teknik meta ifadeler yazma; doğrudan Ahmet'e en mantıklı nihai cevabı ver.\n"
        "2. Doğrulanmış açık kaynak verisi varsa sayılarda ve olgularda her zaman ona sadık kal.\n"
        "3. Yalnızca temiz Türkçe yaz; <think> veya İngilizce kalıntı bırakma."
    )
    hakem_soru = (
        f"Ahmet'in Sorusu: {soru}\n\n"
        + (f"Doğrulanmış Açık Kaynak Verisi:\n{ek_baglam.strip()[:3500]}\n\n" if (ek_baglam and ek_baglam.strip()) else "")
        + f"Aday Yanıtlar:\n{aday_metni}\n\n"
        "En mantıklı, en doğru ve en anlaşılır tek Türkçe yanıtı yaz:"
    )

    nihai_cevap = None
    # Baş Hakem seçiminde de güç ve tutarlılık sırası (70B Bulut > Pollinations > Yerel Ollama)
    if secili in ("groq_cloud", "huggingface", "openrouter") and anahtar:
        nihai_cevap, _ = _bulut_anahtarli_ai_cagir(
            hakem_soru, secili, anahtar, hakem_sistem, [], ek_baglam=""
        )
    if not nihai_cevap and st.session_state.get("acik_kaynak_ai_aktif", True):
        nihai_cevap, _ = _pollinations_ai_cagir(
            hakem_soru, hakem_sistem, [], ek_baglam="", endpoint_url=pollinations_url
        )
    if not nihai_cevap and o_canli:
        nihai_cevap, _ = _ollama_ham_cagir(
            hakem_soru, ollama_url, ek_baglam="", gecmis_mesajlar=[], sistem_prompt_ozel=hakem_sistem, model_adi=ollama_model
        )

    birlesik_etiket = " + ".join(katilanlar)
    if nihai_cevap:
        return (
            f"🧠 **Ar AI (Ortak Akıl):**\n\n{nihai_cevap}",
            f"Ortak Akıl ({birlesik_etiket})",
        )

    return (
        f"🧠 **Ar AI (En Mantıklı Seçim):**\n\n{en_iyi_metin}",
        f"Ortak Akıl ({en_iyi_etiket})",
    )


def acik_kaynak_ai_sor(soru: str, saglayici_kodu: str = None, api_key: str = "", ek_baglam: str = "") -> tuple:
    """
    v7.4 — Mantık Öncelikli Birleşik Açık Kaynak AI & Yerel Ollama Akışı:
      • Varsayılan Ortak Akıl modunda tüm erişilebilir kaynaklardan paralel görüş alıp
        hangisi en mantıklıysa onu (veya Baş Hakem sentezini) ön plana çıkarır.
      • Tekli modda da Ollama zorla öne geçmez: önce güçlü bulut açık kaynak AI,
        bulut erişilemezse veya kullanıcı özellikle 'ollama:' yazarsa yerel Ollama devreye girer.
    """
    secili = saglayici_kodu or st.session_state.get("acik_kaynak_saglayici", "pollinations_free")
    anahtar = (api_key or st.session_state.get("acik_kaynak_api_key", "")).strip()
    ollama_url = _ollama_url_normallestir(st.session_state.get("ollama_url", OLLAMA_VARSAYILAN_URL))
    ollama_model = st.session_state.get("ollama_secili_model", "llama3.2")
    pollinations_url = st.session_state.get("pollinations_url_ozel", "https://text.pollinations.ai/openai")
    gecmis_mesajlar = st.session_state.get("messages") or []

    # 0. Çoklu AI + Ollama Ortak Akıl Konseyi (Hangisi mantıklıysa o ön planda!)
    if st.session_state.get("ortak_akil_aktif", True) and saglayici_kodu != "ollama_local":
        konsey_yanit, konsey_etiket = coklu_ai_ortak_akil_sor(
            soru, saglayici_kodu=secili, api_key=anahtar, ek_baglam=ek_baglam
        )
        if konsey_yanit:
            return konsey_yanit, konsey_etiket

    sistem_prompt = (
        "Sen Ahmet tarafından geliştirilen 'Ar AI Studio' adlı Türkçe yapay zeka asistanısın. "
        "Ahmet İstanbul Fatih'te Fen ve Sosyal Bilimler Proje Okulu 9. sınıf öğrencisi, "
        f"TEKNOFEST İHA ve TÜBİTAK akıllı bebek arabası projeleri geliştiriyor. BUGÜNÜN GERÇEK TARİHİ: {_guncel_tarih_etiketi()}. Güncel açık kaynak verilerini her zaman esas al. "
        "Ahmet ile candan, samimi ve sıcakkanlı ama bilgi verirken son derece net, düzenli ve bozuksuz bir Türkçeyle sohbet et. "
        "Bilmediğin bir veriyi asla uydurma; <think> gibi iç düşünce etiketleri kullanma."
    )
    if ek_baglam and ek_baglam.strip():
        sistem_prompt += (
            "\n\nAşağıda Ar AI otonom ajanının açık kaynaklardan (Wikipedia, TDK, Hava Durumu, "
            "Yemek Tarifleri, 81 İl & 195+ Ülke, Harita, Piyasa/Kur veya Fiyat) senin için topladığı "
            "doğrulanmış güncel veriler var. Bu verileri çarpıtmadan, kopyala-yapıştır yapmadan "
            "Ahmet'e çok akıcı, candan ve mantıklı tek bir Türkçe cevap olarak sentezle:\n"
            f"{ek_baglam[:8000]}"
        )

    # Kullanıcı açıkça 'ollama:' yazdıysa veya sağlayıcı olarak özellikle ollama_local seçtiyse
    if saglayici_kodu == "ollama_local" or secili == "ollama_local":
        o_yanit, o_etiket = ollama_soru_sor(
            soru,
            base_url=ollama_url,
            ek_baglam=ek_baglam,
            gecmis_mesajlar=gecmis_mesajlar,
        )
        if o_yanit:
            return o_yanit, o_etiket

    # 1. Anahtarlı güçlü açık kaynak bulut AI (Groq 70B / HuggingFace 72B / OpenRouter)
    c_metin, c_etiket = _bulut_anahtarli_ai_cagir(
        soru, secili, anahtar, sistem_prompt, gecmis_mesajlar, ek_baglam=ek_baglam
    )
    if c_metin:
        return f"🤖 **Ar AI ({c_etiket}):**\n\n{c_metin}", f"Açık Kaynak AI ({secili})"

    # 2. Anahtarsız Pollinations Açık Kaynak AI
    if st.session_state.get("acik_kaynak_ai_aktif", True):
        p_metin, p_etiket = _pollinations_ai_cagir(
            soru, sistem_prompt, gecmis_mesajlar, ek_baglam=ek_baglam, endpoint_url=pollinations_url
        )
        if p_metin:
            return f"🤖 **Ar AI:**\n\n{p_metin}", "Açık Kaynak AI (Canlı)"

    # 3. Yerel Ollama (Bulut kotası dolduysa veya internet kesikse otomatik devreye girer)
    o_canli, _ = ollama_hizli_durum_kontrol(ollama_url)
    if o_canli:
        o_yanit, o_etiket = ollama_soru_sor(
            soru,
            base_url=ollama_url,
            ek_baglam=ek_baglam,
            gecmis_mesajlar=gecmis_mesajlar,
        )
        if o_yanit:
            return o_yanit, f"{o_etiket} (Yerel Yedek)"

    return None, None
