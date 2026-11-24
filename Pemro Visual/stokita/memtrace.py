"""Integrasi tracemalloc untuk memantau penggunaan memori STOKITA.

Aktifkan dengan salah satu cara:
  python main.py --trace-memory
  set STOKITA_TRACEMALLOC=1        (Windows)   |   export STOKITA_TRACEMALLOC=1   (Linux/macOS)
atau tekan tombol "Diagnostik Memori" di menu Pengaturan lalu "Mulai Pelacakan".

Saat aplikasi ditutup dan pelacakan aktif, laporan ditambahkan ke file memory_report.log.
Catatan: tracemalloc menambah overhead (aplikasi sedikit lebih lambat), jadi nonaktif secara default.
"""
import os
import tracemalloc
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "memory_report.log")
NFRAMES = 10

_baseline = None


def enabled():
    return tracemalloc.is_tracing()


def setup(argv=None):
    """Mulai pelacakan bila diminta lewat argumen --trace-memory atau variabel lingkungan."""
    argv = argv if argv is not None else []
    env = os.environ.get("STOKITA_TRACEMALLOC", "").strip().lower()
    if "--trace-memory" in argv or env in ("1", "true", "yes", "on"):
        start()
        return True
    return False


def start(nframes=NFRAMES):
    """Mulai tracemalloc dan simpan snapshot awal sebagai pembanding pertumbuhan memori."""
    global _baseline
    if not tracemalloc.is_tracing():
        tracemalloc.start(nframes)
    _baseline = _take()


def stop():
    global _baseline
    if tracemalloc.is_tracing():
        tracemalloc.stop()
    _baseline = None


def _take():
    snap = tracemalloc.take_snapshot()
    return snap.filter_traces((
        tracemalloc.Filter(False, tracemalloc.__file__),
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))


def fmt_bytes(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def usage():
    """(memori saat ini, puncak) dalam byte; (0, 0) bila pelacakan nonaktif."""
    return tracemalloc.get_traced_memory() if tracemalloc.is_tracing() else (0, 0)


def report(limit=10):
    """Laporan teks: pemakaian memori, alokasi terbesar, dan pertumbuhan sejak snapshot awal."""
    if not tracemalloc.is_tracing():
        return "Pelacakan memori (tracemalloc) belum aktif."
    cur, peak = usage()
    snap = _take()
    lines = [f"Memori Python saat ini : {fmt_bytes(cur)}",
             f"Puncak penggunaan      : {fmt_bytes(peak)}",
             "", f"== {limit} alokasi terbesar (per baris kode) =="]
    for i, st in enumerate(snap.statistics("lineno")[:limit], 1):
        fr = st.traceback[0]
        lines.append(f"{i:>2}. {fmt_bytes(st.size):>9}  {st.count:>6} blok  "
                     f"{os.path.basename(fr.filename)}:{fr.lineno}")
    if _baseline is not None:
        lines += ["", f"== {limit} pertumbuhan terbesar sejak pelacakan dimulai =="]
        diffs = [d for d in snap.compare_to(_baseline, "lineno") if d.size_diff > 0][:limit]
        if not diffs:
            lines.append("(tidak ada pertumbuhan berarti)")
        for i, d in enumerate(diffs, 1):
            fr = d.traceback[0]
            lines.append(f"{i:>2}. +{fmt_bytes(d.size_diff):>9}  {d.count_diff:+d} blok  "
                         f"{os.path.basename(fr.filename)}:{fr.lineno}")
    return "\n".join(lines)


def write_log(limit=15):
    """Tambahkan laporan ke memory_report.log (hanya bila pelacakan aktif)."""
    if not tracemalloc.is_tracing():
        return None
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n===== STOKITA {datetime.now():%Y-%m-%d %H:%M:%S} =====\n")
            f.write(report(limit) + "\n")
        return LOG_PATH
    except OSError:
        return None
