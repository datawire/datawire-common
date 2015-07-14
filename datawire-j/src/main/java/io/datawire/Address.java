package io.datawire;

public final class Address {
    private String _text;
    private String _network;
    private String _host;
    private String _port;
    
    public static Address parse(String text) {
        if (text == null) {
            return null;
        } else {
            return new Address(text);
        }
    }
    
    public Address(String text) {
        this._text = text;
        _network = networkOfAddress(text);
        String[] hostport = hostportOfNetwork(_network);
        _host = hostport[0];
        _port = hostport[1];
    }

    public static String networkOfAddress(String address) {
        if (address == null)
            return null;
        if (address.startsWith("//")) {
            return address.substring(2).split("/", 2)[0];
        }
        return null;
    }

    public static String[] hostportOfNetwork(String network) {
        if (network == null)
            return new String[2];
        if (network.contains(":")) {
            return network.split(":",2);
        } else {
            return new String[] {network, "5672"};
        }
    }

    public String getText() {
        return _text;
    }

    public String getNetwork() {
        return _network;
    }

    public String getHost() {
        return _host;
    }

    public String getPort() {
        return _port;
    }
    
    @Override
    public String toString() {
        return _text;
    }
}
