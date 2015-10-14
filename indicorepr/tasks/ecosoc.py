# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from datetime import timedelta

from indico.core.db import DBMgr
from indico.modules.scheduler.tasks.periodic import PeriodicTask
from indicorepr.ecosoclist import ECOSOCList

class ECOSOCListTask(PeriodicTask):

    def run(self):
        dbi = DBMgr.getInstance()
        logger = self.getLogger()

        logger.info("ECOSOC list download task started")
        try:
            ECOSOCList.getInstance().update()
            logger.info("ECOSOC list download finished, persisting....")
            dbi.commit()
            logger.info("ECOSOC list download finished, persisted")
        except Exception as e:
            logger.exception("ECOSOC list download exception '{}'".format(e))
