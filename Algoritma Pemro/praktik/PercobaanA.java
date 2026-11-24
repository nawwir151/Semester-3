import java.util.Scanner;

public class PercobaanA {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        double total = 0;
        double nilai = 0;

        for (int i = 1; i <= 5; i++) {
            System.out.print("Masukkan nilai mahasiswa ke-" + i + ": ");
            nilai = input.nextDouble();
            total += nilai;
        }

        double rata = total / 5.0;
        System.out.println("Rata-rata nilai: " + rata);
        input.close();
    }
}