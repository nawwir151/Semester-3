import java.util.Scanner;

public class SubprogramRekursif {

    // Fungsi Rekursif Faktorial
    public static int faktorial(int n) {
        // TODO [1]: Tentukan Base Case (jika n == 0 atau n == 1)
        if (n <= 1) {
            return 1;
        }
        // TODO [2]: Tentukan Call Case (n * faktorial(n - 1))
        return n * faktorial(n - 1);
    }

    // Fungsi Rekursif Fibonacci
    public static int fibonacci(int n) {
        if (n == 0) return 0;
        if (n == 1) return 1;
        // TODO [3]: Kembalikan hasil penjumlahan dua suku fibonacci sebelumnya
        return fibonacci(n - 1) + fibonacci(n - 2);
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Masukkan angka untuk Faktorial (N): ");
        int num = scanner.nextInt();
        System.out.println("Hasil Faktorial " + num + "! = " + faktorial(num));

        System.out.print("\nMasukkan jumlah suku Fibonacci: ");
        int count = scanner.nextInt();
        System.out.print("Deret Fibonacci: ");
        for (int i = 0; i < count; i++) {
            System.out.print(fibonacci(i) + " ");
        }
        System.out.println();

        scanner.close();
    }
}