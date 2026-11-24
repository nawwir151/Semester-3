import java.util.Scanner; //PERTEMUAN2

public class CekKelulusan {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        // Input nilai
        System.out.print("Masukkan Nilai: ");
        int nilai = input.nextInt();

        // Penentuan status kelulusan
        String status;
        if (nilai >= 75) {
            status = "LULUS";
        } else {
            status = "TIDAK LULUS";
        }

        // Tampilkan output
        System.out.println("Nilai  : " + nilai);
        System.out.println("Status : " + status);

        input.close();
    }
}