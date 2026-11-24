import java.util.Scanner;

public class luaslingkaran {
    public static void main(String[] args) {
        // Deklarasi
        double luas, PI;
        int r;

        Scanner input = new Scanner(System.in);

        // Input
        System.out.print("Masukkan nilai PI: ");
        PI = input.nextDouble();

        System.out.print("Masukkan nilai r: ");
        r = input.nextInt();

        // Proses
        luas = PI * r * r;

        // Output
        System.out.println("Luas Lingkaran: " + luas);

    }
}