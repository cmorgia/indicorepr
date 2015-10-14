var limits = [];

function fetchLimits(_confId) {
    jsonRpc(Indico.Urls.JsonRpcService, 'affiliation.get.limits', {
        confId: _confId
    }, function(response, error){
        var killProgress = IndicoUI.Dialogs.Util.progress();
        if (exists(error)) {
            killProgress();
            IndicoUtil.errorReport(error);
        }
        else {
            killProgress();
            limits = response;
            decorateList();
        }
    });
}

function decorateList() {
    $('#inPlaceRegistrars > .UIPerson').each(function(idx,elem){
        var id = $(elem).attr('id');
        var line = 2000+parseInt(idx)*2+1;
        var line1 = line-1;
        $(elem).find('.nameLink').after(function(index) {
            var maxdelegates = limits[id]!=undefined ? limits[id]['threshold'] : '';
            var affiliation = limits[id]!=undefined ? limits[id]['affiliation'] : '';
            return '<span style="float: right;">Affiliation' +
                '<input tabindex="'+line+'" class="affiliation rounded-field" type="text" size="10" style="width: 300px" ' +
                'value="'+affiliation+'"></span>' +
                '<span style="float: right;">Max delegates' +
                '<input tabindex="'+line1+'" class="maxdelegates rounded-field" type="text" size="5" ' +
                'value="'+maxdelegates+'"></span>';

        });
    });
}

var ecosocList = new Bloodhound({
    datumTokenizer: function (d) {
        return Bloodhound.tokenizers.whitespace(d.value);
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url: Indico.Urls.JsonRpcService,

        prepare: function (query, settings) {
            settings.type = "POST";
            settings.contentType = "application/json; charset=UTF-8";
            settings.beforeSend = function (jqXhr, settings) {
                jqXhr.setRequestHeader("X-CSRF-Token", $('#csrf-token').attr('content'));
                settings.data = JSON.stringify({
                    version: '1.1',
                    method: 'ecosoc.nameslist',
                    params: {
                        'query': query,
                        'full': true
                    }
                });
            };
            settings.data = {'query': query};

            return settings;
        },
        transform: function(response) {
            var res = $.map(response.result.suggestions[0],function(item,key) {
                return {label:key,value:key, status: item.status, code: item.code};
            });
            return res;
        }
    }
});

ecosocList.initialize();

function remoteUpdate(event) {
    var payload = [];
    var confId = $('input[name="confId"]:first').val();
    $('#inPlaceRegistrars > .UIPerson').each(function(idx,elem){
        var id = $(elem).attr('id');
        var affiliation = $(elem).find('.tt-input').typeahead('val');
        var threshold = $(elem).find('.maxdelegates').val();
        payload.push({id:id,threshold:threshold,affiliation:(affiliation!=undefined) ? affiliation : '' });
    });

    /*var parentLi = $(event.target).parents("li");
     var registrarId = parentLi.attr("id");
     var org = parentLi.find('.affiliation').val();
     var maxdelegates = parentLi.find('.maxdelegates').val();*/
    jsonRpc(Indico.Urls.JsonRpcService, 'affiliation.update.limits', {
        confId: confId,
        limits: payload
    }, function(response, error){
        var killProgress = IndicoUI.Dialogs.Util.progress();
        if (exists(error)) {
            killProgress();
            IndicoUtil.errorReport(error);
        }
        else {
            killProgress();
            console.log("updated")
        }
    });
};

$(function(){
    var confId = $('input[name="confId"]:first').val();
    fetchLimits(confId);
    $('#inPlaceAddManagerButton[value=\"Add registrar\"]').after("<input type=\"button\" id=\"remoteUpdate\" onclick=\"remoteUpdate();\" value=\"Update limits\">");
    $('#inPlaceRegistrars').on('listUpdated', decorateList);
    $('.affiliation.rounded-field').typeahead({
        highlight: true,
        //hint: false,
    }, {
        name: 'ecosoclist',
        display: 'value',
        source: ecosocList,

        engine: Hogan,
        limit: 1000,
        //template: '<div>{{ key }}<strong>{{ value }}</strong></div>'
        templates: {
            suggestion: function(data) {
                var text = '<p>' + data.value + ' - <strong><a style="float: right;" href="http://esango.un.org/civilsociety/showProfileDetail.do?method=showProfileDetails&profileCode='+data.code+'">' + data.status + '</a></strong></p>';
                return text;
            }
        }
    });

});