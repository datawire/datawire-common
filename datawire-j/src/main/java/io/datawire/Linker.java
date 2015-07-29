package io.datawire;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import org.apache.qpid.proton.reactor.Reactor;

public class Linker {

    private Map<Sender.Config, Sender> senders = new HashMap<Sender.Config, Sender>();
    public boolean started = false;
    public Reactor reactor;
    
    public void start(Reactor reactor) {
        this.reactor = reactor;
        ArrayList<Sender> senders = new ArrayList<>(this.senders.values());
        started = true;
        for (Sender snd : senders) {
            snd.start(reactor);
        }
    }
    
    public void stop(Reactor reactor) {
        if (this.reactor != reactor) {
            throw new IllegalArgumentException("Must use the same reactor as for start");
        }
        ArrayList<Sender> senders = new ArrayList<>(this.senders.values());
        started = false;
        for (Sender snd : senders) {
            snd.stop(reactor);
        }
    }
    
    public class Builder extends Sender.Builder {
        Builder() {}
        @Override
        public Sender create() {
            Sender.Config key = getConfig();
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
    
    public Builder sender() {
        return new Builder();
    }
    
    public Sender sender(String target, Handler...handlers) {
        return new Builder().setTarget(target).addHandlers(handlers).create();
    }
}
