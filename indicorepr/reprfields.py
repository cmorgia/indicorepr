from MaKaC.registration import DropdownInput


class DynamicDropdownInput(DropdownInput):
    _subtype = "dynamic-dropdown"
    _icon = "icon-dynamic-dropmenu"
    _label = "Dynamic Dropdown"
    _directives = "nd-dynamic-dropdown-field"

    def getName(cls):
        return "Dynamic Dropdown"
    getName = classmethod(getName)

    def getValueDisplay(self, value):
        result = super(DynamicDropdownInput,self).getValueDisplay(value)
        return result

    def _getModifHTML(self, item, registrant, default=None):
        result = super(DynamicDropdownInput,self)._getModifHTML(item,registrant,default)
        return result

    def _setResponseValue(self, item, params, registrant, override=False, validate=True):
        result = super(DynamicDropdownInput,self).getValueDisplay(item,params,registrant,override,validate)
        return result


    def _getSpecialOptionsHTML(self):
        return ""
