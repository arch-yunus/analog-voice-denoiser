<p align="center">
  <img src="assets/signal_analysis.png" width="800" alt="Analog Voice Denoiser Görsel Analiz">
</p>

# Analog Voice Denoiser (AVD)

[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Durum: Araştırma](https://img.shields.io/badge/Durum-Ara%C5%9Ft%C4%B1rma-orange.svg)]()

**Analog Voice Denoiser (AVD)**, ses kayıtlarındaki spektral gürültüyü, statik paraziti ve analog hışırtıyı nötralize etmek için tasarlanmış yüksek sadakatli bir ses işleme aracıdır. Gelişmiş STFT (Short-Time Fourier Transform) ve Spektral Maskeleme algoritmalarını kullanan AVD, gürültü tabanını cerrahi bir hassasiyetle bastırırken insan vokal frekanslarını izole eder.

---

## 🔬 Temel Metodoloji

AVD, hassas sinyal manipülasyonu sağlamak için frekans domaininde çalışır. Süreç titiz bir boru hattını takip eder:

1.  **Short-Time Fourier Transform (STFT):** Sinyalin zamanla değişen frekans içeriğini yakalamak için parçalı dönüşüm uygulaması.
2.  **Wiener Filtreleme:** Güç spektral yoğunluğu tabanlı, sinyalin gürültülü kısımlarını baskılayan adaptif filtreleme.
3.  **VAD (Ses Aktivite Algılama):** Enerji tabanlı ses algılama ile sadece aktif konuşma alanlarının korunması.
4.  **Ters STFT (ISTFT):** Temizlenmiş sinyalin yüksek sadakatli çıktı için zaman domainine geri dönüştürülmesi.

## 🌟 Öne Çıkan Özellikler

- **Gelişmiş STFT Mimari:** Minimum faz distorsiyonu ile hassas, zaman-frekans tabanlı gürültü bastırma.
- **Dinamik Eşikleme:** Değişen kayıt ortamlarına uyum sağlayan adaptif gürültü tabanı algılama.
- **WAV I/O Desteği:** Standart .wav dosyalarını okuma, işleme ve yüksek çözünürlüklü olarak kaydetme.
- **Profesyonel Türkçe Dokümantasyon:** Teknik standartlara uygun, tamamen Türkçe içerik.
- **Entegre Görselleştirici:** Gerçek zamanlı spektral izleme için profesyonel düzeyde kontrol paneli.

## 📊 Analitik Kontrol Paneli

Proje, gürültü giderme performansını, SNR (Sinyal-Gürültü Oranı) iyileştirmelerini ve sistem gecikmesini izlemek için premium bir görsel arayüz sunan `DASHBOARD.html` dosyasını içerir. Modern web teknolojilerini kullanarak yüksek kaliteli bir ses mühendisliği iş istasyonunu simüle eder.

## 🛠 Kurulum ve Kullanım

### Gereksinimler
- Python 3.8 veya üzeri
- NumPy

### Hızlı Başlangıç
```bash
# Depoyu klonlayın
git clone https://github.com/bahattinyunus/analog-voice-denoiser.git
cd analog-voice-denoiser

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Tanısal testi çalıştırın
python denoiser.py --test
```

### CLI Seçenekleri
```bash
python denoiser.py --input <giriş.wav> --output <çıkış.wav> --verbose
```

## 🗺 Yol Haritası

- [x] **Aşama I:** Spektral eşikleme motoru uygulaması.
- [x] **Aşama II:** Profesyonel UI/Dashboard mimarisi.
- [x] **Aşama III:** STFT tabanlı gelişmiş sinyal işleme ve WAV I/O.
- [x] **Aşama IV:** Wiener filtreleme ve VAD tabanlı akıllı gürültü kestirimi.
- [x] **Aşama V:** Çoklu algoritma motoru ve gerçek zamanlı metrik analizi.

## 📜 Lisans

MIT Lisansı altında dağıtılmaktadır. Daha fazla bilgi için `LICENSE` dosyasına bakın.

---

<p align="right">
  <i>Profesyonel sinyal bütünlüğü ve vokal netliği için tasarlandı.</i>
</p>