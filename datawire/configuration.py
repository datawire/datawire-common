# Copyright 2015 datawire. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, sys
from cStringIO import StringIO
from ConfigParser import SafeConfigParser as ConfigParser


class Configuration(object):

    def __init__(self, default_config=None):
        self.default_dirs = ["/etc/datawire", os.path.expanduser("~/.datawire")]
        self.filenames = ["/etc/datawire/datawire.conf", os.path.expanduser("~/.datawire/config")]
        self.parsed_filenames = None
        self.default_config = default_config

    def add_file_relative(self, filename):
        for path in self.default_dirs:
            self.filenames.append(os.path.join(path, filename))

    def add_file_absolute(self, filename):
        self.filenames.append(filename)

    def parse(self, *scp_args):
        parser = ConfigParser(*scp_args)
        if self.default_config is not None:
            parser.readfp(StringIO(self.default_config))
        self.parsed_filenames = parser.read(self.filenames)
        return parser

    def exit_with_config_error(self, message):
        sys.stderr.write(message + "\n")
        sys.exit(78)  # EX_CONFIG = 78 according to sysexits.h
