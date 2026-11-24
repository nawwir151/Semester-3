import csv
import hashlib
import os
import shutil
import sqlite3
from datetime import datetime, timedelta

# Berkas salt eksternal sebagai pengalih (pepper) di folder proyek
DEFAULT_SALT_FILE = "stokita.salt"

# Karakter kosong / tak terlihat yang wajib ditolak pada input teks
INVISIBLE_CHARS = ("\u00a0", "\u200b", "\u200c", "\u200d", "\ufeff", "\u3000")


# =========================================================
# HELPER VALIDASI BLANK CHARACTER & SANITASI INPUT
# =========================================================


def sanitize_text(value, field_name="Input", required=True):
    """
    Membersihkan spasi berlebih dan karakter kosong tak terlihat (blank character).
    Jika required=True dan hasilnya kosong, melempar ValueError.
    """
    if value is None:
        cleaned = ""
    else:
        cleaned = str(value)
        for ch in INVISIBLE_CHARS:
            cleaned = cleaned.replace(ch, "")
        cleaned = cleaned.strip()

    if required and not cleaned:
        raise ValueError(
            f"{field_name} tidak boleh kosong atau hanya berisi spasi/karakter kosong!"
        )
    return cleaned


def validate_password_input(password, field_name="Password"):
    """Memastikan password tidak kosong dan tidak hanya berisi blank character."""
    if password is None:
        raise ValueError(f"{field_name} tidak boleh kosong!")
    pwd_str = str(password)
    cleaned = pwd_str
    for ch in INVISIBLE_CHARS:
        cleaned = cleaned.replace(ch, "")
    if not cleaned.strip():
        raise ValueError(
            f"{field_name} tidak boleh kosong atau hanya berisi spasi/karakter kosong!"
        )
    return pwd_str


# =========================================================
# HELPER FILE SALT (STOKITA.SALT) & ENKRIPSI PBKDF2-HMAC-SHA256
# =========================================================


