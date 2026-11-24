import os
import shutil
import subprocess
import sys


def build_executable():
    print("=== MEMULAI PROSES PACKAGING APLIKASI STOKITA (.EXE) ===")

    # 1. Pastikan PyInstaller tersedia
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("[ERROR] PyInstaller belum terpasang.")
        print("Jalankan perintah: pip install pyinstaller")
        sys.exit(1)

    entry_file = "main.py"
    if not os.path.exists(entry_file):
        print(f"[ERROR] File utama '{entry_file}' tidak ditemukan di folder ini.")
        sys.exit(1)

    # 2. Susun perintah PyInstaller (mode folder agar stokita.db & backups mudah diakses)
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "STOKITA",
        entry_file,
    ]

    # Sertakan folder assets/gambar jika ada di proyek
    for asset_dir in ("assets", "images", "icons"):
        if os.path.isdir(asset_dir):
            cmd.extend(["--add-data", f"{asset_dir}{os.pathsep}{asset_dir}"])

    print("Menjalankan:", " ".join(cmd))
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("[GAGAL] Proses build executable mengalami kendala.")
        sys.exit(result.returncode)

    # 3. Siapkan struktur folder produksi di dist/STOKITA
    dist_dir = os.path.join("dist", "STOKITA")
    os.makedirs(os.path.join(dist_dir, "backups"), exist_ok=True)

    # Salin file salt jika sudah ada agar sinkron dengan database existing
    if os.path.exists("stokita.salt"):
        shutil.copy2("stokita.salt", os.path.join(dist_dir, "stokita.salt"))

    print("\n=== BUILD SELESAI ===")
    print(f"Aplikasi siap dijalankan di: {os.path.abspath(dist_dir)}\\STOKITA.exe")


if __name__ == "__main__":
    build_executable()