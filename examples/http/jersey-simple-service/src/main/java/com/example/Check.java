package com.example;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

/**
 * Provides a health check for the service.
 */
@Path("liveness_check")
public class Check {

    /**
     * Perform a health check on the service.
     *
     * @return String Any result at all is interpreted as success.
     */
    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public String check() {
        // Here would be the place to perform any deeper checks, e.g.
        // a simple database query to ensure the backend is also up.
        return "OK";
    }
}
