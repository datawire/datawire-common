package io.datawire;

import org.apache.qpid.proton.message.Message;

/**
 * TBD: drop this, it's just a store, except for ...
 * 
 * Note: MultiStore preserves only partial ordering, per message address as specified in {@link Store#put(Message, String)}
 */
public interface MultiStore extends Store {
    public static class Factory {
        public static MultiStore create() { return null; }
    }
}
