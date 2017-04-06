#!python
# -*- coding: utf-8 -*-

from __future__ import print_function

from flask import (Flask,
                   render_template,
                   request,
                   jsonify)
import db

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("hello.html")

@app.route("/annotation/<num>")
def annotation(num=1):
    num = int(num) # default type of num is unicode.
    fragments = db.get_fragments()
    length = len(fragments)
    idx = num - 1
    if idx <= 0:
        idx = 0
    elif idx >= length:
        idx = length - 1
    return render_template("annotation.html", 
            cur_num=idx+1, 
            fragments_num=length,
            source_origin=db.WordSource.ORIGIN,
            source_unknown=db.WordSource.UNKNOWN)

@app.route("/annotation/get_text")
def get_text():
    fragment_id = request.args.get("fragment_id", 23, type=int)
    fragment, _ = db.get_certain_fragment(fragment_id)
    return jsonify(fragment)

@app.route("/annotation/current_match")
def get_current_match_range():
    '''
    return current match range
    @fragment_id current fragment id
    @return current fragment match result.
    '''
    fragment_id = request.args.get("fragment_id", 23, type=int)
    fragment, _ = db.get_certain_fragment(fragment_id)
    len2word_set = db.get_len2word_set()
    match_result, word2line_list = db.match_all_line_and_get_word2line_list(
        fragment, len2word_set)
    # for lazy update.
    db.set_current_word2line_list(word2line_list)
    return jsonify(match_result)

@app.route("/annotation/add_word")
def add_word_and_get_new_matched():
    '''
    @fragment_id current fragment id
    @word new word
    @return new word's new match result(only the new word!)
    '''
    fragment_id = request.args.get("fragment_id", 23, type=int)
    # default type is unicode
    # shouln't given type=str, this may cause an failed convertion
    # unicode -> str for UTF8 of Chinese!
    word = request.args.get("word", u"", type=unicode)
    fragment, _ = db.get_certain_fragment(fragment_id)
    if word == "":
        return jsonify({})
    # add to new word to new len2wordset
    db.add_new_word_and_set_source_and_record(word)
    # construct an tmp len2wordset
    tmp_len2set = {len(word): set([word, ])}
    # get the newly matched result
    match_result, new_word2line_list = db.match_all_line_and_get_word2line_list(
        fragment, tmp_len2set)
    db.add_word2line_list(new_word2line_list)
    return jsonify(match_result)

@app.route("/annotation/check_word_source")
def check_word_source():
    '''
    @word to be removed word
    @return word source
    '''
    word = request.args.get("word", u"", type=unicode)
    word = word.strip()
    return jsonify(db.get_word_source(word))

@app.route("/annotation/remove_word")
def remove_word_and_get_updated_match():
    '''
    remove word and get updated match result
    @fragment_id 
    @word
    '''
    fragment_id = request.args.get("fragment_id", 23, type=int)
    word = request.args.get("word", u"", type=unicode)
    word = word.strip()
    db.remove_word_and_source_and_record(word)
    tmp_len2set = {len(word): set([word, ])}
    fragment, _ = db.get_certain_fragment(fragment_id)
    # get removed word affected line
    line_list = db.get_word2line_list(word)
    len2set = db.get_len2word_set()
    # may get new word matched! so must update the word2line_list
    updated_match_result, new_word2line_list = db.match_some_line(fragment, line_list, len2set)
    db.add_word2line_list(new_word2line_list)
    return jsonify(updated_match_result)

@app.route("/finish")
def finish():
    '''
    render finish page.
    '''
    return render_template("finish.html")
