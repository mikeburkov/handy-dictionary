'''
Created on Nov 14, 2013

@author: mburkov
'''

from __future__ import division
from google.appengine.api import search
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
import json
import math
import os
import random
import webapp2


PARENT_KEY = 'dictionary'
DEFAULT_PAGE_SIZE = 5
WORDS_PER_PAGE = 30


def create_dictionary_key():
    return ndb.Key('Dictionary', PARENT_KEY)

def get_template_path(filename):
    return os.path.join(os.path.dirname(__file__), 'html/' + filename)

def get_document_index():
    return search.Index(name='word')

def index_document(word, description, example):
    fields = [
          search.TextField('word', value=word),
          search.TextField('description', value=description),
          search.TextField('example', value=example)]
    d = search.Document(fields=fields)
    index = get_document_index()
    try:
      index.put(d)
    except search.Error:
      print search.Error

class Word(ndb.Model):
    word = ndb.StringProperty(indexed=True)
    description = ndb.StringProperty()
    example = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class WordDTO():
    def __init__(self, word = None, description = None, example = None):
      self.word = word
      self.description = description
      self.example = example
    

class PersistWordHandler(webapp2.RequestHandler):
    def post(self):
        word = Word(parent=create_dictionary_key())
        word.word = self.request.get('word')
        word.description = self.request.get('description')
        word.example = self.request.get('example')
        word.put()
        
        index_document(word.word, word.description, word.example)
        
        words = [word]
        template_values = {
            'words': words
        }
        self.response.out.write(template.render(get_template_path('index.html'), template_values))


class LookupWordHandler(webapp2.RequestHandler):
    def post(self):
        query = self.request.get('query')
        try:
            index = get_document_index()
            search_results = index.search(query)
            words = []
            for doc in search_results:
                fields = doc.fields
                word = WordDTO()
                word.word = fields[0].value
                word.description = fields[1].value
                word.example = fields[2].value
                words.append(word)
                
            template_values = {
                               'words' : words
                               }
            self.response.out.write(template.render(get_template_path('view_words.html'), template_values))
        except search.Error:
            self.response.out.write(search.Error)

class ViewAllWordsPage(webapp2.RequestHandler):
    def get(self):
        f_cursor_param = self.request.get('f_cursor')
        b_cursor_param = self.request.get('b_cursor')

        template_values = {}
        if b_cursor_param:	
            words_query = Word.query(ancestor=create_dictionary_key()).order(Word.date)
            b_cursor = Cursor(urlsafe=self.request.get('b_cursor'))
            template_values['f_cursor'] = b_cursor.urlsafe()
            rev_curs = b_cursor.reversed()	
            words, next_cursor, more = words_query.fetch_page(WORDS_PER_PAGE, start_cursor=rev_curs)
            words.reverse()
            if more and next_cursor:
                template_values['b_cursor'] = next_cursor.reversed().urlsafe()
        else:
            words_query = Word.query(ancestor=create_dictionary_key()).order(-Word.date)
            f_cursor = Cursor(urlsafe=self.request.get('f_cursor'))
            template_values['b_cursor'] = f_cursor.urlsafe() 
            words, next_cursor, more = words_query.fetch_page(WORDS_PER_PAGE, start_cursor=f_cursor)
            if more and next_cursor:
			    template_values['f_cursor'] = next_cursor.urlsafe() 
        wordDTOs = []
        for word in words:
            wordDTOs.append(WordDTO(word.word, word.description, word.example))
        template_values['words'] = wordDTOs
        self.response.out.write(template.render(get_template_path('view_words.html'), template_values))

class GetRandomWords(webapp2.RequestHandler):
    def get(self):
        words_query = Word.query(ancestor=create_dictionary_key())
        randrange = words_query.count() if words_query.count() < DEFAULT_PAGE_SIZE else words_query.count() - DEFAULT_PAGE_SIZE + 1
        query_offset = random.randrange(randrange)
        words = words_query.fetch(5, offset=query_offset)
        result = []
        for word in words:
            result.append({'word' : word.word, 'description' : word.description, 'example' : word.example})
        self.response.out.write(json.dumps(result))

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(template.render(get_template_path('index.html'), dict()))

application = webapp2.WSGIApplication([
                                       ('/', MainPage),
                                       ('/save', PersistWordHandler),
                                       ('/viewall', ViewAllWordsPage),
                                       ('/random', GetRandomWords),
                                       ('/search', LookupWordHandler), ], debug=True)

