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

from MaKaC.services.implementation.base import ServiceBase
from indicorepr.ecosoclist import ECOSOCList


class VerifyStatus(ServiceBase):

    def _checkParams(self):
        ServiceBase._checkParams(self)
        self._organization = self._params['org']

    def _getAnswer(self):
        try:
            entry = ECOSOCList.getInstance().getStatus(self._organization)
            status = entry['status']
            return {"status": status }
        except IndexError:
            return {"status": None, "error": "Organisation not found"}
        except Exception as e:
            return {"status": None, "error": "Unable to query iCSO"}


class NamesList(ServiceBase):

    def _checkParams(self):
        ServiceBase._checkParams(self)
        self._query = self._params['query'] if 'query' in self._params else None
        self._full = self._params['full'] if 'full' in self._params else None

    def _getAnswer(self):
        try:
            names = ECOSOCList.getInstance().getNames(self._query,self._full)
            #names = names if len(names)<30 else names[0:30]
            return {"suggestions": names }
        except Exception as e:
            return {"status": None, "error": "Unable to query iCSO"}

methodMap = {
    "verify": VerifyStatus,
    "nameslist": NamesList
}
