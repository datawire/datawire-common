package io.datawire;

import static org.junit.Assert.*;

import org.apache.qpid.proton.reactor.Reactor;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class SourceTest {
    
    public static class Counter extends BaseDatawireHandler {
        private final Template template;
        private final int count;
        public Counter(Template template, int count) {
            this.template = template;
            this.count = count;
        }
        public boolean openEvent = false;
        private int received = 0;
        private Receiver receiver;
        public void onLinkRemoteOpen(org.apache.qpid.proton.engine.Event e) {
            openEvent = true;
        }
        @Override
        public void onMessage(DatawireEvent e) {
            String actual = DatawireUtils.stringify(e.getMessage().getBody());
            assertEquals("unexpected message", template.render(received), actual);
            received += 1;
            if (received == count) {
                receiver.stop(e.getReactor());
            }
                
        }
        public void setReceiver(Receiver rcv) {
            this.receiver = rcv;
        }

    }

    private Template template = new Template("test-%d");
    private Source source;
    private Server server;
    private Reactor reactor;

    @Before
    public void setUp() throws Exception {
        source = new Source(template);
        server = new Server(source);
        reactor = Reactor.Factory.create();
        reactor.getHandler().add(server);
    }

    @After
    public void tearDown() throws Exception {
    }

    public void testReceiver(int count) {
        server.setMaxConnections(1);
        source.setLimit(count);
        Counter counter = new Counter(template, count);
        Receiver rcv = Receiver.Builder()
                .withSource(String.format("//localhost:%s", Server.PORT))
                .withHandlers(new Processor(counter))
                .create();
        counter.setReceiver(rcv);
        reactor.getHandler().add(rcv);
        rcv.start(reactor);
        reactor.run();
        assertEquals("Number of messages received", count, counter.received);
        assertTrue("open event", counter.openEvent);
    }

    
    @Test
    public void testReceiver1() {
        testReceiver(1);
    }
    
    @Test
    public void testReceiver150() {
        testReceiver(150);
    }
}
