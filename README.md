# Camera Capture Otomatis

Aplikasi sederhana untuk menampilkan kamera, mengambil gambar secara manual atau otomatis, dan menyimpan hasil capture ke dalam folder sesi yang terpisah.

Panduan ini ditujukan untuk pengguna baru yang belum pernah menggunakan Python.

## 1. Fitur aplikasi

Aplikasi ini dapat:

- menampilkan preview kamera;
- memilih kamera yang tersedia;
- memilih resolusi otomatis sesuai kamera atau resolusi tertentu;
- mengambil gambar secara manual;
- mengambil gambar otomatis berdasarkan interval;
- berhenti setelah durasi tertentu, misalnya 1 atau 2 jam;
- berhenti setelah jumlah capture tertentu, misalnya 5 atau 6 gambar;
- berjalan sampai pengguna menekan tombol Berhenti;
- memilih folder penyimpanan;
- menampilkan gambar terakhir yang berhasil disimpan;
- menampilkan log file capture pada sesi aktif;
- membuat folder baru untuk setiap sesi;
- membuat `session_log.json` yang mencatat pengaturan dan hasil sesi.

## 2. Yang perlu disiapkan

Siapkan:

1. Komputer Windows 10 atau Windows 11.
2. Kamera internal laptop atau webcam USB.
3. Koneksi internet saat instalasi Python dan library.
4. Ruang penyimpanan untuk hasil gambar.

Git, GitHub, PyTorch, CUDA, dan dataset tidak diperlukan.

## 3. Instalasi Python untuk pengguna baru

Jika Python belum ada:

1. Buka browser.
2. Kunjungi:

   https://www.python.org/downloads/

3. Download Python versi 3.11 atau yang lebih baru.
4. Jalankan file installer.
5. Pada halaman pertama installer, centang:

   `Add python.exe to PATH`

6. Klik `Install Now`.
7. Setelah selesai, tutup installer.
8. Buka PowerShell:
   - tekan tombol Windows;
   - ketik `PowerShell`;
   - buka Windows PowerShell.
9. Periksa instalasi:

```powershell
python --version
```

Hasilnya harus menampilkan versi Python, misalnya:

```text
Python 3.11.9
```

Jika muncul pesan bahwa `python` tidak dikenali, tutup PowerShell, buka kembali, lalu coba lagi. Jika masih gagal, ulangi instalasi Python dan pastikan `Add python.exe to PATH` dicentang.

## 4. Isi folder aplikasi

Folder ini harus memiliki file berikut:

```text
CameraCaptureApp/
├── camera_capture_app.py
├── requirements.txt
└── README.md
```

Jangan menjalankan file dari dalam arsip ZIP. Ekstrak ZIP terlebih dahulu jika aplikasi dikirim dalam bentuk ZIP.

## 5. Membuka PowerShell pada folder aplikasi

Cara mudah:

1. Buka folder `CameraCaptureApp` di File Explorer.
2. Klik area alamat folder di bagian atas.
3. Ketik `powershell`.
4. Tekan Enter.

PowerShell akan terbuka langsung pada folder aplikasi.

Alternatif, gunakan perintah berikut dan sesuaikan lokasinya:

```powershell
cd "C:\Users\NamaAnda\Downloads\CameraCaptureApp"
```

## 6. Membuat lingkungan Python

Langkah ini membuat lingkungan khusus agar library aplikasi tidak mengganggu Python atau aplikasi lain.

Di PowerShell, jalankan:

```powershell
python -m venv .venv
```

Tunggu sampai selesai. Biasanya tidak ada pesan jika berhasil.

Aktifkan lingkungan tersebut:

```powershell
.venv\Scripts\Activate.ps1
```

Jika berhasil, awal baris PowerShell akan menampilkan:

```text
(.venv)
```

### Jika PowerShell menolak aktivasi

Jika muncul pesan tentang `ExecutionPolicy`, jalankan perintah ini satu kali:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Jika PowerShell meminta konfirmasi, ketik:

```text
Y
```

Kemudian aktifkan kembali:

```powershell
.venv\Scripts\Activate.ps1
```

## 7. Menginstal library aplikasi

Pastikan tulisan `(.venv)` masih terlihat, lalu jalankan:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Library yang dipasang:

- `opencv-python`: membaca kamera dan menyimpan gambar;
- `Pillow`: menampilkan gambar pada antarmuka aplikasi;
- `pyautogui`: library pendukung untuk fitur posisi kursor lama.

Aplikasi capture kamera tidak bergantung pada auto-click untuk mengambil gambar.

## 8. Mengatur izin kamera Windows

Jika kamera tidak muncul:

1. Buka `Settings` Windows.
2. Pilih `Privacy & security`.
3. Pilih `Camera`.
4. Aktifkan `Camera access`.
5. Aktifkan `Let desktop apps access your camera`.
6. Tutup aplikasi lain yang sedang memakai kamera, seperti Camera, Zoom, Teams, atau browser.

## 9. Menjalankan aplikasi

Dengan lingkungan `.venv` masih aktif, jalankan:

```powershell
python camera_capture_app.py
```

Jendela `Camera Capture Otomatis` akan terbuka.

## 10. Cara menggunakan aplikasi

### A. Menampilkan kamera

1. Klik `Cari kamera`.
2. Pilih kamera pada daftar.
3. Pilih resolusi:
   - `Otomatis (resolusi kamera)`;
   - `640x480`;
   - `1280x720`;
   - `1920x1080`;
   - `3840x2160` jika kamera mendukung.
4. Klik `Mulai kamera`.
5. Periksa preview kamera.
6. Aplikasi menampilkan `Resolusi aktual`, karena kamera mungkin tidak menerima semua resolusi yang diminta.