def get_or_create_file_salt(salt_path=DEFAULT_SALT_FILE):
    """
    Membaca berkas salt eksternal (stokita.salt).
    Jika belum tersedia, otomatis membuat 32-byte salt acak baru.
    """
    if os.path.exists(salt_path):
        try:
            with open(salt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                try:
                    return bytes.fromhex(content)
                except ValueError:
                    return content.encode("utf-8")
        except Exception:
            pass

    new_file_salt = os.urandom(32)
    with open(salt_path, "w", encoding="utf-8") as f:
        f.write(new_file_salt.hex())
    return new_file_salt


def hash_password(password, salt=None, salt_path=DEFAULT_SALT_FILE):
    """
    Mengenkripsi password menggunakan PBKDF2-HMAC-SHA256
    dengan kombinasi File Salt (stokita.salt) + User Salt acak 16-byte.
    """
    pwd_valid = validate_password_input(password)
    if salt is None:
        user_salt = os.urandom(16)
    elif isinstance(salt, str):
        user_salt = bytes.fromhex(salt)
    else:
        user_salt = salt

    file_salt = get_or_create_file_salt(salt_path)
    combined_salt = file_salt + user_salt

    key = hashlib.pbkdf2_hmac(
        "sha256", pwd_valid.encode("utf-8"), combined_salt, 100000
    )
    return f"{user_salt.hex()}${key.hex()}"


def verify_password(
    stored_password, provided_password, salt_path=DEFAULT_SALT_FILE
):
    """Memverifikasi kecocokan password menggunakan File Salt + User Salt."""
    try:
        if not provided_password:
            return False
        salt_hex, key_hex = stored_password.split("$")
        user_salt = bytes.fromhex(salt_hex)
        file_salt = get_or_create_file_salt(salt_path)
        combined_salt = file_salt + user_salt

        new_key = hashlib.pbkdf2_hmac(
            "sha256",
            str(provided_password).encode("utf-8"),
            combined_salt,
            100000,
        )
        return new_key.hex() == key_hex
    except Exception:
        return False


# =========================================================
# KELAS UTAMA DATABASE STOKITA
# =========================================================


class Database:

    # Batas maksimal percobaan gagal login & durasi kunci sementara (detik)
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_SECONDS = 30

    # Daftar role resmi (Strict Whitelist) & batas kuota akun Admin
    VALID_ROLES = {"admin", "staff"}
    MAX_ADMIN_ACCOUNTS = 3

    # Daftar aksi yang dikunci eksklusif untuk Admin
    ADMIN_ONLY_ACTIONS = {
        "hapus_barang",
        "kelola_user",
        "lihat_log",
        "restore_db",
        "reset_data",
    }

    def __init__(
        self,
        db_path="stokita.db",
        backup_dir="backups",
        salt_path=DEFAULT_SALT_FILE,
    ):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.salt_path = salt_path
        os.makedirs(self.backup_dir, exist_ok=True)

        # Pastikan berkas pengalih (stokita.salt) tersedia
        get_or_create_file_salt(self.salt_path)

        # Sesi pengguna aktif
        self.current_user = "guest"
        self.current_role = ""

        # Inisialisasi koneksi dengan proteksi Auto-Recovery jika DB korup
        self.conn = self._connect_with_recovery()
        self._create()

    # =========================================================
    # PEMBATASAN LOGIN PERSISTEN (MAX 3X TRY & ERROR)
    # =========================================================
    def _get_failed_attempts(self):
        val = self.settings_get("login_failed_count", "0")
        try:
            return int(val)
        except (ValueError, TypeError):
            return 0

    def _set_failed_attempts(self, count):
        self.settings_set("login_failed_count", str(max(0, int(count))))

    def is_login_locked(self):
        """Mengecek status penguncian login secara persisten dari database."""
        lock_str = self.settings_get("login_lockout_until", "")
        if not lock_str:
            return False, 0

        try:
            lock_until = datetime.fromisoformat(lock_str)
            now = datetime.now()
            if now < lock_until:
                sisa_detik = int((lock_until - now).total_seconds()) + 1
                return True, sisa_detik
        except ValueError:
            pass

        self.reset_login_attempts()
        return False, 0

    def get_remaining_login_attempts(self):
        """Mengembalikan sisa kesempatan percobaan login sebelum terkunci."""
        locked, _ = self.is_login_locked()
        if locked:
            return 0
        return max(0, self.MAX_LOGIN_ATTEMPTS - self._get_failed_attempts())

    def reset_login_attempts(self):
        """Mereset penghitung gagal login dan membuka kunci."""
        self._set_failed_attempts(0)
        self.settings_set("login_lockout_until", "")

    # =========================================================
    # ROLE-BASED ACCESS CONTROL (STRICT WHITELIST & ANOMALY GUARD)
    # =========================================================
    def normalize_role(self, role):
        """Memvalidasi dan menormalkan nilai role."""
        role_clean = sanitize_text(role, field_name="Role", required=False).lower()
        if role_clean == "admin":
            return "Admin"
        if role_clean == "staff":
            return "Staff"
        raise PermissionError(
            f"Anomali hak akses terdeteksi: Role '{role}' tidak valid. Sistem menolak akses!"
        )

    def is_admin(self, role=None):
        """Mengecek secara ketat apakah role adalah Admin."""
        active_role = role if role is not None else self.current_role
        return str(active_role).strip().lower() == "admin"

    def has_permission(self, action, role=None):
        """Mengecek izin akses berdasarkan prinsip Whitelist ketat."""
        active_role = (
            str(role if role is not None else self.current_role).strip().lower()
        )
        if active_role not in self.VALID_ROLES:
            return False
        if active_role == "admin":
            return True
        return str(action).strip().lower() not in self.ADMIN_ONLY_ACTIONS

    def check_permission(self, action, role=None):
        """Memvalidasi izin di backend dan melempar PermissionError jika tidak berhak."""
        if not self.has_permission(action, role):
            raise PermissionError(
                f"Akses ditolak: Fitur '{action}' tidak diizinkan untuk role '{self.current_role}'."
            )
        return True

    # =========================================================
    # HELPER RESOLUSI PRIMARY KEY AMAN
    # =========================================================
    def _resolve_barang_id(self, identifier):
        """Mengonversi ID atau Kode Barang menjadi Primary Key integer yang valid."""
        if identifier is None:
            raise ValueError("ID atau Kode Barang tidak boleh kosong.")

        ident_str = sanitize_text(
            identifier, field_name="ID/Kode Barang", required=True
        )
        if ident_str.isdigit():
            row = self.conn.execute(
                "SELECT id FROM barang WHERE id = ?", (int(ident_str),)
            ).fetchone()
        else:
            row = self.conn.execute(
                "SELECT id FROM barang WHERE kode = ?", (ident_str,)
            ).fetchone()

        if not row:
            raise ValueError(
                f"Data barang '{ident_str}' tidak ditemukan di basis data."
            )
        return int(row["id"])

    # =========================================================
    # KONEKSI, AUTO-BACKUP & AUTO-RECOVERY
    # =========================================================
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _connect_with_recovery(self):
        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row

                check = conn.execute("PRAGMA integrity_check;").fetchone()
                if check and check[0] == "ok":
                    conn.execute("PRAGMA foreign_keys = ON;")
                    return conn
                conn.close()
            except Exception:
                pass

            print(
                "[WARNING] File database terdeteksi rusak! Memulai Auto-Recovery..."
            )
            self._auto_restore_latest()

        return self._connect()

    def _auto_restore_latest(self):
        if not os.path.exists(self.backup_dir):
            return False

        backups = [
            os.path.join(self.backup_dir, f)
            for f in os.listdir(self.backup_dir)
            if f.endswith(".db")
        ]
        if not backups:
            return False

        latest_backup = max(backups, key=os.path.getmtime)
        try:
            shutil.copy2(latest_backup, self.db_path)
            print(
                f"[SUCCESS] Database berhasil dipulihkan otomatis dari: {latest_backup}"
            )
            return True
        except Exception:
            return False

    def auto_backup(self):
        try:
            if hasattr(self, "conn") and self.conn:
                self.conn.commit()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"stokita_autobackup_{timestamp}.db"
            target_path = os.path.join(self.backup_dir, backup_filename)

            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, target_path)

                latest_path = os.path.join(
                    self.backup_dir, "stokita_latest_backup.db"
                )
                shutil.copy2(self.db_path, latest_path)

                self._cleanup_old_backups(max_files=10)
                return True
        except Exception as e:
            print(f"[ERROR] Auto-backup gagal: {e}")
        return False

    def _cleanup_old_backups(self, max_files=10):
        try:
            files = [
                os.path.join(self.backup_dir, f)
                for f in os.listdir(self.backup_dir)
                if f.startswith("stokita_autobackup_") and f.endswith(".db")
            ]
            files.sort(key=os.path.getmtime)
            while len(files) > max_files:
                oldest = files.pop(0)
                os.remove(oldest)
        except Exception:
            pass

    def close(self):
        if hasattr(self, "conn") and self.conn:
            try:
                self.auto_backup()
            except Exception:
                pass
            self.conn.close()

    def refresh(self):
        pass

    def reload(self):
        pass

    def reset_data(self):
        self.check_permission("reset_data")
        with self.conn as c:
            c.execute("DELETE FROM riwayat;")
            c.execute("DELETE FROM opname;")
            c.execute("DELETE FROM barang;")
            c.execute("DELETE FROM kategori;")
            c.execute("DELETE FROM remark;")
            try:
                c.execute(
                    "DELETE FROM sqlite_sequence WHERE name IN ('barang', 'riwayat', 'opname', 'kategori', 'remark');"
                )
            except sqlite3.OperationalError:
                pass
        self._create()
        self.log_aktivitas(
            self.current_user,
            "Reset Data",
            "Mereset seluruh data operasional sistem",
        )
        self.conn.commit()

    reset_database = reset_data
    clear_data = reset_data
    reset_all_data = reset_data

    # =========================================================
    # DDL: PEMBUATAN SKEMA TABEL & MIGRASI AMAN
    # =========================================================
    def _create(self):
        with self.conn as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    nama_lengkap TEXT NOT NULL DEFAULT 'Administrator',
                    role TEXT NOT NULL DEFAULT 'Staff' CHECK (role IN ('Admin', 'Staff'))
                );
            """
            )

            cols = [
                row["name"]
                for row in c.execute("PRAGMA table_info(users)").fetchall()
            ]
            if "nama_lengkap" not in cols:
                c.execute(
                    "ALTER TABLE users ADD COLUMN nama_lengkap TEXT DEFAULT 'Administrator';"
                )
            if "role" not in cols:
                c.execute(
                    "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Admin';"
                )

            if not c.execute("SELECT 1 FROM users").fetchone():
                default_pass = hash_password(
                    "admin123", salt_path=self.salt_path
                )
                c.execute(
                    "INSERT INTO users (username, password, nama_lengkap, role) VALUES (?, ?, ?, ?)",
                    ("admin", default_pass, "Administrator Utama", "Admin"),
                )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """
            )

            defaults = {
                "nama_toko": "Toko Saya",
                "nama_admin": "Administrator",
                "stok_min_default": "5",
                "remember_user": "",
                "login_failed_count": "0",
                "login_lockout_until": "",
            }
            for k, v in defaults.items():
                c.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    (k, v),
                )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS kategori (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT UNIQUE NOT NULL
                );
            """
            )

            if not c.execute("SELECT 1 FROM kategori").fetchone():
                for nama in ("ATK", "Makanan", "Minuman"):
                    c.execute(
                        "INSERT INTO kategori (nama) VALUES (?)", (nama,)
                    )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS remark (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kode TEXT UNIQUE NOT NULL,
                    tipe TEXT NOT NULL DEFAULT 'Umum',
                    keterangan TEXT NOT NULL
                );
            """
            )

            if not c.execute("SELECT 1 FROM remark").fetchone():
                default_remarks = [
                    ("RMK001", "Masuk", "Pembelian Stok Baru"),
                    ("RMK002", "Keluar", "Penjualan Toko"),
                    ("RMK003", "Keluar", "Barang Rusak / Kadaluarsa"),
                    ("RMK004", "Opname", "Penyesuaian Stock Opname"),
                ]
                c.executemany(
                    "INSERT INTO remark (kode, tipe, keterangan) VALUES (?, ?, ?)",
                    default_remarks,
                )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS barang (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kode TEXT UNIQUE NOT NULL,
                    nama TEXT NOT NULL,
                    kategori_id INTEGER,
                    satuan TEXT NOT NULL,
                    stok INTEGER DEFAULT 0 CHECK (stok >= 0),
                    stok_min INTEGER DEFAULT 0 CHECK (stok_min >= 0),
                    deskripsi TEXT DEFAULT '',
                    FOREIGN KEY (kategori_id) REFERENCES kategori(id) ON DELETE SET NULL
                );
            """
            )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS riwayat (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barang_id INTEGER,
                    remark_id INTEGER,
                    kode TEXT NOT NULL,
                    nama TEXT NOT NULL,
                    jenis TEXT NOT NULL,
                    jumlah INTEGER NOT NULL,
                    stok_akhir INTEGER NOT NULL,
                    keterangan TEXT DEFAULT '',
                    tanggal TEXT NOT NULL,
                    FOREIGN KEY (barang_id) REFERENCES barang(id) ON DELETE SET NULL,
                    FOREIGN KEY (remark_id) REFERENCES remark(id) ON DELETE SET NULL
                );
            """
            )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS opname (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kode TEXT NOT NULL,
                    nama TEXT NOT NULL,
                    stok_sistem INTEGER NOT NULL,
                    stok_fisik INTEGER NOT NULL,
                    selisih INTEGER NOT NULL,
                    tanggal TEXT NOT NULL
                );
            """
            )

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    aksi TEXT NOT NULL,
                    detail TEXT DEFAULT '',
                    waktu TEXT NOT NULL
                );
            """
            )
        self.conn.commit()

    # =========================================================
    # AUDIT TRAIL / LOG AKTIVITAS SISTEM (KHUSUS ADMIN)
    # =========================================================
    def log_aktivitas(self, username, aksi, detail=""):
        try:
            with self.conn as c:
                c.execute(
                    """
                    INSERT INTO activity_log (username, aksi, detail, waktu)
                    VALUES (?, ?, ?, datetime('now', 'localtime'))
                    """,
                    (str(username), str(aksi), str(detail)),
                )
            self.conn.commit()
        except Exception:
            pass

    def activity_log_list(self, limit=100):
        if not self.has_permission("lihat_log"):
            return []
        return self.conn.execute(
            "SELECT * FROM activity_log ORDER BY id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()

    add_log = log_aktivitas
    get_activity_logs = activity_log_list
    list_activity_log = activity_log_list

    # =========================================================
    # OTENTIKASI & MULTI-USER MANAGEMENT
    # =========================================================
    def login(self, username, password):
        locked, sisa_detik = self.is_login_locked()
        if locked:
            raise PermissionError(
                f"Login dikunci sementara karena 3x gagal! Silakan tunggu {sisa_detik} detik lagi."
            )

        user_clean = sanitize_text(
            username, field_name="Username", required=True
        )
        pwd_clean = validate_password_input(password, field_name="Password")

        cur = self.conn.execute(
            "SELECT * FROM users WHERE username = ?", (user_clean,)
        )
        user = cur.fetchone()

        if user and verify_password(
            user["password"], pwd_clean, salt_path=self.salt_path
        ):
            raw_role = user["role"] if "role" in user.keys() else ""
            validated_role = self.normalize_role(raw_role)

            self.reset_login_attempts()
            self.current_user = user["username"]
            self.current_role = validated_role
            self.log_aktivitas(
                self.current_user,
                "Login",
                f"Masuk ke sistem dengan role {self.current_role}",
            )
            return user

        gagal_ke = self._get_failed_attempts() + 1
        self._set_failed_attempts(gagal_ke)
        sisa_coba = self.get_remaining_login_attempts()

        self.log_aktivitas(
            user_clean,
            "Login Gagal",
            f"Percobaan gagal ke-{gagal_ke} dari {self.MAX_LOGIN_ATTEMPTS}",
        )

        if sisa_coba <= 0:
            lock_until = datetime.now() + timedelta(
                seconds=self.LOCKOUT_SECONDS
            )
            self.settings_set("login_lockout_until", lock_until.isoformat())
            self.log_aktivitas(
                user_clean,
                "Login Dikunci",
                f"Akses login dikunci {self.LOCKOUT_SECONDS} detik setelah 3x gagal",
            )
            raise PermissionError(
                f"Anda telah gagal login 3 kali! Akses dikunci selama {self.LOCKOUT_SECONDS} detik."
            )

        return None

    def logout(self):
        self.log_aktivitas(self.current_user, "Logout", "Keluar dari sistem")
        self.current_user = "guest"
        self.current_role = ""

    def user_list(self):
        if not self.has_permission("kelola_user"):
            return []
        return self.conn.execute(
            "SELECT id, username, nama_lengkap, role FROM users ORDER BY id ASC"
        ).fetchall()

    def user_add(self, username, password, nama_lengkap="", role="Staff"):
        self.check_permission("kelola_user")
        user_clean = sanitize_text(
            username, field_name="Username", required=True
        )
        pwd_clean = validate_password_input(password, field_name="Password")
        nama_clean = sanitize_text(
            nama_lengkap if nama_lengkap else user_clean.title(),
            field_name="Nama Lengkap",
            required=True,
        )
        role_clean = self.normalize_role(role)

        if role_clean == "Admin":
            jml_admin = self.conn.execute(
                "SELECT COUNT(*) FROM users WHERE LOWER(role) = 'admin'"
            ).fetchone()[0]
            if jml_admin >= self.MAX_ADMIN_ACCOUNTS:
                raise ValueError(
                    f"Jumlah akun Admin sudah mencapai batas maksimal ({self.MAX_ADMIN_ACCOUNTS} akun)."
                )

        hashed = hash_password(pwd_clean, salt_path=self.salt_path)
        with self.conn as c:
            c.execute(
                "INSERT INTO users (username, password, nama_lengkap, role) VALUES (?, ?, ?, ?)",
                (user_clean, hashed, nama_clean, role_clean),
            )
        self.log_aktivitas(
            self.current_user,
            "Tambah User",
            f"Menambahkan user {user_clean} ({role_clean})",
        )
        self.conn.commit()

    def user_update(self, user_id, nama_lengkap, role, password_baru=None):
        self.check_permission("kelola_user")
        uid = int(user_id)
        nama_clean = sanitize_text(
            nama_lengkap, field_name="Nama Lengkap", required=True
        )
        role_clean = self.normalize_role(role)

        if uid == 1 and role_clean != "Admin":
            raise ValueError(
                "Role akun Administrator utama tidak boleh diturunkan."
            )

        if role_clean == "Admin":
            jml_admin = self.conn.execute(
                "SELECT COUNT(*) FROM users WHERE LOWER(role) = 'admin' AND id != ?",
                (uid,),
            ).fetchone()[0]
            if jml_admin >= self.MAX_ADMIN_ACCOUNTS:
                raise ValueError(
                    f"Jumlah akun Admin sudah mencapai batas maksimal ({self.MAX_ADMIN_ACCOUNTS} akun)."
                )

        with self.conn as c:
            if password_baru is not None and str(password_baru) != "":
                pwd_clean = validate_password_input(
                    password_baru, field_name="Password Baru"
                )
                hashed = hash_password(pwd_clean, salt_path=self.salt_path)
                c.execute(
                    "UPDATE users SET nama_lengkap=?, role=?, password=? WHERE id=?",
                    (nama_clean, role_clean, hashed, uid),
                )
            else:
                c.execute(
                    "UPDATE users SET nama_lengkap=?, role=? WHERE id=?",
                    (nama_clean, role_clean, uid),
                )
        self.log_aktivitas(
            self.current_user,
            "Update User",
            f"Memperbarui data user ID {uid}",
        )
        self.conn.commit()

    def user_delete(self, user_id):
        self.check_permission("kelola_user")
        uid = int(user_id)
        if uid == 1:
            raise ValueError("Akun Administrator utama tidak dapat dihapus.")
        with self.conn as c:
            c.execute("DELETE FROM users WHERE id = ?", (uid,))
        self.log_aktivitas(
            self.current_user, "Hapus User", f"Menghapus user ID {uid}"
        )
        self.conn.commit()

    get_all_users = user_list
    add_user = user_add
    update_user = user_update
    delete_user = user_delete

    def check_password(self, *args, **kwargs):
        if not args and not kwargs:
            return False

        password = ""
        username = self.current_user

        if len(args) == 1:
            password = str(args[0])
        elif len(args) >= 2:
            arg1, arg2 = str(args[0]), str(args[1])
            for u, p in [(arg1, arg2), (arg2, arg1)]:
                row_pair = self.conn.execute(
                    "SELECT password FROM users WHERE username = ?", (u,)
                ).fetchone()
                if row_pair and verify_password(
                    row_pair["password"], p, salt_path=self.salt_path
                ):
                    return True
            password = arg1

        if "password" in kwargs:
            password = str(kwargs["password"])
        if "username" in kwargs:
            username = str(kwargs["username"])

        cur = self.conn.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        )
        row = cur.fetchone()
        if row and verify_password(
            row["password"], password, salt_path=self.salt_path
        ):
            return True

        cur_all = self.conn.execute("SELECT password FROM users")
        for r in cur_all.fetchall():
            if verify_password(
                r["password"], password, salt_path=self.salt_path
            ):
                return True

        return False

    verify_admin_password = check_password
    validate_password = check_password
    verifikasi_password = check_password
    cek_password = check_password

    def user_update_password(self, username, password_baru):
        user_clean = sanitize_text(
            username, field_name="Username", required=True
        )
        pwd_clean = validate_password_input(
            password_baru, field_name="Password Baru"
        )
        new_hash = hash_password(pwd_clean, salt_path=self.salt_path)
        with self.conn as c:
            c.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (new_hash, user_clean),
            )
        self.log_aktivitas(
            self.current_user,
            "Ubah Password",
            f"Memperbarui kata sandi akun {user_clean}",
        )
        self.conn.commit()

    update_password = user_update_password
    change_password = user_update_password

    # =========================================================
    # PENGATURAN APLIKASI (KEY-VALUE & DEFAULT MIN)
    # =========================================================
    def settings_get(self, key, default=""):
        cur = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?", (str(key),)
        )
        row = cur.fetchone()
        return row["value"] if row else default

    def settings_set(self, key, value):
        key_clean = sanitize_text(key, field_name="Key Setting", required=True)
        with self.conn as c:
            c.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key_clean, str(value)),
            )
        self.conn.commit()

    def get_setting(self, key, default=""):
        return self.settings_get(key, default)

    def set_setting(self, key, value):
        return self.settings_set(key, value)

    def save_setting(self, key, value):
        return self.settings_set(key, value)

    def settings_all(self):
        cur = self.conn.execute("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in cur.fetchall()}

    def get_settings(self):
        return self.settings_all()

    def get_all_settings(self):
        return self.settings_all()

    def default_min(self):
        val = self.settings_get("stok_min_default", "5")
        try:
            return int(val)
        except (ValueError, TypeError):
            return 5

    get_default_min = default_min
    default_stok_min = default_min
    stok_min_default = default_min

    # =========================================================
    # CRUD KATEGORI
    # =========================================================
    def kategori_list(self):
        sql = """
            SELECT 
                k.id, 
                k.nama, 
                k.nama AS kategori,
                k.nama AS nama_kategori,
                COUNT(b.id) AS jumlah,
                COUNT(b.id) AS total,
                COUNT(b.id) AS count,
                COUNT(b.id) AS jumlah_barang,
                COUNT(b.id) AS total_barang,
                COUNT(b.id) AS barang_count
            FROM kategori k 
            LEFT JOIN barang b ON k.id = b.kategori_id 
            GROUP BY k.id, k.nama 
            ORDER BY k.nama ASC
        """
        return self.conn.execute(sql).fetchall()

    def kategori_get(self, kat_id):
        return self.conn.execute(
            """
            SELECT 
                k.id, 
                k.nama, 
                k.nama AS kategori, 
                k.nama AS nama_kategori 
            FROM kategori k WHERE id = ?
        """,
            (int(kat_id),),
        ).fetchone()

    def kategori_add(self, *args, **kwargs):
        raw_nama = args[0] if args else kwargs.get("nama", "")
        nama = sanitize_text(
            raw_nama, field_name="Nama Kategori", required=True
        )
        with self.conn as c:
            c.execute("INSERT INTO kategori (nama) VALUES (?)", (nama,))
        self.conn.commit()

    def kategori_update(self, *args, **kwargs):
        kat_id = args[0] if len(args) > 0 else kwargs.get("id")
        raw_nama = args[1] if len(args) > 1 else kwargs.get("nama", "")
        if not kat_id:
            raise ValueError("ID Kategori tidak valid.")
        nama = sanitize_text(
            raw_nama, field_name="Nama Kategori", required=True
        )
        with self.conn as c:
            c.execute(
                "UPDATE kategori SET nama = ? WHERE id = ?",
                (nama, int(kat_id)),
            )
        self.conn.commit()

    def kategori_delete(self, *args, **kwargs):
        kat_id = args[0] if args else kwargs.get("id")
        if kat_id:
            with self.conn as c:
                c.execute("DELETE FROM kategori WHERE id = ?", (int(kat_id),))
            self.conn.commit()

    add_kategori = kategori_add
    update_kategori = kategori_update
    delete_kategori = kategori_delete
    get_all_kategori = kategori_list
    get_kategori_list = kategori_list
    list_kategori = kategori_list
    get_kategori = kategori_get

    # =========================================================
    # CRUD MASTER REMARK
    # =========================================================
    def remark_list(self, tipe=None):
        tipe_clean = sanitize_text(tipe, required=False)
        if tipe_clean.lower() in ("semua", "all"):
            tipe_clean = ""
        sql = """
            SELECT 
                id, 
                kode, 
                kode AS kode_remark, 
                tipe, 
                tipe AS jenis, 
                keterangan, 
                keterangan AS nama, 
                keterangan AS ket 
            FROM remark 
            WHERE (? = '' OR tipe = ? OR tipe = 'Umum')
            ORDER BY id ASC
        """
        return self.conn.execute(sql, (tipe_clean, tipe_clean)).fetchall()

    def remark_get(self, remark_id):
        return self.conn.execute(
            "SELECT * FROM remark WHERE id = ?", (int(remark_id),)
        ).fetchone()

    def remark_add(self, *args, **kwargs):
        raw_kode = args[0] if len(args) > 0 else kwargs.get("kode", "")
        raw_tipe = args[1] if len(args) > 1 else kwargs.get("tipe", "Umum")
        raw_ket = args[2] if len(args) > 2 else kwargs.get("keterangan", "")

        kode = sanitize_text(raw_kode, field_name="Kode Remark", required=True)
        tipe = sanitize_text(raw_tipe, field_name="Tipe Remark", required=True)
        keterangan = sanitize_text(
            raw_ket, field_name="Keterangan Remark", required=True
        )

        with self.conn as c:
            c.execute(
                "INSERT INTO remark (kode, tipe, keterangan) VALUES (?, ?, ?)",
                (kode, tipe, keterangan),
            )
        self.conn.commit()

    def remark_update(self, *args, **kwargs):
        remark_id = args[0] if len(args) > 0 else kwargs.get("id")
        raw_kode = args[1] if len(args) > 1 else kwargs.get("kode", "")
        raw_tipe = args[2] if len(args) > 2 else kwargs.get("tipe", "Umum")
        raw_ket = args[3] if len(args) > 3 else kwargs.get("keterangan", "")

        if not remark_id:
            raise ValueError("ID Remark tidak valid.")
        kode = sanitize_text(raw_kode, field_name="Kode Remark", required=True)
        tipe = sanitize_text(raw_tipe, field_name="Tipe Remark", required=True)
        keterangan = sanitize_text(
            raw_ket, field_name="Keterangan Remark", required=True
        )

        with self.conn as c:
            c.execute(
                "UPDATE remark SET kode=?, tipe=?, keterangan=? WHERE id=?",
                (kode, tipe, keterangan, int(remark_id)),
            )
        self.conn.commit()

    def remark_delete(self, *args, **kwargs):
        remark_id = args[0] if args else kwargs.get("id")
        if remark_id:
            with self.conn as c:
                c.execute("DELETE FROM remark WHERE id = ?", (int(remark_id),))
            self.conn.commit()

    add_remark = remark_add
    update_remark = remark_update
    delete_remark = remark_delete
    get_all_remark = remark_list
    get_remark_list = remark_list
    list_remark = remark_list
    get_remark = remark_get

    # =========================================================
    # CRUD BARANG (QUERY STATIS TERPARAMETERISASI & FILTER AMAN)
    # =========================================================
    def next_kode(self):
        cur = self.conn.execute(
            "SELECT kode FROM barang ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        if not row:
            return "BRG0001"
        try:
            num = int(row["kode"].replace("BRG", "")) + 1
            return f"BRG{num:04d}"
        except ValueError:
            return "BRG0001"

    def get_notifikasi_stok(self):
        sql = """
            SELECT 
                b.id, b.kode, b.nama, b.stok, b.stok_min, b.satuan,
                COALESCE(k.nama, '-') AS kategori,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    ELSE 'Kritis' 
                END AS status
            FROM barang b
            LEFT JOIN kategori k ON b.kategori_id = k.id
            WHERE b.stok <= b.stok_min
            ORDER BY b.stok ASC, b.nama ASC
        """
        return self.conn.execute(sql).fetchall()

    get_stok_kritis = get_notifikasi_stok
    notifikasi_stok = get_notifikasi_stok

    def barang_list(self, search="", kategori_id=None, status_stok=None):
        """
        Mengambil daftar barang menggunakan QUERY STATIS 100% TERPARAMETERISASI.
        Menangani nilai default dropdown GUI ('Semua Kategori', 'Semua Status', atau 0) dengan aman.
        """
        search_clean = sanitize_text(search, required=False)
        search_like = f"%{search_clean}%"

        kat_id_val = None
        if kategori_id is not None:
            kat_str = str(kategori_id).strip()
            if kat_str.isdigit() and int(kat_str) > 0:
                kat_id_val = int(kat_str)

        raw_status = sanitize_text(status_stok, required=False).lower()
        status_val = (
            raw_status if raw_status in ("kritis", "habis", "aman") else ""
        )

        sql = """
            SELECT 
                b.*, 
                COALESCE(k.nama, '-') AS nama_kategori,
                COALESCE(k.nama, '-') AS kategori,
                COALESCE(k.nama, '-') AS kategori_nama,
                COALESCE(k.nama, '-') AS kat_nama,
                b.stok_min AS min_stok,
                b.stok_min AS default_min,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    WHEN b.stok <= b.stok_min THEN 'Kritis' 
                    ELSE 'Aman' 
                END AS status,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    WHEN b.stok <= b.stok_min THEN 'Kritis' 
                    ELSE 'Aman' 
                END AS status_stok,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    WHEN b.stok <= b.stok_min THEN 'Kritis' 
                    ELSE 'Aman' 
                END AS status_barang
            FROM barang b
            LEFT JOIN kategori k ON b.kategori_id = k.id
            WHERE (? = '' OR b.kode LIKE ? OR b.nama LIKE ?)
              AND (? IS NULL OR b.kategori_id = ?)
              AND (
                    ? = ''
                    OR (? = 'kritis' AND b.stok <= b.stok_min AND b.stok > 0)
                    OR (? = 'habis' AND b.stok = 0)
                    OR (? = 'aman' AND b.stok > b.stok_min)
              )
            ORDER BY b.id DESC
        """
        params = (
            search_clean,
            search_like,
            search_like,
            kat_id_val,
            kat_id_val,
            status_val,
            status_val,
            status_val,
            status_val,
        )
        return self.conn.execute(sql, params).fetchall()

    def barang_get(self, barang_id):
        sql = """
            SELECT 
                b.*, 
                COALESCE(k.nama, '-') AS nama_kategori,
                COALESCE(k.nama, '-') AS kategori,
                COALESCE(k.nama, '-') AS kategori_nama,
                COALESCE(k.nama, '-') AS kat_nama,
                b.stok_min AS min_stok,
                b.stok_min AS default_min,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    WHEN b.stok <= b.stok_min THEN 'Kritis' 
                    ELSE 'Aman' 
                END AS status,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    WHEN b.stok <= b.stok_min THEN 'Kritis' 
                    ELSE 'Aman' 
                END AS status_stok,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    WHEN b.stok <= b.stok_min THEN 'Kritis' 
                    ELSE 'Aman' 
                END AS status_barang
            FROM barang b
            LEFT JOIN kategori k ON b.kategori_id = k.id
            WHERE b.id = ?
        """
        return self.conn.execute(sql, (int(barang_id),)).fetchone()

    def barang_by_kode(self, kode):
        kode_clean = sanitize_text(kode, required=False)
        sql = """
            SELECT 
                b.*, 
                COALESCE(k.nama, '-') AS nama_kategori,
                COALESCE(k.nama, '-') AS kategori,
                COALESCE(k.nama, '-') AS kategori_nama,
                COALESCE(k.nama, '-') AS kat_nama,
                b.stok_min AS min_stok,
                b.stok_min AS default_min,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    WHEN b.stok <= b.stok_min THEN 'Kritis' 
                    ELSE 'Aman' 
                END AS status,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    WHEN b.stok <= b.stok_min THEN 'Kritis' 
                    ELSE 'Aman' 
                END AS status_stok,
                CASE 
                    WHEN b.stok = 0 THEN 'Habis' 
                    WHEN b.stok <= b.stok_min THEN 'Kritis' 
                    ELSE 'Aman' 
                END AS status_barang
            FROM barang b
            LEFT JOIN kategori k ON b.kategori_id = k.id
            WHERE b.kode = ?
        """
        return self.conn.execute(sql, (kode_clean,)).fetchone()

    get_barang_by_kode = barang_by_kode
    get_by_kode = barang_by_kode
    barang_get_by_kode = barang_by_kode
    get_barang_kode = barang_by_kode

    def barang_add(self, *args, **kwargs):
        self.check_permission("tambah_barang")

        kode = self.next_kode()
        nama = ""
        kategori_id = None
        satuan = "Pcs"
        stok = 0
        stok_min = 5
        deskripsi = ""
        remark_id = None

        if len(args) >= 1:
            kode = args[0]
        if len(args) >= 2:
            nama = args[1]

        rem = list(args[2:])
        if len(rem) >= 1:
            kat_val = rem[0]
            if kat_val is not None and str(kat_val).strip().isdigit():
                kategori_id = int(kat_val)
            elif kat_val is None or str(kat_val).strip() == "":
                kategori_id = None
        if len(rem) >= 2:
            satuan = rem[1]
        if len(rem) >= 3:
            try:
                stok = int(rem[2])
            except (ValueError, TypeError):
                pass
        if len(rem) >= 4:
            try:
                stok_min = int(rem[3])
            except (ValueError, TypeError):
                pass
        if len(rem) >= 5:
            deskripsi = rem[4]
        if len(rem) >= 6:
            try:
                remark_id = int(rem[5])
            except (ValueError, TypeError):
                pass

        if "kode" in kwargs:
            kode = kwargs["kode"]
        if "nama" in kwargs:
            nama = kwargs["nama"]
        if "kategori_id" in kwargs:
            kategori_id = kwargs["kategori_id"]
        if "satuan" in kwargs:
            satuan = kwargs["satuan"]
        if "stok" in kwargs:
            stok = int(kwargs["stok"])
        if "stok_min" in kwargs:
            stok_min = int(kwargs["stok_min"])
        if "deskripsi" in kwargs:
            deskripsi = kwargs["deskripsi"]
        if "remark_id" in kwargs:
            remark_id = kwargs["remark_id"]

        kode_clean = sanitize_text(
            kode, field_name="Kode Barang", required=True
        )
        nama_clean = sanitize_text(
            nama, field_name="Nama Barang", required=True
        )
        satuan_clean = sanitize_text(
            satuan, field_name="Satuan Barang", required=True
        )
        deskripsi_clean = sanitize_text(deskripsi, required=False)

        if stok < 0 or stok_min < 0:
            raise ValueError("Stok dan Stok Minimum tidak boleh bernilai negatif.")

        if kategori_id is not None:
            cur = self.conn.execute(
                "SELECT 1 FROM kategori WHERE id=?", (int(kategori_id),)
            )
            if not cur.fetchone():
                kategori_id = None

        if remark_id is not None:
            cur = self.conn.execute(
                "SELECT 1 FROM remark WHERE id=?", (int(remark_id),)
            )
            if not cur.fetchone():
                remark_id = None

        with self.conn as c:
            cur = c.execute(
                """
                INSERT INTO barang (kode, nama, kategori_id, satuan, stok, stok_min, deskripsi)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    kode_clean,
                    nama_clean,
                    kategori_id,
                    satuan_clean,
                    stok,
                    stok_min,
                    deskripsi_clean,
                ),
            )
            barang_id = cur.lastrowid

            c.execute(
                """
                INSERT INTO riwayat (barang_id, remark_id, kode, nama, jenis, jumlah, stok_akhir, keterangan, tanggal)
                VALUES (?, ?, ?, ?, 'Masuk', ?, ?, 'Stok Awal Sistem', datetime('now', 'localtime'))
            """,
                (
                    barang_id,
                    remark_id,
                    kode_clean,
                    nama_clean,
                    stok,
                    stok,
                ),
            )
        self.log_aktivitas(
            self.current_user,
            "Tambah Barang",
            f"Menambahkan {kode_clean} - {nama_clean}",
        )
        self.conn.commit()
        return barang_id

    def barang_update(self, *args, **kwargs):
        self.check_permission("edit_barang")

        if not args and not kwargs:
            return

        raw_identifier = (
            args[0] if args else kwargs.get("barang_id", kwargs.get("id"))
        )
        target_id = self._resolve_barang_id(raw_identifier)
        cur_barang = self.barang_get(target_id)

        nama = cur_barang["nama"]
        kategori_id = cur_barang["kategori_id"]
        satuan = cur_barang["satuan"]
        stok = cur_barang["stok"]
        stok_min = cur_barang["stok_min"]
        deskripsi = cur_barang["deskripsi"]

        rem = list(args[1:])
        if len(rem) >= 1:
            nama = rem[0]

        rem_args = rem[1:]
        if (
            rem_args
            and isinstance(rem_args[0], str)
            and (
                rem_args[0].strip().startswith("BRG")
                or rem_args[0].strip() == cur_barang["kode"]
            )
        ):
            rem_args = rem_args[1:]

        if len(rem_args) >= 1:
            kat_val = rem_args[0]
            if kat_val is not None and str(kat_val).strip().isdigit():
                kategori_id = int(kat_val)
            elif kat_val is None or str(kat_val).strip() == "":
                kategori_id = None
        if len(rem_args) >= 2:
            satuan = rem_args[1]

        if len(rem_args) == 3:
            try:
                stok_min = int(rem_args[2])
            except (ValueError, TypeError):
                pass
        elif len(rem_args) == 4:
            try:
                stok_min = int(rem_args[2])
            except (ValueError, TypeError):
                pass
            deskripsi = rem_args[3]
        elif len(rem_args) == 5:
            try:
                stok = int(rem_args[2])
                stok_min = int(rem_args[3])
                deskripsi = rem_args[4]
            except (ValueError, TypeError):
                try:
                    stok_min = int(rem_args[2])
                except (ValueError, TypeError):
                    pass
                deskripsi = rem_args[3]
        elif len(rem_args) >= 6:
            try:
                stok = int(rem_args[2])
            except (ValueError, TypeError):
                pass
            try:
                stok_min = int(rem_args[3])
            except (ValueError, TypeError):
                pass
            deskripsi = rem_args[4]

        if "nama" in kwargs:
            nama = kwargs["nama"]
        if "kategori_id" in kwargs:
            kategori_id = kwargs["kategori_id"]
        if "satuan" in kwargs:
            satuan = kwargs["satuan"]
        if "stok" in kwargs:
            stok = int(kwargs["stok"])
        if "stok_min" in kwargs:
            stok_min = int(kwargs["stok_min"])
        if "deskripsi" in kwargs:
            deskripsi = kwargs["deskripsi"]

        nama_clean = sanitize_text(
            nama, field_name="Nama Barang", required=True
        )
        satuan_clean = sanitize_text(
            satuan, field_name="Satuan Barang", required=True
        )
        deskripsi_clean = sanitize_text(deskripsi, required=False)

        if stok < 0 or stok_min < 0:
            raise ValueError("Stok dan Stok Minimum tidak boleh bernilai negatif.")

        if kategori_id is not None:
            cur = self.conn.execute(
                "SELECT 1 FROM kategori WHERE id=?", (int(kategori_id),)
            )
            if not cur.fetchone():
                kategori_id = None

        with self.conn as c:
            c.execute(
                """
                UPDATE barang 
                SET nama=?, kategori_id=?, satuan=?, stok=?, stok_min=?, deskripsi=?
                WHERE id=?
            """,
                (
                    nama_clean,
                    kategori_id,
                    satuan_clean,
                    stok,
                    stok_min,
                    deskripsi_clean,
                    target_id,
                ),
            )
        self.log_aktivitas(
            self.current_user,
            "Edit Barang",
            f"Memperbarui barang ID {target_id} ({nama_clean})",
        )
        self.conn.commit()

    def barang_delete(self, *args, **kwargs):
        self.check_permission("hapus_barang")

        raw_identifier = (
            args[0] if args else kwargs.get("barang_id", kwargs.get("id"))
        )
        target_id = self._resolve_barang_id(raw_identifier)
        with self.conn as c:
            c.execute("DELETE FROM barang WHERE id = ?", (target_id,))
        self.log_aktivitas(
            self.current_user,
            "Hapus Barang",
            f"Menghapus barang ID {target_id}",
        )
        self.conn.commit()

    add_barang = barang_add
    update_barang = barang_update
    delete_barang = barang_delete
    get_barang = barang_get
    get_all_barang = barang_list
    get_barang_list = barang_list
    list_barang = barang_list

    # =========================================================
    # TRANSAKSI STOK & LOG RIWAYAT
    # =========================================================
    def ubah_stok(self, *args, **kwargs):
        raw_identifier = kwargs.get(
            "barang_id", args[0] if len(args) > 0 else None
        )
        target_id = self._resolve_barang_id(raw_identifier)

        jenis_raw = kwargs.get("jenis", args[1] if len(args) > 1 else "Masuk")
        jenis_clean = sanitize_text(
            jenis_raw, field_name="Jenis Transaksi", required=True
        )
        jumlah = int(kwargs.get("jumlah", args[2] if len(args) > 2 else 0))

        if jumlah <= 0:
            raise ValueError("Jumlah transaksi stok harus lebih dari 0.")

        remark_id = kwargs.get("remark_id", None)
        ket_tambahan = kwargs.get("ket_tambahan", kwargs.get("keterangan", ""))

        if len(args) == 4:
            val = args[3]
            if isinstance(val, int) or (
                isinstance(val, str) and val.strip().isdigit()
            ):
                r_id = int(val)
                cur = self.conn.execute(
                    "SELECT 1 FROM remark WHERE id=?", (r_id,)
                )
                if cur.fetchone():
                    remark_id = r_id
                else:
                    ket_tambahan = str(val)
            else:
                ket_tambahan = str(val)
        elif len(args) >= 5:
            r_val = args[3]
            if r_val is not None and str(r_val).strip().isdigit():
                r_id = int(r_val)
                cur = self.conn.execute(
                    "SELECT 1 FROM remark WHERE id=?", (r_id,)
                )
                if cur.fetchone():
                    remark_id = r_id
            ket_tambahan = str(args[4])

        ket_clean = sanitize_text(ket_tambahan, required=False)

        if remark_id is not None:
            cur = self.conn.execute(
                "SELECT 1 FROM remark WHERE id=?", (int(remark_id),)
            )
            if not cur.fetchone():
                remark_id = None

        with self.conn as c:
            row = c.execute(
                "SELECT id, kode, nama, stok FROM barang WHERE id = ?",
                (target_id,),
            ).fetchone()
            if not row:
                raise ValueError("Barang tidak ditemukan.")

            stok_lama = row["stok"]
            is_keluar = any(
                k in jenis_clean.lower() for k in ["keluar", "jual", "out"]
            )
            stok_baru = stok_lama - jumlah if is_keluar else stok_lama + jumlah

            if stok_baru < 0:
                raise ValueError("Stok tidak mencukupi.")

            c.execute(
                "UPDATE barang SET stok=? WHERE id=?", (stok_baru, target_id)
            )

            c.execute(
                """
                INSERT INTO riwayat (barang_id, remark_id, kode, nama, jenis, jumlah, stok_akhir, keterangan, tanggal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'))
            """,
                (
                    target_id,
                    remark_id,
                    row["kode"],
                    row["nama"],
                    jenis_clean,
                    jumlah,
                    stok_baru,
                    ket_clean,
                ),
            )
        self.conn.commit()

    def riwayat_list(self):
        sql = """
            SELECT 
                r.id,
                r.barang_id,
                r.remark_id,
                r.tanggal,
                r.tanggal AS waktu,
                r.tanggal AS tanggal_transaksi,
                r.kode,
                r.kode AS kode_barang,
                r.nama,
                r.nama AS nama_barang,
                r.jenis,
                r.jenis AS tipe,
                r.jenis AS jenis_transaksi,
                r.jumlah,
                r.jumlah AS qty,
                r.jumlah AS total,
                r.stok_akhir,
                r.stok_akhir AS stok,
                r.keterangan,
                COALESCE(rm.keterangan, r.keterangan, 'Umum') AS remark_keterangan,
                COALESCE(rm.keterangan, r.keterangan, 'Umum') AS remark,
                COALESCE(rm.keterangan, r.keterangan, 'Umum') AS remark_nama,
                r.keterangan AS catatan_tambahan
            FROM riwayat r
            LEFT JOIN remark rm ON r.remark_id = rm.id
            ORDER BY r.id DESC
        """
        return self.conn.execute(sql).fetchall()

    def riwayat_list_dengan_remark(self):
        return self.riwayat_list()

    get_riwayat = riwayat_list
    get_all_riwayat = riwayat_list
    get_riwayat_list = riwayat_list
    list_riwayat = riwayat_list
    get_riwayat_remark = riwayat_list_dengan_remark

    # =========================================================
    # FILTER RIWAYAT MULTI-KRITERIA (100% QUERY STATIS TERPARAMETERISASI)
    # =========================================================
    def riwayat_filter(
        self, tgl_mulai=None, tgl_selesai=None, jenis=None, search=""
    ):
        tgl_awal = sanitize_text(tgl_mulai, required=False)
        tgl_akhir = sanitize_text(tgl_selesai, required=False)
        jenis_clean = sanitize_text(jenis, required=False)
        if jenis_clean.lower() in (
            "semua",
            "semua jenis",
            "semua transaksi",
            "all",
        ):
            jenis_clean = ""
        jenis_like = f"%{jenis_clean.lower()}%"

        search_clean = sanitize_text(search, required=False)
        search_like = f"%{search_clean}%"

        sql = """
            SELECT 
                r.id, r.barang_id, r.remark_id, r.tanggal,
                r.tanggal AS waktu, r.tanggal AS tanggal_transaksi,
                r.kode, r.kode AS kode_barang, r.nama, r.nama AS nama_barang,
                r.jenis, r.jenis AS tipe, r.jenis AS jenis_transaksi,
                r.jumlah, r.jumlah AS qty, r.jumlah AS total,
                r.stok_akhir, r.stok_akhir AS stok, r.keterangan,
                COALESCE(rm.keterangan, r.keterangan, 'Umum') AS remark_keterangan,
                COALESCE(rm.keterangan, r.keterangan, 'Umum') AS remark,
                COALESCE(rm.keterangan, r.keterangan, 'Umum') AS remark_nama,
                r.keterangan AS catatan_tambahan
            FROM riwayat r
            LEFT JOIN remark rm ON r.remark_id = rm.id
            WHERE (? = '' OR ? = '' OR date(r.tanggal) BETWEEN date(?) AND date(?))
              AND (? = '' OR r.jenis = ? OR LOWER(r.jenis) LIKE ?)
              AND (? = '' OR r.kode LIKE ? OR r.nama LIKE ? OR r.keterangan LIKE ?)
            ORDER BY r.id DESC
        """
        params = (
            tgl_awal,
            tgl_akhir,
            tgl_awal,
            tgl_akhir,
            jenis_clean,
            jenis_clean,
            jenis_like,
            search_clean,
            search_like,
            search_like,
            search_like,
        )
        return self.conn.execute(sql, params).fetchall()

    def riwayat_list_by_date(self, tgl_mulai, tgl_selesai):
        return self.riwayat_filter(tgl_mulai=tgl_mulai, tgl_selesai=tgl_selesai)

    get_riwayat_filtered = riwayat_filter
    filter_riwayat = riwayat_filter

    # =========================================================
    # EKSPOR & IMPOR DATA LAPORAN (CSV / EXCEL)
    # =========================================================
    def export_riwayat_csv(
        self, filepath, tgl_mulai=None, tgl_selesai=None, jenis=None, search=""
    ):
        rows = self.riwayat_filter(tgl_mulai, tgl_selesai, jenis, search)
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "ID",
                        "Tanggal",
                        "Kode Barang",
                        "Nama Barang",
                        "Jenis Transaksi",
                        "Jumlah",
                        "Stok Akhir",
                        "Keterangan",
                    ]
                )
                for r in rows:
                    writer.writerow(
                        [
                            r["id"],
                            r["tanggal"],
                            r["kode"],
                            r["nama"],
                            r["jenis"],
                            r["jumlah"],
                            r["stok_akhir"],
                            r["remark_keterangan"],
                        ]
                    )
            self.log_aktivitas(
                self.current_user,
                "Ekspor Laporan",
                f"Ekspor riwayat ke {os.path.basename(filepath)}",
            )
            return True
        except Exception as e:
            print(f"[ERROR] Ekspor riwayat gagal: {e}")
            return False

    def export_barang_csv(self, filepath):
        rows = self.barang_list()
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "Kode Barang",
                        "Nama Barang",
                        "Kategori",
                        "Satuan",
                        "Sisa Stok",
                        "Stok Minimum",
                        "Status",
                        "Deskripsi",
                    ]
                )
                for b in rows:
                    writer.writerow(
                        [
                            b["kode"],
                            b["nama"],
                            b["kategori"],
                            b["satuan"],
                            b["stok"],
                            b["stok_min"],
                            b["status"],
                            b["deskripsi"],
                        ]
                    )
            self.log_aktivitas(
                self.current_user,
                "Ekspor Barang",
                f"Ekspor stok barang ke {os.path.basename(filepath)}",
            )
            return True
        except Exception as e:
            print(f"[ERROR] Ekspor barang gagal: {e}")
            return False

    def import_barang_csv(self, filepath):
        self.check_permission("tambah_barang")
        berhasil = 0
        try:
            with open(filepath, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_nama = row.get("Nama Barang") or row.get("nama")
                    nama = sanitize_text(raw_nama, required=False)
                    if not nama:
                        continue
                    kode = sanitize_text(
                        row.get("Kode Barang")
                        or row.get("kode")
                        or self.next_kode(),
                        required=True,
                    )
                    satuan = sanitize_text(
                        row.get("Satuan") or row.get("satuan") or "Pcs",
                        required=True,
                    )
                    stok = int(row.get("Sisa Stok") or row.get("stok") or 0)
                    stok_min = int(
                        row.get("Stok Minimum") or row.get("stok_min") or 5
                    )
                    deskripsi = sanitize_text(
                        row.get("Deskripsi") or row.get("deskripsi") or "",
                        required=False,
                    )

                    kat_nama = sanitize_text(
                        row.get("Kategori") or row.get("kategori") or "",
                        required=False,
                    )
                    kat_id = None
                    if kat_nama and kat_nama != "-":
                        kat_row = self.conn.execute(
                            "SELECT id FROM kategori WHERE LOWER(nama) = ?",
                            (kat_nama.lower(),),
                        ).fetchone()
                        if kat_row:
                            kat_id = kat_row["id"]

                    if not self.barang_by_kode(kode):
                        self.barang_add(
                            kode, nama, kat_id, satuan, stok, stok_min, deskripsi
                        )
                        berhasil += 1
            self.log_aktivitas(
                self.current_user,
                "Impor Barang",
                f"Mengimpor {berhasil} data barang dari CSV",
            )
            return berhasil
        except Exception as e:
            print(f"[ERROR] Impor CSV gagal: {e}")
            return berhasil

    ekspor_riwayat = export_riwayat_csv
    ekspor_barang = export_barang_csv
    impor_barang = import_barang_csv

    # =========================================================
    # STOCK OPNAME & STATISTIK OPNAME
    # =========================================================
    def opname_add(self, *args, **kwargs):
        kode = None
        nama = ""
        stok_sistem = 0
        stok_fisik = 0
        selisih = 0

        if len(args) == 5:
            kode, nama, stok_sistem, stok_fisik, selisih = args
        elif len(args) == 2:
            kode, stok_fisik = args
            b = self.barang_by_kode(kode)
            if b:
                nama = b["nama"]
                stok_sistem = int(b["stok"])
            else:
                nama = str(kode)
                stok_sistem = 0
            stok_fisik = int(stok_fisik)
            selisih = stok_fisik - stok_sistem
        elif len(args) == 3:
            kode, stok_sistem, stok_fisik = args
            b = self.barang_by_kode(kode)
            nama = b["nama"] if b else str(kode)
            stok_sistem = int(stok_sistem)
            stok_fisik = int(stok_fisik)
            selisih = stok_fisik - stok_sistem
        elif len(args) == 4:
            kode, nama, stok_sistem, stok_fisik = args
            stok_sistem = int(stok_sistem)
            stok_fisik = int(stok_fisik)
            selisih = stok_fisik - stok_sistem
        else:
            kode = kwargs.get("kode", args[0] if len(args) > 0 else "")
            stok_fisik = int(
                kwargs.get(
                    "stok_fisik",
                    kwargs.get("fisik", args[1] if len(args) > 1 else 0),
                )
            )
            b = self.barang_by_kode(kode)
            if b:
                nama = b["nama"]
                stok_sistem = int(b["stok"])
            else:
                nama = kwargs.get("nama", str(kode))
                stok_sistem = int(kwargs.get("stok_sistem", 0))
            selisih = stok_fisik - stok_sistem

        kode_clean = sanitize_text(
            kode, field_name="Kode Barang", required=True
        )
        nama_clean = sanitize_text(
            nama, field_name="Nama Barang", required=True
        )

        with self.conn as c:
            c.execute(
                """
                INSERT INTO opname (kode, nama, stok_sistem, stok_fisik, selisih, tanggal)
                VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
            """,
                (
                    kode_clean,
                    nama_clean,
                    int(stok_sistem),
                    int(stok_fisik),
                    int(selisih),
                ),
            )
        self.conn.commit()
        return selisih

    def opname_list(self):
        sql = """
            SELECT 
                id,
                kode,
                kode AS kode_barang,
                nama,
                nama AS nama_barang,
                stok_sistem,
                stok_sistem AS sistem,
                stok_fisik,
                stok_fisik AS fisik,
                selisih,
                tanggal,
                tanggal AS waktu,
                tanggal AS tanggal_opname
            FROM opname 
            ORDER BY id DESC
        """
        return self.conn.execute(sql).fetchall()

    def opname_stats(self):
        c = self.conn.cursor()
        total = c.execute("SELECT COUNT(*) FROM opname").fetchone()[0]
        selisih_count = c.execute(
            "SELECT COUNT(*) FROM opname WHERE selisih != 0"
        ).fetchone()[0]
        sesuai_count = c.execute(
            "SELECT COUNT(*) FROM opname WHERE selisih = 0"
        ).fetchone()[0]
        total_selisih_pcs = c.execute(
            "SELECT COALESCE(SUM(ABS(selisih)), 0) FROM opname"
        ).fetchone()[0]

        return {
            "total": total,
            "total_opname": total,
            "count": total,
            "selisih": selisih_count,
            "total_selisih": selisih_count,
            "sesuai": sesuai_count,
            "total_sesuai": sesuai_count,
            "total_pcs_selisih": total_selisih_pcs,
            "selisih_pcs": total_selisih_pcs,
        }

    add_opname = opname_add
    opname_save = opname_add
    save_opname = opname_add
    insert_opname = opname_add
    get_all_opname = opname_list
    get_opname_list = opname_list
    list_opname = opname_list
    get_opname_stats = opname_stats

    # =========================================================
    # DASHBOARD STATISTICS & GRAFIK LANJUTAN
    # =========================================================
    def stats(self):
        c = self.conn.cursor()
        total_jenis = c.execute("SELECT COUNT(*) FROM barang").fetchone()[0]
        total_stok = c.execute(
            "SELECT COALESCE(SUM(stok), 0) FROM barang"
        ).fetchone()[0]
        stok_kritis = c.execute(
            "SELECT COUNT(*) FROM barang WHERE stok <= stok_min AND stok > 0"
        ).fetchone()[0]
        stok_habis = c.execute(
            "SELECT COUNT(*) FROM barang WHERE stok = 0"
        ).fetchone()[0]
        total_kategori = c.execute("SELECT COUNT(*) FROM kategori").fetchone()[
            0
        ]

        total_keluar = c.execute(
            """
            SELECT COALESCE(SUM(jumlah), 0) 
            FROM riwayat 
            WHERE LOWER(jenis) LIKE '%keluar%' 
               OR LOWER(jenis) LIKE '%jual%' 
               OR LOWER(jenis) = 'out'
            """
        ).fetchone()[0]

        total_masuk = c.execute(
            """
            SELECT COALESCE(SUM(jumlah), 0) 
            FROM riwayat 
            WHERE LOWER(jenis) LIKE '%masuk%' 
               OR LOWER(jenis) = 'in'
            """
        ).fetchone()[0]

        return {
            "total_barang": total_stok,
            "total_stok": total_stok,
            "stok": total_stok,
            "total_jenis": total_jenis,
            "jenis": total_jenis,
            "total_varian": total_jenis,
            "varian": total_jenis,
            "stok_kritis": stok_kritis,
            "kritis": stok_kritis,
            "total_kritis": stok_kritis,
            "stok_habis": stok_habis,
            "habis": stok_habis,
            "total_habis": stok_habis,
            "total_kategori": total_kategori,
            "kategori": total_kategori,
            "terjual": total_keluar,
            "total_terjual": total_keluar,
            "keluar": total_keluar,
            "total_keluar": total_keluar,
            "barang_keluar": total_keluar,
            "stok_terjual": total_keluar,
            "total_stok_terjual": total_keluar,
            "masuk": total_masuk,
            "total_masuk": total_masuk,
            "barang_masuk": total_masuk,
        }

    def stats_grafik_7_hari(self):
        sql = """
            SELECT 
                date(tanggal) AS tgl,
                SUM(CASE WHEN LOWER(jenis) LIKE '%masuk%' THEN jumlah ELSE 0 END) AS total_masuk,
                SUM(CASE WHEN LOWER(jenis) LIKE '%keluar%' OR LOWER(jenis) LIKE '%jual%' THEN jumlah ELSE 0 END) AS total_keluar
            FROM riwayat
            WHERE date(tanggal) >= date('now', '-7 days')
            GROUP BY date(tanggal)
            ORDER BY tgl ASC
        """
        return self.conn.execute(sql).fetchall()

    def stats_per_kategori(self):
        sql = """
            SELECT 
                COALESCE(k.nama, 'Tanpa Kategori') AS kategori,
                COUNT(b.id) AS total_varian,
                COALESCE(SUM(b.stok), 0) AS total_stok
            FROM kategori k
            LEFT JOIN barang b ON k.id = b.kategori_id
            GROUP BY k.id, k.nama
            ORDER BY total_stok DESC
        """
        return self.conn.execute(sql).fetchall()

    def stats_grafik_bulanan(self):
        sql = """
            SELECT 
                strftime('%Y-%m', tanggal) AS bulan,
                SUM(CASE WHEN LOWER(jenis) LIKE '%masuk%' THEN jumlah ELSE 0 END) AS total_masuk,
                SUM(CASE WHEN LOWER(jenis) LIKE '%keluar%' OR LOWER(jenis) LIKE '%jual%' THEN jumlah ELSE 0 END) AS total_keluar
            FROM riwayat
            GROUP BY strftime('%Y-%m', tanggal)
            ORDER BY bulan ASC
        """
        return self.conn.execute(sql).fetchall()

    get_stats = stats
    dashboard_stats = stats
    get_dashboard_stats = stats
    get_grafik_stats = stats_grafik_7_hari
    stats_7_hari = stats_grafik_7_hari
    get_kategori_stats = stats_per_kategori
    get_grafik_bulanan = stats_grafik_bulanan

    # =========================================================
    # BACKUP & PULIHKAN (RESTORE) DATABASE DENGAN UJI INTEGRITAS
    # =========================================================
    def backup_database(self, target_path):
        target_clean = sanitize_text(
            target_path, field_name="Lokasi Backup", required=True
        )
        try:
            self.conn.commit()
            shutil.copy2(self.db_path, target_clean)
            self.log_aktivitas(
                self.current_user,
                "Backup Manual",
                f"Backup database ke {os.path.basename(target_clean)}",
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Gagal mencadangkan database: {e}")

    def restore_database(self, source_path):
        self.check_permission("restore_db")
        source_clean = sanitize_text(
            source_path, field_name="File Backup", required=True
        )
        if not os.path.exists(source_clean):
            raise FileNotFoundError("Berkas cadangan tidak ditemukan.")

        test_conn = None
        try:
            test_conn = sqlite3.connect(source_clean)
            check = test_conn.execute("PRAGMA integrity_check;").fetchone()
            if not check or check[0] != "ok":
                raise ValueError("File cadangan rusak (corrupt) dan tidak dapat dipulihkan.")

            tables = {
                r[0]
                for r in test_conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            if not {"users", "barang", "riwayat"}.issubset(tables):
                raise ValueError(
                    "File yang dipilih bukan berkas cadangan STOKITA yang valid."
                )
        finally:
            if test_conn:
                test_conn.close()

        self.auto_backup()

        try:
            if hasattr(self, "conn") and self.conn:
                self.conn.close()
            shutil.copy2(source_clean, self.db_path)
            self.conn = self._connect()
            self._create()
            self.log_aktivitas(
                self.current_user,
                "Restore Database",
                f"Memulihkan database dari {os.path.basename(source_clean)}",
            )
            return True
        except Exception as e:
            self.conn = self._connect()
            raise RuntimeError(f"Gagal memulihkan database: {e}")

    backup = backup_database
    restore = restore_database