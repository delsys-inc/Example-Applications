"""
Generic Plot class

Creation of this gives a canvas widget that can be placed within a GUI.

Once you create the canvas, you can instantiate it as a grid of n-by-m subplots. 
You can also specify the number of samples that you want displayed at a time.

You can set color and index of the data if desired. If not, set these to null.

Update the plot with a call to plot_new_data(). New data should come as an np array shaped to rows and columns.
For example: to update a 4x1 grid of subplots, data should be a 4xn array where n is how many new data points are being plotted.

Use Example:
plotCanvas = PlottingCanvas()
plotCanvas.initiateCanvas(None,None,1, 1,numSamples)
"""

from vispy import gloo
from vispy import app
import numpy as np
import math
import random


class GenericPlot(app.Canvas):
    def __init__(self, plot_mode: str = 'windowed'):
        app.use_app('PySide6')
        app.Canvas.__init__(self, title='Use your wheel to zoom!',
                            keys='interactive', app='PySide6')
        gloo.set_viewport(0, 0, *self.physical_size)
        gloo.set_state(clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))
        self.plot_interact_flag = True
        self.is_initialized = False
        self.y = None
        self.plot_mode = plot_mode
        self.last_plotted_column = -1

    def initiateCanvas(self, color, index, nrows=1, ncols=1, plot_window_sample_count=10000):
        #---- Define subplot dimensions and plot granularity
        self.nrows = nrows
        self.ncols = ncols
        self.plot_window_sample_count = int(plot_window_sample_count)

        #---- Number of signals.
        self.m = self.nrows * self.ncols

        #---- Number of samples per signal
        self.n = int(self.plot_window_sample_count)

        #---- Generate the signals as a (m, n) array
        self._reset_data_plot_buffer()

        #---- Color of each vertex (TODO: make it more efficient by using a GLSL-based color map and the index).
        if color is None:
            color = np.repeat(np.random.uniform(size=(self.m, 3), low=.5, high=.9), self.n, axis=0).astype(np.float32)

        if index is None:
            index = np.c_[np.repeat(np.repeat(np.arange(self.ncols), self.nrows), self.n),
                          np.repeat(np.tile(np.arange(self.nrows), self.ncols), self.n),
                          np.tile(np.arange(self.n), self.m)].astype(np.float32)

        # Signal 2D index of each vertex (row and col) and x-index (sample index
        # within each signal).

        #---- Define GLSL shaders for the VisPy plot
        VERT_SHADER = """
        #version 120
        // y coordinate of the position.
        attribute float a_position;
        // row, col, and time index.
        attribute vec3 a_index;
        varying vec3 v_index;
        // 2D scaling factor (zooming).
        uniform vec2 u_scale;
        // Size of the table.
        uniform vec2 u_size;
        // Number of samples per signal.
        uniform float u_n;
        // Color.
        attribute vec3 a_color;
        varying vec4 v_color;
        // Varying variables used for clipping in the fragment shader.
        varying vec2 v_position;
        varying vec4 v_ab;
        void main() {
            float nrows = u_size.x;
            float ncols = u_size.y;
            // Compute the x coordinate from the time index.
            float x = -1 + 2*a_index.z / (u_n-1);
            vec2 position = vec2(x - (1 - 1 / u_scale.x), a_position);
            // Find the affine transformation for the subplots.
            vec2 a = vec2(1./ncols, 1./nrows)*1;
            vec2 b = vec2(-1 + 2*(a_index.x+.5) / ncols,
                          -1 + 2*(a_index.y+.5) / nrows);
            // Apply the static subplot transformation + scaling.
            gl_Position = vec4(a*u_scale*position+b, 0.0, 1.0);
            v_color = vec4(a_color, 1.);
            v_index = a_index;
            // For clipping test in the fragment shader.
            v_position = gl_Position.xy;
            v_ab = vec4(a, b);
        }
        """

        FRAG_SHADER = """
        #version 120
        varying vec4 v_color;
        varying vec3 v_index;
        varying vec2 v_position;
        varying vec4 v_ab;
        void main() {
            gl_FragColor = v_color;
            // Discard the fragments between the signals (emulate glMultiDrawArrays).
            if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
                discard;
            // Clipping test.
            vec2 test = abs((v_position.xy-v_ab.zw)/v_ab.xy);
            if ((test.x > 1) || (test.y > 1))
                discard;
        }
        """

        #---- Configure the rendering
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['a_position'] = self.y.reshape(-1, 1)
        self.program['a_color'] = color
        self.program['a_index'] = index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (nrows, ncols)
        self.program['u_n'] = self.n

        self.pause = False
        self.is_initialized = True

        # self.show()

    #-----------------------------------------------------------------------
    #---- Event Handlers
    def on_resize(self, event):
        if self.plot_interact_flag:
            gloo.set_viewport(0, 0, event.physical_size[0], event.physical_size[1])
            self.update()

    def on_mouse_wheel(self, event):
        if self.plot_interact_flag:
            dx = np.sign(event.delta[1]) * .05
            scale_x, scale_y = self.program['u_scale']
            scale_x_new, scale_y_new = (scale_x * math.exp(0.0 * dx),
                                        scale_y * math.exp(2.5 * dx))
            self.program['u_scale'] = (max(1, scale_x_new), max(1, scale_y_new))
            self.update()

    def on_pause(self):
        if self.plot_interact_flag:
            if self.pause:
                self.pause = False
            else:
                self.pause = True

    #-----------------------------------------------------------------------
    #---- Plotting Functions
    def plot_new_data(self, data_frame, next_val):
        #---- Process possibly jagged array into rectangular array
        emgLen = max(len(x) for x in data_frame)                 # All processing is normalized to the fastest EMG rate
        for i in range(len(data_frame)):
            #--- Spread out / interpolate data 
            if len(data_frame[i]) < emgLen:
                #-- Generate Index Vector 
                indexVector = []
                for j in range(len(data_frame[i])):
                    indexVector.append(emgLen/len(data_frame[i]) * j)
                #-- Quantize Index Vector 
                quantIndexVector = []
                for j in range(len(indexVector)):
                    quantIndexVector.append(round(indexVector[j]))
                #-- Copy data values to quantized indices
                quantData = [None] * emgLen
                dataInd = 0
                for j in quantIndexVector:
                    quantData[j] = data_frame[i][dataInd]
                    dataInd += 1
                #-- Piecewise linearly interpolate any empty points
                for j in range(len(quantIndexVector)):
                    if j == len(quantIndexVector)-1:
                        #- Interpolate the last recorded point of time T to the first point of time T+1
                        arrToInsert = np.linspace(quantData[quantIndexVector[j]], next_val[i], len(quantData)-quantIndexVector[j], endpoint=True)
                        quantData[quantIndexVector[j]:] = arrToInsert
                    else:
                        #- Interpolate between points of time T
                        arrToInsert = np.linspace(quantData[quantIndexVector[j]], quantData[quantIndexVector[j+1]], quantIndexVector[j+1]-quantIndexVector[j], endpoint=False)
                        quantData[quantIndexVector[j]:quantIndexVector[j+1]] = arrToInsert
                #-- Overwrite data_frame[i]
                data_frame[i] = quantData
            #--- Shrink data (shouldn't happen, but kept just in case)
            elif len(data_frame[i]) > emgLen:
                #-- Randomly delete data until length matches
                while len(data_frame[i]) != emgLen:
                    randIndex = random.randint(1, len(data_frame[i])-2)
                    data_frame[i] = np.delete(data_frame[i], randIndex)

        #---- Plot according to mode defined in Plotter() in CollectDataWindow.py
        if self.plot_mode.lower() == 'scrolling':
            self.plot_scrolling_data(data_frame)
        elif self.plot_mode.lower() == 'windowed':
            self.plot_windowed_data(data_frame)
        else:
            raise Exception('Plot mode not defined')

    def plot_scrolling_data(self, data_frame):
        new = np.asarray(data_frame, dtype='object')
        sp = np.shape(new)
        self.y[:, :-sp[1]] = self.y[:, sp[1]:]
        self.y[:, -sp[1]:] = new
        self._update_data()

    def plot_windowed_data(self, data_frame):
        new_data = np.asarray(data_frame, dtype='object')

        try: 
            new_data_count = np.size(new_data, 1)
        except:
            new_data_count = np.size(new_data, 0)

        #---- Detect if there's too much data to fit on the screen
        start_index = self.last_plotted_column + 1
        end_index = start_index + new_data_count
        is_data_continued_to_next_window = end_index >= self.plot_window_sample_count

        if not is_data_continued_to_next_window:
            #---- Visualize all available data
            plot_data_indexes = range(start_index, end_index)
            self.y[:, plot_data_indexes] = new_data
            self.last_plotted_column = plot_data_indexes[-1]
            self._update_data()
        else:
            #---- Visualize in the remaining plot space and cache leftover data
            plot_data_indexes = range(start_index, self.plot_window_sample_count)
            data_count_in_first_frame = len(plot_data_indexes)
            from_data_index = range(data_count_in_first_frame)
            try:
                self.y[:, plot_data_indexes] = new_data[:, from_data_index]
            except:
                self.y[:, plot_data_indexes] = new_data[from_data_index]
            self._update_data()

            #---- Wrap the graph to the next window
            self._reset_data_plot_buffer()

            #---- Visualize cached data
            from_data_index = range(data_count_in_first_frame, new_data_count)
            remaining_data_count = len(from_data_index)
            if remaining_data_count > 0:
                plot_data_indexes = range(0, remaining_data_count)
                try:
                    self.y[:, plot_data_indexes] = new_data[:, from_data_index]
                except:
                    self.y[:, plot_data_indexes] = new_data[from_data_index]
                self.last_plotted_column = plot_data_indexes[-1]
                self._update_data()

    #-----------------------------------------------------------------------
    #---- Helper Functions
    def _reset_data_plot_buffer(self):
        self.y = np.nan * np.zeros((self.m, self.n)).astype(np.float32)
        self.last_plotted_column = -1

    def _update_data(self):
        if not self.pause:
            self.program['a_position'].set_data(self.y.ravel().astype(np.float32))
            self.update()

    def on_draw(self, event):
        if self.is_initialized:
            gloo.clear()
            self.program.draw('line_strip')

    def set_scaling(self, x_int, y_int):
        if self.is_initialized:
            self.program['u_scale'] = (float(x_int), float(y_int))

    def set_interactive(self, flag):
        self.plot_interact_flag = flag
