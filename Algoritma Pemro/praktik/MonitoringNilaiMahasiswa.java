import java.util.Scanner;

public class MonitoringNilaiMahasiswa {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        char ulang;

        do {
            System.out.print("\nMasukkan jumlah mahasiswa: ");
            int jumlahMahasiswa = input.nextInt();

            while (jumlahMahasiswa <= 0) {
                System.out.println("Jumlah mahasiswa harus lebih dari 0!");
                System.out.print("Masukkan kembali jumlah mahasiswa: ");
                jumlahMahasiswa = input.nextInt();
            }

            double totalNilai = 0;
            int lulus = 0;
            int tidakLulus = 0;

            for (int i = 1; i <= jumlahMahasiswa; i++) {
                System.out.print("Masukkan nilai mahasiswa ke-" + i + " (0-100): ");
                double nilai = input.nextDouble();

                while (nilai < 0 || nilai > 100) {
                    System.out.println("Nilai tidak valid! Nilai harus antara 0 - 100.");
                    System.out.print("Masukkan kembali nilai mahasiswa ke-" + i + ": ");
                    nilai = input.nextDouble();
                }

                totalNilai += nilai;

                if (nilai >= 60) {
                    lulus++;
                } else {
                    tidakLulus++;
                }
            }

            double rataRata = totalNilai / jumlahMahasiswa;

            System.out.println("\n--- HASIL REKAPITULASI NILAI ---");
            System.out.println("Total Nilai            : " + totalNilai);
            System.out.printf("Rata-rata Kelas        : %.2f\n", rataRata);
            System.out.println("Jumlah Mahasiswa Lulus    : " + lulus);
            System.out.println("Jumlah Mahasiswa Tidak Lulus : " + tidakLulus);

            System.out.print("\nHitung rata-rata kelas lain? (y/t): ");
            ulang = input.next().charAt(0);

        } while (ulang == 'y' || ulang == 'Y');

        System.out.println("Program Selesai. Terima kasih!");
        input.close();
    }
}