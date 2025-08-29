import io
import logging
from threading import Condition

from flask import Flask, Response
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

picam2 = None
output = None


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)


def generate_frames():
    global output
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    """Serves the main HTML page with the video stream."""
    return """<html>
  <head>
    <title>Picamera2 MJPEG Streaming</title>
  </head>
  <body>
    <h1>Picamera2 MJPEG Streaming</h1>
    <img src="/video_feed" style="width:640px; height:480px;">
  </body>
</html>"""


@app.route('/video_feed')
def video_feed():
    """The video streaming route."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def start_camera():
    """Initializes and starts the camera."""
    global picam2, output
    picam2 = Picamera2()
    picam2.set_controls({"Saturation": 0.0})
    video_config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(video_config)
    
    output = StreamingOutput()
    
    picam2.start_recording(JpegEncoder(), FileOutput(output))
    logging.info("Camera started and recording.")


if __name__ == '__main__':
    try:
        start_camera()
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if picam2:
            picam2.stop_recording()
            logging.info("Camera stopped.")
