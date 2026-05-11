#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import NewType

JobID = NewType("JobID", int)
INVALID_JOB_ID: JobID = -1

SequenceID = NewType("SequenceID", int)
INVALID_SEQUENCE_ID: SequenceID = -1

TaskID = NewType("TaskID", int)
INVALID_TASK_ID: TaskID = -1

PrecedenceMapID = NewType("PrecedenceMapID", int)
INVALID_PRECEDENCE_MAP_ID: PrecedenceMapID = -1

PolicyID = NewType("PolicyID", int)
INVALID_POLICY_ID: PolicyID = -1