/**
 * Copyright 2015 datawire. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package io.datawire;

/**
 * AMQP address
 *
 */
public final class Address {
    /**
     * Default port for datawire services
     */
    public static final String DEFAULT_PORT = "5672";
    private String _text;
    private String _network;
    private String _host;
    private String _port;

    /**
     * Parse the supplied text into an AMQP address object
     * 
     * @param text
     *            String representation of the address to parse. Can be
     *            {@literal null}
     * @return an {@link Address} instance or {@literal null} if
     *         {@literal null was supplied}
     */
    public static Address parse(String text) {
        if (text == null) {
            return null; // XXX: Would it not be better to return a static
                         // instance of Address(null)
        } else {
            return new Address(text);
        }
    }

    /**
     * An address instance containing parsed text
     * 
     * @param text
     *            Address to parse. When {@literal null} is supplied all
     *            instance getters will return null.
     */
    public Address(String text) {
        this._text = text;
        _network = networkOfAddress(text);
        String[] hostport = hostportOfNetwork(_network);
        _host = hostport[0];
        _port = hostport[1];
    }

    /**
     * For addresses of the form {@literal "//<network>][/...]"} returns the network address part
     * @param address
     *  the address to parse, can be {@literal null}
     * @return the extracted network address part or {@literal null} if the parameter is null or the address does not start with "//"
     */
    public static String networkOfAddress(String address) {
        if (address == null)
            return null;
        if (address.startsWith("//")) {
            return address.substring(2).split("/", 2)[0];
        }
        return null;
    }

    /**
     * split the network part of the address into host and port parts. If the address does not specify port the {@link Address#DEFAULT_PORT} is returned as port.
     * @param network Can be null
     * @return Array of two Strings, representing the tuple [host, port]. A {@literal null} network will result in an array of two {@literal null} strings.
     */
    public static String[] hostportOfNetwork(String network) {
        if (network == null)
            return new String[] { null, null };
        if (network.contains(":")) {
            return network.split(":", 2);
        } else {
            return new String[] { network, DEFAULT_PORT };
        }
    }

    /**
     * The whole address as supplied to the {@link Address#Address(String)} constructor
     * @return the address as supplied
     */
    public String getText() {
        return _text;
    }

    /**
     * The network part of an address of the form {@literal "//<network>[...]"}
     * @return The network part or {@literal null} if it's not a network address
     */
    public String getNetwork() {
        return _network;
    }

    /**
     * The host of the network part of an address of the form {@literal "//<network>[...]"}
     * @return The host or {@literal null} if it's not a network address
     */
    public String getHost() {
        return _host;
    }

    /**
     * The port of the network part of an address of the form {@literal "//<network>[...]"}
     * @return The port or {@literal null} if it's not a network address
     */
    public String getPort() {
        return _port;
    }

    @Override
    public String toString() {
        return _text;
    }
}
