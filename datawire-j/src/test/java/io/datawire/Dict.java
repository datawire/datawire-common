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
