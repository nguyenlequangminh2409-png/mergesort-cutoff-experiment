import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

/** java Benchmark data measurements.csv StudentMergeSort [rounds] [cutoffs] */
public final class Benchmark {
    static volatile long guard;

    static Comparable[] read(Path p) throws IOException {
        try (Stream<String> lines = Files.lines(p)) {
            return lines.map(Integer::valueOf).toArray(Comparable[]::new);
        }
    }

    static void verify(Comparable[] actual, Comparable[] expected, Path file, int k) {
        if (!Arrays.equals(actual, expected))
            throw new IllegalStateException("Wrong result: " + file + " cutoff=" + k);
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 3 || args.length > 5) {
            System.err.println("java Benchmark DATA_DIR OUT.csv SORT_CLASS [rounds=7] [cutoffs=0,4,6,7,8,9,10,11,12,14,16,20]");
            System.exit(2);
        }
        Path dir = Paths.get(args[0]), output = Paths.get(args[1]);
        SortAlgorithm sort = (SortAlgorithm) Class.forName(args[2]).getDeclaredConstructor().newInstance();
        int rounds = args.length >= 4 ? Integer.parseInt(args[3]) : 7;
        if (rounds < 3) throw new IllegalArgumentException("Use at least 3 timed rounds");
        String csv = args.length >= 5 ? args[4] : "0,4,6,7,8,9,10,11,12,14,16,20";
        List<Integer> cutoffs = new ArrayList<>();
        for (String part : csv.split(",")) {
            int k = Integer.parseInt(part.trim());
            if (k < 0 || !cutoffs.add(k)) throw new IllegalArgumentException("Invalid or duplicate cutoff: " + k);
        }
        List<Path> files;
        try (Stream<Path> s = Files.list(dir)) {
            files = s.filter(p -> p.getFileName().toString().matches("(random|sorted|reverse|few_values)_n[0-9]+_s[0-9]+\\.txt"))
                .sorted().collect(Collectors.toList());
        }
        if (files.isEmpty()) throw new IllegalArgumentException("No datasets in " + dir);
        if (output.getParent() != null) Files.createDirectories(output.getParent());
        if (Files.exists(output)) throw new FileAlreadyExistsException(output.toString());
        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(output))) {
            out.println("dataset,n,kind,seed,cutoff,round,elapsed_ns");
            for (Path file : files) {
                String name = file.getFileName().toString();
                String[] parts = name.substring(0, name.length() - 4).split("_n|_s");
                Comparable[] base = read(file), expected = base.clone();
                int n = Integer.parseInt(parts[1]);
                if (n != base.length) throw new IllegalStateException("Wrong length: " + file);
                Arrays.sort(expected);
                // Warm up the very same implementation for every candidate outside measurement.
                for (int i = 0; i < 3; i++) for (int k : cutoffs) {
                    Comparable[] copy = base.clone();
                    sort.sort(copy, k);
                    verify(copy, expected, file, k);
                    guard ^= copy[copy.length / 2].hashCode();
                }
                for (int round = 0; round < rounds; round++) {
                    List<Integer> order = new ArrayList<>(cutoffs);
                    Collections.shuffle(order, new Random(7191L + round * 97L + name.hashCode()));
                    for (int k : order) {
                        Comparable[] copy = base.clone(); // Excluded from timing.
                        long start = System.nanoTime();
                        sort.sort(copy, k);
                        long elapsed = System.nanoTime() - start;
                        verify(copy, expected, file, k); // Outside timing; checks every sample.
                        guard ^= copy[copy.length / 2].hashCode();
                        out.printf(Locale.ROOT, "%s,%d,%s,%s,%d,%d,%d%n", name, n, parts[0], parts[2], k, round, elapsed);
                    }
                }
                out.flush();
                System.out.println("Done: " + name);
            }
        }
        System.out.println("Saved " + output + " guard=" + guard);
    }
}
