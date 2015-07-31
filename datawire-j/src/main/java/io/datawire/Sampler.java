/**
 * Copyright (C) k736, inc. All Rights Reserved.
 * Unauthorized copying or redistribution of this file is strictly prohibited.
 */
package io.datawire;

import java.util.Iterator;

import org.apache.qpid.proton.engine.EndpointState;
import org.apache.qpid.proton.engine.Event;
import org.apache.qpid.proton.engine.Handler;
import org.apache.qpid.proton.engine.Link;

/**
 * Fixed interval recurring timer event for monitoring of {@link EndpointState#ACTIVE} {@link Link}.
 * 
 * @author bozzo
 *
 */
public class Sampler extends BaseDatawireHandler {

    private final org.apache.qpid.proton.engine.Handler delegate;
    private float frequency;

    private Event event;

    public Sampler() {
        this(null);
    }

    public Sampler(float frequency) {
        this(null, frequency);
    }

    public Sampler(org.apache.qpid.proton.engine.Handler _delegate) {
        this(_delegate, 1);
    }

    public Sampler(org.apache.qpid.proton.engine.Handler _delegate, float frequency) {
        this.delegate = _delegate != null ? _delegate : this;
        setFrequency(frequency);
    }

    @Override
    public void onLinkLocalOpen(Event event) {
        this.event = event.copy();
        sample();
    }

    private void sample() {
        Link link = event.getLink();
        if (link != null && link.getLocalState() == EndpointState.ACTIVE) {
            event.redispatch(DatawireEvent.Type.SAMPLE, delegate);
            event.getReactor().schedule(getInterval(), sampler);
        }
    }

    private int getInterval() {
        int interval = (int) (1000.0 / frequency);
        return Math.max(interval, 1);
    }

    public float getFrequency() {
        return frequency;
    }

    public void setFrequency(float frequency) {
        if (frequency < 0.000001)
            throw new IllegalArgumentException("Bad frequency");
        this.frequency = frequency;
    }

    private org.apache.qpid.proton.engine.Handler sampler = new org.apache.qpid.proton.engine.BaseHandler() {
        @Override
        public void onTimerTask(Event ignored) {
            sample();
        }
    };

}
