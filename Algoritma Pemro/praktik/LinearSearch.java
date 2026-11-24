public class LinearSearch {
    public static int linearSearch(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            // Lengkapi kondisi pengecekan target
            if (arr[i] == target) {
                return i;
            }
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] data = {45000, 12000, 8900, 33000, 2700};
        
        // Uji coba 1: Data ditemukan
        int cari1 = 33000;
        int hasil1 = linearSearch(data, cari1);
        if (hasil1 != -1) {
            System.out.println("Data " + cari1 + " ditemukan pada indeks " + hasil1);
        } else {
            System.out.println("Data " + cari1 + " tidak ditemukan");
        }

        // Uji coba 2: Data tidak ditemukan
        int cari2 = 50000;
        int hasil2 = linearSearch(data, cari2);
        if (hasil2 != -1) {
            System.out.println("Data " + cari2 + " ditemukan pada indeks " + hasil2);
        } else {
            System.out.println("Data " + cari2 + " tidak ditemukan");
        }
    }
}