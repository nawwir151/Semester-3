import java.util.Scanner; //PERTEMUAN2

public class HitungLuas { 
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
                
        // Deklarasi variabel
        double panjang, lebar, luas;
        String kategori;
        // Input
        System.out.print("Masukkan panjang: ");
        panjang = input.nextDouble();
        System.out.print("Masukkan lebar: ");
        lebar = input.nextDouble();

        // Proses
        luas = panjang * lebar;

        // Percabangan
        if (luas > 50) {
        kategori = "Besar";
        } else {
        kategori = "Kecil";
        }

        // Output
        System.out.println("Luas: " + luas);
        System.out.println("Kategori: " + kategori);
        input.close();
    }
}