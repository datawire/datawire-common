package io.datawire;

import static org.junit.Assert.*;
import static io.datawire.Range.range;
import static io.datawire.Dict.dict;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;

import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.message.Message;
import org.apache.qpid.proton.reactor.Reactor;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class SinkTest {
    private final Template template = new Template("test-%d");
    private Sink sink;
    private Server server;
    private Reactor reactor;

    @Before
    public void setUp() throws Exception {
        sink = new Sink();
        server = new Server(sink);
        reactor = Reactor.Factory.create();
        reactor.getHandler().add(server);
    }

    @After
    public void tearDown() throws Exception {
    }

    @Test
    public void testSender1() {
        testSender(1);
    }

    private void testSender(int count) {
        ArrayList<String> expected = new ArrayList<String>(count);
        for (int i = 0; i < count; i++) {
            expected.add(template.render(i));
        }
        server.setMaxConnections(1);
        Sender snd = Sender.Builder()
                .withTarget(server.address())
                .create();
        reactor.getHandler().add(snd);
        snd.start(reactor);
        for (String msg: expected) {
            snd.send(msg);
        }
        snd.close();
        reactor.run();
        assertEquals("messages received", expected, sink.getMessages());
    }

    @Test
    public void testSender4k() {
        testSender(4*1024);
    }
    
    private void testSampler(final int count, float frequency) {
        server.setMaxConnections(1);
        final ArrayList<String> expected = new ArrayList<String>(count);
        Timeout gen = new Timeout() {
            SimpleTag tag = new SimpleTag(0);
            int sent = 0;
            @Override
            public void onSample(DatawireEvent e) {
                String body = template.render(sent);
                expected.add(body);
                Message message = Message.Factory.create();
                message.setBody(new AmqpValue(body));
                DatawireUtils.send(e.getLink(), tag, message);
                sent += 1;
                if (sent >= count) {
                    e.getLink().close();
                    cancel();
                }
            }
        };
        Sender snd = Sender.Builder()
                .withTarget(server.address())
                .withHandlers(new Sampler(gen, frequency))
                .create();
        reactor.getHandler().add(snd);
        gen.setTimeout(reactor, 2000);
        snd.start(reactor);
        reactor.run();
        assertTrue("Sampling timed out", gen.isCancelled());
        assertEquals("Expected messages", expected, sink.getMessages());
    }
    
    @Test
    public void testSampler1M10F() {
        testSampler(1, 10);
    }
    
    @Test
    public void testSampler100M1000F() {
        testSampler(100, 1000);
    }
    
    @SuppressWarnings("serial")
    private void testLinker(int addressCount, int messageCount) {
        server.setMaxConnections(addressCount);
        Linker linker = new Linker();
        linker.start(reactor);
        for (int i : range(addressCount)) {
            for (int j: range(messageCount)) {
                Sender snd = linker.sender(server.address(i));
                assertEquals("sender per address", i + 1, linker.sendersSize());
                final int fi = i, fj = j;
                snd.send(dict("i", fi, "j", fj));
            }
        }
        linker.close();
        reactor.run();
        
        HashMap<Integer, ArrayList<Map<?, ?>>> by_addr = new HashMap<>();
        for (int i : range(addressCount)) {
            by_addr.put(i, new ArrayList<Map<?,?>>());
        }
        ArrayList<Map<?, ?>> messagesDicts = sink.getMessagesDicts();
        for (Map<?, ?> m : messagesDicts) {
            assertNotNull("did not receive a dict", m);
            by_addr.get(m.get("i")).add(m);
        }
        for (int i : range(addressCount)) {
            ArrayList<Map<?,?>> actual = by_addr.get(i);
            ArrayList<Map<?,?>> expected = new ArrayList<>(messageCount);
            for (int j : range(messageCount)) {
                expected.add(dict("i", i, "j", j));
            }
            assertEquals(String.format("Messages for address %d", i), expected, actual);
        }
        assertEquals("total messages", addressCount * messageCount, messagesDicts.size());
    }

    @Test public void testLinker1A1M()   { testLinker(1,1); }
    @Test public void testLinker2A1M()   { testLinker(2, 1); }
    @Test public void testLinker4A1M()   { testLinker(4, 1); }
    @Test public void testLinker16A1M()  { testLinker(16, 1); }
    @Test public void testLinker1A2M()   { testLinker(1, 2); }
    @Test public void testLinker1A4M()   { testLinker(1, 4); }
    @Test public void testLinker1A16M()  { testLinker(1, 16); }
    @Test public void testLinker2A2M()   { testLinker(2, 2); }
    @Test public void testLinker4A4M()   { testLinker(4, 4); }
    @Test public void testLinker16A16M() { testLinker(16, 16); }
}