Jika mengganti kamera atau resolusi setelah kamera aktif, klik `Stop kamera`, lalu `Mulai kamera` kembali.

### B. Capture manual

Klik:

```text
Capture sekarang
```

Satu gambar disimpan ke folder sesi. Gambar terakhir akan muncul pada panel `Last capture`.

### C. Capture otomatis setiap 10 detik

1. Pastikan kamera sudah aktif.
2. Isi `Interval (detik)` dengan `10`.
3. Pilih mode berhenti.
4. Pilih folder penyimpanan.
5. Klik `Mulai auto-capture`.

Capture pertama dilakukan saat proses dimulai. Capture berikutnya mengikuti interval yang dipilih.

### D. Pilihan mode berhenti

`Sampai dihentikan`

- Proses terus berjalan.
- Klik `Berhenti` jika ingin menghentikan.

`Durasi (jam)`

- Isi nilai, misalnya `1`, `2`, atau `5`.
- Proses berhenti otomatis setelah durasi tersebut.

`Jumlah capture`

- Isi jumlah gambar, misalnya `5` atau `6`.
- Proses berhenti otomatis setelah jumlah gambar tercapai.

### E. Menghentikan proses

Klik:

```text
Berhenti
```

Aplikasi akan memperbarui `session_log.json` dengan waktu selesai, durasi, dan jumlah gambar.

## 11. Struktur hasil penyimpanan

Jika folder penyimpanan dipilih sebagai:

```text
D:\Hasil Kamera
```

Aplikasi akan membuat struktur seperti ini:

```text
D:\Hasil Kamera\
└── Cap-Session_2026-09-24-21\
    ├── cap0001-210530-2026-09-24.jpg
    ├── cap0002-210540-2026-09-24.jpg
    ├── cap0003-210550-2026-09-24.jpg
    └── session_log.json
```

Format nama folder:

```text
Cap-Session_YYYY-MM-DD-HH
```

Format nama file:

```text
capID-HHMMSS-YYYY-MM-DD.jpg
```

Contoh:

```text
cap0001-210530-2026-09-24.jpg
```

`cap0001` adalah nomor urut gambar pada sesi tersebut.

## 12. Isi session_log.json

File `session_log.json` disimpan di dalam folder sesi. File ini menggunakan format JSON dengan indentasi agar mudah dibaca.

Contoh isi:

```json
{
  "application": "Camera Capture Otomatis",
  "status": "completed",
  "session": {
    "folder": "D:\\Hasil Kamera\\Cap-Session_2026-09-24-21",
    "started_at": "2026-09-24T21:05:30",
    "finished_at": "2026-09-24T21:15:42",
    "duration_seconds": 612.35
  },
  "settings": {
    "camera": "0 - Kamera 0",
    "camera_index": 0,
    "requested_resolution": "Otomatis (resolusi kamera)",
    "actual_resolution": "1920x1080",
    "interval_seconds": 10.0,
    "stop_mode": "Jumlah capture",
    "stop_value": 6,
    "output_root": "D:\\Hasil Kamera"
  },
  "result": {
    "capture_count": 6,
    "files": [
      "cap0001-210530-2026-09-24.jpg",
      "cap0002-210540-2026-09-24.jpg"
    ]
  }
}
```

Catatan sesi dibuat saat proses mulai dan diperbarui setiap kali gambar berhasil disimpan serta saat proses berhenti.

## 13. Menjalankan lagi di kemudian hari

Buka PowerShell pada folder aplikasi, lalu aktifkan `.venv`:

```powershell
.venv\Scripts\Activate.ps1
python camera_capture_app.py
```

Library tidak perlu diinstal ulang selama folder `.venv` masih ada.

## 14. Menutup lingkungan Python

Setelah selesai menggunakan aplikasi, tekan `Ctrl+C` jika aplikasi dijalankan dari terminal atau tutup jendela aplikasi. Untuk keluar dari `.venv`, jalankan:

```powershell
deactivate
```

Perintah ini tidak menghapus aplikasi atau hasil capture.

## 15. Masalah umum

### Kamera tidak terdeteksi

- Pastikan webcam terhubung.
- Pastikan aplikasi lain tidak memakai kamera.
- Klik `Cari kamera` lagi.
- Periksa izin kamera Windows.
- Coba tutup dan jalankan ulang aplikasi.

### Preview kosong

- Klik `Stop kamera`.
- Klik `Cari kamera`.
- Pilih kamera yang benar.
- Klik `Mulai kamera`.

### Resolusi tidak sesuai pilihan

Tidak semua kamera mendukung semua resolusi. Lihat tulisan `Resolusi aktual`. Pilih `Otomatis (resolusi kamera)` jika ragu.

### `No module named cv2`

Pastikan `.venv` aktif, ditandai tulisan `(.venv)`, lalu jalankan:

```powershell
python -m pip install -r requirements.txt
```

### `python` tidak dikenali

Python belum terpasang atau belum masuk PATH. Instal ulang Python dan centang `Add python.exe to PATH`.

### Folder hasil tidak dapat dibuat

Pilih folder yang dapat ditulis oleh user, misalnya folder `Pictures` atau `Documents`. Hindari folder sistem seperti `C:\Windows` atau `C:\Program Files`.

## 16. Catatan distribusi

Untuk pengguna teknis, distribusikan folder ini beserta:

```text
camera_capture_app.py
requirements.txt
README.md
```

Untuk pengguna yang tidak ingin memasang Python, aplikasi sebaiknya dikemas menjadi `.exe` menggunakan PyInstaller pada komputer pembuat aplikasi.
