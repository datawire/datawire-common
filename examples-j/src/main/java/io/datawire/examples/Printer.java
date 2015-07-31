package io.datawire.examples;

import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.inject.Inject;

import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.reactor.Reactor;

import io.datawire.Address;
import io.datawire.BaseHandler;
import io.datawire.DatawireEvent;
import io.datawire.Processor;
import io.datawire.Tether;

import com.github.rvesse.airline.Arguments;
import com.github.rvesse.airline.Command;
import com.github.rvesse.airline.HelpOption;
import com.github.rvesse.airline.Option;
import com.github.rvesse.airline.examples.ExampleExecutor;
import com.github.rvesse.airline.examples.ExampleRunnable;

@Command(name="printer", description="print messages received from address")
public class Printer extends BaseHandler implements ExampleRunnable {
    private Reactor reactor;
    private Tether tether;
    @Override
    public int run() {
        try {
            String svcHost = new Address(address).getHost();
            String announce_address = 
                    "//" + or(annHost, host, svcHost) +
                    ":" + or(annPort, port);
            host = or(host, svcHost);
            tether = Tether.Builder().withDirectory(directory).withAddress(address).withRedirectTarget(announce_address).create();
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
    
    @Override
    public void onReactorInit(Event event) {
        try {
            reactor.acceptor(host, Integer.valueOf(port), new Processor(this));
        } catch (NumberFormatException | IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        tether.start(reactor);
    }
    
    @Override
    public void onMessage(DatawireEvent event) { // XXX: imho this is ugly and confusing DatawireEvent would be nicer
        System.out.println("Received message "+ event.getMessage());
    }

    String or(String...strings) {
        for(String s : strings)
            if (s != null)
                return s;
        return null;
    }

    @SuppressWarnings("unused")
    @Inject
    private HelpOption help;

    @Option(name={"-d", "--directory"}, description="datawire directory")
    private String directory;

    @Option(name={"-n", "--host"}, description="hostName binding")
    private String host;

    @Option(name={"-p", "--port"}, description="hostName binding")
    private String port = "5678";

    @Option(name={"--ann-host"}, description="announced hostname (EC2)")
    private String annHost;

    @Option(name={"--ann-port"}, description="announced port (EC2)")
    private String annPort;

    @Arguments(description="service address", arity=1, required=true)
    private String address;

    public static void main(String[] args) {
        Logger.getGlobal().setLevel(Level.INFO);
        ExampleExecutor.executeSingleCommand(Printer.class, args);
    }

}
