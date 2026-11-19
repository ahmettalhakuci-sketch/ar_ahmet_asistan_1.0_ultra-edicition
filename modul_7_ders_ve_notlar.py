# -*- coding: utf-8 -*-
"""
==============================================================================
AR AI STUDIO v4.0 — MODÜL 7: 9. SINIF TÜM DERS ÖZETLERİ, KİŞİSEL DERS NOTLARI VE
GÜNLÜK SORU ÇÖZÜM TAKİP MERKEZİ (modul_7_ders_ve_notlar.py)
==============================================================================
"""
from datetime import datetime
import json
import streamlit as st
import importlib.util
import os
import sys

_MODUL_DIZINI = os.path.dirname(os.path.abspath(__file__))
if _MODUL_DIZINI not in sys.path:
    sys.path.insert(0, _MODUL_DIZINI)


def _guvenli_modul_yukle(modul_adi: str):
    if modul_adi in sys.modules and getattr(sys.modules[modul_adi], "__file__", None):
        return sys.modules[modul_adi]
    aday_yollar = [os.path.join(_MODUL_DIZINI, f"{modul_adi}.py")]
    for _ana in [_MODUL_DIZINI, os.path.dirname(_MODUL_DIZINI)]:
        for _kok, _altlar, _dosyalar in os.walk(_ana):
            _altlar[:] = [d for d in _altlar if not d.startswith(".") and d not in ("__pycache__", "venv", ".venv")]
            if f"{modul_adi}.py" in _dosyalar:
                tam = os.path.join(_kok, f"{modul_adi}.py")
                if tam not in aday_yollar:
                    aday_yollar.append(tam)
    for yol in aday_yollar:
        if os.path.exists(yol):
            spec = importlib.util.spec_from_file_location(modul_adi, yol)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[modul_adi] = mod
                spec.loader.exec_module(mod)
                return mod
    return __import__(modul_adi)

_m1 = _guvenli_modul_yukle("modul_1_arayuz_ve_tema")
DERS_NOTLARI_DOSYASI = _m1.DERS_NOTLARI_DOSYASI
SORU_TAKIP_DOSYASI = _m1.SORU_TAKIP_DOSYASI
bilgi_karti_olustur = _m1.bilgi_karti_olustur

