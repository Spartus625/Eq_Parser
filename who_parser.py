import sys
import time
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PySide6.QtCore import QThread, Slot, Signal, QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QPushButton, QWidget


DIRECTORY = 'H:\Everquest\Logs'


class WorkerKilledException(Exception):
    pass


class WorkerSignals(QObject):

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)


class Thread(QThread):
    """
    Worker thread
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """
        Initialize the runner function with passed args, kwargs.
        """
        # Retrieve args/kwargs here; and fire processing using them
        try:
            print("start of thread")
            result = self.fn(*self.args, **self.kwargs)
            print("end of thread", result)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))

        else:
            self.signals.result.emit(result)


class Watcher:

    def __init__(self, directory, handler):
        self.observer = Observer()
        self.directory = directory
        self.handler = handler

    def run(self):
        self.observer.schedule(self.handler, self.directory, recursive=False)
        self.observer.start()
        try:
            while self.observer.is_alive():
                self.observer.join(1)

        except:
            self.observer.stop()
            self.observer.join()


class MyHandler(FileSystemEventHandler):

    def on_modified(self, event):
        self.source_path = event.src_path
        self.file_name = self.source_path.split('\\')[-1]
        return self.file_name


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.directory_watch_thread = Thread(self.watch_directory)
        self.directory_watch_thread.start()

        self.setWindowTitle("Who Parser")

        widget = QWidget()
        layout = QVBoxLayout()

        self.editor = QPlainTextEdit()
        self.clear_button = QPushButton("Clear Text")
        self.clear_button.clicked.connect(self.clear_text)

        layout.addWidget(self.editor)
        layout.addWidget(self.clear_button)
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.show()

    def watch_directory(self):
        print("in watch_directory")
        self.directory = DIRECTORY
        self.event_handler = MyHandler()
        self.watcher = Watcher(self.directory, self.event_handler)
        self.watcher.run()
        print("after watcher.run")

    def set_text(self, current_file):
        print("in set_text")
        print(current_file)
        # textbox = self.editor.toPlainText()
        # if textbox == "":
        #     self.logfile = open(self.log_file, "r")
        #     loglines = self.log_tail(self.logfile)
        #     for line in loglines:
        #         print(line)

    def closeEvent(self, event):
        # events to trigger when app is closed out
        self.watcher.observer.stop()

    def clear_text(self):
        self.editor.setPlainText("")
        self.set_text()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())


# def worker_output(self, s):
#     self.editor.setPlainText(s)

# def worker_error(self, t):
#     print("ERROR: %s" % t)

# def log_tail(self, current_file):
#     print("log_tail has been called")
#     file_to_follow = current_file
#     file_to_follow.seek(0, 2)
#     while True:
#         line = file_to_follow.readline()
#         if not line:
#             time.sleep(0.1)
#             continue
#         yield line

# def search_who():

#     who = []
#     match = "players in"
#     top_of_search = "Players on EverQuest:"
#     end = True
#     y = -1

#     with open(latest_file, encoding='ISO-8859-1') as f:
#         lines = f.readlines()
#         last_line = lines[-1]

#         if match in last_line:
#             while end:
#                 if top_of_search in lines[y]:
#                     end = False
#                 who.insert(0, lines[y].strip())
#                 y -= 1
#             return who

# while go:
#                 results = search_who()
#                 if results != None:
#                     go = False
#                 if self.is_killed:
#                     raise WorkerKilledException
#             f = ""
#             for i in results:
#                 f += i + "\n"
