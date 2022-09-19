# LogLines.py
import time
import re
import sys
from datetime import datetime
from PySide6.QtWidgets import QFileDialog, QApplication


class LogParse():
    def __init__(self):
        self.status = "idle"
        self.standard_pattern = re.compile(
            r'^(?P<timestamp>\[[a-zA-Z\s]{8}[\d\s:]{16}\])\s(?P<content>.*)')
        self.who_pattern = re.compile(r'Players on EverQuest:')
        self.who_all_pattern = re.compile(r'Players in EverQuest:')
        self.who_content_pattern = re.compile(
            r'\[((?P<level>\d{1,2})\s(?P<class>\w+)|(?P<anon>ANONYMOUS))\]\s(?P<player>\w+)\s(?P<race>\(.+\))?\s?(?P<guild><.+>)?')
        self.who_all_content_pattern = re.compile(
            r'\[((?P<level>\d{1,2})\s(?P<class>\w+)|(?P<anon>ANONYMOUS))\]\s(?P<player>\w+)\s(?P<race>\(.+\))?\s?(?P<guild><.+>)?\s?ZONE:\s?(?P<zone>\w+)?')
        self.zone_pattern = re.compile(
            r'There are \d+? players in (?P<zone>.+).')
        self.who_buffer = []
        self.players = {}

    def parse_text(self, log_line):
        if not self.standard_pattern.match(log_line):
            return None

        player_data = {}
        list_data = []

        matched_line = self.standard_pattern.match(log_line)

        timestamp = datetime.strptime(matched_line.group(
            'timestamp'), '[%a %b %d %H:%M:%S %Y]').isoformat()
        content = matched_line.group('content')

        if self.status == "idle":
            if self.who_pattern.match(content):
                self.who_buffer.append(content)
                self.status = "who_processing"
            elif self.who_all_pattern.match(content):
                self.who_buffer.append(content)
                self.status = "who_all_processing"
        elif self.status == "who_processing":
            if content.startswith('There'):
                self.status = "complete"
                zone = re.finditer(self.zone_pattern, content)
                for item in zone:
                    self.zone = item.group('zone')
                    for player in self.players:
                        for item in self.players[player]:
                            self.players[player][0]['zone'] = self.zone

                self.who_buffer.append(content)
            elif content.startswith('-'):
                self.who_buffer.append(content)
            else:
                who_match = re.finditer(self.who_content_pattern, content)
                for item in who_match:
                    name = item.group('player')
                    self.players[name] = {}
                    player_data['timestamp'] = timestamp

                    if item.group('level'):
                        player_data['level'] = item.group(
                            'level')
                        player_data['class'] = item.group(
                            'class')
                        player_data['race'] = item.group(
                            'race')
                        if item.group('guild'):
                            player_data['guild'] = item.group(
                                'guild')
                        list_data.append(player_data)
                        self.players[name] = list_data
                    else:
                        player_data['level'] = item.group(
                            'anon')
                        player_data['class'] = item.group(
                            'anon')
                        player_data['race'] = item.group(
                            'anon')
                        if item.group('guild'):
                            player_data['guild'] = item.group(
                                'guild')
                        list_data.append(player_data)
                        self.players[name] = list_data
        elif self.status == 'who_all_processing':
            if content.startswith('There') or content.startswith('Your'):
                self.status = "complete"
                self.who_buffer.append(content)
            elif content.startswith('-'):
                self.who_buffer.append(content)
            else:
                who_all_match = re.finditer(
                    self.who_all_content_pattern, content)
                for item in who_all_match:
                    name = item.group('player')
                    self.players[name] = {}
                    player_data['timestamp'] = timestamp

                    if item.group('level'):
                        player_data['level'] = item.group(
                            'level')
                        player_data['class'] = item.group(
                            'class')
                        player_data['race'] = item.group(
                            'race')
                        if item.group('guild'):
                            player_data['guild'] = item.group(
                                'guild')
                        if item.group('zone'):
                            player_data['zone'] = item.group('zone')
                        list_data.append(player_data)
                        self.players[name] = list_data
                    else:
                        player_data['level'] = item.group(
                            'anon')
                        player_data['class'] = item.group(
                            'anon')
                        player_data['race'] = item.group(
                            'anon')
                        if item.group('guild'):
                            player_data['guild'] = item.group(
                                'guild')
                        if item.group('zone'):
                            player_data['zone'] = item.group('zone')
                        list_data.append(player_data)
                        self.players[name] = list_data


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
