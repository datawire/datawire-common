# Copyright (C) k736, inc. All Rights Reserved.
# Unauthorized copying or redistribution of this file is strictly prohibited.

from proton.handlers import CHandshaker
from .sampler import Sampler

class Agent:

    def __init__(self, delegate):
        self.__delegate = delegate
        self.sampler = Sampler(self.__delegate)
        self.handlers = [CHandshaker(), self.sampler]
