# Restaurant Order Management System

Sebuah aplikasi berbasis Flask untuk mengelola menu restoran, pesanan pelanggan, dan pembayaran.

## Fitur Utama
- **Manajemen Menu**: Tambah, edit, dan hapus menu makanan dengan gambar dan harga.
- **Pemesanan Pelanggan**: Pelanggan dapat memesan makanan dan minuman.
- **Manajemen Pesanan**: Admin dapat melihat dan memperbarui status pesanan.
- **Kasir**: Sistem pembayaran dengan perhitungan kembalian dan pencetakan struk.

## Teknologi yang Digunakan
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap (via Jinja2 Templates)
- **File Upload**: `werkzeug.utils.secure_filename`

## Instalasi
1. **Clone repository ini**
   ```bash
   git clone https://github.com/username/repository.git
   cd repository
   ```
2. **Buat virtual environment (opsional)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Mac/Linux
   venv\Scripts\activate     # Untuk Windows
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Jalankan aplikasi**
   ```bash
   python app.py
   ```
5. **Akses aplikasi**
   Buka browser dan kunjungi `https://localhost:5000`

## Struktur Proyek
```
restaurant-app/
│── static/
│   ├── uploads/   # Direktori untuk menyimpan gambar menu
│── templates/
│   ├── index.html  # Halaman utama pelanggan
│   ├── admin.html  # Halaman admin untuk mengelola menu
│   ├── orders.html # Halaman admin untuk melihat pesanan
│   ├── cashier.html # Halaman kasir untuk pembayaran
│   ├── receipt.html # Halaman struk pembayaran
│── app.py          # Aplikasi utama Flask
│── restaurant.db   # Database SQLite
│── requirements.txt # Daftar dependencies
│── cert.pem, key.pem # Sertifikat SSL untuk HTTPS
```

## Endpoint Utama
| Endpoint | Metode | Deskripsi |
|----------|--------|-------------|
| `/` | GET | Halaman utama pelanggan |
| `/admin` | GET, POST | Manajemen menu restoran |
| `/order` | POST | Membuat pesanan baru |
| `/orders` | GET | Menampilkan daftar pesanan |
| `/update_order/<id>` | POST | Memperbarui status pesanan |
| `/cashier` | GET, POST | Halaman kasir untuk pembayaran |
| `/receipt/<id>` | GET | Menampilkan struk pembayaran |

## Keamanan
Aplikasi ini menggunakan HTTPS dengan sertifikat SSL (`cert.pem` dan `key.pem`).

## Kontribusi
Jika ingin berkontribusi, silakan buat pull request atau buka issue di repository.

## Lisensi
Proyek ini dilisensikan di bawah [MIT License](LICENSE).

