import java.util.Scanner;

public class SegitigaAngkaAsteris {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Masukkan nilai N: ");
        int N = scanner.nextInt();

        for (int i = 1; i <= N; i++) {
            for (int j = 1; j <= i; j++) {
                if (j % 2 == 0) {
                    System.out.print("* ");
                } else {
                    System.out.print(j + " ");
                }
            }
            System.out.println(); // Pindah ke baris baru
        }
        scanner.close();
    }
}
