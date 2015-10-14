from MaKaC.conference import Conference
from MaKaC.user import Avatar

Conference._registrarsLimits = {}


def decorateAddToRegistrars(fn):
    def new_funct(*args, **kwargs):
        ret = fn(*args, **kwargs)
        self = args[0]
        av = args[1]
        if isinstance(av, Avatar):
            self.getRegistrarLimits(av.getId())
        return ret

    return new_funct


Conference.addToRegistrars = decorateAddToRegistrars(Conference.addToRegistrars)


def decorateRemoveFromRegistrars(fn):
    def new_funct(*args, **kwargs):
        ret = fn(*args, **kwargs)
        self = args[0]
        av = args[1]
        if isinstance(av, Avatar):
            try:
                del self._registrarsLimits[av.getId()]
            except IndexError:
                pass
        return ret

    return new_funct


Conference.removeFromRegistrars = decorateRemoveFromRegistrars(Conference.removeFromRegistrars)


def getRegistrarsLimits(self):
    try:
        return self._registrarsLimits
    except AttributeError:
        self._registrarsLimits = {}
        return self._registrarsLimits

Conference.getRegistrarsLimits = getRegistrarsLimits


def removeRegistrarLimits(self, id):
    if self.getRegistrarLimits(id):
        del self._registrarsLimits[id]

Conference.removeRegistrarLimits = removeRegistrarLimits


def getRegistrarLimits(self, id):
    try:
        elem = self._registrarsLimits[id]
    except KeyError:
        elem = self._registrarsLimits[id] = {'threshold': '', 'affiliation': ''}
    return elem

Conference.getRegistrarLimits = getRegistrarLimits


def setRegistrarThreshold(self, id, threshold):
    elem = self.getRegistrarLimits(id)
    elem['threshold'] = threshold

Conference.setRegistrarThreshold=setRegistrarThreshold


def setRegistrarAffiliation(self, id, affiliation):
    elem = self.getRegistrarLimits(id)
    elem['affiliation'] = affiliation

Conference.setRegistrarAffiliation = setRegistrarAffiliation


def setRegistrarLimits(self, id, limits):
    self._registrarsLimits[id] = limits
    self.notifyModification()

Conference.setRegistrarLimits = setRegistrarLimits
