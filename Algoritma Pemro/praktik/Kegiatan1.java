public class Kegiatan1 {
    public static void merge(int[] A, int l, int m, int r) {
        int n1 = m - l + 1;
        int n2 = r - m;

        int[] L = new int[n1];
        int[] R = new int[n2];

        for (int i = 0; i < n1; i++) L[i] = A[l + i];
        for (int j = 0; j < n2; j++) R[j] = A[m + 1 + j];

        int i = 0, j = 0, k = l;
        while (i < n1 && j < n2) {
            if (L[i] <= R[j]) {
                A[k] = L[i];
                i++;
            } else {
                A[k] = R[j]; // [FILL CODE 1]
                j++;
            }
            k++;
        }

        while (i < n1) { A[k++] = L[i++]; }
        while (j < n2) { A[k++] = R[j++]; }
    }

    public static void mergeSort(int[] A, int l, int r) {
        if (l < r) { // [FILL CODE 2]
            int m = l + (r - l) / 2;
            mergeSort(A, l, m); // [FILL CODE 3]
            mergeSort(A, m + 1, r);
            merge(A, l, m, r);
        }
    }

    public static void main(String[] args) {
        int[] nilai = {78, 45, 90, 62, 53, 85};
        
        System.out.println("Data Sebelum Diurutkan:");
        for (int val : nilai) System.out.print(val + " ");
        System.out.println();

        mergeSort(nilai, 0, nilai.length - 1);

        System.out.println("\nHasil Merge Sort (Ascending):");
        for (int val : nilai) System.out.print(val + " ");
        System.out.println();
    }
}
