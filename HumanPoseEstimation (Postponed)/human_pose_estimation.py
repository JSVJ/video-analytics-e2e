# The following code is inspired from the repository
# https://github.com/openvinotoolkit/dlstreamer_gst/blob/master/samples/gst_launch/human_pose_estimation/README.md

# Model is downloaded from model downloader's downloader.py
# Model-proc is downloaded from 
# https://github.com/openvinotoolkit/dlstreamer_gst/blob/master/samples/model_proc/intel/human_pose_estimation/human-pose-estimation-0001.json

# importing all the dependencies
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

if __name__ == '__main__':

    # Model is downloaded from model downloader's downloader.py
    # Model-proc is downloaded from 
    # https://github.com/openvinotoolkit/dlstreamer_gst/blob/master/samples/model_proc/intel/human_pose_estimation/human-pose-estimation-0001.json

    VIDEO_FILE = 'HumanPoseEstimation/Sample_Video/face-demographics-walking.mp4'
    ESTIMATION_MODEL = "HumanPoseEstimation/Models/intel/human-pose-estimation-0001/FP32/human-pose-estimation-0001.xml"
    ESTIMATION_MODEL_PROC = "HumanPoseEstimation/Models/intel/human-pose-estimation-0001/human-post-estimation-0001-proc.json"
    SINK_LOCATION = "HumanPoseEstimation/output.mp4"

    # GStreamer pipeline
    GST_PIPELINE = f'''
    filesrc location={VIDEO_FILE}
    ! decodebin
    ! videoconvert
    ! queue
    ! gvaclassify model={ESTIMATION_MODEL} model-proc={ESTIMATION_MODEL_PROC} device=CPU
    ! queue
    ! textoverlay text="Human Pose Estimation"
    ! gvawatermark
    ! x264enc
    ! h264parse
    ! qtmux
    ! filesink location={SINK_LOCATION}
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