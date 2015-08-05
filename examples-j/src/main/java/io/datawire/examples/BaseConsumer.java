package io.datawire.examples;

import java.io.IOException;

import javax.inject.Inject;

import org.apache.qpid.proton.reactor.Reactor;

import io.datawire.BaseDatawireHandler;

import com.github.rvesse.airline.examples.ExampleRunnable;

public class BaseConsumer extends BaseDatawireHandler   implements ExampleRunnable {

    private Reactor reactor;
    @Inject
    private ServiceConsumer consumer = new ServiceConsumer();

    public BaseConsumer() {
        super();
    }

    @Override
    public int run() {
        try {
            reactor = Reactor.Factory.create();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            return -1;
        }
        try {
            consumer.start(reactor, this);
            reactor.run();
        } finally {
            reactor.stop();
        }
        return 0;
    }

}