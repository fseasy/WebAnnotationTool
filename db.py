
'''
inspired from http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
'''

from __future__ import print_function

import bisect
import sqlite3
import os
import logging

DATABASE = 'annotation.db'

DATA_DIR_PATH = "data"

RAW_DATA_NAME = "raw.txt"
RAW_DATA_PATH = os.path.join(DATA_DIR_PATH, RAW_DATA_NAME)

WORD_LIST_NAME = "business_words.txt"
WORD_LIST_PATH = os.path.join(DATA_DIR_PATH, WORD_LIST_NAME)

ACTION_RECORD_NAME = "action.txt"
ACTION_RECORD_PATH = os.path.join(DATA_DIR_PATH, ACTION_RECORD_NAME)

# see http://stackoverflow.com/questions/2827623/python-create-object-and-add-attributes-to-it
# default object() has no `__dict__`, so can't set attr to it.
# following codes solves it
class ObjectWithDict(object):
    pass

_global_cached_data = ObjectWithDict()


def get_db():
    db = getattr(_global_cached_data, '_database', None)
    if db is None:
        db = _global_cached_data._database = sqlite3.connect(DATABASE)
    return db


def close_connection(exception):
    db = getattr(_global_cached_data, '_database', None)
    if db is not None:
        db.close()

def _fragments_loader():
    fragment_list = []
    with open(RAW_DATA_PATH) as input_f:
        all_content = input_f.read()
        all_content = all_content.decode("utf-8").strip()
        parts = all_content.split(u"\n\n")
        for part in parts:
            fragment = part.split(u"\n")
            fragment_list.append(fragment)
    return fragment_list


def get_fragments():
    fragments = getattr(_global_cached_data, '_fragments', None)
    if fragments is None:
        print("LOAD!!-----")
        fragments = _global_cached_data._fragments = _fragments_loader()
    return fragments

def get_fragments_num():
    return len(get_fragments())

def get_certain_fragment(in_fragment_id):
    fragments = get_fragments()
    fragment_id = in_fragment_id
    if in_fragment_id < 0:
        fragment_id = 0
    elif in_fragment_id >= get_fragments_num():
        fragment_id = get_fragments_num() - 1
    fragment = fragments[fragment_id]
    return fragment, fragment_id


class Len2WordSet(object):
    def __init__(self):
        self._len2set = dict()
    
    def add_word(self, word):
        word_len = len(word)
        if word_len == 0:
            return False
        word_set = self._len2set.setdefault(word_len, set())
        word_set.add(word)
        return True

    def remove_word(self, word):
        word_len = len(word)
        if word_len == 0 or word_len not in self._len2set:
            return False
        word_set = self._len2set[word_len]
        #word_set.discard(word) # discard- no raise, remove raise error if no key
        if word in word_set:
            word_set.remove(word)
            return True
        else:
            return False

    def parse_from_file(self, word_file_path):
        '''
        parse from file
        '''
        with open(word_file_path) as input_f:
            for line in input_f:
                word = line.decode("utf-8").strip()
                self.add_word(word)

    def parse_from_word_list(self, word_list):
        '''
        parse form word list
        '''
        for word in word_list:
            self.add_word(word)

    def debug_output(self):
        '''
        debug output.
        '''
        for word_len in self._len2set:
            word_set = self._len2set[word_len]
            for word in word_set:
                print("{}, {}".format(word.encode("utf-8"), word_len))
   
    def __iter__(self):
        return self._len2set.__iter__()
    
    def __next__(self):
        return next(self.__iter__())

    def next(self):
        return self.__iter__().next()
    
    def __getitem__(self, idx):
        return self._len2set.__getitem__(idx)
    def __contains__(self, k):
        return self._len2set.__contains__(k)
    
    def setdefault(self, key, default):
        return self._len2set.setdefault(key, default)

    def keys(self):
        return self._len2set.keys()
    
    def items(self):
        return self._len2set.items()

