import java.util.Scanner;

public class TugasMatriks {

    // Method modular untuk menampilkan matriks
    public static void tampilkanMatriks(int[][] mtr, int r, int c, String label) {
        System.out.println("\n--- " + label + " ---");
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                System.out.printf("%4d", mtr[i][j]);
            }
            System.out.println();
        }
    }

    // Method modular untuk menghitung dan menampilkan Transpose Matriks (N x M)
    public static void prosesTranspose(int[][] A, int m, int n) {
        int[][] transpose = new int[n][m];
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                transpose[j][i] = A[i][j];
            }
        }
        tampilkanMatriks(transpose, n, m, "Matriks Transpose A^T (N x M)");
    }

    // Method modular untuk menghitung dan menampilkan Rotasi 90 Derajat Searah Jarum Jam (N x M)
    public static void prosesRotasi90(int[][] A, int m, int n) {
        int[][] rotasi = new int[n][m];
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                rotasi[j][m - 1 - i] = A[i][j];
            }
        }
        tampilkanMatriks(rotasi, n, m, "Matriks Rotasi 90 Derajat Searah Jarum Jam (N x M)");
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Masukkan jumlah baris (M): ");
        int m = scanner.nextInt();
        System.out.print("Masukkan jumlah kolom (N): ");
        int n = scanner.nextInt();

        int[][] A = new int[m][n];

        System.out.println("\n=== Input Elemen Matriks A (" + m + "x" + n + ") ===");
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                System.out.print("Elemen [" + i + "][" + j + "]: ");
                A[i][j] = scanner.nextInt();
            }
        }

        // Pemanggilan method-method modular
        tampilkanMatriks(A, m, n, "Matriks Asal A (M x N)");
        prosesTranspose(A, m, n);
        prosesRotasi90(A, m, n);

        scanner.close();
    }
}