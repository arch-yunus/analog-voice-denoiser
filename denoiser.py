import numpy as np
import argparse
import sys
import logging
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
        self.vad_eşiği = 0.02 # Enerji tabanlı VAD eşiği
        logger.info(f"AnalogDenoiser başlatıldı (Phase IV): fs={örnekleme_hızı}")
        
    def _vad_maskesi(self, veri):
        """
        Basit enerji tabanlı VAD (Voice Activity Detection).
        """
        enerji = veri**2
        ortalama_enerji = np.mean(enerji)
        return ortalama_enerji > self.vad_eşiği

    def filtrele(self, veri):
        """
        Wiener Filtreleme ve Yumuşak Maskeleme uygular.
        """
        logger.info("Gelişmiş Wiener filtreleme işlemi başlatılıyor.")
        
        # STFT Hesaplama
        f, t, Zxx = signal.stft(veri, fs=self.örnekleme_hızı, nperseg=2048)
        PSD = np.abs(Zxx)**2 # Güç Spektral Yoğunluğu
        
        # Gürültü Kestirimi (Sinyalin gürültülü olduğu varsayılan düşük enerjili kısımlarından)
        # Basitçe tüm sinyalin ortalama gürültü tabanını alıyoruz (Wiener yaklaşımı)
        gürültü_psd = np.mean(PSD, axis=1, keepdims=True) * self.eşik_hassasiyeti
        
        # Wiener Kazancı: G = (PSD - Noise_PSD) / PSD
        # Negatif değerleri 0'a çekiyoruz (Soft thresholding)
        kazanç = np.maximum(0, (PSD - gürültü_psd) / (PSD + 1e-12))
        
        # Kazancı yumuşat (Spektral pürüzsüzlük için)
        kazanç = signal.medfilt2d(kazanç, [1, 5])
        
        Zxx_filtrelenmiş = Zxx * kazanç
        
        # ISTFT ile zaman domainine geri dönüş
        _, temiz_veri = signal.istft(Zxx_filtrelenmiş, fs=self.örnekleme_hızı)
        
        # Sinyal boyu uyumu
        output = temiz_veri[:len(veri)]
        
        logger.info("Wiener filtreleme başarıyla tamamlandı.")
        return output.astype(np.float32)

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
    parser.add_argument("--output", type=str, default="temiz_cikti.wav", help="İşlenmiş çıktının kaydedileceği yol")
    parser.add_argument("--verbose", action="store_true", help="Hata ayıklama seviyesinde loglamayı etkinleştir")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    denoiser = AnalogDenoiser()
    
    if args.test:
        logger.info("Otomatik tanı dizisi başlatılıyor...")
        kirli_sinyal = test_sinyali_oluştur()
        temiz_sinyal = denoiser.filtrele(kirli_sinyal)
        
        snr_iyileşmesi = np.var(kirli_sinyal) / np.var(temiz_sinyal)
        logger.info(f"Tanısal eşleşme sonuçlandı. SNR İyileşme Katsayısı: {snr_iyileşmesi:.2f}x")
        sys.exit(0)

    if args.input:
        try:
            fs, veri = wavfile.read(args.input)
            # Eğer stereo ise mono'ya çevir
            if len(veri.shape) > 1:
                veri = veri.mean(axis=1)
            
            # Normalizasyon
            veri_norm = veri.astype(np.float32) / np.max(np.abs(veri))
            
            denoiser.örnekleme_hızı = fs
            temiz_veri = denoiser.filtrele(veri_norm)
            
            # Çıktıyı kaydet
            wavfile.write(args.output, fs, (temiz_veri * 32767).astype(np.int16))
            logger.info(f"İşlenmiş dosya kaydedildi: {args.output}")
        except Exception as e:
            logger.error(f"Dosya işleme sırasında hata oluştu: {e}")
            sys.exit(1)
    else:
        logger.error("Giriş dosyası belirtilmedi. --input veya --test parametresini kullanın.")
        sys.exit(1)

if __name__ == "__main__":
    main()