DOKUZUNCU_SINIF_DERS_OZETLERI = {   '⚗️ Kimya (9. Sınıf)': {   'konular': 'Kimya Bilimi, Atom ve Periyodik Sistem, Kimyasal Türler '
                                          'Arası Etkileşimler, Maddenin Halleri',
                               'ozet': '• **Atom Yapısı:** `Kütle Numarası (A) = Proton (Z) + '
                                       'Nötrön (n)`. Nötr atomda `Proton = Elektron`.\n'
                                       '• **Periyodik Cetvel:** Soldan sağa gidildikçe atom çapı '
                                       'küçülür, iyonlaşma enerjisi (3A-2A ve 6A-5A küresel '
                                       'simetri istisnası hariç) ve elektronegatiflik artar.\n'
                                       '• **Güçlü Etkileşimler (Kimyasal Bağlar):** İyonik bağ '
                                       '(metal + ametal, elektron alışverişi), Kovalent bağ '
                                       '(ametal + ametal, elektron ortaklaşması) ve Metalik bağ.\n'
                                       '• **Zayıf Etkileşimler:** Hidrojen bağı (`H` atomunun `F, '
                                       'O, N` ile yaptığı güçlü fiziksel bağ) ve Van der Waals '
                                       'kuvvetleri.'},
    '⚡ Fizik (9. Sınıf)': {   'konular': 'Fizik Bilimine Giriş, Madde ve Özellikleri, Hareket ve '
                                         'Kuvvet, Enerji, Isı ve Sıcaklık, Elektrostatik',
                              'ozet': '• **Kuvvet & Hareket:** Yer değiştirme `Δx = x_son - '
                                      "x_ilk`, Hız `v = Δx / Δt`, İvme `a = Δv / Δt`, Newton'un 2. "
                                      'Yasası `F_net = m · a`.\n'
                                      '• **Madde ve Özkütle:** Özkütle `d = m / V` (Kütle / '
                                      'Hacim). Dayanıklılık `Kesit Alanı / Hacim` (`1/h`) ile '
                                      'orantılıdır.\n'
                                      '• **İş, Güç ve Enerji:** İş `W = F · Δx`, Güç `P = W / t`, '
                                      'Kinetik Enerji `E_k = ½ m v²`, Potansiyel Enerji `E_p = m g '
                                      'h`.\n'
                                      '• **Isı ve Sıcaklık:** `Q = m · c · ΔT` (Hal değişiminde `Q '
                                      '= m · L`).'},
    '🌍 Coğrafya (9. Sınıf)': {   'konular': "Doğa ve İnsan, Dünya'nın Şekli ve Hareketleri, "
                                            'Coğrafi Konum, Harita Bilgisi, İklim Bilgisi',
                                 'ozet': '• **Coğrafi Konum:** Paraleller (1° arası 111 km) ve '
                                         'Meridyenler (ardışık iki meridyen arası 4 dakika yerel '
                                         'saat farkı).\n'
                                         '• **Harita Bilgisi:** `Gerçek Uzunluk = Harita Uzunluğu '
                                         '× Ölçek Paydası`. Payda büyüdükçe ölçek küçülür.\n'
                                         '• **İklim Elemanları:** Sıcaklık, basınç ve rüzgârlar '
                                         '(Kayıp Sakal: Karayel, Yıldız, Poyraz - Samyeli, Kıble, '
                                         'Lodos), nem ve yağış.'},
    '💻 Bilişim Teknolojileri & Yazılım Mühendisliği (Proje Özel)': {   'konular': 'Algoritma '
                                                                                  'Tasarımı, '
                                                                                  'Python Veri '
                                                                                  'Yapıları, Nesne '
                                                                                  'Yönelimli '
                                                                                  'Programlama '
                                                                                  '(OOP), Gömülü '
                                                                                  'Sistemler '
                                                                                  '(Arduino/ESP32)',
                                                                       'ozet': '• **Veri '
                                                                               'Yapıları:** `dict` '
                                                                               '(Hash tablosu, '
                                                                               '`O(1)` arama '
                                                                               'hızı), `list` '
                                                                               '(dinamik dizi), '
                                                                               '`set` (benzersiz '
                                                                               'küme), `tuple` '
                                                                               '(değişmez dizi).\n'
                                                                               '• **Sensör & '
                                                                               'Kontrol:** HC-SR04 '
                                                                               'ultrasonik mesafe '
                                                                               '`d = (t × 0.034) / '
                                                                               '2`, PID kontrol '
                                                                               '`u(t) = Kp·e + '
                                                                               'Ki·∫e·dt + '
                                                                               'Kd·de/dt`.'},
    '📐 Matematik (9. Sınıf Proje Okulu)': {   'konular': 'Mantık, Kümeler, Denklemler ve '
                                                         'Eşitsizlikler, Üslü ve Köklü İfadeler, '
                                                         'Oran-Orantı, Üçgenler',
                                              'ozet': '• **Mantık:** `p ∧ q` (ve) sadece ikisi de '
                                                      "1 iken 1'dir; `p ∨ q` (veya) ikisi de 0 "
                                                      "iken 0'dır; `p ⇒ q ≡ p' ∨ q`.\n"
                                                      '• **Kümeler:** `s(A ∪ B) = s(A) + s(B) - '
                                                      's(A ∩ B)`. Alt küme sayısı `2ⁿ`, öz alt '
                                                      'küme sayısı `2ⁿ - 1`.\n'
                                                      '• **Üslü & Köklü Sayılar:** `aⁿ · aᵐ = '
                                                      'aⁿ⁺ᵐ`, `√(a²·b) = |a|√b`. Paydada kök varsa '
                                                      'eşleniğiyle çarpılır.\n'
                                                      '• **Üçgenler:** Pisagor `a² + b² = c²`; '
                                                      'açıortay, kenarortay (ağırlık merkezi `G`, '
                                                      '`k` ve `2k` oranı) ve benzerlik '
                                                      'teoremleri.'},
    '📖 Türk Dili ve Edebiyatı & Tarih (9. Sınıf)': {   'konular': 'Hikâye, Şiir, Masal/Fabl, '
                                                                  'Roman, İslamiyet Öncesi ve İlk '
                                                                  'Türk-İslam Devletleri Tarihi',
                                                       'ozet': '• **Edebiyat:** Olay hikâyesi '
                                                               '(Maupassant tarzı - Ömer '
                                                               'Seyfettin) ve Durum hikâyesi '
                                                               '(Çehov tarzı - Sait Faik, Memduh '
                                                               "Şevket Esendal). Mustafa Kutlu'nun "
                                                               '*Uzun Hikâye* eseri.\n'
                                                               '• **Tarih:** Tarih biliminin '
                                                               'yöntemi (Tarama, Tasnif, Tahlil, '
                                                               'Tenkit, Terkip), İlk Çağ '
                                                               'medeniyetleri, İslamiyet öncesi '
                                                               'Türk devletleri (Hun, Göktürk, '
                                                               'Uygur) ve Karahanlılar / '
                                                               'Gazneliler / Büyük Selçuklu '
                                                               'Devleti.'},
    '🕌 Din Kültürü ve Ahlak Bilgisi & Arapça (9. Sınıf)': {   'konular': "Bilgi ve İnanç, İslam'da "
                                                                         'Bilgi Kaynakları (Selim '
                                                                         'Akıl, Sadık Haber, Salim '
                                                                         'Duyular), İbadet, Ahlak '
                                                                         've Değerler',
                                                              'ozet': "• **İslam'da Bilgi "
                                                                      'Kaynakları:** 1) **Sadık '
                                                                      'Haber** (Vahiy ve Mütevatir '
                                                                      'Haber), 2) **Selim Akıl**, '
                                                                      '3) **Salim Duyular**.\n'
                                                                      '• **İman Esasları '
                                                                      "(Âmentü):** Allah'a, "
                                                                      'meleklerine, kitaplarına, '
                                                                      'peygamberlerine, ahiret '
                                                                      'gününe ve kaza/kadere '
                                                                      'iman.\n'
                                                                      "• **Mükellefiyet ve Ef'âl-i "
                                                                      'Mükellefîn:** Farz '
                                                                      '(Ayn/Kifaye), Vacip, Sünnet '
                                                                      '(Müekked/Gayri Müekked), '
                                                                      'Müstehap, Mübah, Mekruh, '
                                                                      'Haram.'},
    '🧬 Biyoloji (9. Sınıf)': {   'konular': 'Yaşam Bilimi Biyoloji, Canlıların Ortak Özellikleri, '
                                            'İnorganik/Organik Bileşikler, Hücre, Canlılar Dünyası',
                                 'ozet': '• **Organik Bileşikler:** Karbonhidratlar (glikozit '
                                         'bağı, 1. sırada enerji), Lipitler (ester bağı), '
                                         'Proteinler (amino asit + peptit bağı, yapıcı-onarıcı), '
                                         'Enzimler (aktivasyon enerjisini düşüren biyolojik '
                                         'katalizörler), ATP ve DNA/RNA.\n'
                                         '• **Hücre Organelleri:** **Ribozom** (zarsız, protein '
                                         'sentezi), **Mitokondri** (çift zarlı, oksijenli '
                                         'solunumla ATP üretimi), **Kloroplast** (fotosentez), '
                                         '**Golgi** (salgı ve paketleme), **Lizozom** (hücre içi '
                                         'sindirim).'}}

