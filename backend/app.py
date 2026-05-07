# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import json
# import os
# import difflib
# from dotenv import load_dotenv

# from google import genai
# from google.genai import types

# load_dotenv()

# app = Flask(__name__)
# CORS(app) 

# client = genai.Client()

# # ===== Load Database =====
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.join(BASE_DIR, "nutrition.json")

# # Template nutrisi jika ada data yang kosong
# DEFAULT_NUTRISI = {
#     "kalori": "-", "protein": "-", "lemak": "-", 
#     "karbohidrat": "-", "serat": "-", "gula": "-",
#     "vitamin_a": "-", "vitamin_c": "-", "kalsium": "-"
# }

# try:
#     with open(file_path) as f:
#         data = json.load(f)
# except Exception:
#     data = {}

# @app.route("/")
# def home():
#     return "Server AI Kalori Berjalan!"

# # ==========================================
# # 1. RUTE PENCARIAN MANUAL (DENGAN ANTI-TYPO)
# # ==========================================
# @app.route("/food/<name>")
# def get_food(name):
#     name = name.lower().strip()
#     match_found = None
#     daftar_makanan = list(data.keys())

#     # Cek Logika 1: Kecocokan langsung
#     for key in daftar_makanan:
#         if key in name or name in key:
#             match_found = key
#             break
            
#     # Cek Logika 2: Fuzzy Matching (Menebak Typo)
#     if not match_found:
#         kemungkinan = difflib.get_close_matches(name, daftar_makanan, n=1, cutoff=0.6)
#         if kemungkinan:
#             match_found = kemungkinan[0]
            
#     if match_found:
#         hasil_nutrisi = {**DEFAULT_NUTRISI, **data[match_found]}
#         return jsonify({
#             "prediksi_makanan": match_found,
#             "nutrisi": hasil_nutrisi
#         })
        
#     return jsonify({"error": "Makanan tidak ditemukan. Coba ketik nama lain."}), 404

# # ==========================================
# # 2. RUTE ANALISIS AI (FOTO/KAMERA)
# # ==========================================
# @app.route("/analyze", methods=["POST"])
# def analyze():
#     if "image" not in request.files:
#         return jsonify({"error": "Tidak ada file gambar"}), 400

#     file = request.files["image"]
#     img_bytes = file.read() 

#     try:
#         daftar_makanan = ", ".join(data.keys())
#         prompt = f"Gambar ini makanan apa? Jawab HANYA dengan satu nama dari daftar berikut: {daftar_makanan}."

#         response = client.models.generate_content(
#             model='gemini-2.5-flash', 
#             contents=[prompt, types.Part.from_bytes(data=img_bytes, mime_type=file.mimetype)]
#         )
        
#         if not response or not response.text:
#             return jsonify({"error": "Server AI sibuk"}), 503

#         food_name = response.text.strip().lower()

#         match_found = None
#         for key in data.keys():
#             if key in food_name:
#                 match_found = key
#                 break
        
#         if match_found:
#             nutrisi_lengkap = {**DEFAULT_NUTRISI, **data[match_found]}
#         else:
#             nutrisi_lengkap = DEFAULT_NUTRISI
#             food_name = f"{food_name} (tidak ada di database)"

#         return jsonify({
#             "prediksi_makanan": match_found or food_name,
#             "nutrisi": nutrisi_lengkap
#         })
        
#     except Exception as e:
#         error_msg = str(e).upper()
#         print("Error System:", error_msg)
#         if "503" in error_msg or "UNAVAILABLE" in error_msg:
#             return jsonify({"error": "Server Google penuh. Gunakan tombol Cari Manual!"})
#         elif "429" in error_msg or "EXHAUSTED" in error_msg:
#             return jsonify({"error": "Kuota harian API habis. Gunakan API Key baru atau pakai Cari Manual."})
#         else:
#             return jsonify({"error": "Gagal memproses gambar."})

# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask, request, jsonify
# Penjelasan: 
# - Flask: Framework (kerangka kerja) untuk membuat server web/backend menggunakan Python.
# - request: Berfungsi untuk menangkap data yang dikirim dari Frontend (HTML), seperti menangkap file foto yang diunggah.
# - jsonify: Berfungsi untuk mengubah data hasil proses Python menjadi format JSON agar bisa dikirim kembali dan dibaca oleh Frontend (HTML/JS).

from flask_cors import CORS
# Penjelasan: CORS (Cross-Origin Resource Sharing) adalah izin keamanan. Ini mengizinkan file index.html Anda untuk berkomunikasi dengan server app.py meskipun dijalankan dari tempat (port) yang berbeda.

import json
import os
import difflib
# Penjelasan:
# - json: Modul bawaan Python untuk membaca file berekstensi .json.
# - os: Modul untuk berinteraksi dengan sistem operasi komputer (seperti mencari lokasi sebuah file).
# - difflib: Modul kecerdasan algoritma bawaan Python yang digunakan untuk membandingkan teks (sangat berguna untuk mendeteksi Typo/salah ketik).

from dotenv import load_dotenv
# Penjelasan: Modul untuk membaca file rahasia bernama '.env' yang berisi API Key, agar API Key tidak terlihat langsung di dalam kodingan utama.

from google import genai
from google.genai import types
# Penjelasan: Ini adalah pustaka (library) resmi terbaru dari Google untuk menghubungkan program Python kita dengan otak AI Gemini (Machine Learning & Deep Learning).

# Menjalankan fungsi untuk membaca file .env
load_dotenv()

# Membuat "Pabrik" utama dari aplikasi backend kita
app = Flask(__name__)
# Memberikan izin CORS ke aplikasi agar tidak diblokir oleh browser
CORS(app) 

# Membuka koneksi/jembatan langsung ke server AI Google Gemini menggunakan API Key dari .env
client = genai.Client()


# BAGIAN: MEMUAT DATABASE (Load Database)


# Mencari tahu di mana folder tempat file app.py ini berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Menentukan lokasi pasti dari file 'nutrition.json'
file_path = os.path.join(BASE_DIR, "nutrition.json")

# Membuat template default (nilai awal) jika makanan ditemukan, tapi datanya ada yang kosong
DEFAULT_NUTRISI = {
    "kalori": "-", "protein": "-", "lemak": "-", 
    "karbohidrat": "-", "serat": "-", "gula": "-",
    "vitamin": "-", "kalsium": "-"
}

try:
    # Mencoba membuka file nutrition.json dan mengubah isinya menjadi variabel 'data' (Dictionary)
    with open(file_path) as f:
        data = json.load(f)
except Exception:
    # Jika file json hilang atau rusak, buat 'data' menjadi kosong agar server tidak crash/mati total
    data = {}



# BAGIAN: FUNGSI KECERDASAN BUATAN TEKS (NLP)

def generate_explanation(food_name):
    # Penjelasan: Fungsi ini bertugas khusus untuk meminta Gemini membuatkan artikel 3 poin (Manfaat, Tips Diet, Cara Olah).
    try:
        # Prompt (perintah) yang dikirim ke AI. Kita memaksa AI untuk menjawab HANYA dalam format kode HTML yang sudah kita desain, tanpa basa-basi.
        prompt = f"""Berikan informasi tentang makanan '{food_name}'.
        Berikan jawaban HANYA dalam format HTML di bawah ini, tanpa teks pembuka/penutup apapun:
        <div style="display: flex; flex-direction: column; gap: 20px; margin-top: 10px;">
            <div>
                <strong style="font-size: 1.15rem; color: #000;">1. Manfaat makanan</strong>
                <p style="margin-top: 5px; color: #27272a; line-height: 1.6;">[Tulis penjelasan manfaat di sini]</p>
            </div>
            <div>
                <strong style="font-size: 1.15rem; color: #000;">2. Tips untuk diet</strong>
                <p style="margin-top: 5px; color: #27272a; line-height: 1.6;">[Tulis tips diet di sini]</p>
            </div>
            <div>
                <strong style="font-size: 1.15rem; color: #000;">3. Cara pengelolaan jika pengguna ingin diet</strong>
                <p style="margin-top: 5px; color: #27272a; line-height: 1.6;">[Tulis cara pengelolaan sehat di sini]</p>
            </div>
        </div>
        """
        
        # Mengirim perintah ke model Gemini Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        
        # Mengambil balasan teks dari AI dan membersihkan tanda kutip (```html) yang kadang tidak sengaja ditambahkan oleh AI
        hasil = response.text.strip()
        hasil = hasil.replace("```html", "").replace("```", "")
        return hasil.strip()
    except Exception as e:
        # Jika AI gagal membalas (karena server penuh), tampilkan pesan error rapi ke pengguna
        return "<p>Penjelasan diet tidak tersedia saat ini karena server AI sedang sibuk.</p>"



