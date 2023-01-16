import os
import urllib
from urllib.parse import urlparse
print ("<h2>You have succeeded in getting a python page!</h2>")
print ("<h3>Hello</h3>")

get = os.getenv("_GET")
post = os.getenv("_POST")
print ("<p>Get Environment variable is: ",get)
print ("<p>Post Environment variable is: ",post)

if get :

    try:
        get_lib = urllib.parse.parse_qs(get, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace', max_num_fields=None)

        print ("<p>Get: Hello %s %s" %(get_lib['firstname'][0],get_lib['lastname'][0]) )
    except:
        print ("<p>You did not parse the 'get' data properly</p>")
else:
    print ("<p>No 'get' data</p>")


if post :

    try:
        post_lib = urllib.parse.parse_qs(post, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace', max_num_fields=None)

        print ("<p>Post: Hello %s %s" %(post_lib['firstname'][0],post_lib['lastname'][0]) )
    except:
        print ("<p>You did not parse the 'post' data properly</p>")
else:
    print ("<p>No 'post' data</p>")
