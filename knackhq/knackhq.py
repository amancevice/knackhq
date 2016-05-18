""" KnackHQ Objects/Records """


import collections
import os
import json
import urllib

from urlparse import urlparse


class KnackHQRecord(collections.Mapping):
    """ KnackHQ Record.
    """
    @property
    def record(self):
        """ Memoized response of a GET on the record. """
        if self._record is None:
            self._record = self.object.client.request(self.url.geturl())
        return self._record

    @property
    def object(self):
        """ Get parent KnackHQObject. """
        return self._object

    def __init__(self, knackobj, url, record=None):
        self._object = knackobj
        self._record = record
        self.url = urlparse(url)

    def __getitem__(self, key):
        return self.record[key]

    def __iter__(self):
        return iter(self.record)

    def __len__(self):
        return len(self.record)

    def get_field(self, key):
        """ Get value of record field by field key. """
        fields = [x for x in self.object['fields'] if x['name'] == key]
        if len(fields) == 1:
            field_key = fields[0]['key']
            field_raw = "%s_raw" % field_key
            is_field = lambda x: x in (field_key, field_raw)
            return dict([(key, val) for key, val in self.record.iteritems() if is_field(key)])

        raise KeyError("More than one field named '%s'" % key)


class KnackHQObject(collections.Iterable):
    """ KnackHQ Object (ie, table).

        Arguments:
            client (Client):  KnackHQ Client instance
            url    (str):     URL to object resource

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
    @property
    def object(self):
        """ Memoized response of a GET on the object. """
        if self._object is None:
            self._object = self.client.request(self.url.geturl())['object']
        return self._object

    def __init__(self, client, key):
        self.client = client
        self._len = None
        self._object = None
        self.key = key
        self.url = urlparse(self.client.endpoint('objects', key))

    def __repr__(self):
        return "<%s %s>" % (self['name'], self.url.path)

    def __getitem__(self, key):
        return self.object[key]

    def __iter__(self):
        return self.get_records()

    def __len__(self):
        if self._len is None:
            page = self.get_records().next()
            self._len = page['total_records']
        return self._len

    def get_records(self, **kwargs):
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
        url = self.client.endpoint('objects', self.key, 'records')
        url += '?'
        for key, val in kwargs.iteritems():
            if key == 'filters':
                val = urllib.quote_plus(json.dumps(val))
            url += "%s=%s&" % (key, val)
        try:
            page = self.client.request(url)
        except ValueError:
            raise StopIteration
        record_url = urlparse(url).path
        for record in page['records']:
            record_url = os.path.join(self.url.geturl(), 'records', record['id'])
            yield KnackHQRecord(self, record_url, record)
        kwargs['page'] = int(page['current_page']) + 1
        self.get_records(**kwargs)

    def get_record(self, record_id):
        """ Get record by ID.

            Arguments:
                record_id (str):  Record ID string

            Returns:
                REST response JSON dict.
        """
        url = self.client.endpoint(self.url.path.lstrip('/'), 'records', record_id)
        return self.client.request(url)

    def keys(self):
        """ Return keys of KnackHQ object definiton. """
        return self.object.keys()