# RUTE URL: HALAMAN UTAMA (Test Koneksi)

@app.route("/")
def home():
    # Penjelasan: Jika Anda membuka [http://127.0.0.1:5000/](http://127.0.0.1:5000/) di browser, teks ini akan muncul sebagai tanda server hidup.
    return "Server AI Kalori Berjalan!"



# RUTE URL: PENCARIAN MANUAL (Search DB)

@app.route("/food/<name>")
def get_food(name):
    # Penjelasan: Rute ini akan dipanggil saat pengguna mengetik di kolom pencarian manual.
    
    # Mengubah teks ketikan pengguna menjadi huruf kecil semua dan menghapus spasi di ujungnya agar rapi
    name = name.lower().strip()
    
    # Mengambil semua daftar nama makanan yang ada di file nutrition.json
    daftar_makanan = list(data.keys())
    match_found = None

    # LOGIKA PENCARIAN BERTINGKAT (ALGORITMA SEARCHING)
    
    # PRIORITAS 1: Exact Match (Kecocokan Sempurna)
    # Mengecek apakah nama yang diketik SAMA PERSIS dengan yang ada di database.
    if name in daftar_makanan:
        match_found = name
    else:
        # PRIORITAS 2: Fuzzy Match (Menebak Typo)
        # Jika tidak ada yang sama persis, gunakan algoritma difflib untuk mencari kemiripan minimal 70% (cutoff=0.7).
        # Contoh: Pengguna ketik "tlor dadar", komputer akan menebak "telur dadar".
        kemungkinan = difflib.get_close_matches(name, daftar_makanan, n=1, cutoff=0.7)
        if kemungkinan:
            match_found = kemungkinan[0]
        else:
            # PRIORITAS 3: Substring Match (Pencarian Bagian Kata)
            # Jika tebakan typo gagal, cek apakah kata yang diketik MERUPAKAN BAGIAN dari nama makanan di database.
            # Contoh: Pengguna ketik "dadar", komputer menemukan "telur dadar".
            for key in daftar_makanan:
                if name in key:
                    match_found = key
                    break
            
    # JIKA MAKANAN BERHASIL DITEMUKAN SETELAH MELEWATI 3 LOGIKA DI ATAS:
    if match_found:
        # Gabungkan template default dengan data asli (agar jika ada nilai kosong, diganti strip '-')
        hasil_nutrisi = {**DEFAULT_NUTRISI, **data[match_found]}
        
        # Panggil fungsi AI untuk membuatkan artikel penjelasannya
        penjelasan_diet = generate_explanation(match_found)
        
        # Kirim ketiga data ini (Nama, Angka Gizi, Artikel) ke Frontend
        return jsonify({
            "prediksi_makanan": match_found,
            "nutrisi": hasil_nutrisi,
            "penjelasan": penjelasan_diet
        })
        
    # Jika setelah 3 logika dicari tapi tetap tidak ketemu, kirim pesan Error 404 (Not Found)
    return jsonify({"error": "Makanan tidak ditemukan. Coba ketik nama lain."}), 404



# RUTE URL: ANALISIS AI GAMBAR (Scan Image)

