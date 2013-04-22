#!/usr/bin/python
#
# Flickr API implementation
#
# Inspired largely by Michele Campeotto's flickrclient and Aaron Swartz'
# xmltramp... but I wanted to get a better idea of how python worked in
# those regards, so I mostly worked those components out for myself.
#
# http://micampe.it/things/flickrclient
# http://www.aaronsw.com/2002/xmltramp/
#
# Release 1: initial release
# Release 2: added upload functionality
# Release 3: code cleanup, convert to doc strings
# Release 4: better permission support
# Release 5: converted into fuller-featured "flickrapi"
# Release 6: fix upload sig bug (thanks Deepak Jois), encode test output
# Release 7: fix path construction, Manish Rai Jain's improvements, exceptions
# Release 8: change API endpoint to "api.flickr.com"
#
# Work by (or inspired by) Manish Rai Jain <manishrjain@gmail.com>:
#
#    improved error reporting, proper multipart MIME boundary creation,
#    use of urllib2 to allow uploads through a proxy, upload accepts
#    raw data as well as a filename
#
# Copyright 2005 Brian "Beej Jorgensen" Hall <beej@beej.us>
#
#    This work is licensed under the Creative Commons
#    Attribution License.  To view a copy of this license,
#    visit http://creativecommons.org/licenses/by/2.5/ or send
#    a letter to Creative Commons, 543 Howard Street, 5th
#    Floor, San Francisco, California, 94105, USA.
#
# This license says that I must be credited for any derivative works.
# You do not need to credit me to simply use the FlickrAPI classes in
# your Python scripts--you only need to credit me if you're taking this
# FlickrAPI class and modifying it or redistributing it.
#
# Previous versions of this API were granted to the public domain.
# You're free to use those as you please.
#
# Beej Jorgensen, Maintainer, November 2005
# beej@beej.us
#

import sys
import md5
import string
import urllib
import urllib2
import mimetools
import httplib
import os.path
import xml.dom.minidom

########################################################################
# Exceptions
########################################################################

class UploadException(Exception):
    pass

########################################################################
# XML functionality
########################################################################

#-----------------------------------------------------------------------
class XMLNode:
    """XMLNode -- generic class for holding an XML node

    xmlStr = \"\"\"<xml foo="32">
    <name bar="10">Name0</name>
    <name bar="11" baz="12">Name1</name>
    </xml>\"\"\"

    f = XMLNode.parseXML(xmlStr)

    print f.elementName              # xml
    print f['foo']                   # 32
    print f.name                     # [<name XMLNode>, <name XMLNode>]
    print f.name[0].elementName      # name
    print f.name[0]["bar"]           # 10
    print f.name[0].elementText      # Name0
    print f.name[1].elementName      # name
    print f.name[1]["bar"]           # 11
    print f.name[1]["baz"]           # 12

    """

    def __init__(self):
        """Construct an empty XML node."""
        self.elementName=""
        self.elementText=""
        self.attrib={}
        self.xml=""

    def __setitem__(self, key, item):
        """Store a node's attribute in the attrib hash."""
        self.attrib[key] = item

    def __getitem__(self, key):
        """Retrieve a node's attribute from the attrib hash."""
        try:
            return self.attrib[key]
        except:
            return "null"
    #-----------------------------------------------------------------------
    #@classmethod
    def parseXML(cls, xmlStr, storeXML=False):
        """Convert an XML string into a nice instance tree of XMLNodes.

        xmlStr -- the XML to parse
        storeXML -- if True, stores the XML string in the root XMLNode.xml

        """

        def __parseXMLElement(element, thisNode):
            """Recursive call to process this XMLNode."""
            thisNode.elementName = element.nodeName

            #print element.nodeName

            # add element attributes as attributes to this node
            for i in range(element.attributes.length):
                an = element.attributes.item(i)
                thisNode[an.name] = an.nodeValue

            for a in element.childNodes:
                if a.nodeType == xml.dom.Node.ELEMENT_NODE:

                    child = XMLNode()
                    try:
                        list = getattr(thisNode, a.nodeName)
                    except AttributeError:
                        setattr(thisNode, a.nodeName, [])

                    # add the child node as an attrib to this node
                    list = getattr(thisNode, a.nodeName);
                    #print "appending child: %s to %s" % (a.nodeName, thisNode.elementName)
                    list.append(child);

                    __parseXMLElement(a, child)

                elif a.nodeType == xml.dom.Node.TEXT_NODE:
                    thisNode.elementText += a.nodeValue
    
            return thisNode

        dom = xml.dom.minidom.parseString(xmlStr)

        # get the root
        rootNode = XMLNode()
        if storeXML: rootNode.xml = xmlStr

        return __parseXMLElement(dom.firstChild, rootNode)
    parseXML = classmethod(parseXML)

