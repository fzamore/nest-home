# nest-home

Code that integrates with Google Nest.

## [`camera/capture_snapshot.py`](camera/capture_snapshot.py)

To capture a current snapshot from a Nest camera: `python3 camera/capture_snapshot.py <output_file.jpg>`
 - The camera label will be prepended onto the output filename (e.g., `backyard_output_file.jpg`).

The script does the following:
- Fetches a new access token using the refresh token from the secrets file.
- For each camera in the secrets file:
- - Fetches a live `rtsps://` streamiing URL for the camera using the access token.
- - Saves a single video frame from that stream using `ffmpeg`.

Ideally, Google would provide an API to fetch a single video frame (so we could avoid fetching a streaming URL).

### Pre-requisites:
- Recent version `ffmpeg` with the ability to handle SSL/TLS.
- Recent version of Python 3.
- Must create `secrets.ini` in the `camera/` directory. See [secrets.ini.sample](camera/secrets.ini.sample) for an example.

### `secrets.ini`

Before running the script, you must add several values to `secrets.ini`. 

Use this guide as a reference: https://developers.google.com/nest/device-access/authorize.

