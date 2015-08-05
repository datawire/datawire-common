package io.datawire.examples;

import java.io.IOException;

import javax.inject.Inject;

import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.reactor.Reactor;

import com.github.rvesse.airline.Arguments;
import com.github.rvesse.airline.HelpOption;
import com.github.rvesse.airline.Option;
import com.github.rvesse.airline.examples.ExampleRunnable;

import io.datawire.Address;
import io.datawire.BaseDatawireHandler;
import io.datawire.Processor;
import io.datawire.Tether;

public class ServiceConsumer {
    private Tether tether;

    public void start(final Reactor reactor, final Handler handler) {
        String svcHost = new Address(address).getHost();
        String announce_address = 
                "//" + or(annHost, host, svcHost) +
                ":" + or(annPort, port);
        host = or(host, svcHost);
        tether = Tether.Builder().withDirectory(directory).withAddress(address).withRedirectTarget(announce_address).create();
        reactor.getHandler().add(new BaseDatawireHandler() {
            @Override
            public void onReactorInit(Event event) {
                try {
                    reactor.acceptor(host, Integer.valueOf(port), new Processor(handler));
                } catch (NumberFormatException | IOException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
                tether.start(reactor);
            }
        });
    }

    private String or(String...strings) {
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

}
