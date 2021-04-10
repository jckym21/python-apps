import pandas as pd
import holoviews as hv
from holoviews import opts

hv.extension('bokeh')
from datetime import datetime
from bokeh.models.formatters import DatetimeTickFormatter

class plot_motion():
    """
    This app reads a csv file indicating motions detected with a start and an end time.
    The motion is then plotted over runtime using holoviews in a 1D graph. An interactive
    graph is then saved in html format. The folder path of the motion file and the motion
    file name needs to be provided.
    """
    def __init__(self, folder, file):
        self.folder = folder  # Folder path
        self.file = file  # Motion log path

        self.motion_time = pd.read_csv(folder + file)  # Read motion log into panda

        # Convert date record to datetime format
        self.motion_time['start'] = pd.to_datetime(self.motion_time['start'],
                                                   format="%Y-%m-%d %H:%M:%S")
        self.motion_time['end'] = pd.to_datetime(self.motion_time['end'],
                                                 format="%Y-%m-%d %H:%M:%S")

        # Initialize graph containers
        self.vspan = [''] * self.motion_time.shape[0]
        self.layout = hv.VSpan()

        # Combine and plot motion bars
        self.combine()

        # Convert default datetime formatter in nanoseconds to readable format
        dtf2 = DatetimeTickFormatter(months='%I:%M:%S %P\n%b-%d',
                                     days='%I:%M:%S %P\n%b-%d',
                                     hours='%I:%M:%S %P\n%b-%d',
                                     minutes='%I:%M:%S %P\n%b-%d')
        # Set graph format
        self.layout.opts(opts.VSpan(height=150,
                                    responsive=True,
                                    yticks=0,
                                    ylabel='START',
                                    xlabel='',
                                    color='red',
                                    apply_ranges=True,
                                    xformatter=dtf2))

        # Display and save graph
        self.layout
        self.save()

    # Combine VSpan bars (i.e. individual motions) into one graph
    def combine(self):
        for i in range(self.motion_time.shape[0]):
            self.vspan[i] = hv.VSpan(self.motion_time["start"][i], self.motion_time["end"][i])
            self.layout = self.layout * self.vspan[i]

    # Save graph
    def save(self):
        hv.save(self.layout, self.folder + r'motion_graph.html')
