import cv2
from pyzbar.pyzbar import decode
import time
import requests
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os
import qrcode

# ThingSpeak API Ayarları
THINGSPEAK_API_URL = "https://api.thingspeak.com/update"
WRITE_API_KEY = "WHJF2CPGA4IE1JVY"

# Veritabanı dizini
DATABASE_DIR = "user_database"
os.makedirs(DATABASE_DIR, exist_ok=True)

# ThingSpeak'e veri gönderme fonksiyonu
def send_to_thingspeak(is_valid):
    params = {
        'api_key': WRITE_API_KEY,
        'field1': 1 if is_valid else 0,
    }
    response = requests.get(THINGSPEAK_API_URL, params=params)
    if response.status_code == 200:
        print(f"ThingSpeak'e veri gönderildi: {'Geçerli' if is_valid else 'Geçersiz'}")
    else:
        print(f"ThingSpeak'e veri gönderme başarısız: {response.status_code}")

# Kayıt olma işlemi
def register_user():
    name = simpledialog.askstring("Kayıt Ol", "Ad ve Soyadınızı Girin:")
    if not name:
        messagebox.showwarning("Uyarı", "Ad ve Soyad girilmelidir!")
        return

    user_dir = os.path.join(DATABASE_DIR, name)
    os.makedirs(user_dir, exist_ok=True)

    # Fotoğraf seçme
    file_path = filedialog.askopenfilename(filetypes=[("Görüntü Dosyaları", ".jpg;.jpeg;*.png")])
    if not file_path:
        messagebox.showerror("Hata", "Fotoğraf seçimi iptal edildi.")
        return

    saved_photo_path = os.path.join(user_dir, f"{name}_photo.jpg")
    cv2.imwrite(saved_photo_path, cv2.imread(file_path))
    messagebox.showinfo("Başarılı", "Fotoğrafınız başarıyla kaydedildi.")

    # QR kod oluşturma
    qr_data = f"{name}_{time.time()}"
    qr = qrcode.make(qr_data)
    qr_path = os.path.join(user_dir, f"{name}_qrcode.png")
    qr.save(qr_path)
    messagebox.showinfo("Başarılı", "QR Kodunuz başarıyla oluşturuldu!")

# QR kod veya fotoğrafla giriş
def login_user():
    def qr_login():
        cap = cv2.VideoCapture(0)
        messagebox.showinfo("Bilgi", "QR kodu kameraya gösterin.")

        while True:
            ret, frame = cap.read()

            if not ret:
                messagebox.showerror("Hata", "Kamera açılamadı.")
                return

            decoded_objects = decode(frame)
            for obj in decoded_objects:
                qr_data = obj.data.decode("utf-8")

                for user in os.listdir(DATABASE_DIR):
                    user_dir = os.path.join(DATABASE_DIR, user)
                    qr_path = os.path.join(user_dir, f"{user}_qrcode.png")

                    if os.path.exists(qr_path):
                        saved_image = cv2.imread(qr_path)
                        saved_data = decode(saved_image)

                        if saved_data and saved_data[0].data.decode("utf-8") == qr_data:
                            messagebox.showinfo("Başarılı", f"{user} olarak giriş yapıldı!")
                            send_to_thingspeak(True)
                            cap.release()
                            cv2.destroyAllWindows()
                            return

                        if saved_data and saved_data[0].data.decode("utf-8") != qr_data:
                            send_to_thingspeak(False)
                            cap.release()
                            cv2.destroyAllWindows()
                            return
            cv2.imshow("QR Kod Tarama", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()


    def face_login():
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        messagebox.showinfo("Bilgi", "Kamerayı yüzünüze doğrultun.")
        while True:
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Hata", "Kamera açılamadı.")
                return
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                for user in os.listdir(DATABASE_DIR):
                    user_dir = os.path.join(DATABASE_DIR, user)
                    photo_path = os.path.join(user_dir, f"{user}_photo.jpg")
                    if os.path.exists(photo_path):
                        saved_image = cv2.imread(photo_path)
                        saved_gray = cv2.cvtColor(saved_image, cv2.COLOR_BGR2GRAY)
                        saved_faces = face_cascade.detectMultiScale(saved_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                        if len(saved_faces) > 0:
                            messagebox.showinfo("Başarılı", f"{user} olarak giriş yapıldı!")
                            send_to_thingspeak(True)
                            cap.release()
                            cv2.destroyAllWindows()
                            return
            cv2.imshow("Yüz Tanıma", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        messagebox.showerror("Hata", "Yüz eşleşmedi.")
        send_to_thingspeak(False)

    # Giriş seçeneklerini sunan pencere
    login_window = tk.Toplevel()
    login_window.title("Giriş Yap")
    tk.Button(login_window, text="QR Kod ile Giriş", command=qr_login).pack(pady=10)
    tk.Button(login_window, text="Fotoğraf ile Giriş", command=face_login).pack(pady=10)

# Ana ekran
root = tk.Tk()
root.title("QR Kod ve Yüz Algılama Giriş Sistemi")
tk.Button(root, text="Kayıt Ol", command=register_user, width=20).pack(pady=10)
tk.Button(root, text="Giriş Yap", command=login_user, width=20).pack(pady=10)
root.mainloop()