########################################################################
# Flickr functionality
########################################################################

#-----------------------------------------------------------------------
class FlickrAPI:
    """Encapsulated flickr functionality.

    Example usage:

      flickr = FlickrAPI(flickrAPIKey, flickrSecret)
      rsp = flickr.auth_checkToken(api_key=flickrAPIKey, auth_token=token)

    """
    flickrHost = "api.flickr.com"
    flickrRESTForm = "/services/rest/"
    flickrAuthForm = "/services/auth/"
    flickrUploadForm = "/services/upload/"

    #-------------------------------------------------------------------
    def __init__(self, apiKey, secret):
        """Construct a new FlickrAPI instance for a given API key and secret."""
        self.apiKey = apiKey
        self.secret = secret

        self.__handlerCache={}

    #-------------------------------------------------------------------
    def __sign(self, data):
        """Calculate the flickr signature for a set of params.

        data -- a hash of all the params and values to be hashed, e.g.
                {"api_key":"AAAA", "auth_token":"TTTT"}

        """
        dataName = self.secret
        keys = data.keys()
        keys.sort()
        for a in keys: dataName += (a + data[a])
        #print dataName
        hash = md5.new()
        hash.update(dataName)
        return hash.hexdigest()

    #-------------------------------------------------------------------
    def __getattr__(self, method, **arg):
        """Handle all the flickr API calls.
        
        This is Michele Campeotto's cleverness, wherein he writes a
        general handler for methods not defined, and assumes they are
        flickr methods.  He then converts them to a form to be passed as
        the method= parameter, and goes from there.

        http://micampe.it/things/flickrclient

        My variant is the same basic thing, except it tracks if it has
        already created a handler for a specific call or not.

        example usage:

                flickr.auth_getFrob(api_key="AAAAAA")
                rsp = flickr.favorites_getList(api_key=flickrAPIKey, \\
                        auth_token=token)

        """

        if not self.__handlerCache.has_key(method):
            def handler(_self = self, _method = method, **arg):
                _method = "flickr." + _method.replace("_", ".")
                url = "http://" + FlickrAPI.flickrHost + \
                        FlickrAPI.flickrRESTForm
                arg["method"] = _method
                postData = urllib.urlencode(arg) + "&api_sig=" + \
                        _self.__sign(arg)
                #print "--url---------------------------------------------"
                #print url
                #print "--postData----------------------------------------"
                #print postData
                f = urllib.urlopen(url, postData)
                data = f.read()
                #print "--response----------------------------------------"
                #print data
                f.close()
                return XMLNode.parseXML(data, True)

            self.__handlerCache[method] = handler;

        return self.__handlerCache[method]

    #-------------------------------------------------------------------
    def __getAuthURL(self, perms, frob):
        """Return the authorization URL to get a token.

        This is the URL the app will launch a browser toward if it
        needs a new token.
                
        perms -- "read", "write", or "delete"
        frob -- picked up from an earlier call to FlickrAPI.auth_getFrob()

        """

        data = {"api_key": self.apiKey, "frob": frob, "perms": perms}
        data["api_sig"] = self.__sign(data)
        return "http://%s%s?%s" % (FlickrAPI.flickrHost, \
                FlickrAPI.flickrAuthForm, urllib.urlencode(data))

    #-------------------------------------------------------------------
    def upload(self, filename=None, jpegData=None, **arg):
        """Upload a file to flickr.

        Be extra careful you spell the parameters correctly, or you will
        get a rather cryptic "Invalid Signature" error on the upload!

        Supported parameters:

        One of filename or jpegData must be specified by name when 
        calling this method:

        filename -- name of a file to upload
        jpegData -- array of jpeg data to upload

        api_key
        auth_token
        title
        description
        tags -- space-delimited list of tags, "tag1 tag2 tag3"
        is_public -- "1" or "0"
        is_friend -- "1" or "0"
        is_family -- "1" or "0"

        """

        if filename == None and jpegData == None or \
                filename != None and jpegData != None:

            raise UploadException("filename OR jpegData must be specified")

        # verify key names
        for a in arg.keys():
            if a != "api_key" and a != "auth_token" and a != "title" and \
                    a != "description" and a != "tags" and a != "is_public" and \
                    a != "is_friend" and a != "is_family":

                sys.stderr.write("FlickrAPI: warning: unknown parameter " \
                        "\"%s\" sent to FlickrAPI.upload\n" % (a))

        arg["api_sig"] = self.__sign(arg)
        url = "http://" + FlickrAPI.flickrHost + FlickrAPI.flickrUploadForm

        # construct POST data
        boundary = mimetools.choose_boundary()
        body = ""

        # required params
        for a in ('api_key', 'auth_token', 'api_sig'):
            body += "--%s\r\n" % (boundary)
            body += "Content-Disposition: form-data; name=\""+a+"\"\r\n\r\n"
            body += "%s\r\n" % (arg[a])

        # optional params
        for a in ('title', 'description', 'tags', 'is_public', \
                'is_friend', 'is_family'):

            if arg.has_key(a):
                body += "--%s\r\n" % (boundary)
                body += "Content-Disposition: form-data; name=\""+a+"\"\r\n\r\n"
                body += "%s\r\n" % (arg[a])

        body += "--%s\r\n" % (boundary)
        body += "Content-Disposition: form-data; name=\"photo\";"
        body += " filename=\"%s\"\r\n" % filename
        body += "Content-Type: image/jpeg\r\n\r\n"

        #print body

        if filename != None:
            fp = file(filename, "rb")
            data = fp.read()
            fp.close()
        else:
            data = jpegData

        postData = body.encode("utf_8") + data + \
                ("--%s--" % (boundary)).encode("utf_8")

        request = urllib2.Request(url)
        request.add_data(postData)
        request.add_header("Content-Type", \
                "multipart/form-data; boundary=%s" % boundary)
        response = urllib2.urlopen(request)
        rspXML = response.read()

        return XMLNode.parseXML(rspXML)


    #-----------------------------------------------------------------------
    #@classmethod
    def testFailure(cls, rsp, exit=True):
        """Exit app if the rsp XMLNode indicates failure."""
        if rsp['stat'] == "fail":
            sys.stderr.write("%s\n" % (cls.getPrintableError(rsp)))
            if exit: sys.exit(1)
    testFailure = classmethod(testFailure)

    #-----------------------------------------------------------------------
    #@classmethod
    def getPrintableError(cls, rsp):
        """Return a printed error message string."""
        return "%s: error %s: %s" % (rsp.elementName, \
                cls.getRspErrorCode(rsp), cls.getRspErrorMsg(rsp))
    getPrintableError = classmethod(getPrintableError)

    #-----------------------------------------------------------------------
    #@classmethod
    def getRspErrorCode(cls, rsp):
        """Return the error code of a response, or 0 if no error."""
        if rsp['stat'] == "fail":
            return rsp.err[0]['code']

        return 0
    getRspErrorCode = classmethod(getRspErrorCode)

    #-----------------------------------------------------------------------
    #@classmethod
    def getRspErrorMsg(cls, rsp):
        """Return the error message of a response, or "Success" if no error."""
        if rsp['stat'] == "fail":
            return rsp.err[0]['msg']

        return "Success"
    getRspErrorMsg = classmethod(getRspErrorMsg)

    #-----------------------------------------------------------------------
    def __getCachedTokenPath(self):
        """Return the directory holding the app data."""
        return os.path.expanduser(os.path.sep.join(["~", ".flickr", \
                self.apiKey]))

    #-----------------------------------------------------------------------
    def __getCachedTokenFilename(self):
        """Return the full pathname of the cached token file."""
        return os.path.sep.join([self.__getCachedTokenPath(), "auth.xml"])

    #-----------------------------------------------------------------------
    def __getCachedToken(self):
        """Read and return a cached token, or None if not found.

        The token is read from the cached token file, which is basically the
        entire RSP response containing the auth element.
        """

        try:
            f = file(self.__getCachedTokenFilename(), "r")
            
            data = f.read()
            f.close()

            rsp = XMLNode.parseXML(data)

            return rsp.auth[0].token[0].elementText

        except IOError:
            return None

    #-----------------------------------------------------------------------
    def __setCachedToken(self, xml):
        """Cache a token for later use.

        The cached tag is stored by simply saving the entire RSP response
        containing the auth element.

        """

        path = self.__getCachedTokenPath()
        if not os.path.exists(path):
            os.makedirs(path)

        f = file(self.__getCachedTokenFilename(), "w")
        f.write(xml)
        f.close()


    #-----------------------------------------------------------------------
    def getToken(self, perms="read", browser="lynx"):
        """Get a token either from the cache, or make a new one from the
        frob.

        This first attempts to find a token in the user's token cache on
        disk.
        
        If that fails (or if the token is no longer valid based on
        flickr.auth.checkToken) a new frob is acquired.  The frob is
        validated by having the user log into flickr (with lynx), and
        subsequently a valid token is retrieved.

        The newly minted token is then cached locally for the next run.

        perms--"read", "write", or "delete"
        browser--whatever browser should be used in the system() call

        """
        
        # see if we have a saved token
        token = self.__getCachedToken()

        # see if it's valid
        if token != None:
            rsp = self.auth_checkToken(api_key=self.apiKey, auth_token=token)
            if rsp['stat'] != "ok":
                token = None
            else:
                # see if we have enough permissions
                tokenPerms = rsp.auth[0].perms[0].elementText
                if tokenPerms == "read" and perms != "read": token = None
                elif tokenPerms == "write" and perms == "delete": token = None

        # get a new token if we need one
        if token == None:
            # get the frob
            rsp = self.auth_getFrob(api_key=self.apiKey)
            self.testFailure(rsp)

            frob = rsp.frob[0].elementText

            # validate online
            os.system("%s '%s'" % (browser, self.__getAuthURL(perms, frob)))

            # get a token
            rsp = self.auth_getToken(api_key=self.apiKey, frob=frob)
            self.testFailure(rsp)

            token = rsp.auth[0].token[0].elementText

            # store the auth info for next time
            self.__setCachedToken(rsp.xml)

        return token

########################################################################
# App functionality
########################################################################

def main(argv):
    # flickr auth information:
    flickrAPIKey = "fa33550d413b36b3fddc473a931a3b3b"  # API key
    flickrSecret = "7fd481bff0916055"                  # shared "secret"

    # make a new FlickrAPI instance
    fapi = FlickrAPI(flickrAPIKey, flickrSecret)

    # do the whole whatever-it-takes to get a valid token:
    token = fapi.getToken(browser="chrome")

    # get my favorites
    rsp = fapi.favorites_getList(api_key=flickrAPIKey,auth_token=token)
    fapi.testFailure(rsp)

    # and print them
    for a in rsp.photos[0].photo:
        print "%10s: %s" % (a['id'], a['title'].encode("ascii", "replace"))

    # upload the file foo.jpg
    #rsp = fapi.upload(filename="foo.jpg", \
    #       api_key=flickrAPIKey, auth_token=token, \
    #       title="This is the title", description="This is the description", \
    #       tags="tag1 tag2 tag3", is_public="1")
    #if rsp == None:
    #       sys.stderr.write("can't find file\n")
    #else:
    #       fapi.testFailure(rsp)

    return 0

# run the main if we're not being imported:
if __name__ == "__main__": sys.exit(main(sys.argv))

