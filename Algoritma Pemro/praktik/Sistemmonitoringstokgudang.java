import java.util.Scanner;

public class Sistemmonitoringstokgudang {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Masukkan jumlah jenis barang (N): ");
        int n = scanner.nextInt();
        int[] stok = new int[n];

        // Input stok barang
        System.out.println("\n=== INPUT STOK BARANG ===");
        for (int i = 0; i < n; i++) {
            System.out.print("Stok barang Indeks [" + i + "]: ");
            stok[i] = scanner.nextInt();
        }

        // Input nilai threshold
        System.out.print("\nMasukkan batas minimum stok (threshold): ");
        int threshold = scanner.nextInt();

        // Pemrosesan & Penyaringan stok
        int jumlahRestock = 0;
        System.out.println("\n=== BARANG YANG PERLU RE-ORDER (RESTOCK) ===");
        for (int i = 0; i < n; i++) {
            if (stok[i] < threshold) {
                System.out.println("-> Indeks Barang: " + i + " (Stok Sisa: " + stok[i] + ")");
                jumlahRestock++;
            }
        }

        System.out.println("----------------------------------------------");
        System.out.println("Total barang di bawah ambang batas: " + jumlahRestock + " jenis.");

        scanner.close();
    }
}