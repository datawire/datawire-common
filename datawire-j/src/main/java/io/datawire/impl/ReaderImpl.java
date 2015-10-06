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
package io.datawire.impl;

import org.apache.qpid.proton.message.Message;

import io.datawire.Entry;
import io.datawire.Reader;
import io.datawire.Store;
import io.datawire.StoreImpl;

public class ReaderImpl implements Reader {
    private final StoreImpl store;
    private final String address;
    private int serial;

    public ReaderImpl(StoreImpl store, String address) {
        this.store = store;
        this.address = address;
        this.serial = store.min();
    }

    @Override
    public String getAddress() {
        return address;
    }

    @Override
    public Entry next() {
        Entry result = null;
        for (int max = store.max(); serial < max;) {
            Entry temp = store.get(serial);
            serial += 1;
            if (!temp.isDeleted()) {
                result = temp;
                break;
            }
        }
        return result;
    }

    @Override
    public boolean more() {
        return serial < store.max();
    }

    @Override
    public void close() {
        store.close(this);
    }

    public int getSerial() {
        return serial;
    }

}
