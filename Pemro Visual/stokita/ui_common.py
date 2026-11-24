"""Komponen UI bersama: style, kartu, header, dialog verifikasi 2 langkah."""
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

STYLE = """
QWidget { font-family: 'Segoe UI', 'Open Sans', 'DejaVu Sans', sans-serif; font-size: 13px; color: #111827; }
QLabel { background: transparent; }
QMainWindow, #root { background: #EEF1F6; }
#content, #loginRoot { background: white; }
#loginBand { background: #DBE8FF; }

#sidebar { background: #1565D8; border-radius: 28px; }
#logoCircle { background: white; border-radius: 75px; }
#navBtn { background: #2F78E6; color: white; border: none; border-radius: 14px;
          padding: 6px 14px; text-align: left; font-weight: 700; font-size: 13px; }
#navBtn:hover { background: #4A8CF0; }
#navBtn:checked { background: #0B3D91; }

#header { background: #1565D8; border-radius: 28px; }
#headerTitle { color: white; font-size: 26px; font-weight: 800; background: transparent; }
#headerSub { color: #DBE8FF; font-weight: 700; background: transparent; }

#statCard { background: white; border: 4px solid #E5E7EB; border-radius: 28px; }
#cardTitle { color: #6B7280; font-weight: 700; font-size: 12px; }
#cardValue { font-size: 24px; font-weight: 800; }
#panel { background: white; border: 4px solid #E5E7EB; border-radius: 30px; }
#panelTitle { font-size: 26px; font-weight: 800; }
#dangerBox { background: #F3F4F6; border-radius: 14px; }
#dangerTitle { color: #DC2626; font-size: 18px; font-weight: 800; }
#loginTitle { color: #0B4DA2; font-size: 30px; font-weight: 800; }
#errorLabel { color: #DC2626; font-size: 11px; }

QLineEdit, QComboBox, QTextEdit { background: #E5E7EB; border: 2px solid transparent;
    border-radius: 12px; padding: 5px 12px; min-height: 24px; selection-background-color: #1565D8; }
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border: 2px solid #1565D8; background: #F3F4F6; }
QLineEdit[error="true"] { background: #FEE2E2; border: 2px solid #FCA5A5; }
QLineEdit:read-only { background: #DBE8FF; }
#searchBox, #filterBox { background: #F3F4F6; border-radius: 16px; padding: 6px 14px; }
QComboBox::drop-down { border: none; width: 28px; subcontrol-origin: padding; subcontrol-position: center right; }
QComboBox::down-arrow { image: none; width: 0; height: 0; margin-right: 10px;
    border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #4B5563; }
QComboBox QAbstractItemView { background: white; selection-background-color: #DBE8FF;
    selection-color: #111827; border: 1px solid #E5E7EB; }

QPushButton { border: none; border-radius: 16px; padding: 8px 18px; font-weight: 700; }
#bigBtn { background: #2F72E4; color: white; border-radius: 18px; font-size: 15px; min-height: 30px; }
#bigBtn:hover { background: #1F62D4; }
#tealBtn { background: #0F766E; color: white; }
#tealBtn:hover { background: #0B5F58; }
#blueBtn { background: #1565D8; color: white; }
#grayBtn { background: #E5E7EB; color: #111827; }
#grayBtn:hover { background: #D1D5DB; }
#greenBtn { background: #16A34A; color: white; }
#greenBtn:hover { background: #15803D; }
#redBtn { background: #DC2626; color: white; }
#redBtn:hover { background: #B91C1C; }
#csvBtn { background: #166534; color: white; }
#pdfBtn { background: #B45309; color: white; }
#opnameBtn { background: #14532D; color: white; }
#tabBtn { background: #E5E7EB; color: #374151; padding: 6px 20px; border-radius: 14px; }
#tabBtn:checked { background: #0F766E; color: white; }

QTableWidget { background: transparent; border: none; gridline-color: transparent; outline: 0; }
QTableWidget::item { border-bottom: 1px solid #F3F4F6; }
QTableWidget::item:selected { background: #E8F0FE; color: #111827; }
QHeaderView::section { background: #F3F4F6; border: none; padding: 10px; font-weight: 600; }
QScrollBar:vertical { background: transparent; width: 10px; }
QScrollBar::handle:vertical { background: #D1D5DB; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QDialog { background: white; }
"""

