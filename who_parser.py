from operator import index
import sys
import os
import json
from configparser import ConfigParser
from LogLines import LogParse
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QPushButton, QWidget, QFileDialog, QMessageBox
from QThreads import Watch_Directory_Thread, File_Stream_Thread, WorkerSignals


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.file = None
        self.parser = LogParse()
        self.setup_ui()
        self.historical_player_data()
        self.setMinimumSize(400, 400)
        self.show()

        self.directory = ''
        res = self.setup_config()
        if not res:
            sys.exit()
        self.start_watcher_directory()

    def setup_config(self):
        """
        checks for an existing config file and returns the EverQuest directory
        if no config file exists, then prompt user to select their directory and create a config file
        """

        config = ConfigParser()
        config_file = 'config.ini'
        # check for config file in current directory
        if os.path.exists(config_file):
            config.read(config_file)
            # if config file exists check for directory setting and return the directory
            if config.has_option('default', 'directory'):
                self.directory = config['default']['directory']
                return config
        # if no config exists prompt user for a directory
        button = QMessageBox.information(
            self,
            "Directory Not Selected",
            "Click Ok to select your EverQuest Directory",
            buttons=QMessageBox.Ok | QMessageBox.Cancel,
        )
        if button != QMessageBox.Ok:
            # quit app if dialog canceled
            return None

        self.directory = QFileDialog.getExistingDirectory(
            caption='Select your EverQuest Directory')

        if not self.directory:
            # quit app if dialog canceled
            print(self.directory)
            return None

        self.directory += '/Logs'
        # check if directory exists, if not, rerun function
        if not os.path.exists(self.directory):
            self.directory = ''
            self.setup_config()
            return

        # add directory to config and create config file
        config.add_section('default')
        config.set('default', 'directory', self.directory)

        with open(config_file, 'w') as cf:
            config.write(cf)

        return config

    def setup_ui(self):
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

    def start_watcher_directory(self):
        self.watch_directory_signals = WorkerSignals()
        self.watch_directory_signals.result.connect(self.file_compare)
        self.watch_directory_thread = Watch_Directory_Thread(
            self.directory, signals=self.watch_directory_signals)
        self.watch_directory_thread.start()

    def file_compare(self, file):
        if self.file != file:
            self.file = file
            self.start_file_stream(self.file)

    def start_file_stream(self, new_file):
        self.file = new_file
        self.file_stream_signals = WorkerSignals()
        self.file_stream_signals.result.connect(self.parser.parse_text)
        self.file_stream_signals.result.connect(self.set_editor_text)
        self.file_stream_thread = File_Stream_Thread(
            self.directory, self.file, self.file_stream_signals)
        self.file_stream_thread.start()

    def set_editor_text(self):
        if self.parser.status == 'complete':
            self.editor.setPlainText('')
            self.editor.appendPlainText(self.parser.who_buffer[0])
            self.editor.appendPlainText(self.parser.who_buffer[1])

            for player in self.parser.players:
                for item in self.parser.players[player]:
                    level = item['level']
                    pclass = item['class']
                    race = item['race']
                    if 'guild' in item:
                        guild = item['guild']

                    if level == 'ANONYMOUS':
                        if 'guild' in item:
                            self.editor.appendPlainText(
                                f'[{level}] {player} {guild}')
                        else:
                            self.editor.appendPlainText(f'[{level}] {player}')
                    else:
                        if 'guild' in item:
                            self.editor.appendPlainText(
                                f'[{level} {pclass}] {player} {race} {guild}')
                        else:
                            self.editor.appendPlainText(
                                f'[{level} {pclass}] {player} {race}')

            self.editor.appendPlainText(self.parser.who_buffer[2])

            if not os.path.exists('players.json'):
                json.dump(self.parser.players, open(
                    'players.json', 'w'), indent=4)

            self.parser.who_buffer = []
            self.parser.players = {}
            self.parser.status = 'idle'

    def closeEvent(self, event):
        # events to trigger when app is closed out
        try:
            self.watch_directory_thread.terminate()
            self.file_stream_thread.terminate()
        except:
            print("no running threads")

    def clear_text(self):
        self.editor.setPlainText("")

    def historical_player_data(self):
        if os.path.exists('player_history.json'):
            json.load('player_history.json', open())


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
