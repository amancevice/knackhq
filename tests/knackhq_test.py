"""
KnackHQ Tests
"""
import mock
from knackhq.knackhq import *


def test_KnackApp_repr():
    app = KnackApp(endpoint='https://localhost/v1')
    assert repr(app) == 'KnackApp(https://localhost/v1)'


def test_RecordCollecion_repr():
    app = KnackApp(endpoint='https://localhost/v1')
    obj = KnackObject(app, key='object_1')
    rds = RecordCollection(obj, {})
    assert repr(rds) == \
        'RecordCollection(https://localhost/v1/objects/object_1/records)'


@mock.patch('requests.request')
def test_KnackApp_request(mock_req):
    app = KnackApp('app_id', 'api_key', 'https://localhost/v1')
    app.request('GET', 'objects', 'object_1')
    mock_req.assert_called_once_with(
        'GET',
        'https://localhost/v1/objects/object_1',
        headers={'Content-Type': 'application/json',
                 'X-Knack-Application-Id': 'app_id',
                 'X-Knack-REST-API-Key': 'api_key'})


@mock.patch('requests.request')
def test_KnackApp_get_json(mock_req):
    mock_res = mock.MagicMock()
    mock_req.return_value = mock_res
    mock_res.status_code = 200
    mock_res.json.return_value = {'fizz': 'buzz'}
    app = KnackApp(endpoint='https://localhost/v1')
    ret = app.get_json('object', 'object_1')
    assert ret == {'fizz': 'buzz'}


@mock.patch('knackhq.KnackApp.get_json')
def test_KnackApp_get_objects(mock_json):
    mock_json.return_value = {'objects': [{'key': 'object_1',
                                           'name': 'MyObject'}]}
    app = KnackApp(endpoint='https://localhost/v1')
    ret = app.get_objects()
    assert ret.objects == [{'key': 'object_1', 'name': 'MyObject'}]


@mock.patch('knackhq.KnackApp.get_json')
def test_KnackApp_get_object(mock_json):
    mock_json.return_value = {'object': {'key': 'object_1',
                                         'name': 'MyObject'}}
    app = KnackApp(endpoint='https://localhost/v1')
    ret = app.get_object('object_1')
    assert ret.object == {'key': 'object_1', 'name': 'MyObject'}
