
""" KnackHQ REST Client. """

import collections
import os
import json
import urllib

import certifi
import urllib3


class KnackHQObject(collections.Mapping):
    """ KnackHQ Object (ie, table).

        Arguments:
            client (KnackHQClient):  KnackHQClient instance
            url    (str):            URL to object resource

        Iterate over records in an object with:

            for record in object:
                # do something

        Iterate over filtered records in an object with:

            filters = [
                {
                    field: 'field_1',
                    operator: 'is',
                    value: 'test'
                }, {
                    field: 'field_2',
                    operator: 'is not blank'
                }
            ]

            for record in object.where(*filters):
                # do something
    """
    def __init__(self, client, url):
        self.client = client
        self.url = url
        self.__object = None

    @property
    def _object(self):
        """ Memoized response of a GET on the object. """
        if self.__object is None:
            self.__object = self.client.request(self.url)
        return self.__object

    def __getitem__(self, key):
        return self._object[key]

    def __iter__(self):
        return self.where()

    def __len__(self):
        page = self.records()
        return page['total_records']

    def get_url(self, *path):
        """ Helper to get URL of object or its children

            Arguments:
                path (tuple):  Optional additional children

            Returns:
                URL string for object-resource.
        """
        return self.client.get_url('objects', self.key(), *path)

    def key(self):
        """ Helper to get object key (eg, object_123). """
        return self['object']['key']

    def fields(self):
        """ Helper to get fields of object. """
        return self['object']['fields']

    def field_key(self, name):
        """ Helper to get field key from field name for object-fields.

            Arguments:
                name (str):  Name of object-field

            Returns:
                key of field (eg. field_123).

            Raises:
                KeyError on field not found.
        """
        for field in self.fields():
            if field['name'] == name:
                return field['key']
        raise KeyError

    def records(self, **kwargs):
        """ Get records from a REST request.

            Arguments:
                page          (int):   Optional page number
                rows_per_page (int):   Optional rows per page number
                sort_field    (str):   Optional sort field key
                sort_order    (str):   Optional sort order
                filters       (list):  Optional list of filter dicts

            Returns:
                REST response JSON dict.
        """
        url = self.client.get_url('objects', self.key(), 'records')
        url += '?'
        for key, val in kwargs.iteritems():
            if key == 'filters':
                val = urllib.quote_plus(json.dumps(val))
            url += "%s=%s&" % (key, val)
        return self.client.request(url)

    def record(self, record_id):
        """ Get record by ID.

            Arguments:
                record_id (str):  Record ID string

            Returns:
                REST response JSON dict.
        """
        url = self.client.get_url('objects', self.key(), 'records', record_id)
        return self.client.request(url)

    def where(self, *filters):
        """ Iterate over object records with filters.

            Arguments:
                filters (tuple):  Optional tuple of filter dicts

            Returns:
                Iterator of filtered results.
        """
        filters = list(filters) or None
        page = self.records(filters=filters)
        current_page = int(page['current_page'])
        total_pages = int(page['total_pages'])
        while current_page <= total_pages:
            for record in page['records']:
                yield record
            page = self.records(page=current_page+1, filters=filters)
            current_page = int(page['current_page'])
            total_pages = int(page['total_pages'])


class KnackHQClient(object):
    """ KnackHQ root client.

        Arguments:
            app_id   (str):  Application ID string
            api_key  (str):  API key
            endpoint (str):  Optional KnackHQ endpoint
    """
    def __init__(self, app_id, api_key, endpoint='https://api.knackhq.com/v1'):
        self.app_id = app_id
        self.api_key = api_key
        self.endpoint = endpoint

    @property
    def headers(self):
        """ Helper to define request headers. """
        return {
            "Content-Type": "application/json",
            "X-Knack-Application-Id": self.app_id,
            "X-Knack-REST-API-Key": self.api_key
        }

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
        resp = http.request(verb, url, headers=self.headers, **kwargs)
        try:
            return json.loads(resp.data)
        except ValueError as err:
            err.message += "\n%s" % resp.data
            raise err

    def get_url(self, *path):
        """ Helper to get URL of object or its children

            Arguments:
                path (tuple):  Optional additional children

            Returns:
                URL string for object-resource.
        """
        return os.path.join(self.endpoint, *path)

    def get_objects(self):
        """ Get all objects for app. """
        url = self.get_url('objects')
        return self.request(url)

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
        url = self.get_url('objects', key)
        return KnackHQObject(self, url)

    def get_object_key(self, name):
        """ Helper to get object key from object name.

            Arguments:
                name (str):  Name of object

            Returns:
                Key of object.

            Raises:
                KeyError on object not found.
        """
        objects = self.get_objects()
        for obj in objects['objects']:
            if obj['name'] == name:
                return obj['key']
        raise KeyError
