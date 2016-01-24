#! -*-:coding=utf-8 -*-

import os
import re
import hashlib
from db_utils import Crash_Info_Model


class Extract(object):
    """ Extract the crash info

    """

    key_words = [r'CEGUI::UnknownObjectException',
        r'CEGUI::AlreadyExistsException',
        r'CEGUI::InvalidRequestException',
        r'CEGUI::ScriptException',
        r'LUA ERROR']
    DATA_PATH='/Users/kevin/project/toys/'

    def __init__(self, date='', data_path=''):
        self.data_dir = os.path.join(data_path or Extract.DATA_PATH, date)
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        self.db = Crash_Info_Model(date)
        self.hash_value = self.db.fetch_all_hash()

    def _check_match_it(self, line):
        for key in Extract.key_words:
            rlt = re.search(key, line)
            if rlt:
                flag = 0
                if str(key) == 'CEGUI::ScriptException':
                    flag = 1
                elif str(key) == 'LUA ERROR' and len(line[63:]) > 5:
                    if not re.search('function refid', line[63:]):
                        flag = 2
                    else:
                        break
                return True, flag
        return False, -1

    def _extrct_crash_info(self, fname):
        ret, special = False, 0
        cnt = 0
        temp = []
        lua_temp = []

        with open(fname) as f:
            for line in f.readlines():
                if len(str(line)) < 2:
                    continue

                if special == 1:
                    cnt += 1
                    temp.append(line.strip())
                    if cnt == 2:
                        cnt = 0
                        ret, special = False, -1
                        s = ''.join(temp)
                        hval = str(hashlib.md5(s).hexdigest())
                        if hval not in self.hash_value:
                            self.hash_value[hval] = 1
                            self.db.save_info(hval, s, 1, 0)
                        else:
                            self.hash_value[hval] += 1
                            self.db.update(hval, self.hash_value[hval])
                        temp = []
                    continue

                ret, special = self._check_match_it(line)
                if ret:
                    line_seq = line.split(' ')
                    s = ' '.join(line_seq[2:])
                    if special == 0:
                        hval = hashlib.md5(s).hexdigest()
                        if hval not in self.hash_value:
                            self.hash_value[hval] = 1
                            self.db.save_info(hval, s, 1, 0)
                        else:
                            self.hash_value[hval] += 1
                            self.db.update(hval, self.hash_value[hval])
                    elif special == 1:
                        temp.append(s)
                    else:
                        s = line[63:]
                        lua_temp.append(s.strip())
                    continue

                if len(lua_temp) > 0:
                    ret, special = False, -1
                    s = '<br/>'.join(lua_temp)
                    hval = hashlib.md5(s).hexdigest()
                    if hval not in self.hash_value:
                        self.hash_value[hval] = 1
                        self.db.save_info(hval, s, 1, 0)
                    else:
                        self.hash_value[hval] += 1
                        self.db.update(hval, self.hash_value[hval])
                    lua_temp = []

    def run_extract(self):
        for f in os.listdir(self.data_dir):
            self._extrct_crash_info(os.path.join(self.data_dir,f))

        # write back all the hash value
        for k, v in self.hash_value.items():
            self.db.save_hash(k, v)

        self.db.when_update()
        self.db.close()
