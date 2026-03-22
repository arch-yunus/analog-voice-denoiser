import numpy as np
import pytest
from denoiser import AnalogDenoiser, test_sinyali_oluştur

def test_denoiser_initialization():
    denoiser = AnalogDenoiser(örnekleme_hızı=44100)
    assert denoiser.örnekleme_hızı == 44100

def test_analyze_metrics():
    denoiser = AnalogDenoiser()
    veri = np.random.normal(0, 1, 1000)
    metrikler = denoiser.analiz_et(veri)
    assert "rms" in metrikler
    assert "zcr" in metrikler
    assert "centroid" in metrikler
    assert metrikler["rms"] > 0

def test_denoising_methods():
    denoiser = AnalogDenoiser()
    kirli = test_sinyali_oluştur(süre=0.5)
    
    for method in ["wiener", "spectral", "lms"]:
        temiz = denoiser.filtrele(kirli, method=method)
        assert len(temiz) == len(kirli)
        assert np.max(np.abs(temiz)) <= 1.5 # Patlama yapmamalı

if __name__ == "__main__":
    # pytest yoksa manuel çalıştır
    test_denoiser_initialization()
    test_analyze_metrics()
    test_denoising_methods()
    print("Tüm testler başarıyla tamamlandı.")
