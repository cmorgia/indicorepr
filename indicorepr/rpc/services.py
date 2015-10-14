from MaKaC.conference import ConferenceHolder
from MaKaC.services.implementation.base import ParameterManager, ServiceBase
from MaKaC.services.implementation.conference import ConferenceModifBase, ConferenceBase
from indico.util.fossilize import fossilize


class ConferenceUpdateLimits(ConferenceBase,ServiceBase):

    def _checkParams(self):
        ConferenceBase._checkParams(self)
        pm = ParameterManager(self._params)
        self._limits = pm.extract("limits", pType=list, allowEmpty=False)

    def _getAnswer(self):
        for limit in self._limits:
            self._conf.setRegistrarLimits(limit['id'],limit)
        return True


class ConferenceGetLimits(ConferenceBase,ServiceBase):

    def _getAnswer(self):
        return fossilize(self._conf.getRegistrarsLimits())


methodMap = {
    "update.limits": ConferenceUpdateLimits,
    "get.limits": ConferenceGetLimits
}