package io.datawire;

import org.apache.qpid.proton.engine.Extendable;
import org.apache.qpid.proton.engine.RecordAccessor;

public interface Accessor<T> extends RecordAccessor<T> {
    public T get(Extendable e);
    public void set(Extendable e, T value);
}