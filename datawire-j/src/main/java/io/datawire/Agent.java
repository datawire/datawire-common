package io.datawire;

import java.util.HashMap;
import java.util.Map;

import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.amqp.messaging.Section;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.message.Message;
import org.apache.qpid.proton.reactor.Handshaker;

public class Agent extends BaseDatawireHandler {

    public static interface Stats extends Map<String, Object> {

    }

    public static interface Probe {
        public void sample(Stats stats);
    }

    private static final Probe NO_PROBE = new Probe() {
        @Override public void sample(Stats stats) { /* nothing */ }
    };

    private final Tether tether;
    private final Probe delegate;
    private final SlidingRate incoming;
    private final SlidingRate outgoing;
    private final SlidingRate incoming_lib;
    private final SlidingRate outgoing_lib;
    private final Sampler sampler;
    private Message message;

    public Agent(Tether tether, Probe delegate) {
        this.tether = tether;
        this.delegate = delegate != null ? delegate : NO_PROBE;
        this.incoming = new SlidingRate();
        this.outgoing = new SlidingRate();
        this.incoming_lib = new SlidingRate();
        this.outgoing_lib = new SlidingRate();
        this.sampler = new Sampler(this);
        this.message = Message.Factory.create();
        add(new Handshaker());
        add(sampler);
    }
    
    public Sampler getSampler() {
        return sampler;
    }

    private static class StatsImpl extends HashMap<String,Object> implements Stats {
        public void put(Object... pairs) {
            for (int i = 0; i < pairs.length; ) {
                String key = (String)pairs[i++];
                Object value = i < pairs.length ? pairs[i++] : null;
                put(key, value);
            }
        }
    }

    Stats sample() {
        StatsImpl stats = new StatsImpl();
        long tstamp = System.currentTimeMillis();
        stats.put(
            "address", tether.getAddress(),
            "agent", tether.getAgent(),
            "type", tether.getAgentType(),
            "timestamp", tstamp,
            "pid", DatawirePlatfomUtils.pid(),
            "rusage", DatawirePlatfomUtils.rusage(),
            "times", DatawirePlatfomUtils.times(),
            "command", DatawirePlatfomUtils.command(),
            "incoming_count", Counts.app.getIncoming(),
            "outgoing_count", Counts.app.getOutgoing(),
            "incoming_count_lib", Counts.lib.getIncoming(),
            "outgoing_count_lib", Counts.lib.getOutgoing(),
            "incoming_rate", incoming.rate(Counts.app.getIncoming(), tstamp),
            "outgoing_rate", outgoing.rate(Counts.app.getOutgoing(), tstamp),
            "incoming_rate_lib", incoming_lib.rate(Counts.lib.getIncoming(), tstamp),
            "outgoing_rate_lib", outgoing_lib.rate(Counts.lib.getOutgoing(), tstamp)
        );
        return stats;
    }

    @Override
    public void onSample(DatawireEvent e) {
        Stats stats = sample();
        delegate.sample(stats);
        message.setBody(new AmqpValue(stats));
        DatawireUtils.send(e.getSender(), message);
    }
}
