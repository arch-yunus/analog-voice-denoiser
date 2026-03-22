import numpy as np
import argparse
import sys
import logging
import os
from pathlib import Path
from scipy import signal
from scipy.io import wavfile

# Profesyonel log yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AnalogDenoiser")

class AnalogDenoiser:
    """
    AnalogDenoiser, ses sinyallerindeki arka plan gürültüsünü (özellikle analog hışırtı 
    ve statik parazitleri) baskılamak için STFT tabanlı Wiener filtreleme 
    ve VAD (Ses Aktivite Algılama) mekanizmalarını uygular.
    """
    def __init__(self, örnekleme_hızı=44100):
        self.örnekleme_hızı = örnekleme_hızı
        self.eşik_hassasiyeti = 1.2
        self.vad_eşiği = 0.02
        logger.info(f"AnalogDenoiser başlatıldı (Phase V): fs={örnekleme_hızı}")
        
    def analiz_et(self, veri):
        """
        Sinyal metriklerini hesaplar: RMS, ZCR, Spektral Centroid.
        """
        rms = np.sqrt(np.mean(veri**2))
        zcr = np.mean(np.abs(np.diff(np.sign(veri)))) / 2
        
        # Spektral Centroid (Basitleştirilmiş)
        spektrum = np.abs(np.fft.rfft(veri))
        frekanslar = np.fft.rfftfreq(len(veri), 1/self.örnekleme_hızı)
        centroid = np.sum(frekanslar * spektrum) / (np.sum(spektrum) + 1e-12)
        
        return {"rms": rms, "zcr": zcr, "centroid": centroid}

    def filtrele(self, veri, method="wiener"):
        """
        Seçilen metoda göre gürültü engelleme uygular.
        Methodlar: 'wiener', 'spectral', 'lms'
        """
        if method == "wiener":
            return self._wiener_filtrele(veri)
        elif method == "spectral":
            return self._spektral_cikarma(veri)
        elif method == "lms":
            return self._lms_filtrele(veri)
        else:
            logger.warning(f"Bilinmeyen metod '{method}', Wiener kullanılıyor.")
            return self._wiener_filtrele(veri)

    def _wiener_filtrele(self, veri):
        logger.info("Wiener filtreleme uygulanıyor.")
        f, t, Zxx = signal.stft(veri, fs=self.örnekleme_hızı, nperseg=2048)
        PSD = np.abs(Zxx)**2
        gürültü_psd = np.mean(PSD, axis=1, keepdims=True) * self.eşik_hassasiyeti
        kazanç = np.maximum(0, (PSD - gürültü_psd) / (PSD + 1e-12))
        kazanç = signal.medfilt2d(kazanç, [1, 5])
        Zxx_filt = Zxx * kazanç
        _, temiz = signal.istft(Zxx_filt, fs=self.örnekleme_hızı)
        return temiz[:len(veri)].astype(np.float32)

    def _spektral_cikarma(self, veri):
        logger.info("Spektral çıkarma uygulanıyor.")
        f, t, Zxx = signal.stft(veri, fs=self.örnekleme_hızı, nperseg=2048)
        genlik = np.abs(Zxx)
        faz = np.angle(Zxx)
        
        gürültü_genlik = np.mean(genlik, axis=1, keepdims=True) * self.eşik_hassasiyeti
        yeni_genlik = np.maximum(0, genlik - gürültü_genlik)
        
        Zxx_yeni = yeni_genlik * np.exp(1j * faz)
        _, temiz = signal.istft(Zxx_yeni, fs=self.örnekleme_hızı)
        return temiz[:len(veri)].astype(np.float32)

    def _lms_filtrele(self, veri):
        """
        Least Mean Squares (LMS) adaptif filtreleme uygulaması.
        Referans sinyal gecikmeli giriş sinyali kullanılarak gürültü tahmini yapılır.
        """
        logger.info("LMS adaptif filtreleme uygulanıyor.")
        mu = 0.01  # Öğrenme hızı
        L = 32     # Filtre boyu
        w = np.zeros(L)
        y = np.zeros(len(veri))
        e = np.zeros(len(veri))
        
        delay = 100
        ref = np.zeros(len(veri))
        ref[delay:] = veri[:-delay]
        
        for i in range(L, len(veri)):
            x = ref[i:i-L:-1]
            y[i] = np.dot(w, x)
            e[i] = veri[i] - y[i]
            w = w + 2 * mu * e[i] * x
            
        return e.astype(np.float32)

