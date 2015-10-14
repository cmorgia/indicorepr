from persistent import Persistent
from indico.core.db import DBMgr
from lxml import html
import requests
import re
import unicodedata

class _ECOSOCList(Persistent):

    def __init__(self):
        self.__list = {}

    def update(self):
        codes = {'Africa':'1','Asia':'2','Europe':'3','North America':'5','Oceania':'6','Latin America and Caribbean':'7','Not Specified':'8'}
        result={}

        for i,region in enumerate(codes):
            r=requests.get('http://esango.un.org')
            r=requests.get('http://esango.un.org/civilsociety/withOutLogin.do?method=getOrgsByRegionsCode&orgByRegionCode='+codes[region]+'&orgByRegionName='+region+'&sessionCheck=false&ngoFlag=',cookies=r.cookies)
            r=requests.get('http://esango.un.org/civilsociety/displayConsultativeStatusSearch.do?method=list&show=100000&from=list&col=&order=&searchType=&index=0',cookies=r.cookies)
            tree = html.fromstring(r.text)
            hrefs = tree.xpath("//tr[contains(string(@class),'searchResult')]/td[1]/a/@href")
            texts = tree.xpath("//tr[contains(string(@class),'searchResult')]/td[1]/a/text()")
            spans = tree.xpath("//tr[contains(string(@class),'searchResult')]/td[2]/span[1]/text()")

            try:
                for idx,value in enumerate(hrefs):
                    code = value.split('=')[-1]
                    text = texts[idx]
                    text = unicodedata.normalize('NFKD', text).encode('ascii','ignore') if isinstance(text,unicode) else str(text)
                    span = re.sub('\s+',' ',str(spans[idx]))
                    result[text]={'status':span,'code':code}
            except Exception as e:
                pass
        self.__list = result

    def getNames(self,query,full=False):
        if query:
            query = query.lower()
            tokens = query.split()
            result = self.__list.keys()
            for token in tokens:
                result = [key for key in result if token in key.lower()]
        else:
            result = self.__list.keys()

        if full:
            result = [ dict((key,value)  for key,value in self.__list.iteritems() if key in result )]

        return result

    def getStatus(self,name):
        return self.__list[name]

    def getList( self ):
        return self.__list


class ECOSOCList:

    def getInstance( self ):
        dbroot = DBMgr.getInstance().getDBConnection().root()
        if dbroot.has_key("ecosoclist"):
            return dbroot["ecosoclist"]
        al = _ECOSOCList()
        dbroot["ecosoclist"] = al
        return al
    getInstance = classmethod(getInstance)
