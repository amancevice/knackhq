
""" KnackHQ REST Client. """


import collections
import json
import os

import certifi
import urllib3
from .knackhq import KnackHQObject


class KnackHQClient(collections.Iterable):
    """ KnackHQ root client.

        Use arguments or ENV variables to initialize client.

        Optional ENV variables are:
            * KNACKHQ_APP_ID
            * KNACKHQ_API_KEY
            * KNACKHQ_ENDPOINT

        Arguments:
            app_id   (str):  Application ID string
            api_key  (str):  API key
            endpoint (str):  KnackHQ endpoint (default: https://api.knackhq.com/v1)
    """
    @property
    def _headers(self):
        """ Helper to define request headers. """
        return {
            "Content-Type": "application/json",
            "X-Knack-Application-Id": self._app_id,
            "X-Knack-REST-API-Key": self._api_key
        }

    def __init__(self, app_id=None, api_key=None, endpoint=None):
        self._app_id = app_id or os.getenv('KNACKHQ_APP_ID')
        self._api_key = api_key or os.getenv('KNACKHQ_API_KEY')
        self._endpoint = endpoint or os.getenv('') \
            or os.getenv('KNACKHQ_ENDPOINT') \
            or 'https://api.knackhq.com/v1'

    def __repr__(self):
        return "<KnackHQClient %s>" % self._endpoint

    def __iter__(self):
        return self.get_objects()

    def __len__(self):
        len(list(self))

    def endpoint(self, *path):
        """ Helper to get URL of object or its children

            Arguments:
                path (tuple):  Optional additional children

            Returns:
                URL string for object-resource.
        """
        return os.path.join(self._endpoint, *path)

    def request(self, url, verb='GET', **kwargs):
        """ Send a request to the API.

            Arguments:
                url    (str):   URL for request
                verb   (str):   Optional verb of request
                kwagrs (dict):  Optional additional request arguments

            Returns:
                JSON response of request.

            Raises:
                ValueError on bad response.
        """
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        resp = http.request(verb, url, headers=self._headers, **kwargs)
        try:
            return json.loads(resp.data)
        except ValueError as err:
            err.message += "\n%s" % resp.data
            raise err

    def get_objects(self, name=None):
        """ Yield a collection of objects. If a name is supplied only objects
            with that name are returned.

            Arguments:
                name (str):  Optional name filter for objects

            Returns:
                Iterator of KnackHQObjects
        """
        for item in self.request(self.endpoint('objects')).get('objects', []):
            if name is None or item['name'] == name:
                yield KnackHQObject(self, item['key'])

    def get_object(self, key=None, name=None):
        """ Get object by key or name. If a key is not provided it
            will be found by filtering on all objects. It is more
            efficient to use the key for getting objects.

            Arguments:
                key  (str):  Object key
                name (str):  Object name

            Returns:
                KnackHQObject instance.

            Raises:
                KeyError if object not found when finding by name.
        """
        if key is None:
            key = self.get_object_key(name)
        return KnackHQObject(self, key)

    def get_object_key(self, name):
        """ Helper to get object key from object name.

            Arguments:
                name (str):  Name of object

            Returns:
                Key of object.

            Raises:
                KeyError on object not found.
        """
        objects = list(self.get_objects(name))
        if len(objects) == 1:
            return objects[0].key
        elif len(objects) > 1:
            raise KeyError("More than one object named '%s'" % name)
        raise KeyError
