#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import os
import jinja2
import cgi

JINJA_ENVIRONMENT = jinja2.Environment(
                                       loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)

class BaseHandler(webapp2.RequestHandler):
    def render(self, html, values={}):
        template = JINJA_ENVIRONMENT.get_template(html)
        self.response.write(template.render(values))

class MergingWords_Input(BaseHandler):
    def get(self):
        return self.render('MergeWord_Page1.html')

class MergingWords_Output(BaseHandler):
    def get(self):
        self.render('MergeWord_Page2.html')
        word1= cgi.escape(self.request.get("word1"))
        word2= cgi.escape(self.request.get("word2"))
        word1 = list(word1)
        word2 = list(word2)
        if len(word1) >= len(word2):
            for i in range(len(word2)):
                word1.insert(2*i+1, word2[i])
            output = ''.join(word1)
        else:
            for i in range(len(word1)):
                word2.insert(2*i+1,word1[i])
            output = ''.join(word2)
        self.response.out.write(output)


app = webapp2.WSGIApplication([
    ('/', MergingWords_Input),
    ('/output', MergingWords_Output)
], debug=True)

