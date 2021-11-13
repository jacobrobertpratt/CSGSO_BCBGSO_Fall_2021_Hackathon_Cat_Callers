#!/usr/bin/python3

import jetson.inference
import jetson.utils
import random

import argparse
import sys

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.",
                                 formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage() +
                                 jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

parser.add_argument("input_URI", type=str, default="",
                    nargs='?', help="URI of the input stream")
parser.add_argument("output_URI", type=str, default="",
                    nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2",
                    help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf",
                    help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5,
                    help="minimum detection threshold to use")

is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

# create video output object
output = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv+is_headless)

# load the object detection network
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

# create video sources
input = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)

# Center coordinates in degrees
point_x = 41
point_y = 21

def gen_randx():
	test_x = random.randrange(-41, 41)

def gen_randy():
	test_y = random.randrange(-26, 26)

def rand_xy(top, bottom, right, left):
	x = gen_randx()
	y = gen_randy()
	while (left < x < right):
		x = gen_randx()

	while (top < y < bottom):
		y = gen_randy()


# process frames until the user exits
while True:
	# capture the next image
	img = input.Capture()

	# detect objects in the image (with overlay)
	detections = net.Detect(img, overlay=opt.overlay)

	# print the detections
	print("detected {:d} objects in image".format(len(detections)))

	for detection in detections:
		if detection.ClassID == 17:
			print(detection)
			rand_xy()
			move(x, y)

	# render the image
	output.Render(img)

	# update the title bar
	output.SetStatus("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))

	# print out performance info
	net.PrintProfilerTimes()

	# exit on input/output EOS
	if not input.IsStreaming() or not output.IsStreaming():
		break

