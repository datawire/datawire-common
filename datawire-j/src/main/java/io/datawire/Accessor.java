package io.datawire;

import org.apache.qpid.proton.engine.Extendable;
import org.apache.qpid.proton.engine.Record;

public interface Accessor<T> extends Record.Accessor<T> {
    public T get(Extendable e);
    public void set(Extendable e, T value);
}