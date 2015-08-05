package io.datawire.examples;

import io.datawire.BaseDatawireHandler;
import io.datawire.Sender;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.inject.Inject;

import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.impl.StringUtils;
import org.apache.qpid.proton.reactor.Reactor;

import com.github.rvesse.airline.Arguments;
import com.github.rvesse.airline.Command;
import com.github.rvesse.airline.HelpOption;
import com.github.rvesse.airline.Option;
import com.github.rvesse.airline.examples.ExampleExecutor;
import com.github.rvesse.airline.examples.ExampleRunnable;

@Command(name="send", description="Send a message to the target")
public class Send extends BaseDatawireHandler implements ExampleRunnable {


    private Sender sender;
    private Reactor reactor;

    @Override
    public void onReactorInit(Event event) {
        sender.start(reactor);
        for (String message: args)
            sender.send(message);
        sender.close();
    }

    @Override
    public int run() {
        if (args == null) 
            args = Arrays.asList("Hello World!");
        try {
            sender = Sender.Builder().withTarget(address).create();
            reactor = Reactor.Factory.create();
            reactor.getHandler().add(this);
            reactor.run();
            return 0;
       } catch (IOException e) {
            e.printStackTrace();
            reactor.stop();
            return -1;
        }
    }

    @SuppressWarnings("unused")
    @Inject
    private HelpOption help;

    @Option(name={"--address"}, description="target address", required=true)
    private String address;

    @Arguments(description="message to send")
    private List<String> args;

    public static void main(String[] args) {
        Logger.getGlobal().setLevel(Level.INFO);
        ExampleExecutor.executeSingleCommand(Send.class, args);
    }
}