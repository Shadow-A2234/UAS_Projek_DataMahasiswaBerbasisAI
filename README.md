**NAMA NAMA KELOMPOK**
- Muhammad Abdi 24302057
- Siti Nor'Hafipah 24302019
- Rabiatul Munawarah 24302020
- Muhammad Amin 24302012
- 


🧠 **UAS ProjeK Data Mahasiswa Berbasis CHATBOT AI**, lengkap dengan:

* Deskripsi
* Cara menjalankan
* Cara install library
* Panduan setup `venv`
* Contoh penggunaan

---

```markdown
# UAS_Projek_DataMahasiswaBerbasisAI 🎓🤖

Proyek ini adalah aplikasi berbasis Python dan AI yang dapat digunakan untuk **mengelola data mahasiswa** serta menyediakan fitur **chatbot berbasis GPT**. Proyek ini menggunakan berbagai library AI dan GUI serta menyimpan data di database SQLite.

---

📦 Fitur

- ✅ Manajemen data mahasiswa (input, lihat, update, delete)
- ✅ Chatbot dengan API GPT (OpenRouter/OpenAI)
- ✅ Admin panel untuk melihat & mengatur data
- ✅ Fitur ekspor ke file `.json`
- ✅ Tampilan antarmuka sederhana berbasis CLI atau GUI (opsional)

````

⚙️ Setup Environment (Wajib)

> 💡 Disarankan menggunakan Python 3.10+ dan virtual environment

1. Clone Repository
```bash
git clone https://github.com/Shadow-A2234/UAS_Projek_DataMahasiswaBerbasisAI.git
cd UAS_Projek_DataMahasiswaBerbasisAI
````

2. Buat Virtual Environment

```bash
python -m venv venv
```

3. Aktifkan Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

📚 Daftar Library yang Digunakan

| Library             | Fungsi                                   |
| ------------------- | ---------------------------------------- |
| `openai`            | Akses ke GPT API (via OpenAI/OpenRouter) |
| `requests`          | HTTP request ke API eksternal            |
| `sqlite3`           | Database lokal                           |
| `cv2` (OpenCV)      | (Opsional) verifikasi wajah/gambar       |
| `mediapipe`         | (Opsional) deteksi gesture/wajah         |
| `flask` / `tkinter` | (Opsional) GUI atau Web Interface        |
| `json`              | Simpan/export riwayat dalam format JSON  |

> Semua library di atas sudah disertakan dalam `requirements.txt`

---

🚀 Menjalankan Aplikasi

```bash
python app.py
```

Atau bisa juga:

```bash
python main.py
```

---

✍️ Kontributor

* **Muhammad Abdi**
*
*
*
*

---

📄 Lisensi

Proyek ini dibuat untuk keperluan Tugas Akhir/UAS. Gunakan dengan bijak. Tidak untuk diperjualbelikan.

---

🧠 Catatan Tambahan
Jika mengalami error module tidak ditemukan (ModuleNotFoundError), pastikan:

Virtual environment aktif

pip install -r requirements.txt sudah dijalankan
Jika mengalami error module tidak ditemukan (`ModuleNotFoundError`), pastikan:

* Virtual environment aktif
* `pip install -r requirements.txt` sudah dijalankan

```
