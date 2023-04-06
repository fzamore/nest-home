# nest-home

Code that integrates with Google Nest.

## [`camera/capture_snapshot.py`](camera/capture_snapshot.py)

To capture a current snapshot from a Nest camera: `python3 camera/capture_snapshot.py <output_file.jpg>`
 - The camera label will be prepended onto the output filename (e.g., `backyard_output_file.jpg`).

The script does the following:
- Fetches a new access token using the refresh token from the secrets file.
- For each camera in the secrets file:
   - Fetches a `rtsps://` streaming URL using the access token (using `GenerateRtspStream` via the [`executeCommand`](https://developers.google.com/nest/device-access/api) API).
   - Saves a single video frame from that stream using `ffmpeg`.

*Ideally, Google would provide an API to fetch a single video frame (to avoid fetching a streaming URL).*

### Prerequisites:
- Recent version of `ffmpeg` with the ability to handle SSL/TLS.
- Recent version of Python 3.
- Must create `secrets.ini` in the `camera/` directory. See [secrets.ini.sample](camera/secrets.ini.sample) for an example.

### `secrets.ini`

Before running the script, you must add several values to `secrets.ini`. As far as I recall, these are the necessary steps (I'm sure I'm forgetting things, and I had to pay $5 at some point during this process):

1. Create a Google Cloud Project: https://console.cloud.google.com/. 
   1. After creating the project, choose "Create Credentials", then "OAuth2 Client ID". 
   1. Configure the client ID as a Web Application and set any redirect URIs to `https://www.google.com`. 
   1. Note the client ID and add it to `secrets.ini` as **`CLIENT_ID`**.
   1. Choose "Add Secret", and add the resulting secret to `secrets.ini` as **`CLIENT_SECRET`**.
1. Create a Google Nest Project: https://console.nest.google.com/device-access/project-list
   1. Add the project ID to `secrets.ini` as **`PROJECT_ID`**.
   1. Add the (OAuth) client ID from the previous step to the Google Nest Project.
1. Obtain the **`REFRESH_TOKEN`** (for `secrets.ini`) via a series of convoluted steps outlined in this guide: https://developers.google.com/nest/device-access/authorize. 
   1. You will also receive a temporary access token along with the refresh token.
1. After receiving the refresh token and access token, you'll need to make a call to [`devices.list`](https://developers.google.com/nest/device-access/reference/rest/v1/enterprises.devices/list) (see the above guide for details). Add the relevant camera IDs and labels to `secrets.ini` (in the `[cameras]` section).



