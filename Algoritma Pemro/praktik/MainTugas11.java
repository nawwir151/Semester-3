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

public class MainTugas11 {

    // Sub-prosedur Merge Multi-Kriteria
    public static void mergeMahasiswa(Mahasiswa[] mhs, int l, int m, int r) {
        int n1 = m - l + 1;
        int n2 = r - m;

        Mahasiswa[] L = new Mahasiswa[n1];
        Mahasiswa[] R = new Mahasiswa[n2];

        for (int i = 0; i < n1; i++) L[i] = mhs[l + i];
        for (int j = 0; j < n2; j++) R[j] = mhs[m + 1 + j];

        int i = 0, j = 0, k = l;
        while (i < n1 && j < n2) {
            // Logika Multi-Kriteria:
            // 1. Utamakan IPK Descending (L[i].ipk > R[j].ipk)
            // 2. Jika IPK Sama, urutkan NIM Ascending (L[i].nim <= R[j].nim)
            if (L[i].ipk > R[j].ipk || (L[i].ipk == R[j].ipk && L[i].nim <= R[j].nim)) {
                mhs[k] = L[i];
                i++;
            } else {
                mhs[k] = R[j];
                j++;
            }
            k++;
        }

        while (i < n1) { mhs[k++] = L[i++]; }
        while (j < n2) { mhs[k++] = R[j++]; }
    }

    // Prosedur Utama Rekursif Merge Sort
    public static void mergeSortMahasiswa(Mahasiswa[] mhs, int l, int r) {
        if (l < r) {
            int m = l + (r - l) / 2;
            mergeSortMahasiswa(mhs, l, m);
            mergeSortMahasiswa(mhs, m + 1, r);
            mergeMahasiswa(mhs, l, m, r);
        }
    }

    // Fungsi Pembantu Cetak Tabel Data
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
        // Data Uji Coba Sesuai Jobsheet
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

        // Eksekusi Pengurutan
        mergeSortMahasiswa(daftarMhs, 0, daftarMhs.length - 1);

        System.out.println("\n[DATA MAHASISWA SETELAH DIURUTKAN]");
        System.out.println("(Kriteria: IPK Descending & NIM Ascending jika IPK Sama)");
        cetakTabel(daftarMhs);
    }
}