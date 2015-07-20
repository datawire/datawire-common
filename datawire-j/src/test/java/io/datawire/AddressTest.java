package io.datawire;

import static org.junit.Assert.*;

import org.junit.Test;

public class AddressTest {

    @Test
    public void testAddressNone() {
        assertNull(new Address(null).getHost());
        assertNull(new Address(null).getPort());
    }

    @Test
    public void testParseNone() {
        assertNull(Address.parse(null));
    }

    public void _testParse(String text, String host, String port) {
        Address addr = Address.parse(text);
        assertEquals(host,  addr.getHost());
        assertEquals(port, addr.getPort());
    }

    @Test
    public void testHost() {
       _testParse("//host",  "host",  "5672");
    }

    @Test
    public void testHostPort() {
       _testParse("//host:5673",  "host",  "5673");
    }

    @Test
    public void testHostPortStuff() {
        _testParse("//host:5673/stuff", "host", "5673");
    }

    @Test
    public void testHostStuff() {
        _testParse("//host/stuff", "host", "5672");
    }
}
