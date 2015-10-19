ndRegForm.value('reprurl',
    Indico.Urls.Base + '/event/:confId/reprtypes'
);

ndRegForm.factory('reprTypeFactory', function($resource, reprurl) {
    return {
        ReprType: $resource(reprurl, {confId: '@confId'}, {
            "query": {method:'GET', isArray: true, cache: false}
        })
    };
});

ndRegForm.directive("ndMySection", function($rootScope, reprTypeFactory) {
    return {
        require: 'ndSection',
        link: function(scope) {
            debugger;
            scope.buttons.disable = true;
            scope.representationType = {};
            scope.isReadonly = false;

            reprType = reprTypeFactory.ReprType.get({confId: scope.confId}, function() {
                scope.representationTypes = reprType.representationTypes;
                scope.contactTypes = reprType.contactTypes;
                scope.countryList = reprType.countryList;
                scope.organizationList = reprType.organizationList;
                scope.representationType.grmodel = scope.representationTypes[reprType.representationType.governmentRepresentative];
                scope.representationType.rtmodel = scope.representationType.grmodel[reprType.representationType.repType];
                scope.representationType.rstmodel = scope.representationType.rtmodel[reprType.representationType.repSubType];
                scope.representationType.ctmodel = scope.contactTypes[reprType.representationType.contactType];
                scope.representationType.ctrymodel = reprType.representationType.countryRepresentative;
                scope.representationType.orgmodel = scope.organizationList[scope.userdata.representationType.organizationRepresentative];
            });
            /*scope.representationTypes = {
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
            scope.organizationList = {};*/
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

ndServices.provider('rurl', function() {
    var baseUrl = Indico.Urls.Base;
    var modulePath = '';

    return {
        setModulePath: function(path) {
            if (path.substr(-1) == '/') {
                path = path.substr(0, path.length - 1);
            }

            modulePath = path;
        },

        $get: function() {
            return {
                tpl: function(path) {
                    return baseUrl + modulePath + '/tpls/' + path;
                }
            };
        }
    };
});

ndRegForm.config(function(rurlProvider) {
    rurlProvider.setModulePath('/static/assets/plugins/indicorepr');
});

ndRegForm.directive('ndDynamicDropdownField', function(rurl) {
    return {
        require: 'ndRadioField',
        controller: function ($scope) {
            $scope.tplInput = rurl.tpl('dynamic-dropdown.tpl.html');
        }
    }
});