package io.datawire;

public class Counts {
    public static class Counters {
        private int incoming = 0;
        private int outgoing = 0;
        public int getIncoming() {
            return incoming;
        }
        public void setIncoming(int incoming) {
            this.incoming = incoming;
        }
        public int getOutgoing() {
            return outgoing;
        }
        public void setOutgoing(int outgoing) {
            this.outgoing = outgoing;
        }
    }
    public static final Counters app = new Counters();
    public static final Counters lib = new Counters();
}
