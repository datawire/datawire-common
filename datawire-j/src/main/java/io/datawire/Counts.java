/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

/**
 * Statistic counts for messages exchanged via datawire
 * @author bozzo
 *
 */
public class Counts {
    /**
     * Counters of incoming and outgoint messages
     * @author bozzo
     *
     */
    public static class Counters {
        private int incoming = 0;
        private int outgoing = 0;
        /**
         * 
         * @return
         */
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