STATUS_COLORS = {
    "Aman": ("#DCFCE7", "#15803D"), "Sesuai": ("#DCFCE7", "#15803D"),
    "Kritis": ("#FEF3C7", "#B45309"), "Habis": ("#FEE2E2", "#B91C1C"),
    "Selisih": ("#FEE2E2", "#B91C1C"),
}


def asset(name):
    p = os.path.join(ASSETS, name)
    return p if os.path.exists(p) else None


def repolish(w):
    w.style().unpolish(w)
    w.style().polish(w)


def fit_dialog(dlg):
    """Pastikan dialog muat di layar: ukuran mengikuti isi, dibatasi 92% tinggi layar."""
    from PyQt5.QtWidgets import QApplication
    dlg.adjustSize()
    screen = QApplication.primaryScreen()
    if screen is None:
        return
    avail = screen.availableGeometry()
    w = min(max(dlg.width(), dlg.sizeHint().width()), int(avail.width() * 0.92))
    h = min(max(dlg.height(), dlg.sizeHint().height()), int(avail.height() * 0.92))
    dlg.resize(w, h)


def pill(text, bg=None, fg=None):
    bg0, fg0 = STATUS_COLORS.get(text, ("#E5E7EB", "#374151"))
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setFixedSize(70, 24)
    lbl.setStyleSheet(f"background:{bg or bg0};color:{fg or fg0};border-radius:11px;"
                      "font-weight:600;font-size:11px;")
    return lbl


def small_button(text, bg, fg, width=None):
    b = QPushButton(text)
    b.setCursor(Qt.PointingHandCursor)
    b.setFixedHeight(24)
    if width:
        b.setFixedWidth(width)
    b.setStyleSheet(f"QPushButton{{background:{bg};color:{fg};border-radius:12px;padding:0 12px;"
                    f"font-size:11px;font-weight:600;}}QPushButton:hover{{background:{fg};color:white;}}")
    return b


def center(widget):
    box = QWidget()
    lay = QHBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setAlignment(Qt.AlignCenter)
    lay.addWidget(widget)
    return box


def button(text, name, cursor=True):
    b = QPushButton(text)
    b.setObjectName(name)
    if cursor:
        b.setCursor(Qt.PointingHandCursor)
    return b


# ------------------------------------------------------------------ logo
def logo_label(font_px=22, tagline=False, circle=False, width=None):
    """Logo STOKITA. Memakai assets/logo.png jika ada, jika tidak digambar sebagai teks."""
    lbl = QLabel()
    lbl.setAlignment(Qt.AlignCenter)
    p = asset("logo.png")
    if p:
        pm = QPixmap(p)
        w = width or (140 if circle else 300)
        lbl.setPixmap(pm.scaledToWidth(w, Qt.SmoothTransformation))
        return lbl
    html = (f"<span style='font-size:{font_px}px;font-weight:900;color:#0B2A5B;'>STOK</span>"
            f"<span style='font-size:{font_px}px;font-weight:900;color:#F59E0B;'>ITA</span>")
    if tagline:
        html += ("<br><span style='font-size:10px;font-weight:700;color:#0B2A5B;'>"
                 "MANAJEMEN STOK BARANG &amp; INVENTARIS</span>")
    lbl.setText(html)
    return lbl


def app_icon():
    from PyQt5.QtGui import QIcon
    p = asset("logo.png")
    return QIcon(p) if p else QIcon()


