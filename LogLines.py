# LogLines.py
import time
import re
import sys
from datetime import datetime
from tokenize import group
from PySide6.QtWidgets import QFileDialog, QApplication


class LogLine():
    def __init__(self, time_stamp, content, line_type):
        self.time_stamp = time_stamp
        self.content = content
        self.line_type = line_type


class Who(LogLine):
    def __init__(self, time_stamp, content, line_type):
        super().__init__(time_stamp, content, line_type)


def parse_text(log_line):

    pattern = re.compile(
        r'^(?P<timestamp>\[[a-zA-Z\s]{8}[\d\s:]{16}\])(?P<content>.*)')
    who_pattern = re.compile(
        r'\[((?P<level>\d{1,2})\s(?P<class>\w+)|(?P<anon>ANONYMOUS))]\s(?P<player>\w+)\s(?P<race>\(.+\))?\s(?P<guild><.+>)?')
    matched_line = pattern.match(log_line)
    if matched_line:
        timestamp = datetime.strptime(matched_line.group(
            'timestamp'), '[%a %b %d %H:%M:%S %Y]').isoformat()
        content = matched_line.group('content')
        who_match = who_pattern.match(content)
        print(content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    log_to_parse = QFileDialog.getOpenFileName(caption='Select Log to Parse')
    with open(log_to_parse[0], encoding='ISO-8859-1', mode='r') as log:
        print("WRITTING FILES")
        start = time.perf_counter()
        for line in log:
            # print(f"processing {line}")
            parse_text(line)
        print("DONE WRITTING FILES")
        print(f"Completed Execution in {time.perf_counter() - start} seconds")
    app.quit()
    # message = '[Sat Aug 13 12:32:44 2022] a Shai`din Bloodomen begins to cast a spell.'
    # print("starting...")
    # start = time.perf_counter()
    # for i in range(10000000):
    #     parse_text(message)
    # print(f"Completed Execution in {time.perf_counter() - start} seconds")
