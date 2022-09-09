# LogLines.py
import time
import re
import sys
from datetime import datetime
from PySide6.QtWidgets import QFileDialog, QApplication


# class player():
#     def __init__(self, player_level, player_class, player_name, player_race, player_guild, date_time):
#         self.player_level = player_level
#         self.player_class = player_class
#         self.player_name = player_name
#         self.player_race = player_race
#         self.player_guild = player_guild
#         self.date_time = date_time


class LogParse():
    def __init__(self):
        self.status = "idle"
        self.standard_pattern = re.compile(
            r'^(?P<timestamp>\[[a-zA-Z\s]{8}[\d\s:]{16}\])\s(?P<content>.*)')
        self.who_pattern = re.compile(r'Players on EverQuest:')
        self.who_content_pattern = re.compile(
            r'\[((?P<level>\d{1,2})\s(?P<class>\w+)|(?P<anon>ANONYMOUS))\]\s(?P<player>\w+)\s(?P<race>\(.+\))?\s?(?P<guild><.+>)?')
        self.zone_pattern = re.compile(
            r'There are \d+? players in (?P<zone>.+).')
        self.who_buffer = []
        self.players = {}

    def parse_text(self, log_line):
        if not self.standard_pattern.match(log_line):
            return None

        matched_line = self.standard_pattern.match(log_line)

        timestamp = datetime.strptime(matched_line.group(
            'timestamp'), '[%a %b %d %H:%M:%S %Y]').isoformat()
        content = matched_line.group('content')

        if self.status == "idle":
            if self.who_pattern.match(content):
                self.who_buffer.append(content)
                self.status = "who_processing"
        elif self.status == "who_processing":
            if content.startswith('There'):
                self.status = "complete"
                zone = re.finditer(self.zone_pattern, content)
                for item in zone:
                    self.zone = item.group('zone')
                for key in self.players:
                    self.players[key]['zone'] = self.zone
                self.who_buffer.append(content)
            else:
                who_match = re.finditer(self.who_content_pattern, content)
                for item in who_match:
                    name = item.group('player')
                    self.players[name] = {}
                    self.players[name]['dt'] = timestamp
                    if item.group('level'):
                        self.players[name]['level'] = item.group('level')
                        self.players[name]['class'] = item.group('class')
                        self.players[name]['race'] = item.group('race')
                        if item.group('guild'):
                            self.players[name]['guild'] = item.group('guild')
                    else:
                        self.players[name]['level'] = item.group('anon')
                        self.players[name]['class'] = item.group('anon')
                        self.players[name]['race'] = item.group('anon')
                        if item.group('guild'):
                            self.players[name]['guild'] = item.group('guild')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    log_to_parse = QFileDialog.getOpenFileName(caption='Select Log to Parse')
    with open(log_to_parse[0], encoding='ISO-8859-1', mode='r') as log:
        start = time.perf_counter()
        parser = LogParse()
        for line in log:
            parser.parse_text(line)
        print(f"Completed Execution in {time.perf_counter() - start} seconds")
    app.quit()
