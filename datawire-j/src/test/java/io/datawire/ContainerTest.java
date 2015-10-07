package io.datawire;

import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.assertThat;
import static org.junit.matchers.JUnitMatchers.*;
import static org.hamcrest.CoreMatchers.*;

public class ContainerTest {
    private static final Logger log = Logger.getLogger(ContainerTest.class.getName());
    @Before
    public void setUp() throws Exception {
    }

    @After
    public void tearDown() throws Exception {
    }

    private List<String> ancestors(String path) {
        ArrayList<String> arrayList = new ArrayList<>(Container.ancestors(path));
        StringBuilder sb = new StringBuilder();
        sb.append("ancestor('").append(path).append("') -> [");
        String sep = "'";
        String end = "]";
        for (String a : arrayList) {
            sb.append(sep).append(a);
            sep = "', '";
            end = "']";
        }
        sb.append(end);
        log.info(sb.toString());
        return arrayList;
    }

    @Test
    public void testNone() {
        String nil = null;
        assertThat(ancestors(null), is(Arrays.asList(nil)));
    }

    @SuppressWarnings("serial")
    Map<String, List<String>> expected = new HashMap<String, List<String>>() {
        {
            put(""     , Arrays.asList(""));
            put("a"    , Arrays.asList("a"));
            put("a/"   , Arrays.asList("a/", "a"));
            put("a/b"  , Arrays.asList("a/b", "a/", "a"));
            put("/"    , Arrays.asList("/", ""));
            put("/a"   , Arrays.asList("/a", "/", ""));
            put("/a/"  , Arrays.asList("/a/", "/a", "/", ""));
            put("/a/b" , Arrays.asList("/a/b", "/a/", "/a", "/", ""));
            put("/a/b/", Arrays.asList("/a/b/", "/a/b", "/a/", "/a", "/", ""));
        }
    };

    private void checkExpectedVariants(String prefix, String postfix) {
        for (String base : expected.keySet()) {
            String path = prefix + base + postfix;
            assertThat("while checking \""+path+"\"", ancestors(path), is(expected.get(base)));
        }
    }

    @Test
    public void testPath() {
        checkExpectedVariants("", "");
    }

    @Test
    public void testPathParam() {
        checkExpectedVariants("", "?param=/value");
    }

    @Test
    public void testHostPath() {
        checkExpectedVariants("//host:12234", "");
    }
    
    @Test
    public void testHostPathParam() {
        checkExpectedVariants("//host:12234", "?param=/value");
    }
}
