import java.util.Random;

/** Kiểm tra thứ tự và tính ổn định; không thay thế việc sinh viên tự viết mã. */
public final class CheckStudent {
    static final class Item implements Comparable<Item> {
        final int key, order;
        Item(int key, int order) { this.key = key; this.order = order; }
        public int compareTo(Item other) { return Integer.compare(key, other.key); }
    }

    public static void main(String[] args) {
        StudentMergeSort sorter = new StudentMergeSort();
        Random rng = new Random(1205);
        int tested = 0;
        for (int n = 0; n <= 130; n++) {
            for (int sample = 0; sample < 30; sample++) {
                Item[] source = new Item[n];
                for (int i = 0; i < n; i++) source[i] = new Item(rng.nextInt(8), i);
                for (int cutoff : new int[]{0, 1, 2, 4, 6, 7, 8, 10, 12, 20, 128}) {
                    Item[] a = source.clone();
                    sorter.sort(a, cutoff);
                    for (int i = 1; i < a.length; i++) {
                        if (a[i - 1].key > a[i].key ||
                            (a[i - 1].key == a[i].key && a[i - 1].order > a[i].order)) {
                            throw new AssertionError("n=" + n + " sample=" + sample +
                                                     " cutoff=" + cutoff);
                        }
                    }
                    tested++;
                }
            }
        }
        System.out.println("PASS sorted + stable: " + tested + " cases");
    }
}