class AnnotationActionRecorder(object):
    ADD_ACTION = u"+"
    REMOVE_ACTION = u"-"
    def  __init__(self, action_fpath=ACTION_RECORD_PATH):
        self._init_file(action_fpath)
        self._action_fpath = action_fpath
        self._working_action_file = open(action_fpath, "at")
        self._action_cnt = 0

    def _init_file(self, action_fpath):
        ''''
        '''
    
    def _append_action2file(self, word, action):
        if len(word) == 0:
            return False
        if isinstance(word, unicode):
            word = word.encode("utf-8")
        action = action.encode("utf-8")
        self._working_action_file.write("{}\t{}\t{}\n".format(
            self._action_cnt, word, action))
        self._action_cnt += 1

    def add_word(self, word):
        '''
        append word to file
        '''
        return self._append_action2file(word, self.ADD_ACTION)

    def remove_word(self, word):
        '''
        append the removed file to removed file.
        '''
        return self._append_action2file(word, self.REMOVE_ACTION)

    def parse_action(self, init_word_fpath=""):
        '''
        parse action to get the result word list.
        `init_word_fpath` is needed if some extra words exists(not
        added by this action, but may be removed and recorded!)
        
        @init_word_fpath string, file path for initialization word list.
            every line contains one word.
        '''
        word_set = set()
        # 1. flush current working file
        self._working_action_file.flush()
        # 2. get from the init_word_fpath
        if init_word_fpath != "":
            with open(init_word_fpath) as init_f:
                for line in init_f:
                    word = line.decode("utf-8").strip()
                    word_set.add(word)
        # 3. parse action
        with open(self._action_fpath) as af:
            for line in af:
                line_u = line.decode("utf-8").strip()
                if line_u == "":
                    continue
                cols = line_u.split(u"\t")
                print(len(cols))
                word = cols[1]
                action = cols[2]
                if action == self.ADD_ACTION:
                    word_set.add(word)
                elif action == self.REMOVE_ACTION:
                    if word not in word_set:
                        logging.getLogger(__name__).error(("{} to be removed but "
                            "not in word set!").format(word.encode("utf-8")))
                    else:
                        word_set.remove(word)
                else:
                    logging.getLogger(__name__).error(("unknow action: "
                        "{}").format(action))
        return list(word_set)

    def close(self):
        '''
        close handling.`
        '''
        print("CLOSE!!!")
        self._working_action_file.close()

    def __del__(self):
        self.close()

def get_action_recorder():
    '''
    get action recoder
    '''
    action_recorder = getattr(_global_cached_data, "_action_recorder", None)
    if action_recorder is None:
        action_recorder = AnnotationActionRecorder()
        setattr(_global_cached_data, "_action_recorder", action_recorder)
    return action_recorder

def close_action_recorder():
    '''
    close action recorder
    '''
    action_recorder = getattr(_global_cached_data, "_action_recorder", None)
    if action_recorder:
        action_recorder.close()

ORIGIN_LEN2WORD_SET_NAME = "ORIGIN"

def get_original_len2wordset():
    len2wordset = getattr(_global_cached_data, "_origin_len2set", None)
    if len2wordset is None:
        len2wordset = _global_cached_data._origin_len2set = Len2WordSet()
        recorder = get_action_recorder()
        word_list = recorder.parse_action(WORD_LIST_PATH)
        len2wordset.parse_from_word_list(word_list)
    return len2wordset

NEW_LEN2WORD_SET_NAME = "NEW"

def get_new_len2wordset():
    len2wordset = getattr(_global_cached_data, "_new_len2wordset", None)
    if len2wordset is None:
        len2wordset = _global_cached_data._new_len2wordset = Len2WordSet()
    return len2wordset

def add_new_word2len2wordset(word):
    new_len2wordset = get_new_len2wordset()
    word_len = len(word)
    new_len2wordset.setdefault(word_len, set()).add(word)


def get_match_word_range(text, len2set):
    '''
    max-forward match, return match range, format is : [ (start_pos, end_pos), ... ]
    may be it could be improved!
    '''
    ascending_len_list = sorted(len2set.keys())
    pos = 0
    text_len = len(text)
    word_range_list = []
    while pos < text_len:
        left_len = text_len - pos
        # bisect.bisect(list, value)
        # return the index of the element which is the first that `bigger` than value
        # so the value at `index - 1` of list equals of less than value
        # do following logic, we get the valid sub-searching-length-list
        biggest_valid_len_index = bisect.bisect(ascending_len_list, left_len) - 1
        search_len_index = biggest_valid_len_index
        while search_len_index >= 0:
            # in descending length search
            word_len = ascending_len_list[search_len_index]
            token = text[pos: pos + word_len]
            wordset = len2set[word_len]
            if token in wordset:
                # found.
                word_range_list.append((pos, pos + word_len))
                pos = pos + word_len
                break
            search_len_index -= 1
        else:
            # not found at this pos
            pos += 1
    return word_range_list


def match_multi_line(line_list, len2set):
    '''
    match multi-line, return dict {line_number: match_range}, 
    if not match for centain line, it will not occur in this dict.
    '''
    multi_line_match_result = dict()
    for line_num, line in enumerate(line_list):
        word_range_list = get_match_word_range(line, len2set)
        if len(word_range_list) > 0:
            multi_line_match_result[line_num] = word_range_list
    return multi_line_match_result

def match_multi_line_with_multi_len2set(line_list, len2set_list):
    '''
    using multi-len2set to match multi-line
    return dict: {line_numberm: match_range}, not line number if corresponding line not match
    '''
    match_result = dict()
    for line_num, line in enumerate(line_list):
        word_range_list = []
        for len2set in len2set_list:
            word_range_list.extend(get_match_word_range(line, len2set))
        if len(word_range_list) > 0:
            # sort is needed!!
            match_result[line_num] = sorted(word_range_list, key=lambda r: r[0])
    return match_result