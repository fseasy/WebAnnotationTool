
'''
copy from http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
'''

import sqlite3
import bisect
from flask import g

DATABASE = 'annotation.db'

RAW_DATA_PATH = "raw.txt"

WORD_LIST_PATH = "business_words.txt"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def close_connection(exception):
    db = getattr(g, '_database', None)
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
    fragments = getattr(g, '_fragments', None)
    if fragments is None:
        print("LOAD!!-----")
        fragments = g._fragments = _fragments_loader()
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

    def parse(self, word_file_path):
        with open(word_file_path) as input_f:
            for line in input_f:
                word = line.decode("utf-8").strip()
                self.add_word(word)
    def debug_output(self):
        for word_len in self._len2set:
            word_set = self._len2set[word_len]
            for w in word_set:
                print("{}, {}".format(w.encode("utf-8"), word_len))
    
    def __iter__(self):
        return self._len2set.__iter__()
    
    def __next__(self):
        return next(self.__iter__())

    def next(self):
        return self.__iter__().next()
    
    def __getitem__(self, idx):
        return self._len2set.__getitem__(idx)
    
    def setdefault(self, key, default):
        return self._len2set.setdefault(key, default)

    def keys(self):
        return self._len2set.keys()
    
    def items(self):
        return self._len2set.items()


def get_original_len2wordset():
    len2wordset = getattr(g, "_origin_len2set", None)
    if len2wordset is None:
        len2wordset = g._origin_len2set = Len2WordSet()
        len2wordset.parse(WORD_LIST_PATH)
    return len2wordset

def get_new_len2wordset():
    len2wordset = getattr(g, "_new_len2wordset", None)
    if len2wordset is None:
        len2wordset = g._new_len2wordset = Len2WordSet()
    return len2wordset

def  add_new_word2len2wordset(word):
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
            match_result[line_num] = word_range_list
    return match_result