import java.util.Scanner;

public class PercobaanB {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Masukkan nilai n1: "); double n1 = input.nextDouble();
        System.out.print("Masukkan nilai n2: "); double n2 = input.nextDouble();
        System.out.print("Masukkan nilai n3: "); double n3 = input.nextDouble();
        System.out.print("Masukkan nilai n4: "); double n4 = input.nextDouble();
        System.out.print("Masukkan nilai n5: "); double n5 = input.nextDouble();

        double rata = (n1 + n2 + n3 + n4 + n5) / 5.0;
        System.out.println("Rata-rata: " + rata);
        System.out.println("Nilai di atas rata-rata:");

        if (n1 > rata) System.out.println(n1);
        if (n2 > rata) System.out.println(n2);
        if (n3 > rata) System.out.println(n3);
        if (n4 > rata) System.out.println(n4);
        if (n5 > rata) System.out.println(n5);

        input.close();
    }
}