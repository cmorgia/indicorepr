# coding=utf-8
from MaKaC.registration import GeneralSectionForm, GeneralField
from MaKaC.webinterface.pages.registrants import WPRegistrantModification
from MaKaC.webinterface.pages.registrationForm import WPRegistrationFormDisplay, WPRegistrationFormModify, \
    WPConfModifRegFormPreview, WPRegistrationForm
import indicorepr.filters
import indicorepr.fileimport
import indicorepr.conference
from MaKaC.webinterface.pages.conferences import WPConfModifAC

from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint
from indico.core import signals
from MaKaC.services.interface.rpc.handlers import endpointMap, importModule

blueprint = IndicoPluginBlueprint('indicorepr', __name__)


class IndicoRepresentationPlugin(IndicoPlugin):
    """Indico Representation Plugin

    """
    configurable = False

    def init(self):
        super(IndicoRepresentationPlugin, self).init()
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

    def get_blueprints(self):
        return blueprint

    def conf_created(self,conf,parent):
        _sectionHeader = {}
        _sectionHeader["title"] = "Representation"
        _sectionHeader["description"] = "Descrizione"
        regForm = conf.getRegistrationForm()
        pos = next((i for i, f in enumerate(regForm.getSortedForms()) if not f.isEnabled()), None)
        section = GeneralSectionForm(regForm, data=_sectionHeader)
        section.directives = "nd-my-section"

        govt = {
            "radioitems":[
                {"id":"isNew","caption":"No"},
                {"id":"isNew","caption":"Yes"}
            ],
            "input":"radio",
            "disabled":False,
            "caption":"Government Representative",
            "inputType":"dropdown",
            "mandatory": True
        }

        field = GeneralField(section, data=govt)
        pos = next((i for i, f in enumerate(section.getSortedFields()) if f.isDisabled()), None)
        section.addToSortedFields(field, i=pos)

        others = {
            "radioitems":[],
            "input":"radio",
            "disabled":False,
            "inputType":"dropdown"
        }

        captions = [
            ('Representation Type',True,{'ng-model':'<model>','ng-options':'...'}),
            ('Rep. Sub Type',True,{'ng-model':'<model>','ng-options':'...'}),
            ('Contact Type',True,{'ng-model':'<model>','ng-options':'...'}),
            ('Organization Representative',False,{'ng-model':'<model>','ng-options':'...'})
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

