import java.util.Scanner;

public class PencarianNISN {

    // 1. Metode Linear Search (O(N))
    public static int linearSearch(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                return i; // Ditemukan
            }
        }
        return -1; // Tidak ditemukan
    }

    // 2. Metode Binary Search (O(log N))
    public static int binarySearch(int[] arr, int target) {
        int low = 0;
        int high = arr.length - 1;

        while (low <= high) {
            int mid = low + (high - low) / 2;

            if (arr[mid] == target) {
                return mid; // Ditemukan
            } else if (arr[mid] < target) {
                low = mid + 1; // Cari di bagian kanan
            } else {
                high = mid - 1; // Cari di bagian kiri
            }
        }
        return -1; // Tidak ditemukan
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Simulasi data 10.000 NISN siswa (terurut)
        int jumlahSiswa = 10000;
        int[] dataNISN = new int[jumlahSiswa];
        
        // Membuka array NISN terurut dari 100010001 sampai 100020000
        for (int i = 0; i < jumlahSiswa; i++) {
            dataNISN[i] = 100010001 + i;
        }

        System.out.println("=================================================");
        System.out.println("   SISTEM PENCARIAN DATA NISN SISWA (10.000 DATA)");
        System.out.println("=================================================");
        System.out.print("Masukkan NISN Siswa yang dicari: ");
        int nisnCari = scanner.nextInt();

        // Uji Coba Binary Search
        long startTimeBS = System.nanoTime();
        int hasilBS = binarySearch(dataNISN, nisnCari);
        long endTimeBS = System.nanoTime();

        // Uji Coba Linear Search
        long startTimeLS = System.nanoTime();
        int hasilLS = linearSearch(dataNISN, nisnCari);
        long endTimeLS = System.nanoTime();

        // Menampilkan Hasil Pencarian
        if (hasilBS != -1) {
            System.out.println("\n[HASIL PENCARIAN: DITEMUKAN]");
            System.out.println("NISN Siswa       : " + nisnCari);
            System.out.println("Posisi (Indeks)  : " + hasilBS);
            System.out.println("Urutan Data Ke   : " + (hasilBS + 1));
        } else {
            System.out.println("\n[HASIL PENCARIAN: TIDAK DITEMUKAN]");
            System.out.println("Pesan Error      : Data NISN " + nisnCari + " tidak terdaftar.");
        }

        System.out.println("\n================ PERBANDINGAN PERFORMA ================");
        System.out.println("Binary Search Execution Time : " + (endTimeBS - startTimeBS) + " ns");
        System.out.println("Linear Search Execution Time : " + (endTimeLS - startTimeLS) + " ns");
        System.out.println("=======================================================");

        scanner.close();
    }
}