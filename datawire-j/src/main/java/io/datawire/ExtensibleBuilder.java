package io.datawire;

/**
 * Base class for an extensible builder pattern
 * @param <S> The type being constructed
 * @param <C> The configuration object
 * @param <B> The builder
 */
public abstract class ExtensibleBuilder<S, C, B extends ExtensibleBuilder<S,C,B>> {
    protected abstract C config();
    protected abstract B self();
    public abstract S create();
}
