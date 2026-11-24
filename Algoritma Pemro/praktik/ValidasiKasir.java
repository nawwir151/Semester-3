import java.util.Scanner;

public class ValidasiKasir {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        double totalBelanja = 0;
        int i = 1;

        while (i <= 10) {
            System.out.print("Masukkan nilai transaksi ke-" + i + ": ");
            double inputNilai = scanner.nextDouble();

            if (inputNilai == 0) {
                break; // Early exit jika diinput 0
            }

            if (inputNilai < 0) {
                System.out.println("Transaksi tidak valid (negatif). Dilewati.");
                i++;
                continue; // Melewati penambahan total dan lanjut ke iterasi berikutnya
            }

            totalBelanja += inputNilai;
            i++;
        }

        System.out.printf("Total belanjaan: %.2f\n", totalBelanja);
        scanner.close();
    }
}