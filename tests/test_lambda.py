# from function.put_object import handler
# import json
# from os import path
# import pytest


# @pytest.fixture
# def test_event():
#     with open(path.join(path.dirname(__file__), "event.json"), "r") as f:
#         event = json.load(f)
#     return event


# def test_lambda_handler(test_event):
#     response = handler(test_event, None)
#     assert response is not None
