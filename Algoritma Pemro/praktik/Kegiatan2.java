public class Kegiatan2 {
    public static int partition(int[] A, int low, int high) {
        int pivot = A[high];
        int i = low - 1; // [FILL CODE 1]

        for (int j = low; j < high; j++) {
            if (A[j] <= pivot) {
                i++;
                int temp = A[i];
                A[i] = A[j];
                A[j] = temp;
            }
        }

        int temp = A[i + 1];
        A[i + 1] = A[high]; // [FILL CODE 2]
        A[high] = temp;

        return i + 1; // [FILL CODE 3]
    }

    public static void quickSort(int[] A, int low, int high) {
        if (low < high) {
            int pi = partition(A, low, high);
            quickSort(A, low, pi - 1); // [FILL CODE 4]
            quickSort(A, pi + 1, high);
        }
    }

    public static void main(String[] args) {
        int[] idPelanggan = {105, 102, 109, 101, 104, 103};

        System.out.println("Data ID Pelanggan Sebelum Diurutkan:");
        for (int val : idPelanggan) System.out.print(val + " ");
        System.out.println();

        quickSort(idPelanggan, 0, idPelanggan.length - 1);

        System.out.println("\nHasil Quick Sort (Ascending):");
        for (int val : idPelanggan) System.out.print("ID-" + val + " ");
        System.out.println();
    }
}
