import java.util.Scanner;

public class StokProduk {

    // Data Produk (Paralel Array / Representasi Matriks Terurut)
    static int[] idProduk = {102, 108, 115, 121, 130};
    static String[] namaProduk = {"Sabun Mandi", "Shampo", "Pasta Gigi", "Detergen", "Minyak Goreng"};
    static int[] stokProduk = {45, 20, 60, 15, 30};

    // 1. Implementation Binary Search Prosedural
    public static int binarySearchProsedural(int targetID) {
        int low = 0;
        int high = idProduk.length - 1;

        while (low <= high) {
            int mid = low + (high - low) / 2;
            if (idProduk[mid] == targetID) {
                return mid;
            } else if (idProduk[mid] < targetID) {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }
        return -1;
    }

    // 2. Implementation Binary Search Rekursif
    public static int binarySearchRekursif(int low, int high, int targetID) {
        if (low > high) {
            return -1;
        }
        int mid = low + (high - low) / 2;
        if (idProduk[mid] == targetID) {
            return mid;
        } else if (idProduk[mid] > targetID) {
            return binarySearchRekursif(low, mid - 1, targetID);
        } else {
            return binarySearchRekursif(mid + 1, high, targetID);
        }
    }

    // Prosedur mencetak informasi produk
    public static void tampilkanHasil(int idx, int idCari) {
        if (idx != -1) {
            System.out.println("\n--- PRODUK DITEMUKAN ---");
            System.out.println("ID Produk   : " + idProduk[idx]);
            System.out.println("Nama Produk : " + namaProduk[idx]);
            System.out.println("Stok Produk : " + stokProduk[idx] + " pcs");
        } else {
            System.out.println("\nPesan Error: Produk tidak ditemukan (ID " + idCari + ")");
        }
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Masukkan ID Produk yang dicari: ");
        int idCari = scanner.nextInt();

        // Pengujian Pencarian Prosedural
        System.out.println("\n[Hasil Pencarian Binary Search Prosedural]");
        int idxPros = binarySearchProsedural(idCari);
        tampilkanHasil(idxPros, idCari);

        // Pengujian Pencarian Rekursif
        System.out.println("\n[Hasil Pencarian Binary Search Rekursif]");
        int idxReks = binarySearchRekursif(0, idProduk.length - 1, idCari);
        tampilkanHasil(idxReks, idCari);

        scanner.close();
    }
}