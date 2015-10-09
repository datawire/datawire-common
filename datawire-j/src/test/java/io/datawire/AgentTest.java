package io.datawire;

import static org.junit.Assert.*;

import java.util.Map;
import java.util.logging.Logger;

import io.datawire.Agent.Stats;

import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.reactor.Reactor;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestName;

public class AgentTest {
    private static final Logger log = Logger.getLogger(AgentTest.class.getName());
    private Agent agent;
    private Server server;
    private Reactor reactor;
    int samples;
    @Rule
    public TestName name = new TestName();

    @Before
    public void setUp() throws Exception {
        Tether fakeTether = Tether.Builder().withAddress(name.getMethodName()).create();
        agent = new Agent(fakeTether, sample);
        server = new Server(agent);
        reactor = Reactor.Factory.create();
        reactor.getHandler().add(server);
        samples = 0;
    }

    @After
    public void tearDown() throws Exception {
    }

    private Agent.Probe sample = new Agent.Probe() {
        @Override
        public void sample(Stats stats) {
            stats.put("samples", samples);
            samples += 1;
        }
    };

    private void testAgent(final int count, float frequency) {
        server.setMaxConnections(1);
        agent.getSampler().setFrequency(frequency);
        final Receiver receiver = Receiver.Builder().withSource(server.address()).create();;
        class Counter extends Timeout {
            public boolean openEvent = false;
            private int received = 0;
            public void onTimerTask(org.apache.qpid.proton.engine.Event e) {
                receiver.stop(e.getReactor());
            }
            @Override
            public void onMessage(DatawireEvent e) {
                @SuppressWarnings("unchecked")
                Map<String,Object> m = ((Map<String,Object>)((AmqpValue)e.getMessage().getBody()).getValue());
                log.info("Got " + m.toString());
                assertEquals("unexpected sample count", m.get("samples"), received);
                received += 1;
                if (received == count) {
                    receiver.stop(e.getReactor());
                    cancel();
                }
            }
        }
        Counter counter = new Counter();
        receiver.add(new Processor(counter));
        receiver.start(reactor);
        counter.setTimeout(reactor, 20000);
        reactor.run();
        assertTrue("Sampling timed out", counter.isCancelled());

    }

    @Test
    public void testAgent1M10F() {
        testAgent(1,10);
    }

    @Test
    public void testAgent10M100F() {
        testAgent(10,100);
    }
}
