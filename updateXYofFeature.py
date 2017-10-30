#sample of updating an ArcGIS Online feature service for attributes and geometry
#R. Neel 9/2017

import getpass, email, os, sys
import urllib, urllib2, json, time, requests

print ('Begin...')

##objectId = 1
##latitude = 30.6897
##longitude = -96.3663
##newName = 'Another Name'

#COMMAND LINE ARGUMENTS TO FEED INTO SCRIPT:
objectId = sys.argv[1]
latitude = sys.argv[2]
longitude = sys.argv[3]
newName = sys.argv[4]


#AGOL Credentials and feature service information
username = "TRXTestUser"
password = "duncanidaho123"

#service name
service = "trxsample" 

#classes and function declarations
class AGOLHandler(object):    
    """
    ArcGIS Online handler class.
      -Generates and keeps tokens
      -template JSON feature objects for point
    """
    
    def __init__(self, username, password, serviceName):
        self.username = username
        self.password = password
        self.serviceName = serviceName
        self.token, self.http, self.expires= self.getToken(username, password)  

    def getToken(self, username, password, exp=60):  # expires in 60minutes
        """Generates a token."""
        referer = "http://www.arcgis.com/"
        query_dict = {'username': username,
                      'password': password,
                      'referer': referer}

        query_string = urllib.urlencode(query_dict)
        url = "https://www.arcgis.com/sharing/rest/generateToken"
        token = json.loads(urllib.urlopen(url + "?f=json", query_string).read())

        if "token" not in token:
            print(token['error'])
            sys.exit(1)
        else:
            httpPrefix = "http://www.arcgis.com/sharing/rest"
            if token['ssl'] is True:
                httpPrefix = "https://www.arcgis.com/sharing/rest"
            return token['token'], httpPrefix, token['expires'] 
        
        
    def jsonPoint(self, X, Y, newName):
        """Customized JSON point object"""
        return {
            "attributes": {
                "Name": newName
            },
            "geometry": {
                "x": X,
                "y": Y,
                "spatialReference":{"wkid" : 4326}
             }
        }


def send_AGOL_Request(URL, query_dict, returnType):
    """
    Helper function which takes a URL and a dictionary and sends the request.
    returnType values = 
         False : make sure the geometry was updated properly
         "JSON" : simply return the raw response from the request, it will be parsed by the calling function
         else (number) : a numeric value will be used to ensure that number of features exist in the response JSON
    """
    
    query_string = urllib.urlencode(query_dict)

    jsonResponse = urllib.urlopen(URL, urllib.urlencode(query_dict))
    jsonOuput = json.loads(jsonResponse.read())
    
    if returnType == "JSON":
        return jsonOuput
    
    if not returnType:
        if "updateResults" in jsonOuput:
            try:            
                for updateItem in jsonOuput['updateResults']:                    
                    if updateItem['success'] is True:
                        print("request submitted successfully")
            except:
                print("Error: {0}".format(jsonOuput))
                return False
            
    else:  # Check that the proper number of features exist in a layer
        if len(jsonOuput['features']) != returnType:
            print("FS layer needs seed values")
            return False
            
    return True


# Initialize the AGOLHandler for token and feature service JSON templates
con = AGOLHandler(username, password, service)

#query for correct OBJECT ID that goes with this recordID. If not found, quit.
URL = "https://services3.arcgis.com/pKp5WOFjeV9KSSfr/arcgis/rest/services/trxsample/FeatureServer/0/applyEdits"

#attributes and geometry
edits = '[{"geometry":{"x":' + str( longitude ) + ',"y":' + str( latitude ) + ',"spatialReference":{"wkid":4326,"latestWkid":3857}}' + \
        ',"attributes":{"OBJECTID":1,"name":"' + newName + '"}}]'

#parameters to go with web request
params = {
    'f': 'json',
    'token': con.token,
    'updates': edits
}

#process response:
updateRequest = send_AGOL_Request( URL, params, 'JSON' )

print updateRequest
