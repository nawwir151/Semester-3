import java.util.Scanner;

public class KasirToko {

    // Prosedur menampilkan banner header kasir
    public static void tampilkanMenuHeader() {
        System.out.println("=============================================");
        System.out.println("        SISTEM KASIR TOKO SERBA ADA         ");
        System.out.println("=============================================");
    }

    // Fungsi menghitung subtotal belanja
    public static double hitungSubtotal(int harga, int qty) {
        return (double) harga * qty;
    }

    // Fungsi menghitung diskon belanja
    public static double hitungDiskon(double total, int isMember) {
        double diskonPersen = 0.0;

        // Diskon member 10%
        if (isMember == 1) {
            diskonPersen += 0.10;
        }

        // Tambahan diskon 5% jika belanja > 100.000
        if (total > 100000) {
            diskonPersen += 0.05;
        }

        return total * diskonPersen;
    }

    // Fungsi menghitung pajak PPN 11%
    public static double hitungPajak(double totalSetelahDiskon) {
        return totalSetelahDiskon * 0.11;
    }

    // Prosedur mencetak struk belanja
    public static void cetakStruk(double subtotal, double diskon, double pajak, double grandTotal) {
        System.out.println("\n================ STRUK BELANJA ================");
        System.out.printf("Subtotal Belanja    : Rp %,10.2f\n", subtotal);
        System.out.printf("Total Diskon        : Rp %,10.2f\n", diskon);
        System.out.printf("Total Stl. Diskon   : Rp %,10.2f\n", (subtotal - diskon));
        System.out.printf("Pajak PPN (11%%)     : Rp %,10.2f\n", pajak);
        System.out.println("-----------------------------------------------");
        System.out.printf("GRAND TOTAL         : Rp %,10.2f\n", grandTotal);
        System.out.println("===============================================");
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        tampilkanMenuHeader();

        System.out.print("Masukkan Harga Barang (Rp) : ");
        int harga = scanner.nextInt();

        System.out.print("Masukkan Jumlah Beli (Qty)  : ");
        int qty = scanner.nextInt();

        System.out.print("Apakah Member? (1 = Ya, 0 = Tidak): ");
        int isMember = scanner.nextInt();

        // Pemanggilan Fungsi-Fungsi Modular
        double subtotal = hitungSubtotal(harga, qty);
        double diskon = hitungDiskon(subtotal, isMember);
        double totalSetelahDiskon = subtotal - diskon;
        double pajak = hitungPajak(totalSetelahDiskon);
        double grandTotal = totalSetelahDiskon + pajak;

        // Cetak Struk menggunakan Prosedur
        cetakStruk(subtotal, diskon, pajak, grandTotal);

        scanner.close();
    }
}