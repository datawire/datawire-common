package io.datawire;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.reactor.Reactor;

/**
 * A caching factory of {@link Sender} objects.
 * @author bozzo
 *
 */
public class Linker {

    private Map<Sender.Config, Sender> senders = new HashMap<Sender.Config, Sender>();
    public boolean started = false;
    public Reactor reactor;

    /**
     * Start all the already created {@link #sender()}s
     * @param reactor The reactor to start the senders on
     */
    public void start(Reactor reactor) {
        if (started) {
            return;
        }
        this.reactor = reactor;
        ArrayList<Sender> senders = new ArrayList<>(this.senders.values());
        started = true;
        for (Sender snd : senders) {
            snd.start(reactor);
        }
    }

    /**
     * Stop all the created senders
     * @param reactor
     */
    public void stop(Reactor reactor) {
        if (!started) {
            return;
        }
        if (this.reactor != reactor) {
            throw new IllegalArgumentException("Must use the same reactor as for start");
        }
        ArrayList<Sender> senders = new ArrayList<>(this.senders.values());
        started = false;
        for (Sender snd : senders) {
            snd.stop(reactor);
        }
    }

    /**
     * A {@link Sender.SenderBuilder} that always returns the same {@link Sender} for the same
     * {@link Sender.Config}
     * 
     * @author bozzo
     *
     */
    public class Builder extends Sender.SenderBuilder {
        Builder() {}

        /**
         * When a new {@link Sender} is created and the
         * {@link Linker#isStarted()} the sender will be also started.
         * 
         * @return
         */
        @Override
        public Sender create() {
            Sender.Config key = config();
            Sender ret = senders.get(key);
            if (ret == null) {
                ret = super.create();
                senders.put(key, ret);
                if (started)
                    ret.start(reactor);
            }
            return ret;
        }
    }

    /**
     * @return a {@link Builder} for a {@link Sender}
     */
    public Builder sender() {
        return new Builder();
    }

    /**
     * Return a Sender with the specified configuration
     * @param target Target address
     * @param handlers child handlers
     * @return A Sender
     */
    public Sender sender(String target, Handler...handlers) {
        return new Builder().withTarget(target).withHandlers(handlers).create();
    }

    /**
     * @return True if {@link #start(Reactor)} was called and {@link #stop(Reactor)} was not called.
     */
    public boolean isStarted() {
        return started;
    }

    /**
     * test helper
     * @return number of senders
     */
    public int sendersSize() {
        return senders.size();
    }

    /**
     * close all senders
     */
    public void close() {
        for (Sender snd : senders.values()) {
            snd.close();
        }
    }
}
