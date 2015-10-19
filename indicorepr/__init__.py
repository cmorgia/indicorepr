# coding=utf-8
import os
from webassets import Bundle
from MaKaC.registration import GeneralSectionForm, GeneralField, FieldInputs
from MaKaC.webinterface.pages.registrants import WPRegistrantModification
from MaKaC.webinterface.pages.registrationForm import WPRegistrationFormDisplay, WPRegistrationFormModify, \
    WPConfModifRegFormPreview, WPRegistrationForm
from MaKaC.webinterface.rh.conferenceBase import RHConferenceBase
from indico.core.fossils.registration import IRegFormGeneralFieldFossil, IRegFormRadioGroupInputFieldFossil
import indicorepr.filters
import indicorepr.fileimport
import indicorepr.conference
from MaKaC.webinterface.pages.conferences import WPConfModifAC

from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint
from indico.core import signals
from MaKaC.services.interface.rpc.handlers import endpointMap, importModule
from indicorepr.reprfields import DynamicDropdownInput
import json

blueprint = IndicoPluginBlueprint('indicorepr', __name__)


class IndicoRepresentationPlugin(IndicoPlugin):
    """Indico Representation Plugin

    """
    configurable = False

    def init(self):
        super(IndicoRepresentationPlugin, self).init()
        #inputs = FieldInputs.getAvailableInputs()
        #inputs[DynamicDropdownInput.getId()] = DynamicDropdownInput
        taggedValue  = IRegFormGeneralFieldFossil.get('getValues').getTaggedValue('result')
        taggedValue["indicorepr.reprfields.DynamicDropdownInput"]=IRegFormRadioGroupInputFieldFossil

        blueprint.add_url_rule('/event/<confId>/reprtypes','reprtypes-read', RHRepresentationTypes, methods=('GET',))

        pages = [
            WPRegistrationFormDisplay,
            WPRegistrationFormModify,
            WPConfModifRegFormPreview,
            WPRegistrationForm,
            WPRegistrantModification]
        for page in pages:
            self.inject_js('indicorepr_js',page)
            self.inject_css('indicorepr_css',page)

        pages = [WPConfModifAC]
        for page in pages:
            self.inject_js('indicoaffiliation_js', page)
            self.inject_css('indicoaffiliation_css', page)

        endpointMap["affiliation"]=importModule("indicorepr.rpc.services")
        endpointMap["ecosoc"]=importModule("indicorepr.rpc.ecosoc")
        self.connect(signals.event.created,self.conf_created)

    def register_assets(self):
        self.register_js_bundle('indicorepr_js', 'js/indicorepr.js')
        self.register_css_bundle('indicorepr_css', 'css/indicorepr.css')
        self.register_js_bundle('indicoaffiliation_js', 'js/lib/typeahead.js','js/lib/hogan-3.0.2.js','js/indicoaffiliation.js')
        self.register_css_bundle('indicoaffiliation_css', 'css/indicoaffiliation.css','css/typeahead.css')
        self.register_tpl_bundle('dynamic-dropdown.tpl.html','tpls/dynamic-dropdown.tpl.html')

    def register_tpl_bundle(self, name, *files):
        def noop(_in, out, **kw):
            out.write(_in.read())
        bundle = Bundle(*files, filters=(noop,), output='tpls/{}'.format(name))
        fileName = bundle.resolve_output(self.assets)
        if os.path.isfile(fileName):
            os.remove(fileName)
        bundle.build(self.assets,force=False,disable_cache=True)
        self.assets.register(name, bundle)

    def get_blueprints(self):
        return blueprint

    def conf_created(self,conf,parent):
        _sectionHeader = {}
        _sectionHeader["title"] = "Representation"
        _sectionHeader["description"] = "Description"
        regForm = conf.getRegistrationForm()
        pos = next((i for i, f in enumerate(regForm.getSortedForms()) if not f.isEnabled()), None)
        section = GeneralSectionForm(regForm, data=_sectionHeader)
        section.directives = "nd-my-section" #to rename nd-representation-section

        govt = {
            "radioitems":[
                {"id":"isNew","caption":"No"},
                {"id":"isNew","caption":"Yes"}
            ],
            "input":"radio",
            "disabled":False,
            "caption":"Government Representative",
            "inputType":"dynamic-dropdown",
            "mandatory": True,
            "defaultItem": "No"
        }

        field = GeneralField(section, data=govt)
        field._directives = "nd-dynamic-dropdown-field"
        field.directives = {
            "ng-model":"representationType.grmodel",
            "ng-options":"gr for (gr,reptypes) in representationTypes"
        }
        pos = next((i for i, f in enumerate(section.getSortedFields()) if f.isDisabled()), None)
        section.addToSortedFields(field, i=pos)

        others = {
            "radioitems":[],
            "input":"radio",
            "disabled":False,
            "inputType":"dynamic-dropdown"
        }

        captions = [
            (
                'Country Representative', True, {
                    "ng-show": "representationType.grmodel==representationTypes['Yes']",
                    "ng-model":"representationType.ctrymodel",
                    "ng-options":"country for (country,name) in countryList"
                }
             ),
            (
                'Representation Type', True, {
                    "ng-model":"representationType.rtmodel",
                    "ng-options":"reptype for (reptype,repsubtypes) in representationType.grmodel"
                }
            ),
            (
                'Rep. Sub Type', True, {
                    "ng-model":"representationType.rstmodel",
                    "ng-options":"repsubtype for (repsubtype,empty) in representationType.rtmodel"
                }
            ),
            (
                'Contact Type', True, {
                    "ng-model":"representationType.ctmodel",
                    "ng-options":"contact for (contact,empty) in contactTypes"
                }
            ),
            (
                'Organization Representative', False, {
                    "ng-model":"representationType.orgmodel",
                    "ng-options":"organization for (organization,code) in organizationList"
                }
            )
        ]
        for caption,mandatory,directives in captions:
            others["caption"]=caption
            others["mandatory"]=mandatory
            field = GeneralField(section, data=others)
            field.directives = directives
            pos = next((i for i, f in enumerate(section.getSortedFields()) if f.isDisabled()), None)
            section.addToSortedFields(field, i=pos)

        regForm.addGeneralSectionForm(section, preserveTitle=True, )

        print "Section ID is %s" % section.getId()


