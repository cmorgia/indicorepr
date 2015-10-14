from MaKaC.services.implementation.base import ParameterManager
from MaKaC.services.implementation.conference import ConferenceModifBase, ConferenceBase
from indico.util.fossilize import fossilize


class ConferenceUpdateLimits(ConferenceModifBase):

    def _checkParams(self):
        ConferenceModifBase._checkParams(self)
        pm = ParameterManager(self._params)
        self._limits = pm.extract("limits", pType=list, allowEmpty=False)

    def _getAnswer(self):
        for limit in self._limits:
            self._conf.setRegistrarLimits(limit['id'],limit)
        return True


class ConferenceGetLimits(ConferenceBase):

    def _checkParams(self):
        ConferenceBase._checkParams(self)

    def _getAnswer(self):
        return fossilize(self._conf.getRegistrarsLimits())


methodMap = {
    "update.limits": ConferenceUpdateLimits,
    "get.limits": ConferenceGetLimits
}