#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Dmitri
#
# Created:     09.03.2022
# Copyright:   (c) Dmitri 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import urllib.request
import urllib.parse
import json
import time
import subprocess

class CommunicatorConfig:
    permissionIfNoData = True
    commandCheckInterval = 10.0

class DataRetriever:
    def log(self, text):
        print('LOG: ' + text)

    def getURL(self, url):
        try:
            f = urllib.request.urlopen(url)
            data = f.read().decode('utf-8')
            data = json.loads(data)
            return data
        except Exception as e:
            self.log(str(e))
            return None

    def getCommands(self, src, login, password):
        url = src + '?action=cmd&dev=' + login + '&pwd=' + password + '&c=get'
        return self.getURL(url)

    def ackCommands(self, src, login, password, ids, success = True):
        ack = 'success' if success else 'fail'
        url = src + '?action=cmd&dev=' + login + '&pwd=' + password + '&c=' + \
            ack + '&id=' + ','.join(map(str, ids))
        return self.getURL(url)

    def loadData(self, src):
        url = src + '?action=rfid'
        return self.getURL(url)

    def getMap(self, src):
        data = self.loadData(src)
        hash = {}
        if isinstance(data, list):
            for item in data:
                if len(item['rfid']) != 8:
                    continue
                if item['rfid'] in hash:
                    self.log('Warning: duplicate entry ' + item['rfid'] + ' ' + str(item['id']))
                hash[item['rfid']] = item['id']
            return hash
        else:
            return None

    def compareData(self, m1, m2):
        k1 = m1.keys()
        k2 = m2.keys()
        removed = list(set(k1) - set(k2))
        added = list(set(k2) - set(k1))
        return {'-': removed, '+': added}

class DatabaseCommunicator:
    db = {}
    url = ''
    id = ''
    password = ''
    retr = DataRetriever()
    conf = CommunicatorConfig()
    timestamp = 0

    def init(self, url, id, password = ''):
        self.url = url
        self.id = id
        self.password = password
        self.updateData()

    def updateData(self):
        db = self.retr.getMap(self.url)
        if isinstance(db, dict):
            if len(db) > 0:
                self.db = db

    def checkCommands(self):
        if time.time() - self.timestamp > self.conf.commandCheckInterval:
            self.timestamp = time.time()
            self.processCommands()

    def checkPermission(self, code):
        if isinstance(self.db, dict):
            if len(self.db) > 0:
                return code in self.db
            else:
                return self.conf.permissionIfNoData
        else:
            return self.conf.permissionIfNoData

    def processCommand(self, command, data):
        if command == 'reload':
            self.updateData()
            return True
        if command == 'exit':
            exit()
            return True
        if command == 'shell':
            print(' '.split(data))
            subprocess.run(data.split(' '))
            return True
        return False

    def processCommands(self):
        cmds = self.retr.getCommands(self.url, self.id, self.password)
        succ = []
        fail = []
        if cmds['error'] == 0:
            for cmd in cmds['commands']:
                if self.processCommand(cmd['c'], cmd['d']):
                    succ.append(cmd['id'])
                else:
                    fail.append(cmd['id'])
            self.retr.ackCommands(self.url, self.id, self.password, succ)
            self.retr.ackCommands(self.url, self.id, self.password, fail, False)

