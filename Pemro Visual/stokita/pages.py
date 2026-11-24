"""Halaman-halaman aplikasi STOKITA."""
import csv
import sqlite3
from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtWidgets import (QAbstractItemView, QButtonGroup, QComboBox, QDialog,
                             QFileDialog, QFrame, QGridLayout, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QMessageBox, QScrollArea, QTableWidget,
                             QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget)

import memtrace
from ui_common import (Header, StatCard, StatsRow, asset, button, center, color_row,
                       fit_dialog, logo_label, pill, repolish, small_button, two_step_confirm)


def make_table(headers):
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setShowGrid(False)
    t.setFocusPolicy(Qt.NoFocus)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    t.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
    return t


def clear_table(t):
    """Hapus semua cell widget lama agar tidak tersisa 'hantu' saat tabel dimuat ulang."""
    for r in range(t.rowCount()):
        for c in range(t.columnCount()):
            w = t.cellWidget(r, c)
            if w is not None:
                t.removeCellWidget(r, c)
                w.hide()
                w.deleteLater()
    t.clearContents()


def cell(text):
    it = QTableWidgetItem(str(text))
    it.setTextAlignment(Qt.AlignCenter)
    return it


def field(label, widget):
    box = QVBoxLayout()
    box.setSpacing(3)
    lb = QLabel(label)
    lb.setStyleSheet("color:#374151;font-size:12px;")
    box.addWidget(lb)
    box.addWidget(widget)
    return box


def grid_field(grid, row, col, label, widget, colspan=1):
    """Taruh label (baris atas) + input (baris bawah) di grid dialog 2 kolom."""
    lb = QLabel(label)
    lb.setStyleSheet("color:#374151;font-size:12px;font-weight:600;")
    grid.addWidget(lb, row * 2, col, 1, colspan)
    grid.addWidget(widget, row * 2 + 1, col, 1, colspan)


def int_input(text="0"):
    e = QLineEdit(text)
    e.setValidator(QIntValidator(0, 10_000_000))
    return e


def to_int(edit):
    try:
        return int(edit.text() or 0)
    except ValueError:
        return 0


