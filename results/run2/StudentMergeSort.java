/**
 * Sinh viên tự cài đặt theo slide Mergesort của môn học.
 * Các thân hàm dưới đây cố ý để trống; không dùng mã ở legacy làm bài nộp.
 */
public final class StudentMergeSort implements SortAlgorithm {
    @Override
    public void sort(Comparable[] a, int cutoff) {
        if (cutoff < 0) {
            throw new IllegalArgumentException("Cutoff cannot be negative");
        }
        Comparable[] aux = new Comparable[a.length];
        sort(a, aux, 0, a.length - 1, cutoff);
    }

    private static void sort(Comparable[] a, Comparable[] aux,
                             int lo, int hi, int cutoff) {
        if (hi <= lo) {
            return;
        }
        if (cutoff > 0 && hi - lo + 1 <= cutoff) {
            insertion(a, lo, hi);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid, cutoff);
        sort(a, aux, mid + 1, hi, cutoff);
        if (a[mid].compareTo(a[mid + 1]) <= 0) {
            return;
        }
        merge(a, aux, lo, mid, hi);
    }

    private static void insertion(Comparable[] a, int lo, int hi) {
        for (int i = lo + 1; i <= hi; i++) {
            for (int j = i; j > lo && less(a[j], a[j - 1]); j--) {
                exch(a, j, j - 1);
            }
        }
    }

    private static boolean less(Comparable v, Comparable w) {
        return v.compareTo(w) < 0;
    }

    private static void exch(Comparable[] a, int i, int j) {
        Comparable temp = a[i];
        a[i] = a[j];
        a[j] = temp;
    }

    private static void merge(Comparable[] a, Comparable[] aux,
                              int lo, int mid, int hi) {
        for (int k = lo; k <= hi; k++) {
            aux[k] = a[k];
        }

        int i = lo, j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if (i > mid) {
                a[k] = aux[j++];
            } else if (j > hi) {
                a[k] = aux[i++];
            } else if (aux[j].compareTo(aux[i]) < 0) {
                a[k] = aux[j++];
            } else {
                a[k] = aux[i++];
            }
        }
    }
}
