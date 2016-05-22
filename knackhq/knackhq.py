""" KnackHQ Objects/Records """


import collections
import json
import os
import re
import urllib

from urlparse import urlparse


class KnackHQRecord(collections.Mapping):
    """ KnackHQ Record.
    """
    @property
    def object(self):
        """ Memoized response of a GET on the record parent. """
        if self._object is None:
            endpoint = re.split(r'/records/.*?', self._endpoint)[0]
            self._object = KnackHQObject(self._client, endpoint)
        return self._object

    @property
    def record(self):
        """ Memoized response of a GET on the record. """
        if self._record is None:
            self._record = self._client.request(self._endpoint)
        return self._record

    def __init__(self, client=None, endpoint=None, record=None):
        self._client = client
        self._endpoint = endpoint
        self._object = None
        self._record = record

    def __repr__(self):
        return "<KnackHQRecord %s>" % urlparse(self._endpoint).path

    def __getitem__(self, key):
        try:
            return self.record[key]
        except KeyError:
            fields = [x for x in self.object['fields'] if x['name'] == key]
            if len(fields) == 1:
                field_key = fields[0]['key']
                field_raw = "%s_raw" % field_key
                is_field = lambda x: x in (field_key, field_raw)
                return dict([(key, val) for key, val in self.record.iteritems() if is_field(key)])

            raise KeyError("More than one field named '%s'" % key)

    def __iter__(self):
        return iter(self.record)

    def __len__(self):
        return len(self.record)


class KnackHQObject(collections.Iterable):
    """ KnackHQ Object (ie, table).

        Arguments:
            client   (Client):  KnackHQ Client instance
            endpoint (str):     URL to object resource

        Iterate over records in an object with:

            for record in object:
                # do something

        Iterate over filtered records in an object with:

            filters = [
                {
                    'field':    'field_1',
                    'operator': 'is',
                    'value':    'test'
                }, {
                    'field':    'field_2',
                    'operator': 'is not blank'
                }
            ]

            for record in object.where(filters=filters):
                # do something
    """
    @property
    def object(self):
        """ Memoized response of a GET on the object. """
        if self._object is None:
            self._object = self._client.request(self._endpoint)['object']
        return self._object

    # pylint: disable=redefined-builtin
    def __init__(self, client=None, endpoint=None, object=None):
        self._client = client
        self._endpoint = endpoint
        self._object = object

    def __repr__(self):
        return "<KnackHQObject %s>" % urlparse(self._endpoint).path

    def __getitem__(self, key):
        return self.object[key]

    def __iter__(self):
        return self.where()

    def __len__(self):
        endpoint = os.path.join(self._endpoint, 'records')
        try:
            page = self._client.request(endpoint)
            return page['total_records']
        except ValueError:
            return 0

    def keys(self):
        """ Return keys of KnackHQ object definiton. """
        return self.object.keys()

    def where(self, **kwargs):
        """ Get records from a REST request.

            Iterate over filtered records in an object with:

                filters = [
                    {
                        'field':    'field_1',
                        'operator': 'is',
                        'value':    'test'
                    }, {
                        'field':    'field_2',
                        'operator': 'is not blank'
                    }
                ]

                for record in object.where(filters=filters):
                    # do something

            Arguments:
                record_id     (str):   Optional ID of record
                page          (int):   Optional page number
                rows_per_page (int):   Optional rows per page number
                sort_field    (str):   Optional sort field key
                sort_order    (str):   Optional sort order
                filters       (list):  Optional list of filter dicts

            Returns:
                REST response JSON dict.
        """
        # Yield single record
        if 'record_id' in kwargs:
            record_id = kwargs['record_id']
            endpoint = os.path.join(self._endpoint, 'records', record_id)
            yield KnackHQRecord(self._client, endpoint)

        # Yield records
        else:
            endpoint = os.path.join(self._endpoint, 'records')
            endpoint += '?'
            for key, val in kwargs.iteritems():
                if key == 'filters':
                    val = urllib.quote_plus(json.dumps(val))
                endpoint += "%s=%s&" % (key, val)

            # Yield records
            try:
                page = self._client.request(endpoint)
            except ValueError:
                raise StopIteration
            for record in page['records']:
                endpoint = os.path.join(self._endpoint, 'records', record['id'])
                yield KnackHQRecord(self._client, endpoint, record)

            # Recurse
            kwargs['page'] = int(page['current_page']) + 1
            self.where(**kwargs)
