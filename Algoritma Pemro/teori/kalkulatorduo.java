import java.util.Scanner;

public class kalkulatorduo {
    public static void main(String[] args) {
        // deklarasi variabel
        double bilangan1, bilangan2, rataRata;

        Scanner input = new Scanner(System.in);

        // bilangan pertama
        System.out.print("Masukkan bilangan pertama: ");
        bilangan1 = input.nextDouble();

        // bilangan kedua
        System.out.print("Masukkan bilangan kedua: ");
        bilangan2 = input.nextDouble();

        // menghitung rata-rata
        rataRata = (bilangan1 + bilangan2) / 2;

        // menampilkan hasil perhitungan
        System.out.println("Rata-rata = " + rataRata);

    }
}