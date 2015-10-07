package io.datawire;

import java.util.Arrays;

public class SlidingRate {
    private final int period;
    private final int[] counts;
    private final long[] tstamps;
    private int head;

    public SlidingRate() { this(10); }
    public SlidingRate(int period) {
        this.period = period;
        this.counts = new int[period];
        this.tstamps = new long[period];
        this.head = 0;
        Arrays.fill(counts, 0);
        Arrays.fill(tstamps, System.currentTimeMillis() - 1); // avoid div by zero at startup
    }

    public double rate(int count, long tstamp) {
        counts[head] = count;
        tstamps[head] = tstamp;
        if (++head == period) {
            head = 0;
        }
        return (count - counts[head]) / ( (tstamp - tstamps[head]) / 1000.0);
    }

}
