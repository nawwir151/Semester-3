import java.util.Scanner; 

public class UjianKampus {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        // Input nilai
        System.out.print("Masukkan NIM: ");
        int NIM = input.nextInt();

        // Penentuan status kelulusan
        String status;
        if (NIM >= 20) {
            status = "TIPE A, Kursi Lt 1";
        } else {
            status = "TIPE B, Kursi Lt 2";
        }

        // Tampilkan output
        System.out.println("NIM  : " + NIM);
        System.out.println("Status : " + status);

        input.close();
    }
}