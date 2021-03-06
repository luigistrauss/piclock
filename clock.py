#!/usr/bin/env python

import datetime
import time

from microdotphat import write_string, set_decimal, clear, show, set_brightness

set_brightness(0.1)

while True:
    clear()
    t = datetime.datetime.now()
    if t.second % 2 == 0:
        set_decimal(2, 1)
        set_decimal(4, 1)
    else:
        set_decimal(2, 0)
        set_decimal(4, 0)
    write_string(t.strftime('%H%M%S'), kerning=False)
    show()
    time.sleep(0.05)
