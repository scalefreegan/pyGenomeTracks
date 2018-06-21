from pygenometracks import makeTracksFile, tracksClass, plotTracks
import tempfile
import pybedtools

def genomecoverage2bigwig(bed, genome, out = None,
                          strand = None, p5 = False,
                          p3 = False, log = False,
                          cutoff = None, gc = True):
    if p5:
        p = {'5': True}
    if p3:
        p = {'3': True}
    if gc:
        if (p3) or (p5):
            if strand is not None:
                gc = bed.genome_coverage(
                    bga = True,
                    strand = strand,
                    g = genome,
                    **p)
            else:
                 gc = bed.genome_coverage(
                    bga = True,
                    g = genome,
                    **p)
        else:
            if strand is not None:
                gc = bed.genome_coverage(
                    bga = True,
                    strand = strand,
                    g = genome
                    )
            else:
                gc = bed.genome_coverage(
                    bga = True,
                    g = genome
                    )
        if gc.count() > 0:
            gc = gc.to_dataframe()
            if cutoff is not None:
                gc = gc.loc[gc.name>=cutoff]
            if log:
                gc.name = np.log2(gc.name+1)
            gc = gc.sort_values(["chrom","start","end"])
            gc_s = pybedtools.BedTool(gc.to_string(index=False, header=False), from_string=True)
        else:
            print("WARNING: No reads overlap supplied interval on strand {}".format(strand))
            return(None)
        if out is None:
            out = tempfile.NamedTemporaryFile(suffix=".bw", delete = False)
            #print(out.name)
            gc_s = pybedtools.contrib.bigwig.bedgraph_to_bigwig(gc_s, genome, output=out.name)
        else:
            gc_s = pybedtools.contrib.bigwig.bedgraph_to_bigwig(gc_s, genome, output=out)
    else:
        if strand is None:
            strand = ["+","-","."]
        if type(strand) is str:
            strand = [strand]
        gc = bed
        gc = gc.to_dataframe()
        gc = gc.loc[gc.strand.isin(strand)]
        gc_s = pybedtools.BedTool(gc.to_string(index=False, header=False), from_string=True)
        if out is not None:
            gc_s.saveas(out)
    return(gc_s)

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
