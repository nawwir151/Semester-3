import java.util.Scanner;

public class HitungTotalBelanja {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        double totalBayar = 0;

        System.out.print("Masukkan jumlah barang: ");
        int jumlahBarang = input.nextInt();

        for (int i = 1; i <= jumlahBarang; i++) {
            System.out.print("Masukkan harga barang ke-" + i + ": Rp");
            double hargaBarang = input.nextDouble();
            totalBayar = totalBayar + hargaBarang;
        }

        System.out.printf("\nTotal Pembayaran: Rp%.2f\n", totalBayar);
        input.close();
    }
}