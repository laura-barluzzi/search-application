import os
import time

import requests


# setup
os.system('docker-compose down')
os.system('FLASK_CONFIG_TESTING=True docker-compose up --build -d')
time.sleep(60)


# tests
response = requests.post('http://localhost:8080/api/documents',
                         json={'document': 'hello'})
assert not response.ok, \
    'FAILED TEST no auth token is error'

response = requests.post('http://localhost:8080/api/documents',
                         headers={'X-Access-Token': 'wrong-token'},
                         json={'document': 'hello'})
assert not response.ok, \
    'FAILED TEST wrong auth token is error'

response = requests.post(
    'http://localhost:8080/api/documents',
    headers={'X-Access-Token': 'test-access-token'},
    json={'document': 'hello'})
assert response.ok and response.json()['status'] == 'created', \
    'FAILED TEST can create documents 1'

response = requests.post(
    'http://localhost:8080/api/documents',
    headers={'X-Access-Token': 'test-access-token'},
    json={'document': 'hello world'})
assert response.ok and response.json()['status'] == 'created', \
    'FAILED TEST can create documents 2'

response = requests.post(
    'http://localhost:8080/api/documents',
    headers={'X-Access-Token': 'test-access-token'},
    json={'document': 'world'})
assert response.ok and response.json()['status'] == 'created', \
    'FAILED TEST can create documents 3'

time.sleep(10)

response = requests.get(
  'http://localhost:8080/api/documents/search/hello',
  headers={'X-Access-Token': 'test-access-token'})
assert response.ok and len(response.json()['results']) == 2, \
    'FAILED TEST can query documents 1'

response = requests.get(
  'http://localhost:8080/api/documents/search/hello%20world',
  headers={'X-Access-Token': 'test-access-token'})
assert response.ok and len(response.json()['results']) == 3, \
    'FAILED TEST can query documents 2'

response = requests.get(
  'http://localhost:8080/api/documents/search/unknown%20word',
  headers={'X-Access-Token': 'test-access-token'})
assert response.ok and len(response.json()['results']) == 0, \
    'FAILED TEST can query documents 3'


# teardown
os.system('docker-compose down')
