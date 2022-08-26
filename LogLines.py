# LogLines.py
import time
import re
import sys
from datetime import datetime
from PySide6.QtWidgets import QFileDialog, QApplication


class LogLine():
    def __init__(self, time_stamp, content, line_type):
        self.time_stamp = time_stamp
        self.content = content
        self.line_type = line_type


class Who(LogLine):
    def __init__(self, time_stamp, content, line_type):
        super().__init__(time_stamp, content, line_type)


class player():
    def __init__(self, player_level, player_class, player_name, player_race, player_guild):
        self.player_level = player_level
        self.player_class = player_class
        self.player_name = player_name
        self.player_race = player_race
        self.player_guild = player_guild


def parse_text(log_line):

    pattern = re.compile(
        r'^(?P<timestamp>\[[a-zA-Z\s]{8}[\d\s:]{16}\])(?P<content>.*)')
    who_all_pattern = re.compile(r'Players on EverQuest:')
    player_pattern = re.compile(
        r'\[((?P<level>\d{1,2})\s(?P<class>\w+)|(?P<anon>ANONYMOUS))]\s(?P<player>\w+)\s(?P<race>\(.+\))?\s(?P<guild><.+>)?')

    matched_line = pattern.match(log_line)

    if matched_line:
        timestamp = datetime.strptime(matched_line.group(
            'timestamp'), '[%a %b %d %H:%M:%S %Y]').isoformat()
        content = matched_line.group('content')

    who_all_match = who_all_pattern.match(content)

    player_match = re.finditer(player_pattern, content)
    for match in player_match:
        if match:
            print(match.group('level'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    log_to_parse = QFileDialog.getOpenFileName(caption='Select Log to Parse')
    with open(log_to_parse[0], encoding='ISO-8859-1', mode='r') as log:
        start = time.perf_counter()
        for line in log:
            parse_text(line)
        print(f"Completed Execution in {time.perf_counter() - start} seconds")
    app.quit()
