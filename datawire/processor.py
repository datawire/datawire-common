# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from proton.handlers import CFlowController, CHandshaker
from .decoder import Decoder

class Processor:

    def __init__(self, delegate=None, window=1024):
        if delegate is None:
            self.__delegate = self
        else:
            self.__delegate = delegate
        self.handlers = [CFlowController(window), CHandshaker(), Decoder(self.__delegate)]

    def on_unhandled(self, name, event):
        if self.__delegate is not self and event.connection:
            try:
                event.dispatch(self.__delegate)
            except:
                raise
