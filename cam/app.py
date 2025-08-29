import io
import logging
from threading import Condition

from flask import Flask, Response
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Global variables for camera and output
picam2 = None
output = None

class StreamingOutput(io.BufferedIOBase):
    """
    Custom output class for picamera2. It buffers frames in memory and
    uses a condition variable to notify waiting threads when a new frame is available.
    """
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)

def generate_frames():
    """Generator function to yield camera frames for the HTTP response."""
    global output
    while True:
        with output.condition:
            # Wait until a new frame is available
            output.condition.wait()
            frame = output.frame
        # Yield the frame in the multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Serves the main HTML page with the video stream."""
    # A simple HTML page with an img tag that points to the video feed
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
    # Returns a multipart response, which is the standard for streaming video
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def start_camera():
    """Initializes and starts the camera."""
    global picam2, output
    picam2 = Picamera2()
    # Configure the camera for video recording
    video_config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(video_config)
    
    # The output object that will receive the frames
    output = StreamingOutput()
    
    # Start recording to our custom output, using a JPEG encoder
    picam2.start_recording(JpegEncoder(), FileOutput(output))
    logging.info("Camera started and recording.")

if __name__ == '__main__':
    try:
        start_camera()
        # Start the Flask web server
        # host='0.0.0.0' makes it accessible on the local network
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Ensure the camera is stopped cleanly on exit
        if picam2:
            picam2.stop_recording()
            logging.info("Camera stopped.")
