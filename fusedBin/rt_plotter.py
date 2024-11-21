import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class LogHandler(FileSystemEventHandler):
    def __init__(self, update_plot_func):
        self.update_plot_func = update_plot_func

    def on_modified(self, event):
        if event.src_path.endswith('ext.tab'):
            # self.update_plot_func()
            QtCore.QMetaObject.invokeMethod(self.update_plot_func, QtCore.Qt.QueuedConnection)

def read_log_file(file_path):
    
    df = pd.read_csv(file_path, sep=" ")
    df.rename(columns={"%time": "time"}, inplace=True)

    # the current measurments are in Amperes, we need to convert them to milliAmperes
    df["icc"] = df["icc"] * 1000
    df["externalCircuitry.i_supply"] = df["externalCircuitry.i_supply"] * 1000

    return df

def update_plot():
    df = read_log_file(log_file)
    plot_data_item_vcc.setData(df['time'], df['vcc'])
    plot_data_item_icc.setData(df['time'], df['icc'])
    plot_data_item_v_cap.setData(df['time'], df['externalCircuitry.v_cap'])

    # Update the text items with the last values
    last_row = df.iloc[-1]
    current_time = last_row['time']
    vcc_value = last_row['vcc']
    icc_value = last_row['icc']
    v_cap_value = last_row['externalCircuitry.v_cap']
    
    text_item.setHtml(f"<b>Time:</b> {current_time:.2f} s<br>"
                      f"<b>VCC:</b> {vcc_value:.2f} V<br>"
                      f"<b>ICC:</b> {icc_value:.2f} mA<br>"
                      f"<b>V_CAP:</b> {v_cap_value:.2f} V")

log_file = 'fusedLogs/ext.tab'

# Set up the pyqtgraph plot
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True, title="Real-Time Power Log")
plot = win.addPlot(title="Real-Time Power Log")
plot.setLabel('bottom', 'Time (s)')
plot.setLabel('left', 'Voltage (V) / Current (mA)')

plot.setMouseEnabled(y=False)
plot.showGrid(x=False, y=True)

# open the window in maximized mode
win.showMaximized()

plot.addLegend()

plot_data_item_vcc = plot.plot(pen='r', name='VCC')
plot_data_item_icc = plot.plot(pen='g', name='ICC')
plot_data_item_v_cap = plot.plot(pen='b', name='V_CAP')

text_item = pg.TextItem(anchor=(1, 0), color='k', border='w')
plot.addItem(text_item, row=1, col=1)

# Customize plot appearance
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

event_handler = LogHandler(update_plot)
observer = Observer()
observer.schedule(event_handler, path='logs/', recursive=False)
observer.start()

timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(1000)

if __name__ == '__main__':
    QtWidgets.QApplication.instance().exec_()
    observer.stop()
    observer.join()