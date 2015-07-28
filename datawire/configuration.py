# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

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
