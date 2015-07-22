# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from .impl import dual_impl

class Counters:
    incoming = 0
    outgoing = 0

@dual_impl
class Counts:
    app = Counters()
    lib = Counters()


app = Counts.app
lib = Counts.lib