# ====================================================================== LOGIN
class LoginPage(QWidget):
    logged_in = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 6, 12, 6)
        root = QFrame()
        root.setObjectName("loginRoot")
        outer.addWidget(root)
        col = QVBoxLayout(root)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        band = QFrame()
        band.setObjectName("loginBand")
        band.setFixedHeight(46)
        col.addWidget(band)

        body = QHBoxLayout()
        body.setContentsMargins(80, 30, 100, 30)
        col.addLayout(body)

        # kiri: logo + ilustrasi
        left = QVBoxLayout()
        left.setAlignment(Qt.AlignCenter)
        left.addWidget(logo_label(64, tagline=True, width=330))
        ill = QLabel()
        ill.setAlignment(Qt.AlignCenter)
        p = asset("ilustrasi.png")
        if p:
            ill.setPixmap(QPixmap(p).scaled(420, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif not asset("logo.png"):
            ill.setText("<span style='font-size:70px;'>🗄️📦📋💻🪴</span>")
        left.addWidget(ill)
        body.addLayout(left, 5)

        # kanan: form
        form = QVBoxLayout()
        form.setAlignment(Qt.AlignVCenter)
        form.setSpacing(0)
        title = QLabel("Selamat Datang!")
        title.setObjectName("loginTitle")
        sub = QLabel("Silahkan masuk untuk melanjutkan ke aplikasi")
        sub.setStyleSheet("font-size:14px;")
        form.addWidget(title)
        form.addWidget(sub)
        form.addSpacing(22)
        self.user = QLineEdit()
        self.user.setPlaceholderText("👤   Username")
        self.pw = QLineEdit()
        self.pw.setPlaceholderText("🔒   Password")
        self.pw.setEchoMode(QLineEdit.Password)
        for w in (self.user, self.pw):
            w.setFixedHeight(50)
            w.returnPressed.connect(self.try_login)
        form.addWidget(self.user)
        self.error = QLabel("")
        self.error.setObjectName("errorLabel")
        self.error.setFixedHeight(22)
        form.addWidget(self.error)
        form.addSpacing(6)
        form.addWidget(self.pw)
        form.addSpacing(34)
        btn = button("Masuk", "bigBtn")
        btn.clicked.connect(self.try_login)
        form.addWidget(btn)
        form.addSpacing(12)
        from PyQt5.QtWidgets import QCheckBox
        self.remember = QCheckBox("Ingat saya")
        self.remember.setStyleSheet("margin-left:24px;font-size:14px;")
        form.addWidget(self.remember)
        body.addLayout(form, 4)
        self.load_remembered()

    def load_remembered(self):
        u = self.db.get_setting("remember_user", "")
        self.user.setText(u)
        self.remember.setChecked(bool(u))
        self.pw.clear()
        self.set_error(None)

    def set_error(self, msg):
        self.error.setText(msg or "")
        self.user.setProperty("error", bool(msg))
        repolish(self.user)

    def try_login(self):
        u, p = self.user.text().strip(), self.pw.text()
        if self.db.login(u, p):
            self.db.set_setting("remember_user", u if self.remember.isChecked() else "")
            self.set_error(None)
            self.pw.clear()
            self.logged_in.emit()
        else:
            self.set_error("Username atau Password salah")


# ====================================================================== DIALOG BARANG
class KategoriDialog(QDialog):
    """Dialog kecil untuk menambah kategori baru."""
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.nama_baru = ""
        self.setWindowTitle("Tambah Kategori")
        self.setModal(True)
        self.setFixedWidth(380)
        v = QVBoxLayout(self)
        v.setContentsMargins(28, 20, 28, 20)
        v.setSpacing(8)
        t = QLabel("Tambah Kategori")
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size:19px;font-weight:800;")
        v.addWidget(t)
        self.nama = QLineEdit()
        self.nama.setPlaceholderText("Mis. Elektronik")
        self.nama.returnPressed.connect(self.save)
        v.addLayout(field("Nama Kategori", self.nama))
        self.err = QLabel("")
        self.err.setObjectName("errorLabel")
        v.addWidget(self.err)
        row = QHBoxLayout()
        cancel = button("Batal", "grayBtn")
        ok = button("Simpan", "greenBtn")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.save)
        row.addWidget(cancel)
        row.addStretch()
        row.addWidget(ok)
        v.addLayout(row)
        self.nama.setFocus()

    def save(self, *_):
        nama = " ".join(self.nama.text().split())
        if not nama:
            self.err.setText("Nama kategori tidak boleh kosong.")
            return
        if any(k["nama"].lower() == nama.lower() for k in self.db.kategori_list()):
            self.err.setText(f"Kategori '{nama}' sudah ada.")
            return
        try:
            self.db.kategori_add(nama)
        except Exception as e:
            QMessageBox.critical(self, "STOKITA", f"Gagal menambah kategori:\n{e}")
            return
        self.nama_baru = nama
        self.accept()


class BarangDialog(QDialog):
    def __init__(self, db, barang=None, parent=None):
        super().__init__(parent)
        self.db, self.barang = db, barang
        self.setWindowTitle("Edit Barang" if barang else "Tambah Barang")
        self.setModal(True)
        v = QVBoxLayout(self)
        v.setContentsMargins(26, 18, 26, 18)
        v.setSpacing(10)
        t = QLabel("Edit Barang" if barang else "Tambah Barang")
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size:20px;font-weight:800;")
        v.addWidget(t)

        self.kode = QLineEdit(barang["kode"] if barang else db.next_kode())
        self.kode.setReadOnly(bool(barang))
        self.nama = QLineEdit(barang["nama"] if barang else "")
        self.kategori = QComboBox()
        self.fill_kategori(barang["kategori_id"] if barang else None)
        cat_box = QWidget()
        cb = QHBoxLayout(cat_box)
        cb.setContentsMargins(0, 0, 0, 0)
        cb.setSpacing(6)
        cb.addWidget(self.kategori, 1)
        plus = small_button("＋", "#D1FAE5", "#059669", 30)
        plus.setToolTip("Tambah kategori baru")
        plus.clicked.connect(self.tambah_kategori)
        cb.addWidget(plus)
        self.satuan = QLineEdit(barang["satuan"] if barang else "pcs")
        self.stok = int_input(str(barang["stok"]) if barang else "0")
        self.stok_min = int_input(str(barang["stok_min"]) if barang else str(db.default_min()))
        self.desc = QTextEdit(barang["deskripsi"] if barang else "")
        self.desc.setAcceptRichText(False)
        self.desc.setFixedHeight(64)
        self.nama.setPlaceholderText("Mis. Buku Tulis")
        self.satuan.setPlaceholderText("pcs / box / kg")

        # Tata letak 2 kolom agar dialog pendek dan semua tombol selalu terlihat
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(3)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid_field(grid, 0, 0, "Kode Barang", self.kode)
        grid_field(grid, 0, 1, "Nama Barang", self.nama)
        grid_field(grid, 1, 0, "Kategori", cat_box)
        grid_field(grid, 1, 1, "Satuan", self.satuan)
        grid_field(grid, 2, 0, "Sisa Stok", self.stok)
        grid_field(grid, 2, 1, "Stok Minimum", self.stok_min)
        grid_field(grid, 3, 0, "Deskripsi (Opsional)", self.desc, colspan=2)
        for r in (1, 3, 5):               # beri jarak antar baris field
            grid.setRowMinimumHeight(r, 40)
        v.addLayout(grid)

        row = QHBoxLayout()
        cancel = button("Batal", "grayBtn")
        save = button("Simpan", "greenBtn")
        save.setDefault(True)
        cancel.setMinimumWidth(100)
        save.setMinimumWidth(100)
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.save)
        row.addWidget(cancel)
        row.addStretch()
        row.addWidget(save)
        v.addSpacing(4)
        v.addLayout(row)
        self.setMinimumWidth(560)
        fit_dialog(self)

    def fill_kategori(self, select_id=None):
        self.kategori.clear()
        self.kategori.addItem("(Tanpa kategori)", None)
        for k in self.db.kategori_list():
            self.kategori.addItem(k["nama"], k["id"])
        if select_id is not None:
            self.kategori.setCurrentIndex(max(self.kategori.findData(select_id), 0))

    def tambah_kategori(self, *_):
        dlg = KategoriDialog(self.db, self)
        if dlg.exec_() == QDialog.Accepted:
            self.fill_kategori()
            self.kategori.setCurrentIndex(max(self.kategori.findText(dlg.nama_baru), 0))

    def save(self):
        kode, nama = self.kode.text().strip(), self.nama.text().strip()
        if not kode or not nama:
            QMessageBox.warning(self, "STOKITA", "Kode dan Nama Barang wajib diisi.")
            return
        args = (self.kategori.currentData(), self.satuan.text().strip() or "pcs",
                to_int(self.stok), to_int(self.stok_min), self.desc.toPlainText().strip())
        try:
            if self.barang:
                self.db.barang_update(self.barang["id"], nama, *args)
            else:
                self.db.barang_add(kode, nama, *args)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "STOKITA", f"Kode barang '{kode}' sudah digunakan.")
            return
        self.accept()


