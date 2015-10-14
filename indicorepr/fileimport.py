import csv

from flask import request, flash
from MaKaC.authentication import AuthenticatorMgr
from MaKaC.errors import NoReportError
from MaKaC.registration import Registrant
from MaKaC.user import AvatarHolder, Avatar, LoginInfo

from MaKaC.webinterface import urlHandlers
from MaKaC.webinterface.rh.registrantsModif import RHRegistrantListModifAction
from MaKaC.webinterface.rh.registrationFormDisplay import RHRegistrationFormDisplayBaseCheckProtection, \
    RHRegistrationFormUserData


def decorateCheckParams(fn):
    def new_funct(self,params):
        fn(self,params)
        #self = args[0]
        #params = args[1]
        self._importCsv = params.has_key("importCsv")

    return new_funct


RHRegistrantListModifAction._checkParams = decorateCheckParams(RHRegistrantListModifAction._checkParams)


def decorateProcess(fn):
    def new_funct(*args, **kwargs):
        self = args[0]
        if self._importCsv:
            myfile = request.files['file']
            errors = self._import(myfile)
            if len(errors) > 0:
                str_errors = ', '.join(map(str, errors))
                flash(_("Rows {0} have not been successfully imported").format(str_errors), 'error')
            else:
                flash(_("All registrants have been successfully imported"), 'success')

            self._redirect(urlHandlers.UHConfModifRegistrantList.getURL(self._conf))
        else:
            return fn(*args, **kwargs)

    return new_funct


RHRegistrantListModifAction._process = decorateProcess(RHRegistrantListModifAction._process)


def _setAffiliation(self, registrant):
    # set same affiliation for registrant as registrar affiliation
    try:
        limit = self._conf.getRegistrarsLimits()[self.getAW().getUser().getId()]
        registrant._representationType['organizationRepresentative'] = limit['affiliation']
    except KeyError:
        return

RHRegistrantListModifAction._setAffiliation = _setAffiliation

def logimport(self, successfuls, unsuccessfuls):
    logInfo = {}
    logInfo["subject"] = _("Completed import procedure: {} success, {} failed").format(len(successfuls),
                                                                                       len(unsuccessfuls))
    logInfo["Success"] = successfuls
    logInfo["Unsuccess"] = unsuccessfuls
    self._conf.getLogHandler().logAction(logInfo, log.ModuleNames.REGISTRATION)

RHRegistrantListModifAction.logimport = logimport

def _processImportData(self, row):
    row["Email"] = row['Email'].lower()
    if "Password" not in row:
        row["Password"] = "indico"
    if "Government Representative" not in row:
        row["Government Representative"] = "No"
    if "Representation Type" in row and row["Representation Type"] == "Government":
        row["Representation Type"] = "Governments (UNCTAD Bodies)"
        row["Government Representative"] = "Yes"

RHRegistrantListModifAction._processImportData = _processImportData


def _import(self, file):
    # check Registration period
    import datetime
    import pytz
    utc = pytz.UTC
    startDate = self._conf.getRegistrationForm().getStartRegistrationDate()
    endDate = self._conf.getRegistrationForm().getEndRegistrationDate()
    current = datetime.datetime.now()
    current = utc.localize(current)

    if (current < startDate or current > endDate):
        raise NoReportError("Import registrants not authorized, outside registration period.")

    reader = csv.DictReader(file)
    i = 1
    errors = []

    successfuls = []
    unsuccessfuls = []

    for row in reader:
        try:
            # row['Email'] = row['Email'].lower()
            self._processImportData(row)
            matchedUsers = AvatarHolder().match({"email": row['Email']}, exact=1)
            if matchedUsers:
                user = matchedUsers[0]
            elif ('Account Creation' in row) and row['Account Creation'].lower() == 'yes':  # account creation
                avData = self._mapAvatar(row)
                user = Avatar(avData)
                user.activateAccount()
                login_info = LoginInfo(row['Login'], row['Password'])
                auth_mgr = AuthenticatorMgr()
                user_id = auth_mgr.createIdentity(login_info, user, "Local")
                auth_mgr.add(user_id)
                AvatarHolder().add(user)
            else:
                user = None

            if not (user):
                reg = Registrant()  # new registration
                self._conf.addRegistrant(reg, user)
            else:
                if user.isRegisteredInConf(self._conf):
                    reg = self._conf.getRegistrantsByEmail(user.getEmail())
                else:  # not registered, new registration
                    reg = Registrant()
                    reg.setAvatar(user)
                    self._conf.addRegistrant(reg, user)
                    user.addRegistrant(reg)

            regData = self._mapRegistrant(row)
            regData['import'] = 'import'
            reg.setValues(regData, user)
            self._setAffiliation(reg)
            successfuls.append(reg.getFullName())
        except Exception:
            errors.append(i)
            unsuccessfuls.append(
                row["Surname"] + ", " + row["First Name"])  # exception : reg or user might not be defined yet
        finally:
            i += 1
    self.logimport(successfuls, unsuccessfuls)
    return errors

RHRegistrantListModifAction._import = _import


def _checkParams(self, params):
    RHRegistrationFormDisplayBaseCheckProtection._checkParams(self,params)
    self._existingId = params.get('existingId',None)
    if self._existingId=='None':
        self._existingId = None
    if 'regId' in params:
        self._existingId = self._conf.getRegistrantById(params.get('regId')).getAvatar().getId()
RHRegistrationFormUserData._checkParams = _checkParams