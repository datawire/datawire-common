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
