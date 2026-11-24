class Mahasiswa {
    int nim;
    String nama;
    double ipk;

    public Mahasiswa(int nim, String nama, double ipk) {
        this.nim = nim;
        this.nama = nama;
        this.ipk = ipk;
    }
}

public class SistemManajemenDataMahasiswa {

    // Insertion Sort Multi-Kriteria (IPK Descending, NIM Ascending)
    public static void sortMahasiswa(Mahasiswa[] mhs) {
        int n = mhs.length;
        for (int i = 1; i < n; i++) {
            Mahasiswa key = mhs[i];
            int j = i - 1;

            /*
             * Kondisi Pengurutan:
             * 1. Utama: IPK Tertinggi ke Terendah (mhs[j].ipk < key.ipk)
             * 2. Sekunder: Jika IPK Sama, NIM Terkecil ke Terbesar (mhs[j].nim > key.nim)
             */
            while (j >= 0 && (mhs[j].ipk < key.ipk || (mhs[j].ipk == key.ipk && mhs[j].nim > key.nim))) {
                mhs[j + 1] = mhs[j];
                j = j - 1;
            }
            mhs[j + 1] = key;
        }
    }

    // Metode Pembantu untuk Mencetak Tabel Clean & Rapi
    public static void cetakTabel(Mahasiswa[] mhs) {
        System.out.println("+-----+------------+-------+");
        System.out.println("| NIM | Nama       | IPK   |");
        System.out.println("+-----+------------+-------+");
        for (Mahasiswa m : mhs) {
            System.out.printf("| %-3d | %-10s | %.2f  |\n", m.nim, m.nama, m.ipk);
        }
        System.out.println("+-----+------------+-------+");
    }

    public static void main(String[] args) {
        // Data Uji Coba (Dummy Data sesuai Soal Jobsheet)
        Mahasiswa[] daftarMhs = {
            new Mahasiswa(102, "Budi", 3.50),
            new Mahasiswa(101, "Siti", 3.85),
            new Mahasiswa(104, "Andi", 3.50),
            new Mahasiswa(103, "Dewi", 3.90),
            new Mahasiswa(105, "Eko",  3.50)
        };

        System.out.println("==================================================");
        System.out.println("  SISTEM MANAJEMEN DATA MAHASISWA (AKADEMIK CAMPUS)");
        System.out.println("==================================================");
        System.out.println("\n[DATA MAHASISWA SEBELUM DIURUTKAN]");
        cetakTabel(daftarMhs);

        // Eksekusi Pengurutan Multi-Kriteria
        sortMahasiswa(daftarMhs);

        System.out.println("\n[DATA MAHASISWA SETELAH DIURUTKAN]");
        System.out.println("(Kriteria: IPK Descending & NIM Ascending jika IPK Sama)");
        cetakTabel(daftarMhs);
    }
}