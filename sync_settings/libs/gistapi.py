# -*- coding: utf-8 -*-

import requests
import json
from .exceptions import GistException
from .helper import Helper

class Gist:
  BASE_URL = 'https://api.github.com'

  def __init__(self, token):
    response = requests.get(self.BASE_URL + '/user?access_token=' + token)

    if response.status_code != 200:
      raise GistException(Gist.__get_response_error('The entered token is invalid', response))
    else:
      self.__user_data = response.json()
      self.__headers = {
        'X-Github-Username': self.__user_data.get('login'),
        'Content-Type': 'application/json',
        'Authorization': 'token %s' %token
      }
      self.__defaults = {
        'public': False,
        'files': {}
      }

  def create(self, gist_data):
    """Creates a Gist with the specified data

    Arguments:
      gist_data {dict}: Gist data

    Returns:
      [dict]: Response Data in JSON format

    Raises:
      GistException: The Gist cannot be created
    """

    _data = json.dumps(Helper.merge_objects(self.__defaults, gist_data))

    response = requests.post(
      self.BASE_URL + '/gists',
      data = _data,
      headers = self.__headers
    )

    if response.status_code == 201:
      return response.json()

    raise GistException(Gist.__get_response_error('Gist cannot created', response))

  def edit(self, gist_id, gist_data):
    """Edits a Gist with the specified data

    Arguments:
      gist_data {dict}: Gist data

    Returns:
      [dict]: Response Data in JSON format

    Raises:
      GistException: The Gist cannot be edited
    """

    self.__defaults.pop('description', None)
    gist_data = json.dumps(Helper.merge_objects(self.__defaults, gist_data))

    response = requests.patch(
      self.BASE_URL + '/gists/%s' %gist_id,
      data=gist_data,
      headers=self.__headers
    )

    if response.status_code == 200:
      return response.json()

    raise GistException(Gist.__get_response_error('Cannot edit the gist', response))

  def list(self):
    """Gets all Gists of the authenticated user

    Returns:
      [dict]: Response Data in JSON format

    Raises:
      GistException: The info cannot be listed
    """

    base_url = ''.join((
      self.BASE_URL + '/users/',
      self.__user_data.get('login') + '/gists',
    ))

    response = requests.get(base_url, headers=self.__headers)

    if response.status_code == 200:
      return response.json()

    raise GistException(Gist.__get_response_error('It is not possible to list files', response))

  def delete(self, gist_id):
    """Deletes a Gist with the specified ID

    Arguments:
      gist_id {string}: Gist identifier

    Returns:
      [bool]

    Raises:
      GistException: The Gist cannot be deleted
    """

    response = requests.delete(
      self.BASE_URL + '/gists/' + gist_id,
      headers=self.__headers
    )

    if response.status_code == 204:
      return True

    raise GistException(Gist.__get_response_error('The Gist cannot be deleted', response))

  def get(self, gist_id):
    """Gets a specific Gist

    Arguments:
      gist_id {string}: Gist identifier

    Returns:
      [dict]: Response Data in JSON format

    Raises:
      GistException: The Gist cannot be reached or not exists
    """

    base_url = self.BASE_URL + '/gists/' + gist_id

    response = requests.get(base_url, headers=self.__headers)
    if response.status_code == 200:
      return response.json()

    raise GistException(Gist.__get_response_error('The Gist cannot be reached or not exists', response))

  @staticmethod
  def __get_response_error(message, response):
    """Converts the response data

    Arguments:
      message {string}: Response error message
      response {HttpResponse}: Object of the current response
    """

    rjson = response.json()
    error_description = "Code %s - %s" %(str(response.status_code), rjson.get('message'))

    return {
      'app_message': "%s - %s" % (error_description, message),
      'error_description': "[%s] - %s" % (message, error_description),
      'code': response.status_code
    }
