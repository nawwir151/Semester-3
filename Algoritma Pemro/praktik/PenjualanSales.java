import java.util.Scanner;

public class PenjualanSales {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Masukkan jumlah sales (K): ");
        int k = scanner.nextInt();
        System.out.print("Masukkan jumlah hari (H): ");
        int h = scanner.nextInt();

        int[][] penjualan = new int[k][h];
        int[] totalSales = new int[k];

        // Input Data Penjualan
        for (int i = 0; i < k; i++) {
            System.out.println("\n--- Data Sales ke-" + (i + 1) + " ---");
            for (int j = 0; j < h; j++) {
                System.out.print("Penjualan Hari ke-" + (j + 1) + ": ");
                penjualan[i][j] = scanner.nextInt();
            }
        }

        // Hitung Total Penjualan per Sales
        for (int i = 0; i < k; i++) {
            int sum = 0;
            for (int j = 0; j < h; j++) {
                // TODO [1]: Akumulasikan penjualan[i][j] ke dalam variabel sum
                sum += penjualan[i][j];
            }
            // TODO [2]: Simpan variabel sum ke dalam totalSales[i]
            totalSales[i] = sum;
        }

        // Cari Penjualan Minimum
        int minPenjualan = penjualan[0][0];
        int minSalesIdx = 0;
        int minHariIdx = 0;

        for (int i = 0; i < k; i++) {
            for (int j = 0; j < h; j++) {
                // TODO [3]: Kondisi perkondisian untuk memperbarui minPenjualan, minSalesIdx, dan minHariIdx
                if (penjualan[i][j] < minPenjualan) {
                    minPenjualan = penjualan[i][j];
                    minSalesIdx = i;
                    minHariIdx = j;
                }
            }
        }

        // Output Hasil
        System.out.println("\n================ REKAP PENJUALAN ================");
        for (int i = 0; i < k; i++) {
            System.out.println("Total Sales " + (i + 1) + ": " + totalSales[i] + " unit");
        }
        System.out.println("\nPenjualan Terendah: " + minPenjualan + " unit (Sales " + (minSalesIdx + 1) + ", Hari " + (minHariIdx + 1) + ")");

        scanner.close();
    }
}