import urllib
import urllib2
import ClientCookie
from xml.dom import minidom




 
def getPage():
    url="http://www.google.com"
 
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    return response.read()


def login():
    
    url = "https://playback.rhapsody.com/login.xml"  


    opts = {
    'username': 'dave2343@gmail.com',
    'password': 'lolhackathon',
    }
 
    data = urllib.urlencode(opts)

 
    headers = {
    'Host': 'playback.rhapsody.com',
    }
 
    req = urllib2.Request(url, data, headers)
 
    response = ClientCookie.urlopen(req)
    return response.read()

 
if __name__ == "__main__":
    namesPage = login()
    f = open('logindump','w')
    f.write(namesPage)
    f.close()
    xmldoc = minidom.parse('logindump')
    itemlist = xmldoc.getElementsByTagName('token') 
    print itemlist[0] 
    
