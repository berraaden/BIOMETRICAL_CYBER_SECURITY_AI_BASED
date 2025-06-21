import customtkinter as ctk
import cv2
from deepface import DeepFace
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageTk

KAYITLI_YUZ = "kayitli_yuz.jpg"
KORUNAN_KLASOR = r"G:\Drive'ım\TEKNOFEST KKTC\KKTC_FINAL_PROJE_4\ORNEK_DATA_DOSYASI\DLP_DENEME"
DESTEKLENEN_UZANTILAR = [".pdf", ".docx", ".xlsx"]
ERISIM_VERILDI = False
BANNER_YOLU = r"G:\Drive'ım\TEKNOFEST KKTC\KKTC_FINAL_PROJE_4\banner.jpg"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def dosyalari_kilitle():
    for kok, _, dosyalar in os.walk(KORUNAN_KLASOR):
        for dosya in dosyalar:
            uzanti = os.path.splitext(dosya)[1].lower()
            if uzanti in DESTEKLENEN_UZANTILAR and not dosya.endswith(".locked"):
                eski_yol = os.path.join(kok, dosya)
                yeni_yol = eski_yol + ".locked"
                os.rename(eski_yol, yeni_yol)

def dosyalari_ac():
    for kok, _, dosyalar in os.walk(KORUNAN_KLASOR):
        for dosya in dosyalar:
            if dosya.endswith(".locked"):
                eski_yol = os.path.join(kok, dosya)
                yeni_yol = eski_yol.replace(".locked", "")
                os.rename(eski_yol, yeni_yol)

class DosyaKoruma(FileSystemEventHandler):
    def on_modified(self, event):
        if not ERISIM_VERILDI:
            dosyalari_kilitle()

def yuz_kaydi():
    kamera = cv2.VideoCapture(0)
    while True:
        ret, kare = kamera.read()
        if not ret:
            continue
        cv2.imshow("Yüz Kaydı - ESC ile Çık", kare)
        if cv2.waitKey(1) & 0xFF == 27:
            cv2.imwrite(KAYITLI_YUZ, kare)
            break
    kamera.release()
    cv2.destroyAllWindows()

def dogrulama_ve_baslat():
    global ERISIM_VERILDI
    kamera = cv2.VideoCapture(0)
    baslangic_zamani = time.time()
    print("[INFO] Yüz doğrulama başlatıldı...")

    while time.time() - baslangic_zamani < 3:
        ret, kare = kamera.read()
        if not ret:
            continue

        cv2.imshow("Yüz Doğrulama - Bekleniyor...", kare)
        cv2.waitKey(1)

        cv2.imwrite("gecici_kisi.jpg", kare)
        try:
            sonuc = DeepFace.verify(img1_path="gecici_kisi.jpg", img2_path=KAYITLI_YUZ, enforce_detection=False)
            if sonuc["verified"]:
                ERISIM_VERILDI = True
                break
        except Exception as e:
            continue

    kamera.release()
    cv2.destroyAllWindows()

    if ERISIM_VERILDI:
        dosyalari_ac()
        durum_label.configure(text="✅ Doğrulama başarılı! Erişim verildi.", text_color="green")
        print("[SİSTEM] Klasör erişimi açıldı.")
    else:
        dosyalari_kilitle()
        durum_label.configure(text="❌ Doğrulama başarısız. Erişim engellendi.", text_color="red")
        print("[SİSTEM] Klasör erişimi engellendi.")

    izleyici = Observer()
    izleyici.schedule(DosyaKoruma(), KORUNAN_KLASOR, recursive=True)
    izleyici.start()

# --- GUI Arayüz ---
pencere = ctk.CTk()
pencere.title("Biyometrik Erişim Koruma Sistemi")
pencere.geometry("1000x600")  # Biraz daha geniş yaptım iki taraf rahat sığsın diye

# Ana Frame: Sol ve Sağ ikiye böl
ana_frame = ctk.CTkFrame(pencere)
ana_frame.pack(expand=True, fill="both")

# Sol Frame (Görsel için)
sol_frame = ctk.CTkFrame(ana_frame, width=500, height=600)
sol_frame.pack(side="left", fill="both", expand=False)

# Sağ Frame (Butonlar ve Yazılar için)
sag_frame = ctk.CTkFrame(ana_frame, width=500, height=600)
sag_frame.pack(side="right", fill="both", expand=True)

# Banner Resmi
try:
    banner_resim = Image.open(BANNER_YOLU)
    banner_resim = banner_resim.resize((480, 580))  # Neredeyse tam doldursun
    banner_foto = ImageTk.PhotoImage(banner_resim)

    banner_label = ctk.CTkLabel(sol_frame, image=banner_foto, text="")
    banner_label.image = banner_foto
    banner_label.pack(expand=True, pady=10)
except Exception as e:
    print(f"[HATA] Banner resmi yüklenemedi: {e}")

# Sağ taraftaki başlık ve butonlar
baslik = ctk.CTkLabel(sag_frame, text="Biyometrik Koruma Sistemi", font=("Arial", 28))
baslik.pack(pady=30)

kaydet_buton = ctk.CTkButton(sag_frame, text="Yüzü Kaydet", width=200, height=40, command=yuz_kaydi)
kaydet_buton.pack(pady=20)

baslat_buton = ctk.CTkButton(sag_frame, text="Doğrula ve Koruma Sistemi Başlat", width=250, height=40, command=dogrulama_ve_baslat)
baslat_buton.pack(pady=20)

durum_label = ctk.CTkLabel(sag_frame, text="Sistem hazır", font=("Arial", 20))
durum_label.pack(pady=30)

pencere.mainloop()
