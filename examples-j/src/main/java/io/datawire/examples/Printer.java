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
