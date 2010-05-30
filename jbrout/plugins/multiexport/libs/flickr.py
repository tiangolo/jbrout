##
##    Copyright (C) 2006 Pieter Edelman p _dot_ edelman [at] gmx _dot_ net
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 2 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##

import urllib, urllib2, hashlib, mimetools, mimetypes, os.path
from xml.dom import minidom

class FlickrAPI:
  def __init__(self, api_key, secret, auth_method, token = None):
    self.api_key = api_key
    self.secret  = secret
    self.auth_method = auth_method
    self.token = token
    self.token_perms = None

  def callMethod(self, method, args, sign = False):
    # Call the Flickr API method with the args dict
    # Return a sequence of True and a xml object if the method succeeds, otherwise a sequence of False and the error message

    # Construct the post data
    args["method"] = method
    post_data = self.__makePost(args, sign)

    # Make the REST request
    return self.__makeRESTRequest("http://api.flickr.com/services/rest/", post_data)

  def upload(self, filepath, comment, tags, privacy):
    # Upload the photo "filepath" with comment "comment", and a list of tags
    # to Flickr. Privacy is [bool, bool, bool] (public, friend, family)

    # Get the filename
    assert type(filepath) == unicode
    filepath = filepath.encode("utf_8")
    filename = os.path.split(filepath)[-1]

    for index in range(len(privacy)):
        if (privacy[index] == True): privacy[index] = 1
        elif (privacy[index] == False): privacy[index] = 0

    # Construct a string of escaped tags
    tags_str = ""
    for tag in tags:
      tags_str += '"' + tag + '" '

    if not (self.checkTokenPerms("write")):
      self.obtainToken("write")
    boundary, post_data = self.__makeImagePost({"auth_token": self.token, "title": filename, "description": comment, "tags": tags_str, "is_public": privacy[0], "is_friend": privacy[1], "is_family": privacy[2]}, filepath)
    response = self.__makeRESTRequest("http://api.flickr.com/services/upload/", post_data, boundary)
    return response

  def obtainToken(self, perms):
    # Get a token with the appropriate permissions.

    token = None

    response = self.callMethod("flickr.auth.getFrob", {}, sign = True)
    if response[0]:
      frob = response[1].childNodes[0].childNodes[1].childNodes[0].data
      success = self.auth_method(self.__makePost({"perms" : perms, "frob" : frob}, sign = True))
      if (success):
        response = self.callMethod("flickr.auth.getToken", {"frob" : frob}, sign = True)
        if (response[0]):
          token = response[1].getElementsByTagName("rsp")[0].getElementsByTagName("token")[0].childNodes[0].data
    if (token):
      self.token = token
      self.checkTokenPerms(perms, force = True)
    else:
      raise "Somehow we couldn't get a proper validation for uploading your pictures to this Flickr account. I'm sorry."

  def checkTokenPerms(self, perms, force = False):
    # Check the permissions of the token we have. If force is true, ignore cached checks and get a response from Flikcr
    if (self.token):
      if ((self.token_perms) and not (force)):
        if (self.token_perms == perms): # We have it cached, so we don't need to check again
          return True
      else:
        response = self.callMethod("flickr.auth.checkToken", {"auth_token": self.token}, sign = True)
        if response[0]:
          returned_perms = response[1].getElementsByTagName("rsp")[0].getElementsByTagName("perms")[0].childNodes[0].data
          self.token_perms = returned_perms
          if (self.token_perms == perms):
            return True
    return False

  def __makeRESTRequest(self, url, post_data, boundary = None):
    # Make a REST request to Flickr with the url and the post data. Boundary is needed for multipart/form-data

    # Construct the request
    req = urllib2.Request(url)
    req.add_data(post_data)
    if (boundary):
      # We're dealing with multipart/form-data instead of application/x-www-form-urlencoded, ans we should tell our request so
      req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)

    # Get a response
    response = urllib2.urlopen(req).read()
    response_obj = minidom.parseString(response)

    # Return failure or success
    if (response_obj.childNodes[0].getAttribute("stat") == "fail"):
      return [False, response_obj.childNodes[0].childNodes[1].getAttribute("code"), response_obj.childNodes[0].childNodes[1].getAttribute("msg")]
    else:
      return [True, response_obj]

  def __makePost(self, args, sign = False):
    # Construct POST data with api key and such

    # Add the api_key to the args list
    args["api_key"] = self.api_key

    # Calculate the signature
    if (sign):
      args["api_sig"] = self.__getSignature(args)

    return urllib.urlencode(args)

  def __makeImagePost(self, args, filepath):
    # Create the POST data for image uploading, which is a bit different then normal POST data

    # Insert the API key
    args["api_key"] = self.api_key

    # Get the signature
    args["api_sig"] = self.__getSignature(args)

    # Choose a MIME boundary
    boundary = mimetools.choose_boundary()

    # Append all parameters
    post_data = ""
    for key in args.keys():
      post_data += "--%s\r\n" % boundary
      post_data += 'Content-Disposition: form-data; name="' + key + '"\r\n\r\n'
      post_data += "%s\r\n" % args[key]

    post_data = post_data.encode("utf_8")

    # Append the image data
    post_data += "--%s\r\n" % (boundary)
    post_data += 'Content-Disposition: form-data; name=\"photo\"; filename=\"%s\"\r\n' % os.path.split(filepath)[-1]
    post_data += "Content-Type: %s\r\n\r\n" % mimetypes.guess_type(filepath)[0]

    photo = open(filepath).read()
    post_data += photo

    # Add a terminator
    terminator = "\r\n--%s--" % boundary
    terminator = terminator.encode("utf_8")
    post_data += terminator

    return boundary, post_data

  def __getSignature(self, args):
    # Calculate the signature
    keys = args.keys()
    keys.sort()
    sig_str = self.secret
    for key in keys:
      sig_str += key + str(args[key])
    try:
      return hashlib.md5.new(sig_str).hexdigest()
    except:
      return hashlib.md5(sig_str).hexdigest()

class FlickrUploader:
  def __init__(self, conf,showAuthWin):
    self.conf = conf

    # This API key is owned by Mr. Pi and only destined for jbrout!
    api_key = "d17736b0c362f26940281359ed3f1f30"
    secret  = "4875575e0d3f526d"

    # Get a token for uploading pictures from the settings
    try:
      token = self.conf["FR.token"]
    except:
      token = None

    # Get a Flickr api class
    self.flickr = FlickrAPI(api_key, secret, showAuthWin, token)

    # Let it obtain a authentication token for writing and store it in the settings
    if not (self.flickr.checkTokenPerms("write")):
      self.flickr.obtainToken("write")
    if (self.flickr.token):
      self.conf["FR.token"] = self.flickr.token

  def upload(self, filepath, comment, tags, privacy):
    # Upload the photo "filepath" with comment "comment", and tags "tags"
    # to Flickr. Privacy in [int, int, int] (public, friend, family)

    response = self.flickr.upload(filepath, comment, tags, privacy)
    if (response[0] == False):
      return str(response[2])
