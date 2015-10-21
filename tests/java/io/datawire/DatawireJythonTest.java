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
package io.datawire;

import java.io.File;
import java.io.FileNotFoundException;

import org.apache.qpid.proton.JythonTest;


public class DatawireJythonTest extends JythonTest {
    /* System properties expected to be defined in test/pom.xml */
    private static final String DATAWIRE_JYTHON_BINDING = "datawireJythonBinding";
    private static final String DATAWIRE_JYTHON_SHIM = "datawireJythonShim";
    
    @Override
    protected void extendPath(JythonTest.PathBuilder pathBuilder) throws Exception {
        pathBuilder.append(getDatawireBinding()).append(getDatawireShim());
        super.extendPath(pathBuilder);
    }
    private String getDatawireBinding() throws FileNotFoundException
    {
        String str = getNonNullSystemProperty(DATAWIRE_JYTHON_BINDING, "System property '%s' must provide the location of the datawire python binding");
        File file = new File(str);
        if (!file.isDirectory())
        {
            throw new FileNotFoundException("Binding location '" + file + "' should be a directory.");
        }
        return file.getAbsolutePath();
    }
    private String getDatawireShim() throws FileNotFoundException
    {
        String str = getNonNullSystemProperty(DATAWIRE_JYTHON_SHIM, "System property '%s' must provide the location of the datawire jython shim");
        File file = new File(str);
        if (!file.isDirectory())
        {
            throw new FileNotFoundException("Shim location '" + file + "' should be a directory.");
        }
        return file.getAbsolutePath();
    }


}
