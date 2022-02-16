# importing 
import gi
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst, GLib, GstApp, GstVideo
import sys
import os
from openvino.inference_engine import IECore

# main loop with which the program runs
def glib_mainloop():
    mainloop = GLib.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        pass

# initializing the bus
def initialize_bus(pipeline):
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, pipeline)

# bus_call function
def bus_call(bus, message, pipeline):
    t = message.type
    if t == Gst.MessageType.EOS:
        print('pipeline ended')
        sys.exit()
    elif t == Gst.MessageType.ERROR:
        print('some problem')
        err, debug = message.parse_error()
        print(err, debug)
        sys.exit()
    else:
        pass
    return True

if __name__ == '__main__':
    VIDEO_FILE = 'BasicObjectDetection/Sample_Videos/person-bicycle-car-detection.mp4'
    GST_PIPELINE = f'''
    rtspsrc location=rtsp://192.168.1.102:5554 latency=2000 buffer-mode=auto
    ! decodebin ! avenc_mpeg4 ! rtpmp4vpay config-interval=1 ! udpsink host=127.0.0.1 port=5000
    '''

    Gst.init(None)

    pipeline = Gst.parse_launch(GST_PIPELINE)

    initialize_bus(pipeline = pipeline)

    pipeline.set_state(Gst.State.PLAYING)

    print('running')

    glib_mainloop()

    print('exit')