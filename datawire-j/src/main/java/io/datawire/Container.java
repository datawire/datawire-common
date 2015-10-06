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

import java.util.AbstractCollection;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Iterator;
import java.util.NoSuchElementException;

public class Container extends BaseDatawireHandler {

    public static Collection<String> ancestors(String address) {
        if (address == null) {
            return Collections.singleton(address);
        } else {
            final String path = address.split("\\?", 2)[0];
            final ArrayList<Integer> cutlist = new ArrayList<>();
            int off = 0;
            for (String part : path.split("/", -1)) {
                int partend = off + part.length();
                if (partend > off || off == 0) {
                    cutlist.add(partend);
                }
                int partslash = partend + 1;
                cutlist.add(partslash);
                off = partslash;
            }
            return new AbstractCollection<String>() {

                @Override
                public Iterator<String> iterator() {
                    return new Iterator<String>() {
                        int last = cutlist.size() - 2; // last item does not have a trailing slash...
                        @Override
                        public boolean hasNext() {
                            return last >= 0;
                        }

                        @Override
                        public String next() {
                            if (!hasNext()) {
                                throw new NoSuchElementException();
                            }
                            return path.substring(0, cutlist.get(last--));
                        }

                        @Override
                        public void remove() {
                            throw new UnsupportedOperationException();
                        }
                    };
                }

                @Override
                public int size() {
                    return cutlist.size() - 1;
                }
            };
        }
    }

}
