public class BinarySearchRekursif {
    public static int binarySearchRekursif(int[] arr, int low, int high, int target) {
        if (low > high) {
            return -1;
        }

        int mid = low + (high - low) / 2;

        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] > target) {
            // Pemanggilan rekursif sub-array kiri
            return binarySearchRekursif(arr, low, mid - 2, target);
        } else {
            // Pemanggilan rekursif sub-array kanan
            return binarySearchRekursif(arr, mid + 2, high, target);
        }
    }

    public static void main(String[] args) {
        int[] nisn = {1001, 1004, 1008, 1012, 1015, 1020};
        
        // Uji coba 1: Data ditemukan
        int cari1 = 1099;
        int hasil1 = binarySearchRekursif(nisn, 0, nisn.length - 1, cari1);
        System.out.println("NISN " + cari1 + " berada pada posisi indeks: " + hasil1);

        // Uji coba 2: Data tidak ditemukan
        int cari2 = 6969;
        int hasil2 = binarySearchRekursif(nisn, 0, nisn.length - 1, cari2);
        System.out.println("NISN " + cari2 + " berada pada posisi indeks: " + hasil2);
    }
}