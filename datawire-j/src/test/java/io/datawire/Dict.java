package io.datawire;

import java.util.HashMap;

public class Dict {
    public static HashMap<Object, Object> dict(Object...objects) {
        HashMap<Object,Object> ret = new HashMap<>();
        for (int i = 0; i < objects.length;) {
            Object key = objects[i++];
            Object value = i < objects.length ? objects[i++] : null;
            ret.put(key, value);
        }
        return ret;
    }
}
