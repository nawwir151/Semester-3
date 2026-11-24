import java.util.Scanner;

public class Inputnilaiujian {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        double[] nilai = new double[5];
        double total = 0.0;
        double rataRata;

        System.out.println("=== PROGRAM HITUNG RATA-RATA NILAI ===");

        // 1. Perulangan untuk menginput data ke array
        for (int i = 0; i < nilai.length; i++) {
            System.out.print("Masukkan nilai mahasiswa ke-" + (i + 1) + ": ");
            nilai[i] = scanner.nextDouble();
            // Accumulate total
            total = total + nilai[i];
        }

        // 2. Hitung rata-rata
        rataRata = total / nilai.length;

        // 3. Tampilkan hasil
        System.out.println("\nTotal Nilai : " + total);
        System.out.println("Rata-rata Nilai : " + rataRata);

        scanner.close();
    }
}