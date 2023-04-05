from collections import namedtuple
import configparser
from http.client import HTTPResponse
import json
import os.path
import subprocess
import sys
from typing import Literal
from urllib.parse import urlencode, urlunparse
from urllib.request import Request, urlopen

# TODO:
# - pass `date +%Y-%m-%d_%H%M` to crontab, e.g., `<script> $(date +%Y-%m-%d_%H%M).jpg`
# - better README that explains how to obtain values for secrets.ini

Camera = namedtuple('Camera', [
    'device_id',
    'label',
])

Secrets = namedtuple('Secrets', [
  'client_id',
  'client_secret',
  'refresh_token',
  'project_id',
  'cameras', # list<Camera>
])

# Builds a URL from the given host, path, and query params. Returns the
# URL as a string.
def buildUrl(hostname: str, path: str, queryParams: dict = {}) -> str:
  # The urlunparse function is terribly documented.
  return urlunparse([
    'https',
    hostname,
    path,
    '', # ???
    urlencode(queryParams),
    '', # anchor
  ])

# Builds a dict of HTTP headers (suitable for passing to Google) using the
# given access token.
def buildHttpHeaders(accessToken: str) -> dict:
  return {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer %s' % accessToken,
  }

# Sends an HTTP request to the given URL, using the given HTTP method,
# HTTP headers, and postdata. Returns an HTTPResponse, or throws if the
# response isn't HTTP status code 200.
def sendHttpRequest(
  url: str,
  method: Literal['GET', 'POST'],
  headers: dict = {},
  postdata: dict = {},
) -> HTTPResponse:
  encodedData = None
  if len(postdata) > 0:
    assert method == 'POST'
    encodedData = bytes(json.dumps(postdata), encoding = 'utf-8')
  req = Request(url, method=method, headers=headers, data=encodedData)
  return urlopen(req)

# Loads secrets from the given secrets file and returns a Secrets object.
def loadSecrets(secretsFile: str) -> Secrets:
  parser = configparser.ConfigParser()
  parser.read(secretsFile)
  section = parser['secrets']
  return Secrets(
    section['CLIENT_ID'],
    section['CLIENT_SECRET'],
    section['REFRESH_TOKEN'],
    section['PROJECT_ID'],
    [Camera(parser['cameras'][label], label) for label in parser['cameras']],
  )

# Return the camera device ID corresponding to the given label from the
# given Secrets object.
def getCameraDeviceID(secrets: Secrets, label: str) -> str:
  label = label.lower()
  assert \
    label in [camera.label for camera in secrets.cameras], \
    'bad camera label: %s' % label
  return [camera.device_id for camera in secrets.cameras if camera.label == label][0]

# Fetches and returns a new access token from Google.
def refreshAccessToken(secrets: Secrets) -> str:
  url = buildUrl('www.googleapis.com', 'oauth2/v4/token', {
    'client_id': secrets.client_id,
    'client_secret': secrets.client_secret,
    'refresh_token': secrets.refresh_token,
    'grant_type': 'refresh_token',
  })

  res = sendHttpRequest(url, 'POST')
  return json.loads(res.read())['access_token']

# Fetches information about a single camera from Google.
def fetchCameraInfo(secrets: Secrets, accessToken: str, label: str) -> dict:
  url = buildUrl(
    'smartdevicemanagement.googleapis.com',
    '/v1/enterprises/%s/devices/%s' % (
      secrets.project_id,
      getCameraDeviceID(secrets, label),
    ),
  )
  res = sendHttpRequest(url, 'GET', buildHttpHeaders(accessToken))
  return json.loads(res.read())

# Fetches an RTSP live stream for the camera with the given label from
# Google.
def fetchCameraStreamUrl(
  secrets: Secrets,
  accessToken: str,
  label: str,
) -> str:
  url = buildUrl(
    'smartdevicemanagement.googleapis.com',
    '/v1/enterprises/%s/devices/%s:executeCommand' % (
      secrets.project_id,
      getCameraDeviceID(secrets, label),
    ),
  )
  res = sendHttpRequest(
    url,
    'POST',
    buildHttpHeaders(accessToken),
    {
      'command': 'sdm.devices.commands.CameraLiveStream.GenerateRtspStream',
      'params': {},
    },
  )
  return json.loads(res.read())['results']['streamUrls']['rtspUrl']

# Saves a single image (to the given output filename) from the given video
# stream using ffmpeg.
def saveImageFromStream(streamUrl: str, filename: str) -> None:
  cmd = 'ffmpeg -i %s -vframes 1 %s' % (streamUrl, filename)
  # We want it to throw errors if the process fails.
  subprocess.run(cmd, shell=True, check=True)

# Appends the given prefix to the filename in the given full path.
def getOutputFilename(fullpath: str, prefix: str) -> str:
  dirname = os.path.dirname(fullpath)
  basename = os.path.basename(fullpath)
  return os.path.join(dirname, '%s_%s' % (prefix, basename))

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print()
    print('USAGE: %s <output_file.jpg>' % sys.argv[0])
    print('  The camera label will be prepended onto the output filename.')
    print()
    sys.exit(-1)

  outputPath = sys.argv[1]

  print()
  print('Starting up...')
  print()
  secretsFile = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'secrets.ini',
  )
  secrets = loadSecrets(secretsFile)
  print('Secrets loaded.')

  accessToken = refreshAccessToken(secrets)
  print('Fetched access token:', accessToken)
  print()

  # Provided as an example:
  # info = fetchCameraInfo(secrets, accessToken, 'backyard')
  # print('Fetched camera info:', info)
  # print()

  for camera in secrets.cameras:
    print('Processing camera: %s' % camera.label)
    print()

    streamUrl = fetchCameraStreamUrl(secrets, accessToken, camera.label)
    print('Fetched stream URL:', streamUrl)

    filename = getOutputFilename(outputPath, camera.label)
    try:
      saveImageFromStream(streamUrl, filename)
      print('Saved image: %s' % filename)
      print()
    except subprocess.CalledProcessError as ex:
      print('ERROR SAVING IMAGE:')
      print(ex)

  print('Done.')
