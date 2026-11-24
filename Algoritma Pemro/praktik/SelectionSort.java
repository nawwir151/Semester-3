public class SelectionSort {
    public static void selectionSortDescending(int[] A) {
        int N = A.length;
        for (int i = 0; i < N - 1; i++) {
            int max_idx = i;                      // [FILL CODE 1]
            for (int j = i + 1; j < N; j++) {
                if (A[j] > A[max_idx]) {          // [FILL CODE 2]
                    max_idx = j;                  // [FILL CODE 3]
                }
            }
            if (max_idx != i) {
                int temp = A[i];
                A[i] = A[max_idx];                // [FILL CODE 4]
                A[max_idx] = temp;                // [FILL CODE 5]
            }
        }
    }

    public static void main(String[] args) {
        int[] tinggi = {170, 185, 168, 192, 178, 180};
        
        System.out.println("Tinggi badan sebelum diurutkan:");
        for (int val : tinggi) {
            System.out.print(val + " cm ");
        }
        System.out.println();

        selectionSortDescending(tinggi);

        System.out.println("\nTinggi badan (Descending):");
        for (int val : tinggi) {
            System.out.print(val + " cm ");
        }
        System.out.println();
    }
}