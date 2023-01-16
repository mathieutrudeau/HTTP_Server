# ====================================================================
# Authors: Mathieu Trudeau & Guillaume Valliere
# Name: HttpServer.py
# Description: Uses the http protocol to handle post and get requests
#               Allows values to be passed by POST or GET
#               
# ====================================================================

# ====================================================================
# Libraries
# ====================================================================
import sys
import socket
import re
import os.path
from os import path
import os
import subprocess
from subprocess import Popen

# ====================================================================
# server Constants
# ====================================================================

# max buffer size
buffer = 2048

# Host IP address (localhost)
host = "127.0.0.1"

# Backlog
backlog = 0

# Folder in which the HTTP server handles the requests
baseDir = "htdocs"

# ====================================================================  
# start server  
# ====================================================================

# which port
inputs = sys.argv
if (len(inputs) <2):
    port = 1632
else:
    port = int (inputs[1])

# open socket for listening
print("opening socket on port ",port)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)

# ===============================================================
# Executes a POST or GET request
# INPUTS:   - method: String "GET" or "POST"
#           - variables: String variables to be save on the
#             environment variable _GET or _POST
#           - filePath: Path of the file to execute
# RETURN:   - String HTTP 200 Response
# ===============================================================
def get_execute_response(method,variables,filePath):
    # Set the GET or POST environment variables with the variables from the request
    if method == "POST":
        os.environ['_POST'] = variables    
    elif method == "GET":
        os.environ['_GET'] = variables
    
    # Create a subprocess to execute the file
    process = Popen([sys.executable,filePath],stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True)
    # Execute the file and capture the output from stdout & stderr
    output, errors = process.communicate()
    # Wait for the process to finish executing
    process.wait()

    # Build the response and return the output from the process
    executeResponse="HTTP/1.1 200 OK\nContent-Type: text/html\n\n"+output

    return executeResponse
# ===============================================================

# ===============================================================
# Creates a 404 Not Found response
# INPUT:    - filename: String name of the file that was not found
# RETURN:   - String HTTP 404 response
# ===============================================================
def not_found_response(filename):
    # Build a not found 404 response
    notFoundResponse="""HTTP/1.1 404 Not Found
    Content-Type: text/html; charset=iso-8859-1

    <!DOCTYPE HTML PUBLIC '-//IETF//DTD HTML 2.0//EN'>
    <html>
        <head>
            <title>404 Not Found</title>
        </head>
        <body>
            <h1>Not Found</h1>
            <p>The requested URL {file_name} was not found on this server.</p>
        </body>
    </html>
    """
    return str(notFoundResponse.format(file_name=filename))
# ===============================================================

# ===============================================================
# Get the Full Path for a Filename
# INPUT:    - filename: String name of the file to get the full 
#             path of
# RETURN    - String Full Path of where the file should be
# ===============================================================
def get_file_path(filename):
    # Get the path for the directory in which the httpServer resides
    currentPath = os.path.abspath(os.path.dirname(__file__))
    # Full path of the file to be retrieved
    fullPath = currentPath

    # Is htdocs already included included in the url?
    if baseDir in filename:
        # If it is, append the url filename to the base path
        fullPath = fullPath + "/" + filename
    else:
        # Otherwise, append htdocs as well as the url filename
        fullPath = fullPath + "/" + baseDir + "/" +filename
    
    # Return the full path for the requested file
    return fullPath
# ===============================================================

# ===============================================================
# Process GET request
# ===============================================================
def process_get(headerArgs):
    # request method (GET)
    method = headerArgs[0]
    # Content that is requested
    content = headerArgs[1]
    # protocol that is used (HTTP/1.1)
    protocol = headerArgs[2]
    # Path to the content in the htdocs folder
    #contentPath = baseFolder+content
    # Response to send back to the browser
    getResponse = ""
    
    content = content.replace('/','',1)
    parts = content.split('?')
    name = parts[0]

    fullPath = get_file_path(name)
    
    print(fullPath)

    # Does the requested content exist?
    # If it does, send it back with the response
    if(path.exists(fullPath)):
        if re.search(".*\.html",fullPath):
            # Get the content file
            content = open(fullPath,'r')
            # Read the requested content from the requested file
            requestedContent = content.read()
            # Send back the requested content with success code
            getResponse="HTTP/1.1 200 OK \nContent-Type: text/html\n"+"\n"+requestedContent
            
        elif re.search(".*\.py",fullPath):
            return get_execute_response("GET", parts[1], fullPath)
    else:
        return not_found_response(name)

    return getResponse
# ===============================================================

# ===============================================================
# Process POST Request
# INPUT:    - String request data from the browser
# RETURN:   - String HTTP 200 or 404 response
# ===============================================================
def process_post(requestData):
    # Split the POST request into lines
    postRequestLines = requestData.split('\n')
    # Try to match any variables at the end of the request
    match = re.search("(^.*=.*$)",postRequestLines[len(postRequestLines)-1])

    # Retrieve the variables if the request has any
    if match:
        variables = match.group()
    else:
        variables=""

    # Match All the elements found in the request header
    header = re.search ( "^(GET|POST) (.+?)(?:\?(.*))? HTTP", postRequestLines[0])

    # Retrieve the method (GET or POST: POST if its here)
    method = header.group(1)
    # Retrieve the filename (File to be executed)
    filename = header.group(2)
    # Retrieve the protocol (HTTP)
    protocol = header.group(3)

    # Get the full path for the requested file
    filePath = get_file_path(filename)

    print(filePath)
    # Does the requested path exist?
    if path.exists(filePath):
        return str(get_execute_response(method,variables,filePath))
    else:
        # If the requested file does not exit, send back a not found response
        return not_found_response(filename)
# ===============================================================

# ===============================================================
# Process Request
# Handles the request
# ===============================================================
def process_request(data):
    # Split the request into lines
    paragraphs = data.split('\n\n')
    # Get the first line of the request
    requestHeader = paragraphs[0]
    # Split the first lines
    headerArgs = requestHeader.split(' ')
    
    # Get the request method
    method = headerArgs[0]

    # Handle a GET request
    if(method=="GET"):
        return process_get(headerArgs)
    elif(method=="POST"):
        return process_post(data)
# ===============================================================


# ---------------------------------------------------------------  
# wait for client request  
# ---------------------------------------------------------------  
while True:
    print("DEBUG: waiting for client request")    
    client_obj, client_addr = s.accept() 
    print ("DEBUG: Client has sent request")    
    
    # assume that the request is never more than the buffer size     
    # ... bad coding, but simplifies the project     
    data = client_obj.recv(buffer)    
    
    # process request and respond     
    print ("\n\n ============ REQUEST ============= \n")
    print (data.decode())
    if data.decode()=="":
        continue
    response = process_request(data.decode())
    print ("\n ========== RESPONSE ============== \n")
    print(response)
    client_obj.send(response.encode())

