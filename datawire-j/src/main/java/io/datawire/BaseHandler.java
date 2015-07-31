/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

/**
 * Default implementation of all {@link DatawireHandler} methods. Use this class as the
 * base for your handlers.
 * 
 * @author bozzo
 *
 */
public class BaseHandler extends org.apache.qpid.proton.engine.BaseHandler
        implements DatawireHandler {

    @Override
    public void onMessage(DatawireEvent e) {
        onUnhandled(e);
    }

    @Override
    public void onSample(DatawireEvent e) {
        onUnhandled(e);
    }

    @Override
    public void onDrained(DatawireEvent e) {
        onUnhandled(e);
    }

}
