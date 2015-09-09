package io.datawire;

import java.util.Iterator;
import java.util.NoSuchElementException;

public class Range {

    public static Iterable<Integer> range(final int from, final int to, final int step) {
        return new Iterable<Integer>() {

            @Override
            public Iterator<Integer> iterator() {
                return new Iterator<Integer>() {
                    int i = from;
                    @Override
                    public boolean hasNext() {
                        return i < to;
                    }

                    @Override
                    public Integer next() {
                        if (!hasNext())
                            throw new NoSuchElementException();
                        try {
                            return i;
                        } finally {
                            i += step;
                        }
                    }

                    @Override
                    public void remove() {
                        throw new UnsupportedOperationException();
                    }
                };
            }
        };
    }

    public static Iterable<Integer> range(final int from, final int to) {
        return range(from, to, 1);
    }

    public static Iterable<Integer> range(final int to) {
        return range(0, to);
    }

}
