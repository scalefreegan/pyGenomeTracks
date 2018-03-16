import argparse
import os
import re
import sys
from pygenometracks.tracksClass import PlotTracks

from pygenometracks._version import __version__


def parse_arguments(args=None):

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Facilitates the creation of a configuration file for pyGenomeTracks. The program takes a list '
                                                 'of files and does the boilerplate for the configuration file.',
                                     usage="%(prog)s --trackFiles <bigwig file> <bed file> etc. -o tracks.ini")

    # define the arguments
    parser.add_argument('--trackFiles', '-f',
                        help='Files to use in for the tracks. The ending of the file is used to define the type of '
                             'track. E.g. `.bw` for bigwig, `.bed` for bed etc. For a arcs or links file, the file '
                             'ending recognized is `.arcs` or `.links`',
                        nargs='+',
                        type=argparse.FileType('r'),
                        required=True)

    parser.add_argument('--out', '-o',
                        help='File to save the tracks',
                        metavar='output file',
                        type=argparse.FileType('w'),
                        required=False)

    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))

    return parser


def main(args=None, options=None, axis="bottom", geneSpacer=False):
    header_x = ("""
[x-axis]
#optional
#fontsize=20
# default is bottom meaning below the axis line
# where=top
""")
    header_s = ("""
[spacer]
# height of space in cm (optional)
height = 0.5
""")
    args = parse_arguments().parse_args(args)
    available_tracks = PlotTracks.get_available_tracks()
    if "x-axis" in options.keys():
        sys.stdout.write("Writing custom header x-axis")
        theseoptions = options["x-axis"]
        for opt, value in theseoptions.items():
            m = re.compile(r"\n{}.+=.+?\n".format(opt)) #uncommented
            if len(m.findall(header_x)) >= 1:
                # unique match to uncommented 
                header_x = re.sub(r"\n{}.+=.+?\n".format(opt), 
                                        "\n{} = {}\n".format(opt, value),
                                        header_x)
            else: 
                header_x = header_x.rstrip(" ") + opt + " = " + value + "\n"
    if "spacer" in options.keys():
        sys.stdout.write("Writing custom header spacer")
        theseoptions = options["spacer"]
        for opt, value in theseoptions.items():
            m = re.compile(r"\n{}.+=.+?\n".format(opt)) #uncommented
            if len(m.findall(header_s)) >= 1:
                # unique match to uncommented 
                header_s = re.sub(r"\n{}.+=.+?\n".format(opt), 
                                        "\n{} = {}\n".format(opt, value),
                                        header_s)
            else: 
                header_s =header_s.rstrip(" ") + opt + " = " + value + "\n"
    if (axis!="bottom"):
        args.out.write(header_x)
        args.out.write(header_s)
    geneiter = 0
    for file_h in args.trackFiles:
        write_spacers = False
        track_added = False
        label = ".".join(os.path.basename(file_h.name).split(".")[0:-1])
        for track_type, track_class in available_tracks.items():
            for ending in track_class.SUPPORTED_ENDINGS:
                if file_h.name.endswith(ending):
                    default_values = track_class.OPTIONS_TXT
                    default_values = default_values.replace("title =", "title = {}".format(label))
                    # here is where I will add custom options supplied as
                    # dictionary: {file_h.name : { option : value }}
                    if options is not None:
                        if label in options.keys():
                            sys.stdout.write("Writing custom options for track {}\n".format(file_h.name))
                            if type(options[label]) is dict:
                                theseoptions = options[label]
                            elif type(options[label]) is list:
                                theseoptions = options[label][geneiter]
                                geneiter = geneiter + 1
                            for opt, value in theseoptions.items():
                                m = re.compile(r"\n{}.+=.+?\n".format(opt)) #uncommented
                                if len(m.findall(default_values)) >= 1:
                                    # unique match to uncommented 
                                    default_values = re.sub(r"\n{}.+=.+?\n".format(opt), 
                                                            "\n{} = {}\n".format(opt, value),
                                                            default_values)
                                else: 
                                    default_values = default_values.rstrip(" ") + opt + " = " + value + "\n"   
                            if "type" in options[label].keys():
                                if geneSpacer:
                                    if options[label]["type"]=="genes":
                                        write_spacers = True
                        else:
                           sys.stdout.write("Couldn't find custom options for track {}\n".format(file_h.name))
                    if write_spacers:
                        args.out.write(header_s)            
                    args.out.write("\n[{label}]\nfile={file}\n{default_values}".
                                   format(label=label, file=file_h.name, default_values=default_values))
                    if write_spacers:
                        args.out.write(header_s)
                    sys.stdout.write("Adding {} file: {}\n".format(track_type, file_h.name))
                    track_added = True

        if track_added is False:
            sys.stdout.write("WARNING: file format not recognized for: {}\n".format(file_h.name))
    if (axis=="bottom"):
        args.out.write(header_s)
        args.out.write(header_x)
        
