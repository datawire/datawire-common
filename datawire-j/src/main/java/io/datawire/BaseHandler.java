/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

/**
 * Default implementation of all {@link Handler} methods. Use this class as the
 * base for your handlers.
 * 
 * @author bozzo
 *
 */
public class BaseHandler extends org.apache.qpid.proton.engine.BaseHandler
        implements Handler {

    @Override
    public void onMessage(io.datawire.Event e) {
        onUnhandled(e);
    }

    @Override
    public void onSample(io.datawire.Event e) {
        onUnhandled(e);
    }

}