class RHRepresentationTypes(RHConferenceBase):
    endpoint = 'reprtypes-read'

    def _checkParams(self, params):
        RHConferenceBase._checkParams(self, params)

    @staticmethod
    def _getCountryList():
        from MaKaC.webinterface.common.countries import CountryHolder
        list = {}
        for country in CountryHolder().getCountryList():
            list[country]= country
        return list

    @staticmethod
    def _getOrganizationList(org=None):
        list = {}
        # if(org): # return only current organization
        #     list[org]= []
        #     return list
        try:
            from MaKaC.ecosoclist import ECOSOCList
            ecolist = ECOSOCList.getInstance().getNames(None,False)
            for key in ecolist:
                if key != "":
                    list[key] = []
                if len(list) == 1000:
                    return list
            return list
        except:
            return []

    def _process(self):
        representationTypes = {
            'Yes': {
                'Governments (ECOSOC Bodies)': {'Member States of the body': [], 'Non-Member States of the Body': [],
                                                'Non-UN Member States': []},
                'Governments (UNCTAD Bodies)': {'UNCTAD Member States': [], 'Non-UNCTAD Member States': [],
                                                'Non-UN Member States': []},
                'Governments (UNECE Bodies)': {'ECE Member States': [], 'Non-ECE Member States': [],
                                               'Non-UN Member States': []},
                'Governments (Treaty Bodies)': {'Contracting Party': [], 'Non-Contracting Party': [],
                                                'Non-UN Member States': []}
            },
            'No': {
                'European Union': {'European Union': []},
                'United Nations': {'UN Regional Commissions': [], 'Departments of UN Secretariat': [],
                                   'UN Conventions': [], 'UN Missions': []},
                'United Nations Bodies and Organs': {'United Nations Bodies and Organs': []},
                'United Nations Funds and Programmes': {'United Nations Funds and Programmes': []},
                'United Nations Specialized Agencies': {'United Nations Specialized Agencies': []},
                'United Nations (Related Organizations)': {'United Nations (Related Organizations)': []},
                'Intergovernmental Organizations': {'Intergovernmental Organizations': [],
                                                    'IGO accredited to UNCTAD': []},
                'Non Governmental Organizations': {'NGO Consultative with ECOSOC': [], 'Other NGO': [],
                                                   'NGO General Category accredited to UNCTAD': [],
                                                   'NGO Special Category accredited to UNCTAD': []},
                'Others': {'Academia': [], 'Private Sector': [], 'Agenda 21 Major Groups': [],
                           'Independent Experts': [], 'Press/Media': [], 'Other': []},
                'Present at the Invitation of the Secretariat': {'Invited': []},
                'UNECE Secretariat': {'UNECE Secretariat': []}
            }
        }
        contactTypes = {'Head of Delegation':[], 'Delegate':[], 'Press':[], 'UN Staff member':[], 'Intern':[], 'Consultant':[], 'Other':[]}
        countryList = RHRepresentationTypes._getCountryList()
        organizationList = RHRepresentationTypes._getOrganizationList()
        return json.dumps({
            'status': 'OK',
            'representationTypes': representationTypes,
            'contactTypes': contactTypes,
            'countryList': countryList,
            'organizationList': organizationList
        })
