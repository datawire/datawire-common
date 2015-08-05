package io.datawire.examples;

import io.datawire.DatawireEvent;

import java.util.logging.Level;
import java.util.logging.Logger;

import com.github.rvesse.airline.Command;
import com.github.rvesse.airline.examples.ExampleExecutor;

@Command(name="printer", description="print messages received from address")
public class Printer extends BaseConsumer {
    @Override
    public void onMessage(DatawireEvent event) {
        System.out.println("Received message "+ event.getMessage());
    }

    public static void main(String[] args) {
        Logger.getGlobal().setLevel(Level.INFO);
        ExampleExecutor.executeSingleCommand(Printer.class, args);
    }
}
