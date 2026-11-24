public class BubbleSort {
    public static void bubbleSort(int[] A) {
        int N = A.length;
        boolean swapped;
        for (int i = 0; i < N - 1; i++) {
            swapped = false;
            for (int j = 0; j < N - i - 1; j++) { // [FILL CODE 1]
                if (A[j] > A[j + 1]) {            // [FILL CODE 2]
                    // Swap
                    int temp = A[j];
                    A[j] = A[j + 1];              // [FILL CODE 3]
                    A[j + 1] = temp;
                    swapped = true;               // [FILL CODE 4]
                }
            }
            if (!swapped) break;                  // [FILL CODE 5]
        }
    }

    public static void main(String[] args) {
        int[] nilai = {64, 34, 25, 12, 22, 11, 90};
        
        System.out.println("Data sebelum diurutkan:");
        for (int val : nilai) {
            System.out.print(val + " ");
        }
        System.out.println();

        bubbleSort(nilai);

        System.out.println("\nHasil pengurutan nilai (Ascending):");
        for (int val : nilai) {
            System.out.print(val + " ");
        }
        System.out.println();
    }
}