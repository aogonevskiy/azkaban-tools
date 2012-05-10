## {{{ http://code.activestate.com/recipes/146306/ (r1)
import httplib, mimetypes
import urlparse
import optparse
import sys
import os

package_to_deploy=''
host=''
port=0

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)

    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    
    errcode, errmsg, headers = h.getreply()
    
    print "CODE=%d"%errcode
    print "ERRMSG=%s"%errmsg
    print "*** Headers ***"
    print headers
    print "*** End of Headers ***"
    
    if 'Failed' in headers.get('Location'):
        print 'ERROR: Upload failed'
        sys.exit(-1)
        
    print 'Package successfully deployed'
    
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
## end of http://code.activestate.com/recipes/146306/ }}}

def posturl(url, fields, files):
    """ method splits url into two parts: hostname and the rest """
    urlparts = urlparse.urlsplit(url)
    return post_multipart(urlparts[1], urlparts[2], fields, files)

def main():    
    option_parser = optparse.OptionParser()
    option_parser.add_option("-z", "--package", dest="package_to_deploy", help="Package to deploy to Azkaban", metavar="<PACKAGE_ZIP_FILE>")
    option_parser.add_option("-a", "--host", dest="host", help="Azkaban host name", metavar="<AZKABAN_HOST>")
    option_parser.add_option("-p", "--port", dest="port", help="Azkaban port number", metavar="<AZKABAN_PORT>")
    options, arguments = option_parser.parse_args()

    if options.package_to_deploy is None:
        print 'Please specify path to the package name (zip file)'
        option_parser.print_help()
        sys.exit(-1)

    if options.host is None:
        print 'Please specify Azkaban host name'
        option_parser.print_help()
        sys.exit(-1)

    if options.port is None:
        print 'Please specify Azkaban port number'
        option_parser.print_help()
        sys.exit(-1)
        
    global package_to_deploy
    global host
    global port
    
    package_to_deploy = os.path.expanduser(options.package_to_deploy)
    host = options.host
    port = int(options.port)
    
    assert os.path.exists(package_to_deploy)
    
    params = []
    params.append(('path', 'rex_feed_manager_jobs'))
    params.append(('redirect', '/'))
    params.append(('redirect_error', '/job-upload'))
    params.append(('redirect_success', '/job-upload'))
    
    #params = {'path':'AAA', 'redirect':'/', 'redirect_error':'/job-upload', 'redirect_success':'/job-upload'}
    
    f = open(package_to_deploy, 'rb')
    files = []
    files.append(('file', 'rex_feed_manager_jobs.zip', f.read()))
#    print files

    url = 'http://' + host + ':' + str(port) + '/api/jobs'
    print url
    print posturl(url, params, files)
    
if __name__ == "__main__":
    main()
