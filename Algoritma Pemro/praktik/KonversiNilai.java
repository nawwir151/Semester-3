import java.util.Scanner;

public class KonversiNilai {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Masukkan Nilai Akhir (0-100): ");
        int nilaiAkhir = input.nextInt();

        String nilaiHuruf;
        if (nilaiAkhir >= 85) {
            nilaiHuruf = "A";
        } else if (nilaiAkhir >= 75) {
            nilaiHuruf = "B";
        } else if (nilaiAkhir >= 60) {
            nilaiHuruf = "C";
        } else if (nilaiAkhir >= 50) {
            nilaiHuruf = "D";
        } else {
            nilaiHuruf = "E";
        }

        System.out.println("Nilai Huruf: " + nilaiHuruf);

        input.close();
    }
}