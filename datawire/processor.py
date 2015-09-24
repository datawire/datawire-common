# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from proton.handlers import CFlowController, CHandshaker
from .decoder import Decoder
from .impl import dual_impl

@dual_impl
class Processor:

    def __init__(self, delegate=None, window=1024):
        self.handlers = [CFlowController(window), CHandshaker(), Decoder()]
        if delegate is not None:
          self.handlers.append(delegate)