class StockDialog(QDialog):
    def __init__(self, db, barang, jenis, parent=None):
        super().__init__(parent)
        self.db, self.barang, self.jenis = db, barang, jenis
        self.setModal(True)
        self.setFixedWidth(360)
        masuk = jenis == "masuk"
        self.setWindowTitle("Tambah Stok" if masuk else "Kurangi Stok")
        v = QVBoxLayout(self)
        v.setContentsMargins(28, 20, 28, 20)
        t = QLabel("Tambah Stok (Barang Masuk)" if masuk else "Kurangi Stok (Barang Keluar)")
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size:17px;font-weight:800;")
        info = QLabel(f"{barang['kode']} - {barang['nama']}\nSisa stok saat ini: {barang['stok']}")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color:#4B5563;")
        self.jumlah = int_input("1")
        self.ket = QLineEdit()
        self.ket.setPlaceholderText("Mis. Penjualan harian / Restock supplier")
        self.warn = QLabel("")
        self.warn.setWordWrap(True)
        self.warn.setAlignment(Qt.AlignCenter)
        self.warn.hide()
        v.addWidget(t)
        v.addWidget(info)
        v.addLayout(field("Jumlah", self.jumlah))
        v.addWidget(self.warn)
        if not masuk:
            self.jumlah.textChanged.connect(self.update_warning)
            self.update_warning()
        v.addLayout(field("Keterangan (opsional)", self.ket))
        v.addSpacing(8)
        row = QHBoxLayout()
        cancel = button("Batal", "grayBtn")
        ok = button("Simpan", "greenBtn")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.save)
        row.addWidget(cancel)
        row.addStretch()
        row.addWidget(ok)
        v.addLayout(row)

    def update_warning(self):
        """Peringatan langsung saat mengetik jumlah barang keluar."""
        b = self.barang
        sisa = b["stok"] - to_int(self.jumlah)
        if sisa < 0 or to_int(self.jumlah) <= 0:
            self.warn.hide()
            return
        if sisa == 0:
            msg, bg, fg = "⛔ Stok akan HABIS setelah barang keluar.", "#FEE2E2", "#B91C1C"
        elif sisa <= b["stok_min"]:
            msg = (f"⚠ Stok akan menjadi {sisa}, sudah melewati stok minimum "
                   f"({b['stok_min']}). Segera lakukan restock!")
            bg, fg = "#FEF3C7", "#92400E"
        else:
            self.warn.hide()
            return
        self.warn.setText(msg)
        self.warn.setStyleSheet(f"background:{bg};color:{fg};border-radius:10px;"
                                "padding:8px;font-weight:700;")
        self.warn.show()

    def save(self):
        try:
            self.db.ubah_stok(self.barang["id"], self.jenis, to_int(self.jumlah), self.ket.text().strip())
        except ValueError as e:
            QMessageBox.warning(self, "STOKITA", str(e))
            return
        if self.jenis == "keluar":
            b = self.db.barang_get(self.barang["id"])
            if b["stok"] <= 0:
                QMessageBox.critical(self, "⛔ Stok Habis",
                                     f"Stok '{b['nama']}' sekarang HABIS (0).\n"
                                     "Segera lakukan pembelian/restock barang ini.")
            elif b["stok"] <= b["stok_min"]:
                QMessageBox.warning(self, "⚠ Stok Kritis",
                                    f"Stok '{b['nama']}' tinggal {b['stok']} {b['satuan'] or ''}, "
                                    f"sudah melewati stok minimum ({b['stok_min']}).\n"
                                    "Segera lakukan restock barang ini.")
        self.accept()


