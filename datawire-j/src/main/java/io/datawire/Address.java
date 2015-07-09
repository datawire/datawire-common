package io.datawire;

public final class Address {
    private String text;
    private String network;
    private String host;
    private String port;
    
    public static Address parse(String text) {
        if (text == null) {
            return null;
        } else {
            return new Address(text);
        }
    }
    
    public Address(String text) {
        this.text = text;
        network = network(text);
        String[] hostport = hostport(network);
        host = hostport[0];
        port = hostport[1];
    }

    public static String network(String address) {
        if (address == null)
            return null;
        if (address.startsWith("//")) {
            return address.substring(2).split("/", 2)[0];
        }
        return null;
    }

    public static String[] hostport(String network) {
        if (network == null)
            return new String[2];
        if (network.contains(":")) {
            return network.split(":",2);
        } else {
            return new String[] {network, "5672"};
        }
    }

    public String getText() {
        return text;
    }

    public String getNetwork() {
        return network;
    }

    public String getHost() {
        return host;
    }

    public String getPort() {
        return port;
    }
    
    @Override
    public String toString() {
        return text;
    }
}
