import os
import shutil
import unittest
from database import Database, sanitize_text


class TestStokitaPertemuan13(unittest.TestCase):
    """
    Suite Pengujian Otomatis (Unit & Security Testing) Aplikasi STOKITA:
    1. Validasi File Salt Eksternal & Enkripsi PBKDF2-HMAC-SHA256
    2. Validasi Penolakan Blank Character
    3. Pembatasan 3x Gagal Login & Penguncian Sementara
    4. Hak Akses RBAC (Admin vs Staff)
    5. Proteksi Anomali Role (misal role berubah menjadi '100')
    6. Transaksi Stok & Filter Query Statis Terparameterisasi
    7. Backup & Restore Database dengan Uji Integritas
    """

    def setUp(self):
        self.test_db = "test_stokita_temp.db"
        self.test_salt = "test_stokita_temp.salt"
        self.test_backup_dir = "test_backups_temp"
        self.manual_backup_file = "test_manual_backup_temp.db"

        self._cleanup_files()
        self.db = Database(
            db_path=self.test_db,
            backup_dir=self.test_backup_dir,
            salt_path=self.test_salt,
        )

    def tearDown(self):
        if hasattr(self, "db") and self.db and self.db.conn:
            self.db.conn.close()
        self._cleanup_files()

    def _cleanup_files(self):
        for f in (self.test_db, self.test_salt, self.manual_backup_file):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass
        if os.path.exists(self.test_backup_dir):
            shutil.rmtree(self.test_backup_dir, ignore_errors=True)

    def test_01_file_salt_dan_enkripsi_sha256(self):
        """Memastikan file salt eksternal otomatis dibuat dan password tidak plaintext."""
        self.assertTrue(os.path.exists(self.test_salt))
        row = self.db.conn.execute(
            "SELECT password FROM users WHERE username = 'admin'"
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertNotEqual(row["password"], "admin123")
        self.assertIn("$", row["password"])

    def test_02_validasi_blank_character(self):
        """Memastikan spasi kosong dan karakter tak terlihat (zero-width) ditolak."""
        with self.assertRaises(ValueError):
            sanitize_text("   \u200b\u00a0\ufeff   ", field_name="Nama Barang")

        with self.assertRaises(ValueError):
            self.db.login("   \u200b  ", "admin123")

    def test_03_pembatasan_login_3x_lockout(self):
        """Memastikan login dikunci otomatis pada percobaan gagal ke-3."""
        # Percobaan gagal ke-1 & ke-2
        self.assertIsNone(self.db.login("admin", "salah1"))
        self.assertEqual(self.db.get_remaining_login_attempts(), 2)

        self.assertIsNone(self.db.login("admin", "salah2"))
        self.assertEqual(self.db.get_remaining_login_attempts(), 1)

        # Percobaan gagal ke-3 -> memicu penguncian PermissionError
        with self.assertRaises(PermissionError):
            self.db.login("admin", "salah3")

        locked, sisa_detik = self.db.is_login_locked()
        self.assertTrue(locked)
        self.assertGreater(sisa_detik, 0)

    def test_04_rbac_admin_vs_staff(self):
        """Memastikan Staff bisa Tambah/Edit Barang, tapi ditolak pada fitur khusus Admin."""
        # Admin membuat akun Staff
        self.db.login("admin", "admin123")
        self.db.user_add("kasir1", "kasir123", "Budi Staff", "Staff")
        self.db.logout()

        # Login sebagai Staff
        user_staff = self.db.login("kasir1", "kasir123")
        self.assertEqual(user_staff["role"], "Staff")

        # Staff diizinkan Tambah & Edit Barang
        brg_id = self.db.barang_add(
            "BRG0001", "Buku Tulis", 1, "Pcs", 30, 5, "Buku bergaris"
        )
        self.db.barang_update(
            brg_id, "Buku Tulis Sinar Dunia", 1, "Pcs", 30, 5, "Update oleh Staff"
        )
        updated = self.db.barang_get(brg_id)
        self.assertEqual(updated["nama"], "Buku Tulis Sinar Dunia")

        # Staff ditolak untuk Hapus Barang, Kelola User, Restore DB, dan Reset Data
        with self.assertRaises(PermissionError):
            self.db.barang_delete(brg_id)

        with self.assertRaises(PermissionError):
            self.db.user_add("hacker", "123456", "Ilegal", "Admin")

        with self.assertRaises(PermissionError):
            self.db.reset_data()

    def test_05_proteksi_anomali_role_100(self):
        """Memastikan nilai role di luar dugaan (seperti '100') ditolak total."""
        with self.assertRaises(PermissionError):
            self.db.normalize_role("100")

        self.assertFalse(self.db.has_permission("tambah_barang", role="100"))
        self.assertFalse(self.db.has_permission("hapus_barang", role="100"))

    def test_06_transaksi_stok_dan_filter_aman(self):
        """Memastikan mutasi stok akurat dan filter dropdown default GUI menampilkan data."""
        self.db.login("admin", "admin123")
        brg_id = self.db.barang_add(
            "BRG0001", "Teh Botol", 3, "Botol", 20, 5, "Minuman dingin"
        )

        # Transaksi keluar 6 botol -> sisa harus 14
        self.db.ubah_stok(brg_id, "Keluar", 6, 2, "Penjualan harian")
        brg = self.db.barang_get(brg_id)
        self.assertEqual(brg["stok"], 14)

        # Uji filter default GUI ('Semua Status' & kategori_id=0)
        hasil_filter = self.db.barang_list(
            search="", kategori_id=0, status_stok="Semua Status"
        )
        self.assertEqual(len(hasil_filter), 1)
        self.assertEqual(hasil_filter[0]["nama"], "Teh Botol")

    def test_07_backup_dan_restore_database(self):
        """Memastikan proses Backup dan Restore mengembalikan data yang terhapus."""
        self.db.login("admin", "admin123")
        brg_id = self.db.barang_add(
            "BRG0001", "Kopi Sachet", 3, "Pcs", 50, 10, "Kopi hitam"
        )

        # Buat backup manual
        self.assertTrue(self.db.backup_database(self.manual_backup_file))

        # Hapus barang dari database aktif
        self.db.barang_delete(brg_id)
        self.assertEqual(len(self.db.barang_list()), 0)

        # Pulihkan dari file backup
        self.assertTrue(self.db.restore_database(self.manual_backup_file))
        self.assertEqual(len(self.db.barang_list()), 1)
        self.assertEqual(self.db.barang_list()[0]["nama"], "Kopi Sachet")


if __name__ == "__main__":
    unittest.main(verbosity=2)