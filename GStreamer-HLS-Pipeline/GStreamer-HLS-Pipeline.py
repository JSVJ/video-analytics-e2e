# Trying to get an RTSP server from mobile camera and giving a HLS output
# http://4youngpadawans.com/stream-live-video-to-browser-using-gstreamer/

# importing the necessary libraries

import gi
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst, GLib, GstApp, GstVideo
from openvino.inference_engine import IECore
import sys

# function to call bus
def bus_call(bus, message, pipeline):
    t = message.type
    if t == Gst.MessageType.EOS:
        print('pipeline ended')
        pipeline.set_state(Gst.State.NULL)
        sys.exit()
    elif t == Gst.MessageType.ERROR:
        print('some error occured')
        err, debug = message.parse_error()
        print('{0} \n{1}'.format(err, debug))
        sys.exit()
    else:
        pass
    return True

if __name__ == '__main__':
    RTSP_SERVER = 'rtsp://192.168.1.100:5540/ch0'
    FACE_DETECTION_MODEL = '/home/vishnu/practice_codes/video_analysis_practice/video-analytics-e2e/GStreamer-HLS-Pipeline/Models/face-detection-adas-0001/FP32/face-detection-adas-0001.xml'

    # GStreamer pipeline with HLS
    GSTREAMER_PIPELINE_HLS = f'''
    rtspsrc location={RTSP_SERVER}
        retry=20
        latency=2000
        buffer-mode=auto
    ! decodebin
    ! videoconvert n-threads=4
    ! videorate
    ! videoscale
    ! video/x-raw,width=640,height=480,framerate=1/10
    ! queue
    ! gvadetect model={FACE_DETECTION_MODEL} device=CPU
    ! gvawatermark
    ! clockoverlay
    ! x264enc tune=zerolatency
    ! mpegtsmux
    ! hlssink playlist-root=http://172.18.37.126:8080
        location=/home/vishnu/practice_codes/video_analysis_practice/video-analytics-e2e/GStreamer-HLS-Pipeline/segment_%05d.ts
        target-duration=20 
        max-files=10
    '''

    Gst.init(None)

    pipeline = Gst.parse_launch(GSTREAMER_PIPELINE_HLS)

    # bus connection
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, pipeline)
    print(bus.peek())

    # starting pipeline
    pipeline.set_state(Gst.State.PLAYING)

    # starting main loop
    try:
        print('starting main loop')
        GLib.MainLoop().run()
        print('running main loop')
    except KeyboardInterrupt:
        print('Exiting')
        sys.exit()

