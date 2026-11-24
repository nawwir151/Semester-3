import java.util.Scanner;

public class PenjualanMinimarket5Hari {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Masukkan penjualan Hari ke-1: "); double h1 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-2: "); double h2 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-3: "); double h3 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-4: "); double h4 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-5: "); double h5 = input.nextDouble();

        double totalPenjualan = h1 + h2 + h3 + h4 + h5;
        double rataRata = totalPenjualan / 5.0;

        System.out.println("\n--- REKAPITULASI PENJUALAN ---");
        System.out.printf("Total Penjualan  : Rp%.2f\n", totalPenjualan);
        System.out.printf("Rata-Rata Harian : Rp%.2f\n", rataRata);

        System.out.println("\nHari dengan penjualan DI BAWAH rata-rata:");
        if (h1 < rataRata) System.out.printf("- Hari ke-1: Rp%.2f\n", h1);
        if (h2 < rataRata) System.out.printf("- Hari ke-2: Rp%.2f\n", h2);
        if (h3 < rataRata) System.out.printf("- Hari ke-3: Rp%.2f\n", h3);
        if (h4 < rataRata) System.out.printf("- Hari ke-4: Rp%.2f\n", h4);
        if (h5 < rataRata) System.out.printf("- Hari ke-5: Rp%.2f\n", h5);

        input.close();
    }
}