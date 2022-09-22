# LogLines.py
import time
import os
import json
import re
import sys
from datetime import datetime
from PySide6.QtWidgets import QFileDialog, QApplication


class LogParse():
    def __init__(self):
        self.status = "idle"
        self.standard_pattern = re.compile(
            r'^(?P<timestamp>\[[a-zA-Z\s]{8}[\d\s:]{16}\])\s(?P<content>.*)')
        self.who_pattern = re.compile(r'Players (on|in) EverQuest:')
        self.who_content_pattern = re.compile(
            r'\[((?P<level>\d{1,2})\s(?P<class>\w+(\s\w+)?)|(?P<anon>ANONYMOUS))\]\s(?P<player>\w+)\s(?P<race>\(.+\))?\s?(?P<guild><.+>)?\s?(ZONE:\s?(?P<zone>\w+))?')
        self.zone_pattern = re.compile(
            r'There are \d+? players in (?P<zone>.+).')
        self.who_buffer = []
        self.players = {}
        self.zone_status = None

    def parse_text(self, log_line):
        if not self.standard_pattern.match(log_line):
            return None

        matched_line = self.standard_pattern.match(log_line)
        timestamp = datetime.strptime(matched_line.group(
            'timestamp'), '[%a %b %d %H:%M:%S %Y]').isoformat()
        content = matched_line.group('content')

        if self.status == "idle":
            self.idle(content)
        elif self.status == "who_processing":
            self.who_processing(content, timestamp)

    def idle(self, content):
        content = content
        if self.who_pattern.match(content):
            self.who_buffer.append(content)
            self.status = "who_processing"

    def who_processing(self, content, timestamp,):
        content = content
        timestamp = timestamp
        player_data = {}
        list_data = []

        if content.startswith('There') or content.startswith('Your'):
            self.who_buffer.append(content)
            self.status = "complete"
            if self.zone_status == 'zone_needed':
                zone = re.finditer(self.zone_pattern, content)
                for item in zone:
                    self.zone = item.group('zone')
                    for player in self.players:
                        for item in self.players[player]:
                            item['zone'] = self.zone
                            self.zone_status = None
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
                    if item.group('zone'):
                        player_data['zone'] = item.group('zone')
                    else:
                        self.zone_status = 'zone_needed'
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
                    else:
                        self.zone_status = 'zone_needed'
                    list_data.append(player_data)
                    self.players[name] = list_data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    count = 0
    if os.path.exists('historical_players.json'):
        print('opening historical data')
        with open('historical_players.json') as f:
            historical = json.load(f)
    else:
        print('no historcal player data found, creating historical data file')
        historical = {}

    log_to_parse = QFileDialog.getOpenFileName(caption='Select Log to Parse')

    with open(log_to_parse[0], encoding='utf-8', mode='r') as log:
        start = time.perf_counter()
        parser = LogParse()
        for line in log:
            parser.parse_text(line)
            if parser.status == 'complete':
                parser.status = 'idle'
                for player in parser.players:
                    if player in historical:
                        for item in parser.players[player]:
                            if item not in historical[player]:
                                historical[player].append(item)
                                seen = len(historical[player])
                                print(
                                    f"found a new log entry for {player}, times seen:{seen}")
                                count += 1
                    else:
                        historical[player] = parser.players[player]
                        print(
                            f'first time {player} has been seen, adding to historical data')
    for player in historical:
        sorted(historical[player], key=lambda x: x['timestamp'], reverse=True)
    with open('historical_players.json', 'w') as f:
        json.dump(historical, f, indent=4)
        print(count)
        print(f"Completed Execution in {time.perf_counter() - start} seconds")
    app.quit()
