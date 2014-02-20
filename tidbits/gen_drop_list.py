#!/usr/local/bin/python
from linkedlist import LinkedList
import numpy as np
from datetime import datetime, timedelta
import pickle
import os


class _node:
    def __init__(self, start, end, bad_list, next = None):
        self.start = start
        self.end = end
        self.bad_list = bad_list
        self.next = next
    

class InvalidList(LinkedList):
    def __init__(self):
        self.len = 0
        self._first = None
        self._last = None

    def add(self, start, bad_list, end = None):
        new_node = _node(start, end, bad_list)

        if self._first == None:
            self._first = new_node
            self._last = self._first
        else:
            if self._last.end == None:
                self._last.end = start
            self._last.next = new_node
            self._last = new_node
        self.len += 1

    def terminate(self, time):
        self._last.end = time

    

if __name__ == '__main__':

    DATA_DIR='/data/cynthia/20120330_board_dropout/'

    files = sorted(os.listdir(DATA_DIR))
    ll = InvalidList()

    prev_fail = None
    bad_boards = []
    for f in files:
        try:
            start_time = datetime.strptime(f, 'samples_valid_%Y%m%d_%H%M%S.npy')
        except ValueError:
            continue
        print f
        if prev_fail == None:
            prev_fail = start_time
        valid = np.load(DATA_DIR + f).swapaxes(0, 1)
        time = np.load(DATA_DIR + 'bolo_utc_' + f[14:])

        for i in range(max(np.shape(valid)) - 1):
            now = start_time + timedelta(days = time[i] - time[0])

            changes = np.array(map(lambda x, y: x^y, valid[i], valid[i + 1]))
            if changes.any() and now - prev_fail > timedelta(minutes = 10):
                for j in range(len(changes)):
                    if valid[i][j] and not valid[i + 1][j]:
                        if (120 + j) not in bad_boards:
                            bad_boards.append(120 + j)
                    try:
                        if not valid[i][j] and valid[i + 1][j]:
                            bad_boards.remove(120 + j)
                    except ValueError:
                        pass
                        
                if len(bad_boards) > 0:
                    ll.add(now, bad_boards)
                else:
                    ll.terminate(now)
                prev_fail = now
                
    pickle.dump(ll, open('/home/ndhuang/code/March_dropouts.pkl', 'w'))
