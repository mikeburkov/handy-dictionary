'''
Created on Nov 14, 2013

@author: mburkov
'''
import os

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import search
import webapp2


PARENT_KEY = 'dictionary'


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
        words_query = Word.query(ancestor=create_dictionary_key()).order(-Word.date)
        words = words_query.fetch()
        wordDTOs = []
        for word in words:
            wordDTOs.append(WordDTO(word.word, word.description, word.example))
        template_values = {
            'words': wordDTOs
        }
        self.response.out.write(template.render(get_template_path('view_words.html'), template_values))

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(template.render(get_template_path('index.html'), dict()))

application = webapp2.WSGIApplication([
                                       ('/', MainPage),
                                       ('/save', PersistWordHandler),
                                       ('/viewall', ViewAllWordsPage),
                                       ('/search', LookupWordHandler), ], debug=True)

