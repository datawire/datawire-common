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

import java.util.Iterator;
import java.util.NoSuchElementException;

public class Range {

    public static Iterable<Integer> range(final int from, final int to, final int step) {
        return new Iterable<Integer>() {

            @Override
            public Iterator<Integer> iterator() {
                return new Iterator<Integer>() {
                    int i = from;
                    @Override
                    public boolean hasNext() {
                        return i < to;
                    }

                    @Override
                    public Integer next() {
                        if (!hasNext())
                            throw new NoSuchElementException();
                        try {
                            return i;
                        } finally {
                            i += step;
                        }
                    }

                    @Override
                    public void remove() {
                        throw new UnsupportedOperationException();
                    }
                };
            }
        };
    }

    public static Iterable<Integer> range(final int from, final int to) {
        return range(from, to, 1);
    }

    public static Iterable<Integer> range(final int to) {
        return range(0, to);
    }

}
