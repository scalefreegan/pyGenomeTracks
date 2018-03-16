from pygenometracks import makeTracksFile, tracksClass, plotTracks
import tempfile

def plot(interval, tracks, options,
                        axis = "bottom", geneSpacer = False,
                        ini = None, out = None):
    """
    Function to generate ini file, manage tracks and manage options for plotting
    internally with pyGenomeTracks. If save files aren't specified then temp
    files are used.
    
    ##args##
    
    interval : [chr, start, stop], list with region to plot
    tracks : [bed, bw, etc...], list of tracks to plot in the order desired
    options : { trackname : { option : value } }, dict of track names and options. for  
        convenience track name is only terminal file name without the file type identifier, 
        e.g./foo/bar.bed would be "bar"
    axis : where to locate the x-axis
    geneSpacer : whether to include spacers around type = gene tracks
    ini : string, name to save ini file  
    out : string, save name of plot
    
    
    """
    
    if ini is None:
        ini_f = tempfile.NamedTemporaryFile()
        ini = ini_f.name
        
    if out is None:
        out_f = tempfile.NamedTemporaryFile()
        out = out_f.name
        
    ini_command = tracks.copy()
    ini_command.insert(0,"--trackFiles")
    ini_command.append("-o")
    ini_command.append(ini)
    
    plot_command = [
        "--tracks={}".format(ini), 
        "--region={}:{}-{}".format(interval[0],interval[1],interval[2]),
        "--outFileName={}".format(out)
    ]

    makeTracksFile.main(ini_command, options, axis, geneSpacer)
    plotTracks.main(plot_command)
    