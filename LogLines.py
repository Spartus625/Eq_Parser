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
                        'race')[1:-1]
                    if item.group('guild'):
                        player_data['guild'] = item.group(
                            'guild')[1:-1]
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
                            'guild')[1:-1]
                    if item.group('zone'):
                        player_data['zone'] = item.group('zone')
                    else:
                        self.zone_status = 'zone_needed'
                    list_data.append(player_data)
                    self.players[name] = list_data


def manual_parse(logfile, parser, historical):
    log_to_parse = logfile
    parser = parser
    historical = historical

    with open(log_to_parse, encoding='latin-1', mode='r') as log:
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
                    else:
                        historical[player] = parser.players[player]
                        print(
                            f'first time {player} has been seen, adding to historical data')
                parser.players = {}
                parser.who_buffer = []

    for player in historical:
        historical[player] = sorted(historical[player],
                                    key=lambda x: x['timestamp'], reverse=True)
    with open('historical_players.json', 'w') as f:
        json.dump(historical, f, indent=4)
    return historical


if __name__ == '__main__':
    app = QApplication(sys.argv)
    total_players = []
    total_new_players = []
    parser = LogParse()
    if os.path.exists('historical_players.json'):
        print('opening historical data')
        with open('historical_players.json') as f:
            historical = json.load(f)
            for player in historical:
                total_players.append(player)
                count_total_players = len(total_players)
            print(f'{count_total_players} players in historical data')
    else:
        print('no historcal player data found, creating historical data file')
        historical = {}

    x = input('Enter 1 to Parse a file, Enter 2 to Parse a Folder: ')

    if x == '1':
        log_to_parse = QFileDialog.getOpenFileName(
            caption='Select Log to Parse')
        log_to_parse = log_to_parse[0]
        start = time.perf_counter()
        manual_parse(logfile=log_to_parse, parser=parser,
                     historical=historical)
    else:
        dir_to_parse = QFileDialog.getExistingDirectory(
            caption='Select Folder to Parse', options=QFileDialog.Option.ShowDirsOnly)
        logs_to_parse = os.listdir(dir_to_parse)
        start = time.perf_counter()
        for item in logs_to_parse:
            if item[:6] == 'eqlog_':
                file = dir_to_parse + '/' + item
                print(f'parsing: {item}')
                historical = manual_parse(
                    logfile=file, parser=parser, historical=historical)
    print(
        f"Completed Execution in {time.perf_counter() - start} seconds")
    app.quit()
