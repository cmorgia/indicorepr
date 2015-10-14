ndRegForm.directive('ndIndicoReplace', function ($compile) {
    return {
        restrict: 'A',
        replace: false,
        terminal: true, //this setting is important, see explanation below
        priority: 1000, //this setting is important, see explanation below
        compile: function compile(element, attrs) {
            element.removeAttr("nd-indico-replace"); //remove the attribute to avoid indefinite loop
            element.removeAttr("data-nd-indico-replace"); //also remove the same attribute with data- prefix in case users specify data-common-things in the html

            return {
                pre: function preLink(scope, iElement, iAttrs, controller) {
                    var types = {
                        "PersonalDataForm":["nd-general-section","nd-personal-data-section"],
                        "AccommodationForm":"nd-accommodation-section",
                        "RepresentationForm":"nd-representation-section",
                        "FurtherInformationForm":"nd-further-information-section",
                        "ReasonParticipationForm":"nd-reason-section",
                        "SessionsForm":"nd-sessions-section",
                        "SocialEventForm":"nd-social-event-section",
                        "GeneralSectionForm": "nd-general-section"
                    };

                    var directives;
                    if (types.hasOwnProperty(scope.section._type)) {
                        directives = types[scope.section._type];
                    } else {
                        directives = "nd-general-section";
                    }
                    if (scope.section.hasOwnProperty('directives') && scope.section.directives!="") {
                        directives = (directives+" "+scope.section.directives).split(" ");
                    }
                    if (typeof directives == 'string' || directives instanceof String) {
                        iElement.attr(directives, directives);
                    } else {
                        for (idx in directives) {
                            iElement.attr(directives[idx],'');
                        }
                    }
                },
                post: function postLink(scope, iElement, iAttrs, controller) {
                    debugger;
                    $compile(iElement)(scope);
                    var elems = iElement.children("select");
                    var elem;
                    for (elem in elems) {
                        elems[elem].attr('ciao','');
                    }
                }
            };
        }
    };
});

ndRegForm.directive("ndMySection", function($rootScope) {
    return {
        require: 'ndSection',
        link: function(scope) {
            scope.buttons.disable = true;
            scope.representationTypes = {
                'Yes': {
                        'Governments (ECOSOC Bodies)': {'Member States of the body': [], 'Non-Member States of the Body':[],'Non-UN Member States':[]},
                        'Governments (UNCTAD Bodies)':  {'UNCTAD Member States': [], 'Non-UNCTAD Member States':[], 'Non-UN Member States':[]},
                        'Governments (UNECE Bodies)':  {'ECE Member States': [], 'Non-ECE Member States':[], 'Non-UN Member States':[]},
                        'Governments (Treaty Bodies)': {'Contracting Party':[],'Non-Contracting Party':[],'Non-UN Member States':[]}
                    },
                'No': {
                        'European Union': {'European Union':[]},
                        'United Nations': {'UN Regional Commissions':[],'Departments of UN Secretariat':[],'UN Conventions':[],'UN Missions':[]},
                        'United Nations Bodies and Organs': {'United Nations Bodies and Organs':[]},
                        'United Nations Funds and Programmes': {'United Nations Funds and Programmes':[]},
                        'United Nations Specialized Agencies': {'United Nations Specialized Agencies':[]},
                        'United Nations (Related Organizations)': {'United Nations (Related Organizations)':[]},
                        'Intergovernmental Organizations': {'Intergovernmental Organizations':[], 'IGO accredited to UNCTAD':[]},
                        'Non Governmental Organizations': {'NGO Consultative with ECOSOC':[],'Other NGO':[],'NGO General Category accredited to UNCTAD':[],'NGO Special Category accredited to UNCTAD':[]},
                        'Others': {'Academia':[],'Private Sector':[],'Agenda 21 Major Groups':[],'Independent Experts':[],'Press/Media':[],'Other':[]},
                        'Present at the Invitation of the Secretariat':{'Invited':[]},
                        'UNECE Secretariat':{'UNECE Secretariat':[]}
                    }
            };
            scope.contactTypes = {'Head of Delegation':[], 'Delegate':[], 'Press':[], 'UN Staff member':[], 'Intern':[], 'Consultant':[], 'Other':[]};

            scope.countryList = {};
            scope.organizationList = {};
            scope.representationType = {};
            scope.isReadonly = false;
            scope.$watch('userdata.representationType', function() {
                if (scope.userdata.representationType === undefined || scope.userdata.representationType === null) {
                    return;
                }
                scope.representationType.grmodel = scope.representationTypes[scope.userdata.representationType.governmentRepresentative];
                scope.representationType.rtmodel = scope.representationType.grmodel[scope.userdata.representationType.repType];
                scope.representationType.rstmodel = scope.representationType.rtmodel[scope.userdata.representationType.repSubType];
                scope.representationType.ctmodel = scope.contactTypes[scope.userdata.representationType.contactType];
                scope.representationType.ctrymodel = scope.userdata.representationType.countryRepresentative;
                scope.countryList = scope.userdata.representationType.countryList;
                scope.organizationList = scope.userdata.representationType.organizationList;
                scope.representationType.orgmodel = scope.organizationList[scope.userdata.representationType.organizationRepresentative];
                //scope.isReadonly = true;
            });

            scope.$watch('userdata.countryList', function() {
                if (scope.userdata.countryList === undefined || scope.userdata.countryList === null) {
                    return;
                }
                scope.countryList = scope.userdata.countryList;
            });

            scope.$watch('userdata.organizationList', function() {
                if (scope.userdata.organizationList === undefined || scope.userdata.organizationList === null) {
                    return;
                }
                scope.organizationList = scope.userdata.organizationList;
            });
        }
    };
});