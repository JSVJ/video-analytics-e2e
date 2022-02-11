# 1. Following the pipeline from here - https://github.com/dlstreamer/dlstreamer/wiki/DL-Streamer-Tutorial#object-classification
# 2. Downloading the models from the open model zoo
# https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/intel/index.md
# 3. Download the proc file for the models
# https://github.com/dlstreamer/dlstreamer/tree/master/samples/model_proc/intel/object_detection


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
    DETECTION_MODEL = 'BasicObjectDetection/Models/intel/person-vehicle-bike-detection-2001/FP32/person-vehicle-bike-detection-2001.xml'
    SINK_LOCATION = 'BasicObjectDetection/output.mp4'
    # gstreamer pipeline
    GST_PIPELINE = f'''
    filesrc location={VIDEO_FILE}
    ! decodebin
    ! gvadetect model={DETECTION_MODEL} device=CPU
    ! queue
    ! gvawatermark
    ! textoverlay text="Basic Object Detection"
    ! videoconvert
    ! x264enc
    ! filesink location={SINK_LOCATION} sync=false
    '''

    Gst.init(None)

    pipeline = Gst.parse_launch(GST_PIPELINE)

    initialize_bus(pipeline = pipeline)

    pipeline.set_state(Gst.State.PLAYING)

    print('running')

    glib_mainloop()

    print('exit')