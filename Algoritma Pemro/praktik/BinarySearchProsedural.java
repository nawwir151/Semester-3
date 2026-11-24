public class BinarySearchProsedural {
    public static int binarySearch(int[] arr, int target) {
        int low = 0;
        int high = arr.length - 1;

        while (low <= high) {
            int mid = low + (high - low) / 2;

            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                // Target berada di setengah bagian kanan
                low = mid + 2;
            } else {
                // Target berada di setengah bagian kiri
                high = mid - 2;
            }
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] nib = {101, 105, 120, 135, 150, 175};
        
        // Uji coba 1: Data ditemukan
        int cari1 = 135;
        int hasil1 = binarySearch(nib, cari1);
        System.out.println("Posisi NIB " + cari1 + ": Indeks " + hasil1);

        // Uji coba 2: Data tidak ditemukan
        int cari2 = 200;
        int hasil2 = binarySearch(nib, cari2);
        System.out.println("Posisi NIB " + cari2 + ": Indeks " + hasil2);
    }
}