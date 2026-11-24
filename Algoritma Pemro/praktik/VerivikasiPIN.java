import java.util.Scanner;

public class VerivikasiPIN {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        final int PIN_BENAR = 1234;

        System.out.print("Masukkan PIN Anda: ");
        int pinInput = input.nextInt();

        while (pinInput != PIN_BENAR) {
            System.out.print("PIN Salah! Masukkan kembali PIN Anda: ");
            pinInput = input.nextInt();
        }

        System.out.println("\nAkses Diterima. Selamat Datang!");
        input.close();
    }
}