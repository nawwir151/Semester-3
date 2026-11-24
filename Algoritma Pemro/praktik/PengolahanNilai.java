import java.util.Scanner;

public class PengolahanNilai {

    // Fungsi menghitung rata-rata elemen array
    public static double hitungRataRata(int[] nilai) {
        int sum = 0;
        for (int n : nilai) {
            sum += n;
        }
        // TODO [1]: Kembalikan nilai rata-rata (type cast ke double)
        return (double) sum / nilai.length;
    }

    // Fungsi mencari nilai maksimum dalam array
    public static int cariMaksimum(int[] nilai) {
        int max = nilai[0];
        // TODO [2]: Buat perulangan untuk menentukan nilai maksimum
        for (int i = 1; i < nilai.length; i++) {
            if (nilai[i] > max) {
                max = nilai[i];
            }
        }
        return max;
    }

    // Fungsi menentukan predikat huruf
    public static String konversiHuruf(double nilai) {
        // TODO [3]: Tentukan predikat (A: >=85, B: >=70, C: >=55, D: >=40, E: <40)
        if (nilai >= 85) return "A";
        else if (nilai >= 70) return "B";
        else if (nilai >= 55) return "C";
        else if (nilai >= 40) return "D";
        else return "E";
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Masukkan jumlah mahasiswa: ");
        int n = scanner.nextInt();

        int[] dataNilai = new int[n];
        for (int i = 0; i < n; i++) {
            System.out.print("Masukkan nilai mahasiswa ke-" + (i + 1) + ": ");
            dataNilai[i] = scanner.nextInt();
        }

        // TODO [4]: Panggil fungsi hitungRataRata dan simpan ke variabel rataRata
        double rataRata = hitungRataRata(dataNilai);

        // TODO [5]: Panggil fungsi cariMaksimum dan simpan ke variabel maxNilai
        int maxNilai = cariMaksimum(dataNilai);

        System.out.println("\n========= REKAPITULASI NILAI =========");
        System.out.printf("Rata-rata Kelas   : %.2f\n", rataRata);
        System.out.println("Nilai Tertinggi   : " + maxNilai);
        System.out.println("Predikat Kelas    : " + konversiHuruf(rataRata));

        scanner.close();
    }
}