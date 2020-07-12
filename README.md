# KnackHQ

![pypi](https://img.shields.io/pypi/v/knackhq?color=yellow&logo=python&logoColor=eee&style=flat-square)
![python](https://img.shields.io/pypi/pyversions/knackhq?logo=python&logoColor=eee&style=flat-square)
[![pytest](https://img.shields.io/github/workflow/status/amancevice/knackhq/pytest?logo=github&style=flat-square)](https://github.com/amancevice/knackhq/actions)
[![coverage](https://img.shields.io/codeclimate/coverage/amancevice/knackhq?logo=code-climate&style=flat-square)](https://codeclimate.com/github/amancevice/knackhq/test_coverage)
[![maintainability](https://img.shields.io/codeclimate/maintainability/amancevice/knackhq?logo=code-climate&style=flat-square)](https://codeclimate.com/github/amancevice/knackhq/maintainability)

Python wrapper for [KnackHQ API](https://www.knack.com/developer-documentation/)

## Installation

```bash
pip install knackhq
```


## Connect to KnackHQ

Create a `KnackApp` instance to begin interacting with KnackHQ. Supply an app ID, an API key, and an optional API endpoint URL to the client:

```python
import knackhq

app = knackhq.KnackApp('<app_id>', '<api_key>')
```

Alternatively, set these values in your environment with:

* `KNACKHQ_APP_ID`
* `KNACKHQ_API_KEY`
* `KNACKHQ_ENDPOINT` (optional)

```python
app = knackhq.KnackApp()
```


## Reading from KnackHQ


### Raw requests

You may wish to send a raw request response from the KnackHQ API:

```python
app.request('GET', 'objects/object_1/records')  # or,
app.request('GET', 'objects', 'object_1', 'records')
```


### Getting Objects

Use dictionary syntax to get objects by name or key:

```python
obj = app['object_1']  # or,
obj = app['MyObject']
```

Access object metadata using dictionary syntax:

```python
obj['name']
obj['key']
obj['fields']
```

### Getting Records

Use the `get_records()` method to iterate over records in an object:

```python
for record in obj.get_records():
    print(record)
```

Supply arguments to `get_records()` to filter records. Options include:
* `record_id`
* `page`
* `rows_per_page`
* `sort_field`
* `sort_order`
* `filters`

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

for record in obj.get_records(filters=filters):
    print(record)
```

If you know the ID of the record, use `get_record()` to return a single record:

```python
record = obj.get_record('1234567890ABCDEF')
```


## Writing Records

*TODO*
