# knackhq

Python wrapper for [KnackHQ API](http://knackhq.com/)

<img src="https://travis-ci.org/amancevice/knackhq.svg?branch=master"/>


## Installation

```bash
pip install knackhq
```


## Connect to KnackHQ

Create a `KnackHQClient` instance to begin interacting with KnackHQ. Supply an app ID, an API key, and an optional API endpoint URL to the client. Alternatively, set these values in your environment with:

* `KNACKHQ_APP_ID`
* `KNACKHQ_API_KEY`
* `KNACKHQ_ENDPOINT`

```python
import knackhq

# KNACKHQ_APP_ID = <set in ENV>
# KNACKHQ_API_KEY = <set in ENV>
# KNACKHQ_ENDPOINT = <set in ENV>

client = knackhq.KnackHQClient()
```


## Reading from KnackHQ


### Raw requests

In some cases you may wish to send a raw HTTP request to the KnackHQ JSON API. This will not normally be necessary but it is available:

```python
client.request("https://api.knackhq.com/v1/objects/object_1", 'GET')
client.request("https://api.knackhq.com/v1/objects/object_1", 'POST', body='{key: val}')
```


### Reading Objects

Iterate over objects in an app using the `client` object:

```python
for obj in client:
    print obj

# => <KnackHQObject /v1/objects/object_1>
#    <KnackHQObject /v1/objects/object_2>
#    <KnackHQObject /v1/objects/object_3>
#    ...
#    <KnackHQObject /v1/objects/object_n>
```

Or, find an object by its key:

```python
obj = client.get_object('object_1')
```

If you are unsure of the key, use the `name` keyword argument to get the object by its name:

```python
obj = client.get_object(name='Customers')
```

Find metadata keys using the `keys()` function. Get metadata on an object using brackets (`[]`):

```python
obj.keys()

# => ['status',
#     'tasks',
#     'name',
#     'inflections',
#     'fields',
#     'connections',
#     'user',
#     'key',
#     '_id']

obj['key']

# => 'object_1'
```


### Reading Records

Iterate over records in an object:

```python
for record in obj:
    print record

# => <KnackHQRecord /v1/objects/object_1/records/...>
#    <KnackHQRecord /v1/objects/object_2/records/...>
#    <KnackHQRecord /v1/objects/object_3/records/...>
#    ...
#    <KnackHQRecord /v1/objects/object_n/records/...>
```

Use the `where()` function to filter records. Where accepts the following keyword-arguments:

* `record_id`
* `page`
* `rows_per_page`
* `sort_field`
* `sort_order`
* `filters`

If `record_id` is provided (and the record exists) `where(record_id=<id>)` will yield a collection of length 1.

Use `filters` to refine your search:

```python
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

for record in obj.where(filters=filters):
    print record

# => <KnackHQRecord /v1/objects/object_1/records/...>
#    <KnackHQRecord /v1/objects/object_2/records/...>
#    <KnackHQRecord /v1/objects/object_3/records/...>
#    ...
#    <KnackHQRecord /v1/objects/object_n/records/...>
```


## Writing to KnackHQ

*TODO*
