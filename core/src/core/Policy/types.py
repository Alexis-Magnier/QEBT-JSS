#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import NewType

PolicyID = NewType("PolicyID", int)
INVALID_POLICY_ID: PolicyID = -1