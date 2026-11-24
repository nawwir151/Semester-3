public class PemantauanSuhu {
    public static void main(String[] args) {
        int L = 2; // Gedung
        int R = 2; // Ruangan
        int S = 3; // Sensor

        // Inisialisasi Array 3D [Gedung][Ruangan][Sensor]
        float[][][] suhu = {
            {
                {24.5f, 25.0f, 24.8f}, // Gedung 1, Ruangan 1
                {26.1f, 25.5f, 25.8f}  // Gedung 1, Ruangan 2
            },
            {
                {22.0f, 23.1f, 22.5f}, // Gedung 2, Ruangan 1
                {28.4f, 27.9f, 28.1f}  // Gedung 2, Ruangan 2
            }
        };

        float totalGedung1 = 0;
        float maxSuhu = suhu[0][0][0];
        int maxG = 0, maxR = 0, maxS = 0;

        // Pemrosesan Data dengan Triple Nested Loop
        for (int i = 0; i < L; i++) {
            for (int j = 0; j < R; j++) {
                for (int k = 0; k < S; k++) {
                    float val = suhu[i][j][k];

                    // Hitung Total khusus Gedung 1 (i = 0)
                    if (i == 0) {
                        totalGedung1 += val;
                    }

                    // Cari Suhu Maksimum
                    if (val > maxSuhu) {
                        maxSuhu = val;
                        maxG = i;
                        maxR = j;
                        maxS = k;
                    }
                }
            }
        }

        float rataGedung1 = totalGedung1 / (R * S);

        // Output
        System.out.printf("Rata-rata Suhu Gedung 1: %.2f °C\n", rataGedung1);
        System.out.printf("Suhu Tertinggi Tercatat : %.1f °C\n", maxSuhu);
        System.out.printf("Lokasi Suhu Tertinggi   : Gedung %d, Ruangan %d, Sensor %d\n", (maxG + 1), (maxR + 1), (maxS + 1));
    }
}