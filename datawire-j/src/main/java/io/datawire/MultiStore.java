package io.datawire;

import org.apache.qpid.proton.message.Message;

public interface MultiStore extends Store {
    public static class Factory {
        public static MultiStore create() { return null; }
    }
}
