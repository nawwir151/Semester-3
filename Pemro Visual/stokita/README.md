# STOKITA - Manajemen Stok Barang & Inventaris

Aplikasi desktop berbasis **Python + PyQt5 + SQLite**.

## Cara menjalankan
```bash
pip install -r requirements.txt
python main.py
```
Login awal: **admin / admin123** (database `stokita.db` dibuat otomatis saat pertama dijalankan).

## Struktur file
| File | Isi |
|------|-----|
| `main.py` | Jendela utama, sidebar, navigasi, logout |
| `pages.py` | Login, Dashboard, Data Barang, Kategori, Laporan, Pengaturan + dialog |
| `ui_common.py` | Style (QSS), kartu, header, dialog verifikasi 2 langkah |
| `memtrace.py` | Integrasi tracemalloc (laporan memori & log) |
| `database.py` | Semua query SQLite (users, barang, kategori, riwayat, opname, settings) |

## Fitur
1. **Login** - username, password, "Ingat saya" (menyimpan username saja), pesan error "Username atau Password salah".
2. **Dashboard** - Total Jenis Barang, Stok Kritis, Total Stok, Total Terjual, daftar barang (cari, filter kategori & status), Tambah Barang.
3. **Data Barang** - tambah/edit/hapus barang, tombol **+** (barang masuk) dan **-** (barang keluar/terjual). Hapus memakai verifikasi 2 langkah.
4. **Kategori** - tambah kategori, hapus kategori (2 langkah; ditolak bila masih dipakai barang).
5. **Laporan** - Laporan Stok, Barang Masuk/Keluar, Stok Opname; Export CSV & PDF (PDF memakai mesin cetak bawaan Qt, tanpa library tambahan); tombol Mulai Opname.
6. **Pengaturan** - nama toko, nama admin, stok minimum default, simpan; Reset Semua Data (2 langkah).
7. **Logout** - konfirmasi 2 langkah (ubah `LOGOUT_TWO_STEP = False` di `main.py` untuk 1 langkah).

## Verifikasi 2 langkah
Langkah 1: dialog konfirmasi. Langkah 2: masukkan **password admin**. Keduanya harus lolos.

## Peringatan stok kritis
- Saat mengisi jumlah **barang keluar (-)**, muncul peringatan langsung bila sisa stok akan melewati stok minimum / habis.
- Setelah disimpan, muncul pop-up peringatan jika stok barang jadi **Kritis** atau **Habis**.
- Baris barang **Kritis** diwarnai kuning dan **Habis** merah (Dashboard & Data Barang), plus banner daftar barang kritis dan kartu "Stok Kritis" berwarna merah.

## Penutupan database & pemantauan memori
- Koneksi SQLite ditutup **eksplisit** saat aplikasi ditutup (`Database.close()`; transaksi menggantung di-commit dulu). Aman dipanggil berulang, dan `Database` juga bisa dipakai dengan `with`.
- **tracemalloc** (nonaktif secara default karena menambah overhead). Aktifkan dengan `python main.py --trace-memory`, atau variabel `STOKITA_TRACEMALLOC=1`, atau tombol **Pengaturan > Diagnostik Memori > Mulai Pelacakan**.
- Dialog diagnostik menampilkan memori saat ini/puncak, alokasi terbesar, dan pertumbuhan sejak pelacakan dimulai. Saat aplikasi ditutup, laporan ditambahkan ke `memory_report.log`.

## Status stok
- **Aman**: stok di atas stok minimum
- **Kritis**: stok <= stok minimum
- **Habis**: stok = 0

## Logo & ilustrasi
Letakkan gambar di folder `assets/` (opsional):
- `assets/logo.png` - logo STOKITA
- `assets/ilustrasi.png` - ilustrasi di halaman login

Logo STOKITA sudah terpasang (`assets/logo.png`) di sidebar, halaman login, dan ikon jendela. Jika file dihapus, aplikasi menampilkan logo teks.

## Diagram Relasi Entitas (ERD)

```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string password
    }
    SETTINGS {
        string key PK
        string value
    }
    KATEGORI {
        int id PK
        string nama
    }
    BARANG {
        int id PK
        string kode UK
        string nama
        int kategori_id FK
        string satuan
        int stok
        int stok_min
        string deskripsi
    }
    REMARK {
        int id PK
        string kode UK
        string tipe
        string keterangan
    }
    RIWAYAT {
        int id PK
        int barang_id FK
        int remark_id FK
        string kode
        string nama
        string jenis
        int jumlah
        int stok_akhir
        string keterangan
        string tanggal
    }
    OPNAME {
        int id PK
        string kode
        string nama
        int stok_sistem
        int stok_fisik
        int selisih
        string tanggal
    }

    KATEGORI ||--o{ BARANG : "memiliki"
    BARANG ||--o{ RIWAYAT : "mencatat log"
    REMARK ||--o{ RIWAYAT : "merujuk catatan"