# ⚡ Ar AI Studio v9.3 — Modüler Türkçe Yapay Zeka Asistanı

**Ar AI Studio**, Python ve Streamlit ile geliştirilmiş; çoklu açık kaynak bilgi ağlarını, yerel ve bulut yapay zeka motorlarını, 13 modüllü kendini onaran (self-healing) mimariyi ve siber güvenlik kalkanını tek merkezde birleştiren Türkçe yapay zeka asistanıdır.

## ✨ Öne Çıkan Özellikler

* **🧠 Otonom Mantık & Çok Turlu Bağlam Motoru:** Sorunun niyetini otomatik analiz eder; aktif konuyu koruyarak `"nerede?"`, `"daha fazla bilgi verir misiniz?"`, `"kısaca anlat"` gibi devam sorularını bağlam kopmadan yanıtlar.
* **🌐 Canlı Açık Kaynak Bilgi Ağı (15+ Servis):**
  * **Wikipedia (Tam-Metin) & TDK Güncel Türkçe Sözlük**
  * **Türkiye 81 İl & Dünya 195+ Ülke** (REST Countries + Paralel Wikipedia)
  * **Canlı Hava Durumu, Avrupa Hava Kalitesi (AQI) & UV İndeksi** (Open-Meteo)
  * **Kimya & Bileşik Formülü Motoru** (PubChem PUG-REST + Türkçe Kimya Tabanı)
  * **Namaz Vakitleri (Diyanet Method 13) & Hicri Takvim** (AlAdhan)
  * **TEKNOFEST / TÜBİTAK 2204-A & Akademik Makaleler** (arXiv API)
  * **Türkiye Canlı Deprem Takibi** (USGS Earthquake GeoJSON)
  * **Canlı Türkçe Haber & Web Arama** (Google News TR RSS + DuckDuckGo)
  * **Güncel Altın, Döviz, Kripto & Futbolcu Piyasa Değerleri**
  * **Şef Yemek Tarifleri, Pratik Yapım Rehberleri & Tarihi Yapıtlar**
* **🤖 Hibrit Yapay Zeka & Yerel Ollama:** Pollinations, Groq (Llama 3.3 70B), Hugging Face, OpenRouter ve yerel **Ollama** (`127.0.0.1:11434`) desteği; isteğe bağlı **Ortak Akıl Konseyi** ve kelime kelime akışlı yanıt (`st.write_stream`).
* **🧮 Eğitim, Dil & Mühendislik Stüdyoları:** 2. derece denklem ve sözel matematik çözücü, 30 İslam Âlimi, 3D çevirmeli dil kartları, Neural TTS sesli okuma ve TEKNOFEST İHA / Akıllı Bebek Arabası hesaplayıcıları.
* **🛡️ Siber Güvenlik Kalkanı:** SQLi, XSS, RCE, Path Traversal, zararlı bot engelleme, SHA-256 + sabit zamanlı PIN doğrulaması ve acil durum ZIP yedekleme.

## 🚀 Kurulum ve Çalıştırma

### Yerel Bilgisayarda
```bash
pip install -r requirements.txt
streamlit run main.py
```
> **Not:** `main.py` çalıştırıldığında 13 yardımcı modülü proje klasörüne otomatik olarak kurar ve güncel tutar.

### Streamlit Community Cloud (Bulut Yayını)
1. Bu depoyu [share.streamlit.io](https://share.streamlit.io/) üzerinden bağlayın.
2. Ana dosya olarak `main.py` seçin ve **Deploy** butonuna tıklayın.
3. İsteğe bağlı olarak **Settings → Secrets** bölümüne `AR_ADMIN_PIN = "gizli_pininiz"` ekleyerek yönetici PIN kodunu güvenli biçimde tanımlayın.

## 📁 Depo Yapısı
* `main.py` — Ana uygulama ve 13 modüllü otomatik kurucu arşiv
* `requirements.txt` — Gerekli Python kütüphaneleri
* `.gitignore` — Yerel log, yedek ve gizli anahtarların GitHub'a yüklenmesini engeller
* `README.md` — Proje tanıtım ve kurulum rehberi
