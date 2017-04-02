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
    return 'hello world!'

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
            fragments_num=length)

@app.route("/annotation/get_text")
def get_text():
    fragment_id = request.args.get("fragment_id", 23, type=int)
    fragment, _ = db.get_certain_fragment(fragment_id)
    return jsonify(fragment)

@app.route("/annotation/current_match")
def get_current_match_range():
    fragment_id = request.args.get("fragment_id", 23, type=int)
    fragment, _ = db.get_certain_fragment(fragment_id)
    original_len2set = db.get_original_len2wordset()
    new_len2set = db.get_new_len2wordset()
    original_match_result = db.match_multi_line_with_multi_len2set(fragment, 
                                            [original_len2set, new_len2set])
    return jsonify(original_match_result)

@app.route("/annotation/add_word")
def add_word_and_get_new_matched():
    fragment_id = request.args.get("fragment_id", 23, type=int)
    # default type is unicode
    # shouln't given type=str, this may cause an failed convertion
    # unicode -> str for UTF8 of Chinese!
    word = request.args.get("word", u"", type=unicode)
    fragment, _ = db.get_certain_fragment(fragment_id)
    if word == "":
        return jsonify({})
    # add to new word to new len2wordset
    db.add_new_word2len2wordset(word)
    db.get_action_recorder().add_word(word)
    # construct an tmp len2wordset
    tmp_len2set = {len(word): set([word, ])}
    # get the newly matched result
    match_result = db.match_multi_line(fragment, tmp_len2set)
    return jsonify(match_result)

@app.route("/annotation/check_word_source")
def check_word_source():
    word = request.args.get("word", u"", type=unicode)
    word_len = len(word)
    # first check the newly len2wordset
    # then original len2wordset
    new_len2set = db.get_new_len2wordset()
    original_len2set = db.get_original_len2wordset()
    if (word_len in new_len2set
         and word in new_len2set[word_len]):
        return jsonify(db.NEW_LEN2WORD_SET_NAME)
    elif (word_len in original_len2set
           and word in original_len2set[word_len] ):
        return jsonify(db.ORIGIN_LEN2WORD_SET_NAME)
    else:
        return jsonify("OTHERS")

@app.route("/annotation/remove_word")
def remove_word_and_get_removed_match():
    fragment_id = request.args.get("fragment_id", 23, type=int)
    word = request.args.get("word", u"", type=unicode)
    word_source = request.args.get("word_source", type=unicode)
    word = word.strip()
    word_source = word_source.encode("utf-8")
    if word_source == db.NEW_LEN2WORD_SET_NAME:
        new_len2set = db.get_new_len2wordset()
        new_len2set.remove_word(word)
    elif word_source == db.ORIGIN_LEN2WORD_SET_NAME:
        original_len2set = db.get_original_len2wordset()
        original_len2set.remove_word(word)
    db.get_action_recorder().remove_word(word)
    tmp_len2set = {len(word): set([word, ])}
    fragment, _ = db.get_certain_fragment(fragment_id)
    match_result = db.match_multi_line(fragment, tmp_len2set)
    return jsonify(match_result)


@app.teardown_appcontext
def close_connection(exception):
    print("CLOSE CONTEXT")
    #db.close_connection(exception)
    #db.close_action_recorder()