# ------------------------------------------------------------------ ikon menu (putih, tanpa warna)
def menu_icon(name, color="#FFFFFF", size=22):
    """Gambar ikon garis satu warna (putih) untuk tombol menu; tidak bergantung pada emoji."""
    from PyQt5.QtCore import QPointF, QRectF
    from PyQt5.QtGui import QColor, QIcon, QPainter, QPen, QPolygonF
    scale = 3
    pm = QPixmap(size * scale, size * scale)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(scale, scale)
    c = QColor(color)
    pen = QPen(c, 1.9, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    P = QPointF
    if name == "home":
        p.drawPolyline(QPolygonF([P(3, 11), P(11, 4), P(19, 11)]))
        p.drawPolyline(QPolygonF([P(5.5, 9.5), P(5.5, 18.5), P(16.5, 18.5), P(16.5, 9.5)]))
        p.drawPolyline(QPolygonF([P(9, 18.5), P(9, 13), P(13, 13), P(13, 18.5)]))
    elif name == "box":
        p.drawPolygon(QPolygonF([P(11, 3), P(18.5, 7), P(18.5, 15), P(11, 19), P(3.5, 15), P(3.5, 7)]))
        p.drawPolyline(QPolygonF([P(3.5, 7), P(11, 11), P(18.5, 7)]))
        p.drawLine(P(11, 11), P(11, 19))
    elif name == "tag":
        p.drawPolygon(QPolygonF([P(3.5, 4), P(11.5, 4), P(19, 11.5), P(11.5, 19), P(3.5, 11)]))
        p.setBrush(c)
        p.drawEllipse(P(8, 8.5), 1.4, 1.4)
    elif name == "chart":
        p.setBrush(c)
        p.drawRoundedRect(QRectF(4, 11, 3.4, 7), 0.8, 0.8)
        p.drawRoundedRect(QRectF(9.3, 6.5, 3.4, 11.5), 0.8, 0.8)
        p.drawRoundedRect(QRectF(14.6, 3.5, 3.4, 14.5), 0.8, 0.8)
    elif name == "gear":
        import math
        p.drawEllipse(P(11, 11), 5.6, 5.6)
        p.drawEllipse(P(11, 11), 2.1, 2.1)
        for i in range(8):
            a = math.radians(i * 45)
            p.drawLine(P(11 + 7.2 * math.cos(a), 11 + 7.2 * math.sin(a)),
                       P(11 + 9.4 * math.cos(a), 11 + 9.4 * math.sin(a)))
    elif name == "logout":
        p.drawPolyline(QPolygonF([P(9, 4), P(4, 4), P(4, 18), P(9, 18)]))
        p.drawLine(P(9, 11), P(18.5, 11))
        p.drawPolyline(QPolygonF([P(15, 7), P(18.5, 11), P(15, 15)]))
    p.end()
    pm.setDevicePixelRatio(scale)
    return QIcon(pm)


# ------------------------------------------------------------------ warna stok kritis
ROW_COLORS = {          # (latar baris, warna teks)
    "Kritis": ("#FEF3C7", "#92400E"),
    "Habis": ("#FEE2E2", "#B91C1C"),
}


def color_row(table, row, status):
    """Beri warna seluruh baris bila stok Kritis (kuning) atau Habis (merah)."""
    if status not in ROW_COLORS:
        return
    from PyQt5.QtGui import QBrush, QColor, QFont
    bg, fg = ROW_COLORS[status]
    for c in range(table.columnCount()):
        it = table.item(row, c)
        if it is not None:
            it.setBackground(QBrush(QColor(bg)))
            it.setForeground(QBrush(QColor(fg)))
            f = QFont(it.font())
            f.setBold(True)
            it.setFont(f)


# ------------------------------------------------------------------ header & kartu
class Header(QFrame):
    def __init__(self, title, subtitle):
        super().__init__()
        self.setObjectName("header")
        self.setFixedHeight(92)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 0, 20, 0)
        lay.setSpacing(2)
        lay.setAlignment(Qt.AlignVCenter)
        self.title = QLabel(title)
        self.title.setObjectName("headerTitle")
        self.sub = QLabel(subtitle)
        self.sub.setObjectName("headerSub")
        lay.addWidget(self.title)
        lay.addWidget(self.sub)


class StatCard(QFrame):
    def __init__(self, icon, title, icon_bg="#DBE8FF", value_color="#111827"):
        super().__init__()
        self.setObjectName("statCard")
        self.setFixedHeight(88)
        v = QVBoxLayout(self)
        v.setContentsMargins(14, 8, 14, 6)
        v.setSpacing(0)
        top = QHBoxLayout()
        top.setSpacing(8)
        ic = QLabel(icon)
        ic.setFixedSize(24, 24)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(f"background:{icon_bg};border-radius:12px;font-size:12px;")
        t = QLabel(title)
        t.setObjectName("cardTitle")
        top.addStretch()
        top.addWidget(ic)
        top.addWidget(t)
        top.addStretch()
        self.value = QLabel("0")
        self.value.setObjectName("cardValue")
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setStyleSheet(f"color:{value_color};")
        v.addLayout(top)
        v.addWidget(self.value)

    def set_value(self, v):
        self.value.setText(str(v))