def batch_isleme(denoiser, input_dir, output_dir, method="wiener"):
    """
    Belirtilen dizindeki tüm .wav dosyalarını toplu olarak işler.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Toplu işleme başlatıldı: {input_path}")
    wav_files = list(input_path.glob("*.wav"))
    for i, wav_file in enumerate(wav_files):
        try:
            fs, veri = wavfile.read(wav_file)
            if len(veri.shape) > 1: veri = veri.mean(axis=1)
            veri_norm = veri.astype(np.float32) / (np.max(np.abs(veri)) + 1e-12)
            
            temiz = denoiser.filtrele(veri_norm, method=method)
            out_name = output_path / f"temiz_{wav_file.name}"
            wavfile.write(out_name, fs, (temiz * 32767).astype(np.int16))
            logger.info(f"[{i+1}/{len(wav_files)}] İşlendi: {wav_file.name}")
        except Exception as e:
            logger.error(f"Hata ({wav_file.name}): {e}")

def test_sinyali_oluştur(süre=3, frekans=440):
    """
    Test amaçlı olarak Gauss beyaz gürültüsü ile karıştırılmış sentetik bir sinüs dalgası oluşturur.
    """
    t = np.linspace(0, süre, int(44100 * süre))
    sinyal = 0.5 * np.sin(2 * np.pi * frekans * t)
    gürültü = 0.1 * np.random.normal(size=t.shape)
    return (sinyal + gürültü).astype(np.float32)

def main():
    parser = argparse.ArgumentParser(description="Analog Voice Denoiser CLI Araç Seti")
    parser.add_argument("--test", action="store_true", help="Otomatik tanısal testi çalıştır")
    parser.add_argument("--input", type=str, help="Giriş .wav dosyasının yolu")
    parser.add_argument("--input-dir", type=str, help="Toplu işleme için giriş dizini")
    parser.add_argument("--output", type=str, default="temiz_cikti.wav", help="İşlenmiş çıktının kaydedileceği yol")
    parser.add_argument("--output-dir", type=str, default="output", help="Toplu işleme için çıkış dizini")
    parser.add_argument("--method", type=str, default="wiener", choices=["wiener", "spectral", "lms"], help="Gürültü engelleme metodu")
    parser.add_argument("--verbose", action="store_true", help="Hata ayıklama seviyesinde loglamayı etkinleştir")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    denoiser = AnalogDenoiser()
    
    if args.test:
        logger.info("Otomatik tanı dizisi başlatılıyor...")
        kirli_sinyal = test_sinyali_oluştur()
        
        for m in ["wiener", "spectral", "lms"]:
            logger.info(f"Test ediliyor: {m}")
            temiz_sinyal = denoiser.filtrele(kirli_sinyal, method=m)
            snr_iyileşmesi = np.var(kirli_sinyal) / np.var(temiz_sinyal)
            metrikler = denoiser.analiz_et(temiz_sinyal)
            logger.info(f"Metod: {m} | SNR İyileşme: {snr_iyileşmesi:.2f}x | RMS: {metrikler['rms']:.4f}")
        
        sys.exit(0)

    # Toplu İşleme (Batch Processing)
    if args.input_dir:
        batch_isleme(denoiser, args.input_dir, args.output_dir, method=args.method)
        sys.exit(0)

    if args.input:
        try:
            fs, veri = wavfile.read(args.input)
            if len(veri.shape) > 1: veri = veri.mean(axis=1)
            veri_norm = veri.astype(np.float32) / (np.max(np.abs(veri)) + 1e-12)
            
            denoiser.örnekleme_hızı = fs
            temiz_veri = denoiser.filtrele(veri_norm, method=args.method)
            
            wavfile.write(args.output, fs, (temiz_veri * 32767).astype(np.int16))
            logger.info(f"İşlenmiş dosya kaydedildi ({args.method}): {args.output}")
        except Exception as e:
            logger.error(f"Dosya işleme sırasında hata oluştu: {e}")
            sys.exit(1)
    else:
        logger.error("Giriş yolu belirtilmedi. --input, --input-dir veya --test kullanın.")
        sys.exit(1)

if __name__ == "__main__":
    main()
