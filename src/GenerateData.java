import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Deterministic datasets; invoke: java GenerateData [directory] */
public final class GenerateData {
    public static void main(String[] args) throws IOException {
        Path dir = Paths.get(args.length > 0 ? args[0] : "data");
        Files.createDirectories(dir);
        int[] sizes = {10000, 100000};
        String[] kinds = {"random", "sorted", "reverse", "few_values"};
        for (int n : sizes) for (String kind : kinds) for (int seed = 0; seed < 3; seed++) {
            int[] a = new int[n];
            Random rng = new Random(20261027L + 1009L * seed + n);
            for (int i = 0; i < n; i++) a[i] = rng.nextInt(1000001) - 500000;
            if (kind.equals("few_values")) {
                for (int i = 0; i < n; i++) a[i] = rng.nextInt(8);
            } else if (kind.equals("sorted") || kind.equals("reverse")) {
                Arrays.sort(a);
                if (kind.equals("reverse")) {
                    for (int i = 0, j = n - 1; i < j; i++, j--) {
                        int t = a[i]; a[i] = a[j]; a[j] = t;
                    }
                }
            }
            Path file = dir.resolve(kind + "_n" + n + "_s" + seed + ".txt");
            try (BufferedWriter w = Files.newBufferedWriter(file)) {
                for (int x : a) { w.write(Integer.toString(x)); w.newLine(); }
            }
            System.out.println(file);
        }
    }
}
