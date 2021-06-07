#!/usr/bin/env python
# encoding: utf-8
"""
test_logging.py

Created by Patrick Shaner on 2021-05-14

Copyright (c) 2021 Patrick Shaner, All rights reserved
THE INFORMATION CONTAINED HEREIN IS PROPRIETARY AND CONFIDENTIAL

Created to unit test the functionality of logging utility.

Version 2021-05-14:
    Initial addition to data-lake project
    Added for centralized logging functionality
"""
import os

import pytest

from custom_logger import StructLogs



def test_subscription_logging():
    import time
    log = StructLogs(team="test", module="subscribe.log")
    log.info("Test Info message")
    log.debug("Test debug")
    log.error("Test Error")
    log.warning("Test Warning")
    log.critical("Test Critical")
    log.exception("Test Exception")
    log.exception("Test Exception", destination="data_steward")

