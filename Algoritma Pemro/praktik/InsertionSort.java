public class InsertionSort {
    public static void insertionSort(int[] A) {
        int N = A.length;
        for (int i = 1; i < N; i++) {
            int key = A[i];                       // [FILL CODE 1]
            int j = i - 1;
            while (j >= 0 && A[j] > key) {        // [FILL CODE 2]
                A[j + 1] = A[j];                  // [FILL CODE 3]
                j = j - 1;                        // [FILL CODE 4]
            }
            A[j + 1] = key;                       // [FILL CODE 5]
        }
    }

    public static void main(String[] args) {
        int[] idPelanggan = {105, 102, 109, 101, 104, 103};
        
        System.out.println("ID Pelanggan sebelum diurutkan:");
        for (int val : idPelanggan) {
            System.out.print("ID-" + val + " ");
        }
        System.out.println();

        insertionSort(idPelanggan);

        System.out.println("\nID Pelanggan Terurut (Ascending):");
        for (int val : idPelanggan) {
            System.out.print("ID-" + val + " ");
        }
        System.out.println();
    }
}