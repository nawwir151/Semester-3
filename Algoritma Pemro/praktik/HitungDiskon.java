import java.util.Scanner; //PERTEMUAN2

public class HitungDiskon {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        // Input total belanja
        System.out.print("Masukkan Total Belanja: Rp ");
        double totalBelanja = input.nextDouble();

        // Hitung diskon berdasarkan kondisi
        double besarDiskon;
        if (totalBelanja >= 100000) {
            besarDiskon = totalBelanja * 0.10;
        } else {
            besarDiskon = 0;
        }

        // Hitung total bayar akhir
        double totalBayar = totalBelanja - besarDiskon;

        // Tampilkan hasil
        System.out.println("Besar Diskon : Rp " + besarDiskon);
        System.out.println("Total Bayar  : Rp " + totalBayar);

        input.close();
    }
}