class StatsRow(QWidget):
    """Empat kartu ringkasan: total jenis, stok kritis, total stok, total terjual."""
    def __init__(self, db):
        super().__init__()
        self.db = db
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(22)
        self.c_jenis = StatCard("📦", "Total Jenis Barang", "#DBE8FF")
        self.c_kritis = StatCard("⚠", "Stok Kritis", "#FEF3C7")
        self.c_stok = StatCard("🛒", "Total Stok", "#DCFCE7")
        self.c_jual = StatCard("🧾", "Total terjual", "#F3E8FF")
        for c in (self.c_jenis, self.c_kritis, self.c_stok, self.c_jual):
            lay.addWidget(c)

    def refresh(self):
        s = self.db.stats()
        self.c_jenis.set_value(s["total_jenis"])
        self.c_kritis.set_value(s["kritis"])
        self.c_kritis.value.setStyleSheet(
            "color:%s;" % ("#DC2626" if s["kritis"] > 0 else "#111827"))
        self.c_stok.set_value(s["total_stok"])
        self.c_jual.set_value(s["terjual"])


# ------------------------------------------------------------------ dialog verifikasi
class ConfirmDialog(QDialog):
    """Dialog konfirmasi bergaya desain (ikon X merah, tombol Batal & aksi)."""
    def __init__(self, parent, title, message, ok_text="Ya", step_text=""):
        super().__init__(parent)
        self.setWindowTitle("STOKITA")
        self.setModal(True)
        self.setFixedWidth(400)
        v = QVBoxLayout(self)
        v.setContentsMargins(30, 26, 30, 24)
        v.setSpacing(10)
        icon = QLabel("✕")
        icon.setFixedSize(56, 56)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:#FEE2E2;color:#DC2626;border-radius:28px;"
                           "font-size:24px;font-weight:800;")
        v.addWidget(icon, alignment=Qt.AlignHCenter)
        if step_text:
            st = QLabel(step_text)
            st.setAlignment(Qt.AlignCenter)
            st.setStyleSheet("color:#6B7280;font-size:11px;font-weight:700;")
            v.addWidget(st)
        t = QLabel(title)
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size:20px;font-weight:800;")
        m = QLabel(message)
        m.setAlignment(Qt.AlignCenter)
        m.setWordWrap(True)
        m.setStyleSheet("color:#4B5563;")
        v.addWidget(t)
        v.addWidget(m)
        v.addSpacing(10)
        row = QHBoxLayout()
        cancel = button("Batal", "grayBtn")
        ok = button(ok_text, "redBtn")
        cancel.setFixedHeight(40)
        ok.setFixedHeight(40)
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        row.addWidget(cancel)
        row.addWidget(ok)
        v.addLayout(row)


class PasswordDialog(QDialog):
    """Langkah 2: admin wajib memasukkan password untuk mengonfirmasi."""
    def __init__(self, parent, db, message):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("STOKITA - Verifikasi")
        self.setModal(True)
        self.setFixedWidth(400)
        v = QVBoxLayout(self)
        v.setContentsMargins(30, 26, 30, 24)
        v.setSpacing(8)
        icon = QLabel("🔒")
        icon.setFixedSize(56, 56)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:#DBE8FF;border-radius:28px;font-size:24px;")
        v.addWidget(icon, alignment=Qt.AlignHCenter)
        st = QLabel("Langkah 2 dari 2")
        st.setAlignment(Qt.AlignCenter)
        st.setStyleSheet("color:#6B7280;font-size:11px;font-weight:700;")
        t = QLabel("Verifikasi Password")
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size:20px;font-weight:800;")
        m = QLabel(message)
        m.setAlignment(Qt.AlignCenter)
        m.setWordWrap(True)
        m.setStyleSheet("color:#4B5563;")
        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.Password)
        self.pw.setPlaceholderText("Password admin")
        self.pw.returnPressed.connect(self.check)
        self.err = QLabel("")
        self.err.setObjectName("errorLabel")
        for w in (st, t, m, self.pw, self.err):
            v.addWidget(w)
        row = QHBoxLayout()
        cancel = button("Batal", "grayBtn")
        ok = button("Verifikasi", "redBtn")
        cancel.setFixedHeight(40)
        ok.setFixedHeight(40)
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.check)
        row.addWidget(cancel)
        row.addWidget(ok)
        v.addLayout(row)

    def check(self):
        if self.db.check_password(self.pw.text()):
            self.accept()
        else:
            self.err.setText("Password salah. Coba lagi.")
            self.pw.clear()


def two_step_confirm(parent, db, title, message, ok_text="Hapus"):
    """Verifikasi 2 langkah: (1) dialog konfirmasi, (2) input password admin."""
    if ConfirmDialog(parent, title, message, ok_text, "Langkah 1 dari 2").exec_() != QDialog.Accepted:
        return False
    return PasswordDialog(parent, db, "Masukkan password admin untuk melanjutkan.").exec_() == QDialog.Accepted
