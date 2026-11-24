import java.util.Scanner;

public class AnalisisNilai {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        // 1. Input Ukuran Matriks
        System.out.print("Masukkan jumlah mahasiswa (M): ");
        int m = input.nextInt();
        System.out.print("Masukkan jumlah mata kuliah (N): ");
        int n = input.nextInt();

        float[][] nilai = new float[m][n];
        float[] rataMhs = new float[m];

        // 2. Input Data dan Hitung Rata-Rata
        for (int i = 0; i < m; i++) {
            System.out.println("\n--- Data Mahasiswa ke-" + (i + 1) + " ---");
            float total = 0;
            for (int j = 0; j < n; j++) {
                System.out.print("Nilai Mata Kuliah ke-" + (j + 1) + ": ");
                nilai[i][j] = input.nextFloat();
                total += nilai[i][j];
            }
            rataMhs[i] = total / n;
        }

        // 3. Cari Mahasiswa Terbaik
        float maxRata = rataMhs[0];
        int idxTerbaik = 0;
        for (int i = 1; i < m; i++) {
            if (rataMhs[i] > maxRata) {
                maxRata = rataMhs[i];
                idxTerbaik = i;
            }
        }

        // 4. Tampilkan Hasil
        System.out.println("\n================ HASIL ANALISIS ================");
        for (int i = 0; i < m; i++) {
            System.out.printf("Rata-rata Mahasiswa ke-%d: %.2f\n", (i + 1), rataMhs[i]);
        }
        System.out.printf("\nMahasiswa Terbaik: Mahasiswa ke-%d (Rata-rata: %.2f)\n", (idxTerbaik + 1), maxRata);

        input.close();
    }
}