def ders_notlarini_oku():
    if os.path.exists(DERS_NOTLARI_DOSYASI):
        try:
            with open(DERS_NOTLARI_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {
            "ders": "Matematik",
            "baslik": "Köklü Sayılar ve Eşlenik Kuralları",
            "etiket": "Önemli Formül",
            "icerik": "√72 = 6√2. Paydada √a varsa √a ile, (√a - √b) varsa (√a + √b) ile çarpılır.",
            "tarih": "2026-11-16 14:00",
        },
        {
            "ders": "Fizik",
            "baslik": "Newton'un Hareket Yasaları & İHA Kuvvet Analizi",
            "etiket": "Sınav Notu",
            "icerik": "F_net = m.a formülünde İHA'nın yukarı ivmelenmesi için Toplam İtki > m.g olmalıdır.",
            "tarih": "2026-11-16 14:15",
        },
    ]


def ders_notu_kaydet(ders: str, baslik: str, etiket: str, icerik: str):
    mevcut = ders_notlarini_oku()
    mevcut.insert(
        0,
        {
            "ders": ders,
            "baslik": baslik.strip(),
            "etiket": etiket,
            "icerik": icerik.strip(),
            "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
    )
    with open(DERS_NOTLARI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(mevcut, f, ensure_ascii=False, indent=4)


def soru_takip_oku():
    if os.path.exists(SORU_TAKIP_DOSYASI):
        try:
            with open(SORU_TAKIP_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {"ders": "Matematik", "konu": "Köklü ve Üslü Sayılar", "soru_sayisi": 40, "sure_dk": 50, "tarih": "2026-11-16"},
        {"ders": "Fizik", "konu": "Hareket ve Kuvvet", "soru_sayisi": 25, "sure_dk": 35, "tarih": "2026-11-16"},
    ]


def soru_takip_ekle(ders: str, konu: str, soru_sayisi: int, sure_dk: int):
    kayitlar = soru_takip_oku()
    kayitlar.insert(
        0,
        {
            "ders": ders,
            "konu": konu.strip(),
            "soru_sayisi": int(soru_sayisi),
            "sure_dk": int(sure_dk),
            "tarih": datetime.now().strftime("%Y-%m-%d"),
        },
    )
    with open(SORU_TAKIP_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(kayitlar, f, ensure_ascii=False, indent=4)




def ders_ve_notlar_studyosu_goster(sesli_soyle_fn):
    st.subheader("📚 9. Sınıf Ders Özetleri, Kişisel Ders Notları & Soru Çözüm Takip Merkezi")
    d_tab1, d_tab2, d_tab3 = st.tabs([
        "📝 Ders Notlarım & Yeni Not Ekle",
        "📖 9. Sınıf Hızlı Ders & Formül Özetleri",
        "✅ Günlük Çalışılan Ders & Soru Takibi",
    ])

    with d_tab1:
        col_dn1, col_dn2 = st.columns([1.05, 1.45], gap="large")
        with col_dn1:
            st.markdown("#### ➕ Yeni Ders Notu Kaydet")
            with st.form("yeni_ders_notu_formu", clear_on_submit=True):
                sec_ders = st.selectbox(
                    "Ders Seç:",
                    ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türk Dili ve Edebiyatı", "Tarih", "Coğrafya", "Din Kültürü", "İngilizce", "Arapça", "Bilişim & Yazılım"],
                )
                sec_etiket = st.selectbox(
                    "Not Türü:",
                    ["📌 Sınavda Çıkar", "📐 Önemli Formül", "📝 Konu Özeti", "📚 Ödev / Tekrar"],
                )
                not_baslik = st.text_input("Konu Başlığı:", placeholder="Örn: Köklü Sayılarda Eşlenik")
                not_icerik = st.text_area("Ders Notun:", height=120, placeholder="Formülü, kuralı veya önemli noktayı buraya yaz...")
                if st.form_submit_button("💾 Ders Notunu Kaydet", use_container_width=True):
                    if not_baslik.strip() and not_icerik.strip():
                        ders_notu_kaydet(sec_ders, not_baslik, sec_etiket, not_icerik)
                        st.success(f"{sec_ders} notu başarıyla kaydedildi!")
                        st.rerun()
                    else:
                        st.warning("Lütfen konu başlığını ve not içeriğini doldur.")

        with col_dn2:
            st.markdown("#### 🗂️ Kayıtlı Ders Notlarım")
            tum_ders_notlari = ders_notlarini_oku()
            filtre_ders = st.selectbox(
                "Derse Göre Filtrele:",
                ["Tümü", "Matematik", "Fizik", "Kimya", "Biyoloji", "Türk Dili ve Edebiyatı", "Tarih", "Coğrafya", "Din Kültürü", "İngilizce", "Arapça", "Bilişim & Yazılım"],
            )
            for idx_dn, dn in enumerate(tum_ders_notlari):
                if filtre_ders != "Tümü" and dn["ders"] != filtre_ders:
                    continue
                st.markdown(
                    bilgi_karti_olustur(
                        f"📘 [{dn['ders']}] {dn['baslik']}",
                        f"{dn['etiket']} | 🕒 {dn['tarih']}",
                        dn["icerik"].replace("\n", "<br>"),
                    ),
                    unsafe_allow_html=True,
                )
                if st.button(f"🔊 Notu Sesli Dinle #{idx_dn + 1}", key=f"ders_not_dinle_{idx_dn}"):
                    sesli_soyle_fn(f"{dn['ders']} dersi, {dn['baslik']}. {dn['icerik']}", dil="tr")

    with d_tab2:
        secili_ozet_ders = st.selectbox("9. Sınıf Ders Özeti Seç:", list(DOKUZUNCU_SINIF_DERS_OZETLERI.keys()))
        ozet_veri = DOKUZUNCU_SINIF_DERS_OZETLERI[secili_ozet_ders]
        st.markdown(
            bilgi_karti_olustur(
                secili_ozet_ders,
                f"📚 Müfredat Konuları: {ozet_veri['konular']}",
                ozet_veri["ozet"].replace("\n", "<br>"),
            ),
            unsafe_allow_html=True,
        )
        if st.button("🔊 Bu Ders Özetini Sesli Anlat"):
            sesli_soyle_fn(ozet_veri["ozet"], dil="tr")

    with d_tab3:
        kayitlar = soru_takip_oku()
        toplam_soru = sum(k.get("soru_sayisi", 0) for k in kayitlar)
        toplam_dk = sum(k.get("sure_dk", 0) for k in kayitlar)
        sk1, sk2, sk3 = st.columns(3)
        sk1.metric("Toplam Çözülen Soru", f"{toplam_soru} Soru", "Aktif Takip")
        sk2.metric("Toplam Çalışma Süresi", f"{toplam_dk} Dakika", f"{toplam_dk / 60:.1f} Saat")
        sk3.metric("Kayıtlı Çalışma Oturumu", f"{len(kayitlar)} Oturum", "9. Sınıf")

        c_st1, c_st2 = st.columns([1.0, 1.4], gap="large")
        with c_st1:
            with st.form("soru_takip_formu", clear_on_submit=True):
                st_ders = st.selectbox("Çalışılan Ders:", ["Matematik", "Fizik", "Kimya", "Biyoloji", "Edebiyat", "Tarih", "Coğrafya", "İngilizce", "Arapça"])
                st_konu = st.text_input("Çalışılan Konu:", placeholder="Örn: Üslü Sayılar Test Çözümü")
                st_soru = st.number_input("Çözülen Soru Sayısı:", min_value=1, max_value=500, value=25, step=5)
                st_sure = st.number_input("Çalışma Süresi (Dakika):", min_value=5, max_value=600, value=40, step=5)
                if st.form_submit_button("➕ Çalışmayı Kaydet", use_container_width=True):
                    soru_takip_ekle(st_ders, st_konu or "Genel Tekrar", st_soru, st_sure)
                    st.success("Çalışma kaydı eklendi Ahmet!")
                    st.rerun()
        with c_st2:
            for k_item in kayitlar[:10]:
                st.markdown(
                    bilgi_karti_olustur(
                        f"✅ {k_item['ders']} — {k_item['konu']}",
                        f"📅 {k_item['tarih']} | ⏱️ {k_item['sure_dk']} dk",
                        f"Bu oturumda **{k_item['soru_sayisi']} soru** çözüldü.",
                    ),
                    unsafe_allow_html=True,
                )
