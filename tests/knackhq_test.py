"""
KnackHQ Tests
"""
from unittest import mock

import pytest
from knackhq.knackhq import (
    KnackApp,
    KnackObject,
    KnackRecord,
    ObjectCollection,
    RecordCollection,
)
from knackhq.exceptions import (
    ApiResponseError,
    NotFoundError,
    ObjectNotFoundError,
)

KnackApp.APP_ID = "app_id"
KnackApp.API_KEY = "api_key"
KnackApp.ENDPOINT = "https://localhost/v1"


def test_KnackApp_repr():
    app = KnackApp()
    assert repr(app) == "KnackApp(https://localhost/v1)"


def test_RecordCollecion_repr():
    app = KnackApp()
    obj = KnackObject(app, {"key": "object_1"})
    rds = RecordCollection(obj, {})
    assert (
        repr(rds) == "RecordCollection(https://localhost/v1/objects/object_1/records)"
    )


@mock.patch("knackhq.KnackApp.get_objects")
def test_KnackApp_getitem(mock_obs):
    app = KnackApp()
    app["MyObject"]
    mock_obs.return_value.__getitem__.assert_called_once_with("MyObject")


@mock.patch("knackhq.KnackApp.get_objects")
def test_KnackApp_iter(mock_obs):
    mock_obs.return_value = ["object_1", "object_2", "object_3"]
    app = KnackApp()
    assert list(app) == ["object_1", "object_2", "object_3"]


@mock.patch("requests.request")
def test_KnackApp_request(mock_req):
    app = KnackApp()
    app.request("GET", "objects", "object_1")
    mock_req.assert_called_once_with(
        "GET",
        "https://localhost/v1/objects/object_1",
        headers={
            "Content-Type": "application/json",
            "X-Knack-Application-Id": "app_id",
            "X-Knack-REST-API-Key": "api_key",
        },
    )


@mock.patch("requests.request")
def test_KnackApp_get_json(mock_req):
    mock_req.return_value.status_code = 200
    mock_req.return_value.json.return_value = {"fizz": "buzz"}
    app = KnackApp()
    ret = app.get_json("object", "object_1")
    assert ret == {"fizz": "buzz"}


@mock.patch("requests.request")
def test_KnackApp_get_json_400(mock_req):
    mock_req.return_value.status_code = 400
    app = KnackApp()
    with pytest.raises(NotFoundError):
        app.get_json("object", "object_1")


@mock.patch("requests.request")
def test_KnackApp_get_json_4XX(mock_req):
    mock_req.return_value.status_code = 429
    app = KnackApp()
    with pytest.raises(ApiResponseError):
        app.get_json("object", "object_1")


@mock.patch("knackhq.KnackApp.get_json")
def test_KnackApp_get_objects(mock_json):
    mock_json.return_value = {"objects": [{"key": "object_1", "name": "MyObject"}]}
    app = KnackApp()
    ret = app.get_objects()
    assert ret.objects == [{"key": "object_1", "name": "MyObject"}]


@mock.patch("knackhq.KnackApp.get_json")
def test_KnackApp_get_object(mock_json):
    mock_json.return_value = {"object": {"key": "object_1", "name": "MyObject"}}
    app = KnackApp()
    ret = app.get_object("object_1")
    assert ret.object == {"key": "object_1", "name": "MyObject"}


@mock.patch("knackhq.KnackApp.get_json")
def test_KnackApp_get_object_err(mock_json):
    mock_json.return_value = {}
    app = KnackApp()
    with pytest.raises(ObjectNotFoundError):
        app.get_object("object_1")


@mock.patch("knackhq.KnackApp.get_object")
def test_KnackApp_get_records(mock_obj):
    app = KnackApp()
    app.get_records("object_1")
    mock_obj.assert_called_once_with("object_1")


def test_ObjectCollection_str():
    app = KnackApp()
    obs = ObjectCollection(app, [])
    assert str(obs) == "https://localhost/v1/objects"


@mock.patch("knackhq.KnackApp.get_object")
def test_ObjectCollection_getitem_by_key(mock_obj):
    app = KnackApp()
    obs = ObjectCollection(
        app,
        [
            {"key": "object_1", "name": "Object1"},
            {"key": "object_2", "name": "Object2"},
        ],
    )
    obs["object_1"]
    mock_obj.assert_called_once_with("object_1")


@mock.patch("knackhq.KnackApp.get_object")
def test_ObjectCollection_getitem_by_name(mock_obj):
    app = KnackApp()
    obs = ObjectCollection(
        app,
        [
            {"key": "object_1", "name": "Object1"},
            {"key": "object_2", "name": "Object2"},
        ],
    )
    obs["Object2"]
    mock_obj.assert_called_once_with("object_2")


@mock.patch("knackhq.KnackApp.get_object")
def test_ObjectCollection_getitem_err(mock_obj):
    mock_obj.side_effect = ApiResponseError
    app = KnackApp()
    obs = ObjectCollection(
        app,
        [
            {"key": "object_1", "name": "Object1"},
            {"key": "object_2", "name": "Object2"},
        ],
    )
    with pytest.raises(ObjectNotFoundError):
        obs["Object3"]


def test_ObjectCollection_iter():
    app = KnackApp()
    obs = ObjectCollection(
        app,
        [
            {"key": "object_1", "name": "Object1"},
            {"key": "object_2", "name": "Object2"},
        ],
    )
    assert list(obs) == ["object_1", "object_2"]


def test_KnackObject_iter():
    app = KnackApp()
    obj = KnackObject(app, {"key": "object_1", "name": "Object1"})
    assert sorted(list(obj)) == ["key", "name"]


def test_KnackObject_get_records():
    app = KnackApp()
    obj = KnackObject(app, {"key": "object_1", "name": "Object1"})
    rds = obj.get_records()
    assert rds.object == obj
    assert rds.query == {}


@mock.patch("knackhq.knackhq.KnackObject.get_records")
def test_KnackObject_get_record(mock_rds):
    app = KnackApp()
    obj = KnackObject(app, {"key": "object_1", "name": "Object1"})
    rec = KnackRecord(obj, {})
    mock_rds.return_value = [rec]
    assert obj.get_record("record_id") == rec
