"""STOKITA - Manajemen Stok Barang & Inventaris (PyQt5 + SQLite)."""
import atexit
import sys

import memtrace
memtrace.setup(sys.argv)   # tracemalloc aktif bila --trace-memory / STOKITA_TRACEMALLOC=1

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QApplication, QButtonGroup, QFrame, QHBoxLayout, QMainWindow,
                             QStackedWidget, QVBoxLayout, QWidget)

from database import Database
from pages import (DashboardPage, DataBarangPage, KategoriPage, LaporanPage, LoginPage,
                   PengaturanPage)
from ui_common import STYLE, app_icon, button, logo_label, menu_icon, two_step_confirm

# Logout memakai verifikasi 2 langkah (konfirmasi + password). Ubah ke False untuk 1 langkah saja.
LOGOUT_TWO_STEP = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STOKITA - Manajemen Stok Barang & Inventaris")
        self.setWindowIcon(app_icon())
        # Ukuran jendela menyesuaikan layar (aman untuk laptop & skala Windows 125%/150%)
        screen = QApplication.primaryScreen().availableGeometry()
        self.setMinimumSize(960, 560)
        self.resize(min(1180, int(screen.width() * 0.92)),
                    min(740, int(screen.height() * 0.92)))
        self.db = Database()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login = LoginPage(self.db)
        self.login.logged_in.connect(self.enter_app)
        self.stack.addWidget(self.login)          # 0
        self.stack.addWidget(self._build_app())   # 1

    # ------------------------------------------------------------ layout utama
    def _build_app(self):
        root = QWidget()
        root.setObjectName("root")
        h = QHBoxLayout(root)
        h.setContentsMargins(14, 14, 14, 14)
        h.setSpacing(0)

        # sidebar
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(184)
        sv = QVBoxLayout(side)
        sv.setContentsMargins(14, 18, 14, 18)
        sv.setSpacing(10)
        circle = QFrame()
        circle.setObjectName("logoCircle")
        circle.setFixedSize(150, 150)
        cl = QVBoxLayout(circle)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.addWidget(logo_label(17, circle=True, width=100))
        sv.addWidget(circle, alignment=Qt.AlignHCenter)
        sv.addSpacing(10)

        self.pages = QStackedWidget()
        self.page_objs = [
            DashboardPage(self.db, self.refresh_all),
            DataBarangPage(self.db, self.refresh_all),
            KategoriPage(self.db, self.refresh_all),
            LaporanPage(self.db, self.refresh_all),
            PengaturanPage(self.db, self.refresh_all),
        ]
        for p in self.page_objs:
            self.pages.addWidget(p)

        self.nav = QButtonGroup(self)
        for i, (icon, label) in enumerate((("home", "Dashboard"), ("box", "Data Barang"),
                                           ("tag", "Kategori"), ("chart", "Laporan"),
                                           ("gear", "Pengaturan"))):
            b = button("  " + label, "navBtn")
            b.setIcon(menu_icon(icon))
            b.setIconSize(QSize(22, 22))
            b.setCheckable(True)
            b.setChecked(i == 0)
            b.setFixedHeight(38)
            self.nav.addButton(b, i)
            sv.addWidget(b)
        self.nav.buttonClicked[int].connect(self.go)
        sv.addStretch()
        logout = button("  Logout", "navBtn")
        logout.setIcon(menu_icon("logout"))
        logout.setIconSize(QSize(22, 22))
        logout.setFixedHeight(38)
        logout.clicked.connect(self.logout)
        sv.addWidget(logout)

        content = QFrame()
        content.setObjectName("content")
        cv = QVBoxLayout(content)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.addWidget(self.pages)

        h.addWidget(side)
        h.addWidget(content, 1)
        return root

    # ------------------------------------------------------------ penutupan
    def shutdown(self):
        """Bersihkan sumber daya: tulis laporan memori (jika aktif) lalu tutup koneksi database."""
        if getattr(self, "_shut", False):
            return
        self._shut = True
        try:
            memtrace.write_log()
        finally:
            self.db.close()

    def closeEvent(self, event):
        self.shutdown()
        super().closeEvent(event)

    # ------------------------------------------------------------ navigasi
    def go(self, index):
        self.pages.setCurrentIndex(index)
        self.page_objs[index].refresh()

    def refresh_all(self):
        for p in self.page_objs:
            p.refresh()

    def enter_app(self):
        self.refresh_all()
        self.nav.button(0).setChecked(True)
        self.pages.setCurrentIndex(0)
        self.stack.setCurrentIndex(1)

    def logout(self):
        if LOGOUT_TWO_STEP:
            ok = two_step_confirm(self, self.db, "Konfirmasi Logout",
                                  "Apakah Anda yakin ingin keluar dari aplikasi STOKITA?", "Logout")
        else:
            from ui_common import ConfirmDialog
            from PyQt5.QtWidgets import QDialog
            ok = ConfirmDialog(self, "Konfirmasi Logout",
                               "Apakah Anda yakin ingin keluar dari aplikasi STOKITA?",
                               "Logout").exec_() == QDialog.Accepted
        if ok:
            self.db.current_user = None
            self.login.load_remembered()
            self.stack.setCurrentIndex(0)


def _excepthook(exc_type, exc, tb):
    """Tampilkan error tak terduga di dialog (bukan menutup aplikasi diam-diam)."""
    import traceback
    from PyQt5.QtWidgets import QMessageBox
    detail = "".join(traceback.format_exception(exc_type, exc, tb))
    print(detail, file=sys.stderr)
    QMessageBox.critical(None, "STOKITA - Terjadi Kesalahan", detail[-1500:])


def main():
    sys.excepthook = _excepthook
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    try:  # skala 125%/150% dihitung halus, tidak dibulatkan ke 200%
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except AttributeError:
        pass
    app = QApplication(sys.argv)
    app.setWindowIcon(app_icon())
    app.setStyleSheet(STYLE)
    win = MainWindow()
    app.aboutToQuit.connect(win.shutdown)      # penutupan lewat jalur apa pun
    atexit.register(win.shutdown)              # jaring pengaman bila keluar tak normal
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