@app.route("/analyze", methods=["POST"])
def analyze():
    # Penjelasan: Rute ini dipanggil saat pengguna mengupload foto atau menjepret kamera. Methodnya POST karena mengirim file besar.

    # 1. Mengecek apakah ada file gambar yang dikirim dari Frontend
    if "image" not in request.files:
        return jsonify({"error": "Tidak ada file gambar"}), 400

    # 2. Mengambil file gambar dan membacanya menjadi data biner (angka-angka piksel)
    file = request.files["image"]
    img_bytes = file.read() 

    try:
        # 3. Menyiapkan daftar makanan dari database untuk dikirim sebagai 'contekan' ke AI
        daftar_makanan = ", ".join(data.keys())
        
        # Prompt (Perintah) ke AI Vision. Kita memaksa AI agar menebak HANYA dari nama yang ada di database kita.
        prompt = f"Gambar ini makanan apa? Jawab HANYA dengan satu nama dari daftar berikut: {daftar_makanan}."

        # 4. Mengirim Gambar (Computer Vision) dan Teks (Prompt) ke otak Google Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=[prompt, types.Part.from_bytes(data=img_bytes, mime_type=file.mimetype)]
        )
        
        # Jika AI gagal menjawab
        if not response or not response.text:
            return jsonify({"error": "Server AI sibuk"}), 503

        # 5. Mengambil hasil tebakan nama makanan dari AI, dibersihkan, dan diubah ke huruf kecil
        food_name = response.text.strip().lower()
        daftar_makanan_keys = list(data.keys())
        match_found = None

        # 6. LOGIKA PENCARIAN (Sama seperti pencarian manual, untuk memastikan tebakan AI benar-benar ada di database)
        
        # PRIORITAS 1: Cek tebakan persis AI
        if food_name in daftar_makanan_keys:
            match_found = food_name
        else:
            # PRIORITAS 2: Cek kemiripan typo (Fuzzy match) tebakan AI
            kemungkinan = difflib.get_close_matches(food_name, daftar_makanan_keys, n=1, cutoff=0.7)
            if kemungkinan:
                match_found = kemungkinan[0]
            else:
                # PRIORITAS 3: Pengecekan bagian kata (Substring)
                for key in daftar_makanan_keys:
                    if key in food_name:
                        match_found = key
                        break
        
        # 7. MENYIAPKAN HASIL AKHIR
        if match_found:
            # Jika tebakan AI cocok dengan database, ambil nutrisinya dan suruh AI buatkan artikelnya
            nutrisi_lengkap = {**DEFAULT_NUTRISI, **data[match_found]}
            penjelasan_diet = generate_explanation(match_found)
        else:
            # Jika tebakan AI ngawur (tidak ada di database kita)
            nutrisi_lengkap = DEFAULT_NUTRISI
            food_name = f"{food_name} (tidak ada di database)"
            penjelasan_diet = "<p>Karena makanan tidak terdeteksi di database kami, kami tidak dapat memberikan tips diet yang spesifik.</p>"

        # Kirim hasil ke Frontend
        return jsonify({
            "prediksi_makanan": match_found or food_name,
            "nutrisi": nutrisi_lengkap,
            "penjelasan": penjelasan_diet
        })
        
    except Exception as e:
        # Penjelasan: Ini adalah blok "Jaring Pengaman". Jika terjadi error sistem (seperti kuota internet habis, server Google mati), program tidak akan crash melainkan mengirim pesan rapi ke layar pengguna.
        error_msg = str(e).upper()
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            return jsonify({"error": "Server Google penuh. Gunakan tombol Cari Manual!"})
        elif "429" in error_msg or "EXHAUSTED" in error_msg:
            return jsonify({"error": "Kuota harian API habis. Gunakan API Key baru atau pakai Cari Manual."})
        else:
            return jsonify({"error": "Gagal memproses gambar."})

# Menjalankan server aplikasi di alamat lokal ([http://127.0.0.1:5000](http://127.0.0.1:5000)) jika file ini dieksekusi secara langsung.
if __name__ == "__main__":
    app.run(debug=True)