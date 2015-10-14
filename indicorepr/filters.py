from MaKaC.common import filters
from MaKaC.webinterface.common.regFilters import RegFilterCrit
from MaKaC.webinterface.rh.registrantsModif import RHRegistrantListModif


def _getRegistrarAffiliation(self):
    # get the limit affiliation of the registrar
    try:
        if self.getAW().getUser():
            limit = self._conf.getRegistrarsLimits()[self.getAW().getUser().getId()]
            affiliation = limit['affiliation']
            return affiliation
        else:
            return ''
    except KeyError:
        return ''


RHRegistrantListModif._getRegistrarAffiliation = _getRegistrarAffiliation

def decorateBuildFilteringCriteria(fn):
    def new_funct(*args, **kwargs):
        self = args[0]
        sessionData = args[1]
        # add registrant filter
        sessionData['registrant'] = self._getRegistrarAffiliation()
        ret = fn(*args, **kwargs)
        return ret

    return new_funct
RHRegistrantListModif._buildFilteringCriteria = decorateBuildFilteringCriteria(RHRegistrantListModif._buildFilteringCriteria)


class RegistrantFilterField(filters.FilterField):
    """
    Filter used for filtering the registrants for Registrar linked to a specific affiliation.
    """
    _id = "registrant"

    def satisfies(self, reg):
        """
        OK if registrant affiliation is same as registrar affiliation.
        """
        ### If no value, there is no need for filtering
        if self.getValues()==['']:
            return True
        affiliation = self.getValues()[0]
        return True if (affiliation == reg.getRepresentationType()["organizationRepresentative"]) else False


RegFilterCrit._availableFields[RegistrantFilterField.getId()]=RegistrantFilterField
