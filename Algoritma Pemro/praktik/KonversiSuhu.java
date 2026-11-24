import java.util.Scanner;
 
public class KonversiSuhu {

    // Prosedur menampilkan header menu
    public static void tampilkanMenu() {
        System.out.println("=========================================");
        System.out.println("     SISTEM KONVERSI SUHU MODULAR       ");
        System.out.println("=========================================");
        System.out.println("Pilih Jenis Konversi:");
        System.out.println("1. Fahrenheit");
        System.out.println("2. Kelvin");
        System.out.println("3. Reamur");
        System.out.println("=========================================");
        System.out.print("Pilihan Anda (1-3): ");
    }

    // TODO [1]: Fungsi celciusToFahrenheit dengan tipe kembalian double
    public static double celciusToFahrenheit(double c) {
        return (9.0 / 5.0) * c + 32;
    }

    // TODO [2]: Fungsi celciusToKelvin dengan tipe kembalian double
    public static double celciusToKelvin(double c) {
        return c + 273.15;
    }

    // TODO [3]: Fungsi celciusToReamur dengan tipe kembalian double
    public static double celciusToReamur(double c) {
        return (4.0 / 5.0) * c;
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Masukkan nilai suhu Celcius: ");
        double celsius = scanner.nextDouble();

        tampilkanMenu();
        int pilihan = scanner.nextInt();
        double hasil = 0;

        switch (pilihan) {
            case 1:
                // TODO [4]: Panggil fungsi celciusToFahrenheit
                hasil = celciusToFahrenheit(celsius);
                break;
            case 2:
                // TODO [5]: Panggil fungsi celciusToKelvin
                hasil = celciusToKelvin(celsius);
                break;
            case 3:
                // TODO [6]: Panggil fungsi celciusToReamur
                hasil = celciusToReamur(celsius);
                break;
            default:
                System.out.println("Pilihan tidak valid!");
        }

        if (pilihan >= 1 && pilihan <= 3) {
            System.out.printf("Hasil Konversi: %.2f\n", hasil);
        }

        scanner.close();
    }
}