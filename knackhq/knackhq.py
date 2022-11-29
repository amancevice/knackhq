"""
KnackHQ Application Client.
"""
import json
import os
from collections import abc

import requests

from knackhq import exceptions


class KnackIterable(abc.Iterable):
    """
    Base KnackHQ Iterable Python object.
    """

    def __repr__(self):
        return "{cls}({self})".format(cls=type(self).__name__, self=self)


class KnackMapping(abc.Mapping):
    """
    Base KnackHQ Mapping Python object.
    """

    def __repr__(self):
        return "{cls}({self})".format(cls=type(self).__name__, self=self)


class KnackApp(KnackMapping):
    """
    KnackHQ Application.

    Use arguments or ENV variables to initialize client.

    Optional ENV variables are:
    - KNACKHQ_APP_ID
    - KNACKHQ_API_KEY
    - KNACKHQ_ENDPOINT

    :param str app_id: Application ID string
    :param str api_key: API key
    :param str endpoint: KnackHQ endpoint
    """

    APP_ID = os.getenv("KNACKHQ_APP_ID")
    API_KEY = os.getenv("KNACKHQ_API_KEY")
    ENDPOINT = os.getenv("KNACKHQ_ENDPOINT", "https://api.knackhq.com/v1")

    def __init__(self, app_id=None, api_key=None, endpoint=None):
        self.app_id = app_id or self.APP_ID
        self.api_key = api_key or self.API_KEY
        self.endpoint = endpoint or self.ENDPOINT
        self.headers = {
            "Content-Type": "application/json",
            "X-Knack-Application-Id": self.app_id,
            "X-Knack-REST-API-Key": self.api_key,
        }

    def __str__(self):
        return self.endpoint

    def __getitem__(self, object_key):
        return self.get_objects()[object_key]

    def __iter__(self):
        for object_key in self.get_objects():
            yield object_key

    def __len__(self):
        return len(self.get_objects())

    def request(self, method, *path):
        """
        Get the raw response of an API request.

        :param str method: Request verb
        :param str path: Path to API endpoint (eg, 'objects/object_1')
        :returns: response object
        """
        uri = os.path.join(self.endpoint, *path)
        response = requests.request(method, uri, headers=self.headers)
        return response

    def get_json(self, *path):
        """
        Get the JSON response of an API request.

        :param str path:  Path to API endpoint (eg, 'objects/object_1')
        :returns dict: JSON response
        :raises NotFoundError: Status code is 400
        :raises ApiResponseError: Status code is not 200 or 400
        """
        response = self.request("GET", *path)

        # Return response JSON
        if response.status_code == 200:
            return response.json()

        # Raise NotFoundError
        elif response.status_code == 400:
            raise exceptions.NotFoundError

        # Raise API error
        headers = {x: y for x, y in response.headers.items() if x.startswith("X-")}
        err = {
            "Status Code": response.status_code,
            "Headers": headers,
        }
        msg = json.dumps(err, indent=4, sort_keys=True)
        raise exceptions.ApiResponseError(msg)

    def get_objects(self):
        """
        Get an ObjectCollection instance.
        """
        return ObjectCollection(self, **self.get_json("objects"))

    def get_object(self, object_key):
        """
        Get a KnackObject instance.

        :param str object_key: KnackHQ object key
        :returns KnackObject: KnackObject instance
        """
        obj = self.get_json("objects", object_key)
        if not obj:
            raise exceptions.ObjectNotFoundError(object_key)
        return KnackObject(self, obj["object"])

    def get_records(self, object_key, **query):
        """
        Get a RecordCollection instance.

        Use the query parameter to define KnackHQ API query parameters.

        :param str object_key:  KnackHQ object key
        :param dict query: KnackHQ API query parameters
        :returns RecordCollection: RecordCollection instance

        :Example:
        >>> app.get_records(
                'object_1',
                filters=[
                    {
                        'field': 'field_1',
                        'operator': 'is',
                        'value': 'test',
                    },
                    {
                        'field': 'field_2',
                        'operator': 'is not blank',
                    },
                ],
            )
        """
        return RecordCollection(self.get_object(object_key), query)


class ObjectCollection(KnackMapping):
    """
    Collection of KnackHQ Objects.
    """

    def __init__(self, app, objects):
        self.app = app
        self.objects = objects
        self._keys = {x["key"]: x["name"] for x in self.objects}
        self._names = {x["name"]: x["key"] for x in self.objects}

    def __str__(self):
        return os.path.join(str(self.app), "objects")

    def __getitem__(self, object_key):
        if object_key not in self._keys and object_key in self._names:
            object_key = self._names[object_key]
        try:
            return self.app.get_object(object_key)
        except exceptions.ApiResponseError:
            raise exceptions.ObjectNotFoundError(object_key)

    def __iter__(self):
        for obj in self.objects:
            yield obj["key"]

    def __len__(self):
        return len(self.objects)


class KnackObject(KnackMapping):
    """
    KnackHQ Object.
    """

    def __init__(self, app, obj):
        self.app = app
        self.object = obj

    def __str__(self):
        return os.path.join(str(self.app), "objects", self["key"])

    def __getitem__(self, object_key):
        return self.object[object_key]

    def __iter__(self):
        for item in self.object:
            yield item

    def __len__(self):
        return len(self.object)

    def get_records(self, **query):
        """
        Get a RecordCollection instance.

        Use the query parameter to define KnackHQ API query parameters.

        :param str object_key: KnackHQ object key
        :param dict query: KnackHQ API query parameters
        :returns RecordCollection: RecordCollection instance

        :Example:
        >>> obj.get_records(
                'object_1', filters=[
                    {
                        'field': 'field_1',
                        'operator': 'is',
                        'value': 'test',
                    },
                    {
                        'field': 'field_2',
                        'operator': 'is not blank',
                    },
                ],
            )

        """
        return RecordCollection(self, query)

    def get_record(self, record_id):
        """
        Get single KnackRecord instance.

        :param str record_id: KnackHQ record ID
        :returns KnackRecord: KnackRecord instance
        """
        for record in self.get_records(record_id=record_id):
            return record


class RecordCollection(KnackIterable):
    """
    Collection of KnackHQ Object Records.
    """

    def __init__(self, obj, query):
        self.object = obj
        self.app = self.object.app
        self.query = query

    def __str__(self):
        return os.path.join(str(self.object), "records")

    def __iter__(self):
        qry = requests.compat.urlencode(self.query)
        response = self.app.get_json(
            "objects",
            self.object["key"],
            "records?{qry}".format(qry=qry),
        )
        current_page = response["current_page"]
        total_pages = response["total_pages"]

        for record in response["records"]:
            yield KnackRecord(self.object, record)

        if current_page < total_pages:
            new = self.query.copy()
            new["page"] = new.get("page", 1) + 1
            for record in RecordCollection(self.object, new):
                yield record

    def __len__(self):
        qry = requests.compat.urlencode(self.query)
        response = self.app.get_json(
            "objects",
            self.object["key"],
            "records?{qry}".format(qry=qry),
        )
        return response["total_records"]


class KnackRecord(KnackMapping):
    """
    KnackHQ Record.
    """

    def __init__(self, obj, record):
        self.object = obj
        self.record = record

    def __str__(self):
        return os.path.join(str(self.object), "records", self.record["id"])

    def __getitem__(self, field_key):
        if field_key not in self.keys():
            fields = {x["name"]: x["key"] for x in self.object["fields"]}
            field_key = fields[field_key]
        return self.record[field_key]

    def __iter__(self):
        for item in self.record:
            yield item

    def __len__(self):
        return len(self.record)
