import java.util.Scanner;

public class PenjualanMinimarket {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Masukkan penjualan Hari ke-1: "); double h1 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-2: "); double h2 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-3: "); double h3 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-4: "); double h4 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-5: "); double h5 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-6: "); double h6 = input.nextDouble();
        System.out.print("Masukkan penjualan Hari ke-7: "); double h7 = input.nextDouble();

        double total = h1 + h2 + h3 + h4 + h5 + h6 + h7;
        double rataRata = total / 7;

        System.out.println("\n--- REKAPITULASI PENJUALAN ---");
        System.out.printf("Total Penjualan Mingguan : Rp%.2f\n", total);
        System.out.printf("Rata-Rata Penjualan Harian: Rp%.2f\n", rataRata);

        System.out.println("\nHari dengan penjualan DI BAWAH rata-rata:");
        if (h1 < rataRata) System.out.printf("- Hari ke-1: Rp%.2f\n", h1);
        if (h2 < rataRata) System.out.printf("- Hari ke-2: Rp%.2f\n", h2);
        if (h3 < rataRata) System.out.printf("- Hari ke-3: Rp%.2f\n", h3);
        if (h4 < rataRata) System.out.printf("- Hari ke-4: Rp%.2f\n", h4);
        if (h5 < rataRata) System.out.printf("- Hari ke-5: Rp%.2f\n", h5);
        if (h6 < rataRata) System.out.printf("- Hari ke-6: Rp%.2f\n", h6);
        if (h7 < rataRata) System.out.printf("- Hari ke-7: Rp%.2f\n", h7);

        input.close();
    }
}