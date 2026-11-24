import java.util.Scanner;

public class TokoOnline {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Masukkan Total Belanja: Rp ");
        double totalBelanja = input.nextDouble();

        double diskon = 0;
        if (totalBelanja >= 100000) {
            diskon = totalBelanja * 0.10;
        } else {
            diskon = 0;
        }

        double totalBayar = totalBelanja - diskon;

        System.out.println("Diskon      : Rp " + diskon);
        System.out.println("Total Bayar : Rp " + totalBayar);

        input.close();
    }
}