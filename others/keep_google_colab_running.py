#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pynput.mouse import Button, Controller
import time
import random

mouse = Controller()

while True:
    t = random.randint(10, 60)
    mouse.click(Button.left, 1)
    print("Waiting {} sec".format(t))
    time.sleep(t)
