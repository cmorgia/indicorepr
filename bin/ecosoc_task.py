from indico.modules.scheduler import Client
from dateutil import rrule
from indico.core.db import DBMgr
from indicorepr.tasks.ecosoc import ECOSOCListTask

dbi = DBMgr.getInstance()
c = Client()
pt = ECOSOCListTask(rrule.HOURLY)
c.enqueue(pt)
dbi.commit()
