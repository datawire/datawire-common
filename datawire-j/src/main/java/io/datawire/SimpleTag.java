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

import java.nio.charset.Charset;

import org.apache.qpid.proton.engine.Delivery;

/**
 * A generator for {@link Delivery} tags. The tag is UTF8 encoded string
 * representation of an integer counter
 *
 */
public class SimpleTag implements Tag {
    private static final Charset UTF8 = Charset.forName("UTF-8");
    private int tag;

    /**
     * @param tag initial value to generate
     */
    public SimpleTag(int tag) {
        this.tag = tag;
    }

    @Override
    public byte[] deliveryTag() {
        return String.valueOf(tag++).getBytes(UTF8);
    }
}