# ====================================================================== PANEL DAFTAR BARANG
class BarangPanel(QFrame):
    """Panel 'Daftar Barang' dipakai di Dashboard (tanpa tombol stok) dan Data Barang."""
    def __init__(self, db, on_change, with_stock_buttons=False):
        super().__init__()
        self.db, self.on_change, self.with_stock = db, on_change, with_stock_buttons
        self.setObjectName("panel")
        self.setMinimumHeight(330)
        v = QVBoxLayout(self)
        v.setContentsMargins(26, 16, 26, 18)
        v.setSpacing(10)
        top = QHBoxLayout()
        title = QLabel("Daftar Barang")
        title.setObjectName("panelTitle")
        add = button("＋  Tambah Barang", "tealBtn")
        add.clicked.connect(self.add)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(add, alignment=Qt.AlignTop)
        v.addLayout(top)

        self.alert = QLabel("")
        self.alert.setWordWrap(True)
        self.alert.hide()
        v.addWidget(self.alert)

        flt = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("🔍  Cari barang...")
        self.search.setFixedWidth(210)
        self.cat = QComboBox()
        self.cat.setObjectName("filterBox")
        self.cat.setFixedWidth(170)
        self.status = QComboBox()
        self.status.setObjectName("filterBox")
        self.status.addItems(["Semua Status", "Aman", "Kritis", "Habis"])
        self.status.setFixedWidth(150)
        flt.addWidget(self.search)
        flt.addWidget(self.cat)
        flt.addWidget(self.status)
        flt.addStretch()
        v.addLayout(flt)

        self.table = make_table(["Kode", "Nama Barang", "Kategori", "Sisa Stok", "Status", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 230 if with_stock_buttons else 140)
        v.addWidget(self.table)

        self.search.textChanged.connect(self.reload)
        self.cat.currentIndexChanged.connect(self.reload)
        self.status.currentIndexChanged.connect(self.reload)
        self._fill_categories()

    def _fill_categories(self):
        cur = self.cat.currentData()
        self.cat.blockSignals(True)
        self.cat.clear()
        self.cat.addItem("Semua Kategori", None)
        for k in self.db.kategori_list():
            self.cat.addItem(k["nama"], k["id"])
        idx = self.cat.findData(cur)
        self.cat.setCurrentIndex(max(idx, 0))
        self.cat.blockSignals(False)

    def refresh(self):
        self._fill_categories()
        self.reload()

    def reload(self):
        rows = self.db.barang_list(self.search.text().strip(), self.cat.currentData(),
                                   self.status.currentText())
        t = self.table
        clear_table(t)
        t.setRowCount(len(rows))
        for r, b in enumerate(rows):
            for c, val in enumerate((b["kode"], b["nama"], b["kategori"] or "-", b["stok"])):
                t.setItem(r, c, cell(val))
            t.setCellWidget(r, 4, center(pill(b["status"])))
            t.setCellWidget(r, 5, center(self._actions(b["id"])))
            t.setRowHeight(r, 48)
            color_row(t, r, b["status"])
        self._update_alert()

    def _update_alert(self):
        """Banner peringatan berisi barang yang stoknya kritis / habis."""
        semua = self.db.barang_list()
        habis = [b["nama"] for b in semua if b["status"] == "Habis"]
        kritis = [b["nama"] for b in semua if b["status"] == "Kritis"]
        if not habis and not kritis:
            self.alert.hide()
            return
        parts = []
        if habis:
            parts.append(f"⛔ HABIS ({len(habis)}): " + ", ".join(habis[:5]) + ("…" if len(habis) > 5 else ""))
        if kritis:
            parts.append(f"⚠ KRITIS ({len(kritis)}): " + ", ".join(kritis[:5]) + ("…" if len(kritis) > 5 else ""))
        self.alert.setText("   |   ".join(parts) + "  — segera restock!")
        color = ("#FEE2E2", "#B91C1C") if habis else ("#FEF3C7", "#92400E")
        self.alert.setStyleSheet(f"background:{color[0]};color:{color[1]};border-radius:12px;"
                                 "padding:8px 14px;font-weight:700;")
        self.alert.show()

    def _actions(self, bid):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        if self.with_stock:
            plus = small_button("＋", "#D1FAE5", "#059669", 30)
            plus.setToolTip("Tambah stok (barang masuk)")
            plus.clicked.connect(lambda _, i=bid: self.ubah_stok(i, "masuk"))
            minus = small_button("－", "#FEF3C7", "#B45309", 30)
            minus.setToolTip("Kurangi stok (barang keluar / terjual)")
            minus.clicked.connect(lambda _, i=bid: self.ubah_stok(i, "keluar"))
            lay.addWidget(plus)
            lay.addWidget(minus)
        edit = small_button("Edit", "#DBEAFE", "#1D4ED8")
        edit.clicked.connect(lambda _, i=bid: self.edit(i))
        hapus = small_button("Hapus", "#FEE2E2", "#DC2626")
        hapus.clicked.connect(lambda _, i=bid: self.hapus(i))
        lay.addWidget(edit)
        lay.addWidget(hapus)
        return w

    # ---- aksi
    def add(self):
        if BarangDialog(self.db, None, self.window()).exec_() == QDialog.Accepted:
            self.on_change()

    def edit(self, bid):
        if BarangDialog(self.db, self.db.barang_get(bid), self.window()).exec_() == QDialog.Accepted:
            self.on_change()

    def ubah_stok(self, bid, jenis):
        if StockDialog(self.db, self.db.barang_get(bid), jenis, self.window()).exec_() == QDialog.Accepted:
            self.on_change()

    def hapus(self, bid):
        b = self.db.barang_get(bid)
        if two_step_confirm(self.window(), self.db, "Hapus Barang?",
                            f"Barang '{b['nama']}' ({b['kode']}) akan dihapus permanen."):
            self.db.barang_delete(bid)
            self.on_change()


# ====================================================================== DASHBOARD & DATA BARANG
class _PageBase(QScrollArea):
    """Halaman dasar. Isi otomatis bisa digulir bila jendela/layar terlalu kecil,
    sehingga elemen tidak pernah terhimpit atau saling bertabrakan."""
    def __init__(self, title, subtitle):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        self.viewport().setAutoFillBackground(False)
        body = QWidget()
        body.setAutoFillBackground(False)
        self.setWidget(body)
        self.lay = QVBoxLayout(body)
        self.lay.setContentsMargins(14, 14, 14, 14)
        self.lay.setSpacing(14)
        self.header = Header(title, subtitle)
        self.lay.addWidget(self.header)


class DashboardPage(_PageBase):
    def __init__(self, db, on_change):
        super().__init__("Dashboard", "Ringkasan informasi stok barang")
        self.stats = StatsRow(db)
        self.panel = BarangPanel(db, on_change, with_stock_buttons=False)
        self.lay.addWidget(self.stats)
        self.lay.addWidget(self.panel, 1)

    def refresh(self):
        self.stats.refresh()
        self.panel.refresh()


class DataBarangPage(_PageBase):
    def __init__(self, db, on_change):
        super().__init__("Data Barang", "Kelola stok masuk, stok keluar, dan data barang")
        self.stats = StatsRow(db)
        self.panel = BarangPanel(db, on_change, with_stock_buttons=True)
        self.lay.addWidget(self.stats)
        self.lay.addWidget(self.panel, 1)

    def refresh(self):
        self.stats.refresh()
        self.panel.refresh()


# ====================================================================== KATEGORI
class KategoriPage(_PageBase):
    def __init__(self, db, on_change):
        super().__init__("Kategori", "Kelola kategori barang")
        self.db, self.on_change = db, on_change
        self.stats = StatsRow(db)
        self.lay.addWidget(self.stats)
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumHeight(330)
        v = QVBoxLayout(panel)
        v.setContentsMargins(26, 16, 26, 18)
        v.setSpacing(10)
        title = QLabel("Kategori")
        title.setObjectName("panelTitle")
        v.addWidget(title)
        row = QHBoxLayout()
        add = button("＋  Tambah Kategori", "tealBtn")
        add.clicked.connect(self.add)
        row.addWidget(add)
        row.addStretch()
        v.addLayout(row)
        self.table = make_table(["Nama Kategori", "Jumlah Barang", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 140)
        v.addWidget(self.table)
        self.lay.addWidget(panel, 1)

    def refresh(self):
        self.stats.refresh()
        rows = self.db.kategori_list()
        clear_table(self.table)
        self.table.setRowCount(len(rows))
        for r, k in enumerate(rows):
            it = cell(k["nama"])
            it.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(r, 0, it)
            self.table.setItem(r, 1, cell(k["jumlah"]))
            b = small_button("Hapus", "#FEE2E2", "#DC2626")
            b.clicked.connect(lambda _, kk=k: self.hapus(kk))
            self.table.setCellWidget(r, 2, center(b))
            self.table.setRowHeight(r, 46)

    def add(self, *_):
        dlg = KategoriDialog(self.db, self.window())
        if dlg.exec_() == QDialog.Accepted:
            self.on_change()

    def hapus(self, k):
        if k["jumlah"] > 0:
            QMessageBox.warning(self, "STOKITA",
                                f"Kategori '{k['nama']}' masih dipakai {k['jumlah']} barang.\n"
                                "Pindahkan atau hapus barangnya terlebih dahulu.")
            return
        if two_step_confirm(self.window(), self.db, "Hapus Kategori?",
                            f"Kategori '{k['nama']}' akan dihapus permanen."):
            self.db.kategori_delete(k["id"])
            self.on_change()


# ====================================================================== LAPORAN
class OpnameDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Mulai Stock Opname")
        self.setModal(True)
        self.setMinimumWidth(520)
        v = QVBoxLayout(self)
        v.setContentsMargins(26, 18, 26, 18)
        v.setSpacing(10)
        t = QLabel("Mulai Stock Opname")
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size:20px;font-weight:800;")
        v.addWidget(t)
        self.kode = QComboBox()
        self.kode.setEditable(True)
        self.kode.addItems([b["kode"] for b in db.barang_list()])
        self.nama = QLineEdit()
        self.nama.setReadOnly(True)
        self.sistem = QLineEdit()
        self.sistem.setReadOnly(True)
        self.fisik = int_input("0")
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(3)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid_field(grid, 0, 0, "Kode Barang", self.kode)
        grid_field(grid, 0, 1, "Nama Barang", self.nama)
        grid_field(grid, 1, 0, "Stok Sistem", self.sistem)
        grid_field(grid, 1, 1, "Stok Fisik", self.fisik)
        for r in (1, 3):
            grid.setRowMinimumHeight(r, 40)
        v.addLayout(grid)
        note = QLabel("Jika ada selisih, stok sistem akan disesuaikan dengan stok fisik.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#6B7280;font-size:11px;")
        v.addWidget(note)
        row = QHBoxLayout()
        cancel = button("Batal", "grayBtn")
        ok = button("Simpan", "greenBtn")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.save)
        row.addWidget(cancel)
        row.addStretch()
        row.addWidget(ok)
        v.addLayout(row)
        self.kode.currentTextChanged.connect(self.lookup)
        self.lookup(self.kode.currentText())
        fit_dialog(self)

    def lookup(self, kode):
        b = self.db.barang_by_kode(kode.strip())
        self.nama.setText(b["nama"] if b else "")
        self.sistem.setText(str(b["stok"]) if b else "")

    def save(self):
        kode = self.kode.currentText().strip()
        if not self.db.barang_by_kode(kode):
            QMessageBox.warning(self, "STOKITA", "Kode barang tidak ditemukan.")
            return
        if not self.fisik.text():
            QMessageBox.warning(self, "STOKITA", "Isi stok fisik terlebih dahulu.")
            return
        selisih = self.db.opname_add(kode, to_int(self.fisik))
        msg = "Stok sesuai." if selisih == 0 else f"Terdapat selisih {selisih:+d}. Stok sistem telah disesuaikan."
        QMessageBox.information(self, "STOKITA", f"Stok opname disimpan. {msg}")
        self.accept()


class PDFExportWorker(QThread):
    """Background Worker untuk memproses ekspor PDF menggunakan QThread (Multi-Threading)."""
    finished = pyqtSignal(bool, str)

    def __init__(self, html_content, file_path):
        super().__init__()
        self.html_content = html_content
        self.file_path = file_path

    def run(self):
        try:
            import os
            from PyQt5.QtGui import QTextDocument
            from PyQt5.QtPrintSupport import QPrinter

            doc = QTextDocument()
            doc.setHtml(self.html_content)

            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(self.file_path)
            printer.setPageSize(QPrinter.A4)
            printer.setOrientation(QPrinter.Landscape)
            printer.setPageMargins(12, 12, 12, 12, QPrinter.Millimeter)

            doc.print_(printer)

            if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
                raise IOError("File PDF tidak berhasil dibuat. Coba pilih folder lain (mis. Documents).")
            
            self.finished.emit(True, self.file_path)
        except PermissionError:
            self.finished.emit(False, "File tidak bisa ditulis.\nTutup dulu file PDF tersebut jika sedang terbuka, atau pilih lokasi lain (mis. folder Documents).")
        except Exception as e:
            self.finished.emit(False, str(e))


class LaporanPage(_PageBase):
    MODES = ("Laporan Stok", "Barang Masuk / Keluar", "Stok Opname")

    def __init__(self, db, on_change):
        super().__init__("Laporan", "Laporan stok, barang masuk/keluar, dan stok opname")
        self.db, self.on_change = db, on_change
        self.mode = 0
        self.headers, self.rows = [], []

        cards = QHBoxLayout()
        cards.setSpacing(22)
        self.c_total = StatCard("📦", "Total Barang", "#DBE8FF")
        self.c_sesuai = StatCard("✔", "Sesuai", "#DCFCE7", "#059669")
        self.c_selisih = StatCard("⚠", "Selisih", "#FEE2E2", "#DC2626")
        for c in (self.c_total, self.c_sesuai, self.c_selisih):
            cards.addWidget(c, 1)
        opname = button("📋  Mulai Opname", "opnameBtn")
        opname.clicked.connect(self.mulai_opname)
        cards.addWidget(opname, 1, alignment=Qt.AlignTop | Qt.AlignRight)
        self.lay.addLayout(cards)

        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumHeight(330)
        v = QVBoxLayout(panel)
        v.setContentsMargins(26, 16, 26, 18)
        v.setSpacing(10)
        tabs = QHBoxLayout()
        tabs.addStretch()
        self.group = QButtonGroup(self)
        for i, name in enumerate(self.MODES):
            b = button(name, "tabBtn")
            b.setCheckable(True)
            b.setChecked(i == 0)
            self.group.addButton(b, i)
            tabs.addWidget(b)
        tabs.addStretch()
        self.group.buttonClicked[int].connect(self.set_mode)
        v.addLayout(tabs)
        exp = QHBoxLayout()
        csv_b = button("Export CSV", "csvBtn")
        pdf_b = button("Export PDF", "pdfBtn")
        csv_b.clicked.connect(self.export_csv)
        pdf_b.clicked.connect(self.export_pdf)
        exp.addWidget(csv_b)
        exp.addWidget(pdf_b)
        exp.addStretch()
        v.addLayout(exp)
        self.table = make_table(["-"])
        v.addWidget(self.table)
        self.lay.addWidget(panel, 1)

    def set_mode(self, i):
        self.mode = i
        self.refresh()

    def mulai_opname(self):
        if not self.db.barang_list():
            QMessageBox.information(self, "STOKITA", "Belum ada barang untuk di-opname.")
            return
        if OpnameDialog(self.db, self.window()).exec_() == QDialog.Accepted:
            self.on_change()

    def refresh(self):
        db = self.db
        self.c_total.set_value(db.stats()["total_jenis"])
        o = db.opname_stats()
        self.c_sesuai.set_value(o["sesuai"])
        self.c_selisih.set_value(o["selisih"])

        jenis_label = {"masuk": "Masuk", "keluar": "Keluar", "opname": "Opname", "koreksi": "Koreksi"}
        if self.mode == 0:
            self.headers = ["Kode", "Nama Barang", "Kategori", "Stok", "Stok Min", "Status"]
            self.rows = [[b["kode"], b["nama"], b["kategori"] or "-", b["stok"], b["stok_min"], b["status"]]
                         for b in db.barang_list()]
        elif self.mode == 1:
            self.headers = ["Tanggal", "Kode", "Nama Barang", "Jenis", "Jumlah", "Stok Akhir", "Keterangan"]
            self.rows = [[r["tanggal"], r["kode"], r["nama"], jenis_label.get(r["jenis"], r["jenis"]),
                          r["jumlah"], r["stok_akhir"], r["keterangan"] or ""] for r in db.riwayat_list()]
        else:
            self.headers = ["Tanggal", "Kode", "Nama Barang", "Stok Sistem", "Stok Fisik", "Selisih", "Status"]
            self.rows = [[r["tanggal"], r["kode"], r["nama"], r["stok_sistem"], r["stok_fisik"],
                          f"{r['selisih']:+d}" if r["selisih"] else 0,
                          "Sesuai" if r["selisih"] == 0 else "Selisih"] for r in db.opname_list()]

        t = self.table
        clear_table(t)
        t.clear()
        t.setColumnCount(len(self.headers))
        t.setHorizontalHeaderLabels(self.headers)
        t.setRowCount(len(self.rows))
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for r, row in enumerate(self.rows):
            for c, val in enumerate(row):
                if self.headers[c] in ("Status", "Jenis"):
                    colors = {"Masuk": ("#DCFCE7", "#15803D"), "Keluar": ("#FEF3C7", "#B45309"),
                              "Opname": ("#DBEAFE", "#1D4ED8"), "Koreksi": ("#F3E8FF", "#7E22CE")}
                    bg, fg = colors.get(val, (None, None))
                    t.setCellWidget(r, c, center(pill(str(val), bg, fg)))
                else:
                    t.setItem(r, c, cell(val))
            t.setRowHeight(r, 46)

    # ---- export
    def _default_name(self, ext):
        slug = ["laporan_stok", "barang_masuk_keluar", "stok_opname"][self.mode]
        return f"stokita_{slug}_{datetime.now():%Y%m%d}.{ext}"

    def export_csv(self):
        if not self.rows:
            QMessageBox.information(self, "STOKITA", "Tidak ada data untuk diekspor.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", self._default_name("csv"), "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(self.headers)
            w.writerows(self.rows)
        QMessageBox.information(self, "STOKITA", f"Berhasil diekspor ke:\n{path}")

    def export_pdf(self, *_):
        """Export PDF menggunakan Multi-Threading (QThread) agar UI tidak freeze."""
        if not self.rows:
            QMessageBox.information(self, "STOKITA", "Tidak ada data untuk diekspor.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", self._default_name("pdf"), "PDF (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        try:
            from html import escape
            from PyQt5.QtCore import QUrl

            toko = escape(str(self.db.get_setting("nama_toko", "STOKITA")))
            head = "".join(f"<th bgcolor='#1565D8' style='color:white;'>{escape(str(h))}</th>"
                           for h in self.headers)
            body = ""
            for i, r in enumerate(self.rows):
                if "Habis" in r:
                    bg = "#FEE2E2"
                elif "Kritis" in r:
                    bg = "#FEF3C7"
                else:
                    bg = "#FFFFFF" if i % 2 == 0 else "#F3F4F6"
                body += f"<tr bgcolor='{bg}'>" + "".join(
                    f"<td align='center'>{escape(str(x))}</td>" for x in r) + "</tr>"
            logo = asset("logo.png")
            logo_html = (f"<img src='{QUrl.fromLocalFile(logo).toString()}' width='90'><br>"
                         if logo else "")
            html = (f"<html><body style='font-family:Arial;font-size:9pt;'>{logo_html}"
                    f"<h2 align='center'>{toko} - {escape(self.MODES[self.mode])}</h2>"
                    f"<p align='center'>Dicetak: {datetime.now():%d-%m-%Y %H:%M}</p>"
                    f"<table border='1' cellspacing='0' cellpadding='5' width='100%'>"
                    f"<tr>{head}</tr>{body}</table></body></html>")

            # Jalankan pencetakan PDF di Background Worker (QThread)
            self.pdf_worker = PDFExportWorker(html, path)
            self.pdf_worker.finished.connect(self._on_pdf_finished)
            self.pdf_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "STOKITA", f"Gagal menyiapkan dokumen PDF:\n{e}")

    def _on_pdf_finished(self, success, result):
        """Callback saat Worker Thread selesai memproses PDF."""
        if success:
            QMessageBox.information(self, "STOKITA", f"Berhasil diekspor ke:\n{result}")
        else:
            QMessageBox.critical(self, "STOKITA", f"{result}")


# ====================================================================== PENGATURAN
class MemoryDialog(QDialog):
    """Diagnostik memori berbasis tracemalloc."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diagnostik Memori (tracemalloc)")
        self.setModal(True)
        self.resize(720, 480)
        v = QVBoxLayout(self)
        v.setContentsMargins(22, 18, 22, 18)
        v.setSpacing(8)
        self.info = QLabel("")
        self.info.setWordWrap(True)
        self.info.setStyleSheet("font-weight:700;")
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet("font-family:Consolas,'DejaVu Sans Mono',monospace;font-size:12px;")
        v.addWidget(self.info)
        v.addWidget(self.text, 1)
        row = QHBoxLayout()
        self.toggle_btn = button("", "blueBtn")
        refresh = button("Segarkan", "grayBtn")
        close = button("Tutup", "grayBtn")
        self.toggle_btn.clicked.connect(self.toggle)
        refresh.clicked.connect(self.refresh)
        close.clicked.connect(self.accept)
        row.addWidget(self.toggle_btn)
        row.addWidget(refresh)
        row.addStretch()
        row.addWidget(close)
        v.addLayout(row)
        self.refresh()

    def refresh(self, *_):
        if memtrace.enabled():
            cur, peak = memtrace.usage()
            self.info.setText(f"Pelacakan AKTIF - saat ini {memtrace.fmt_bytes(cur)}, "
                              f"puncak {memtrace.fmt_bytes(peak)}")
            self.toggle_btn.setText("Hentikan Pelacakan")
            self.text.setPlainText(memtrace.report())
        else:
            self.info.setText("Pelacakan NONAKTIF")
            self.toggle_btn.setText("Mulai Pelacakan")
            self.text.setPlainText(
                "Tekan 'Mulai Pelacakan', gunakan aplikasi seperti biasa, lalu buka kembali\n"
                "dialog ini / tekan 'Segarkan' untuk melihat alokasi memori terbesar dan\n"
                "pertumbuhannya.\n\n"
                "Agar dipantau sejak aplikasi dibuka, jalankan:\n"
                "    python main.py --trace-memory\n"
                "Laporan juga disimpan ke memory_report.log saat aplikasi ditutup.")

    def toggle(self, *_):
        if memtrace.enabled():
            memtrace.stop()
        else:
            memtrace.start()
        self.refresh()


class PengaturanPage(_PageBase):
    def __init__(self, db, on_change):
        super().__init__("Pengaturan", "Atur preferensi aplikasi")
        self.db, self.on_change = db, on_change
        self.stats = StatsRow(db)
        self.lay.addWidget(self.stats)
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumHeight(430)
        v = QVBoxLayout(panel)
        v.setContentsMargins(26, 18, 26, 18)
        v.setSpacing(10)
        self.toko = QLineEdit()
        self.admin = QLineEdit()
        self.minimum = int_input("5")
        v.addLayout(field("Nama Toko", self.toko))
        v.addLayout(field("Nama Admin", self.admin))
        v.addLayout(field("Stok Minimum Default", self.minimum))
        save = button("Simpan Pengaturan", "blueBtn")
        save.clicked.connect(self.save)
        v.addWidget(save, alignment=Qt.AlignLeft)
        mem = button("🧠  Diagnostik Memori", "grayBtn")
        mem.setToolTip("Lihat penggunaan memori aplikasi (tracemalloc)")
        mem.clicked.connect(lambda *_: MemoryDialog(self.window()).exec_())
        v.addWidget(mem, alignment=Qt.AlignLeft)
        v.addStretch()

        danger = QFrame()
        danger.setObjectName("dangerBox")
        d = QVBoxLayout(danger)
        d.setContentsMargins(18, 14, 18, 14)
        dt = QLabel("Zona Berbahaya")
        dt.setObjectName("dangerTitle")
        row = QHBoxLayout()
        txt = QLabel("Menghapus seluruh data barang dan riwayat stok. Tindakan ini tidak dapat dibatalkan")
        txt.setWordWrap(True)
        reset = button("Reset Semua Data", "redBtn")
        reset.clicked.connect(self.reset)
        row.addWidget(txt, 1)
        row.addWidget(reset)
        d.addWidget(dt)
        d.addLayout(row)
        v.addWidget(danger)
        self.lay.addWidget(panel, 1)

    def refresh(self):
        self.stats.refresh()
        self.toko.setText(self.db.get_setting("nama_toko"))
        self.admin.setText(self.db.get_setting("nama_admin"))
        self.minimum.setText(self.db.get_setting("stok_min_default", "5"))

    def save(self):
        if not self.toko.text().strip() or not self.admin.text().strip():
            QMessageBox.warning(self, "STOKITA", "Nama Toko dan Nama Admin wajib diisi.")
            return
        self.db.set_setting("nama_toko", self.toko.text().strip())
        self.db.set_setting("nama_admin", self.admin.text().strip())
        self.db.set_setting("stok_min_default", to_int(self.minimum))
        QMessageBox.information(self, "STOKITA", "Pengaturan berhasil disimpan.")
        self.on_change()

    def reset(self):
        if two_step_confirm(self.window(), self.db, "Reset Semua Data?",
                            "Seluruh data barang, riwayat stok, dan hasil opname akan dihapus permanen.",
                            "Reset"):
            self.db.reset_data()
            self.on_change()
            QMessageBox.information(self, "STOKITA", "Semua data barang dan riwayat stok telah dihapus.")