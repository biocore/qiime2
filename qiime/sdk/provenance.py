# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import time
import uuid


# TODO figure out the public API and make this a safe class
class Provenance:

    def __init__(self, job_uuid, artifact_uuids, parameters,
                 workflow_template_reference):
        self.start_time = time.time()
        self.job_uuid = job_uuid
        self.artifact_uuids = artifact_uuids
        self.parameters = parameters
        self.workflow_template_reference = workflow_template_reference
