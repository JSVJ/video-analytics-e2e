# importing necessary libraries
# the code is from here - https://github.com/openvinotoolkit/dlstreamer_gst/blob/master/README.md
import gi 

gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gst, GLib, GstApp, GstVideo

from openvino.inference_engine import IECore
import sys

# function for calling bus
def bus_call(bus, message, pipeline):
    t = message.type
    if t == Gst.MessageType.EOS:
        print('Pipeline Ended')
        pipeline.set_state(Gst.State.NULL)
        sys.exit()
    elif t == Gst.MessageType.ERROR:
        print('some problem')
        err, debug = message.parse_error()
        print("Error = {0} , debug info = {1}".format(err, debug))
        sys.exit()
    else:
        pass
    return True

# main function
if __name__ == "__main__":

    # connect RTSP camera or a file source location
    VIDEO_FILE = 'video-analytics-e2e/BasicFaceDetection/Sample_Videos/face-demographics-walking.mp4'
    OUTPUT_LOCATION = 'video-analytics-e2e/BasicFaceDetection/Sample_Videos/'
    # download the model from the open vino model zoo repository
    DETECTION_MODEL = 'video-analytics-e2e/BasicFaceDetection/Models/intel/face-detection-adas-0001/FP32/face-detection-adas-0001.xml'

    # setting the GStreamer pipeline
    GST_PIPELINE = f'''
    filesrc location={VIDEO_FILE}
    ! decodebin
    ! videoconvert
    ! queue
    ! gvadetect model = {DETECTION_MODEL} device=CPU
    ! queue
    ! gvawatermark
    ! x264enc
    ! filesink location="video-analytics-e2e/BasicFaceDetection/output.mp4"
    '''

    Gst.init(None)

    pipeline = Gst.parse_launch(GST_PIPELINE)

    # bus is something that transfer messages from one element to another element in a pipeline
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, pipeline)
    print(bus.peek())

    # starting the pipeline
    pipeline.set_state(Gst.State.PLAYING)

    # starting the MainLoop
    try:
        print('Main Loop')
        GLib.MainLoop().run()
        print('running the main loop')
    except KeyboardInterrupt:
        print('Exiting')
        sys.exit()