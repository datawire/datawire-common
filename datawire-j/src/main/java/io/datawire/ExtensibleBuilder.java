package io.datawire;

public abstract class ExtensibleBuilder<S, C, B extends ExtensibleBuilder<S,C,B>> {
    protected abstract C config();
    protected abstract B self();
    public abstract S create();
}
