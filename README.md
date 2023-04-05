# nest-home

Code that integrates with Google Nest.

## camera/

- To capture a current snapshot from a Nest camera: `python camera/capture_snapshot.py <output_file.jpg>`

### Pre-requisites:
- Recent version `ffmpeg` with the ability to handle SSL/TLS.
- Recent version of Python 3.
- Must create `secrets.ini` in the `camera/` directory. See [secrets.ini.sample](camera/secrets.ini.sample) for an example.

