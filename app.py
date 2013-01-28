#!/usr/bin/env python
from flask import Flask, request, redirect, session, url_for, render_template
from conspiracy import ConspiracyGenerator
import json
import random
import base64
import re

app = Flask(__name__)
app.secret_key = 'not a secret key'

@app.route("/")
def index():
  return generate_conspiracy_page()

@app.route("/verification")
def verification():
  return render_template('verification.html')

@app.route("/directory")
def directory():
  links = [(x[0], base64.b64encode(x[1])) \
      for x in ConspiracyGenerator().get_all_subjects()]
  return render_template('directory.html', \
      links=links)

@app.route("/s/<subject>")
def path(subject):
  subject_category = base64.b64decode(request.args.get('c'))
  preset = {}
  preset[subject_category] = [subject]
  return generate_conspiracy_page(preset_mappings=preset)

def generate_conspiracy_page(preset_mappings={}):
  cg = ConspiracyGenerator()
  subject, paragraph, imgurl = cg.generate_paragraph(preset_mappings)
  paragraph = paragraph.replace('\n', '<br><br>')
  citations = cg.generate_citations()
  return render_template('index.html', subject=subject, text=paragraph,\
      imgurl=imgurl, citations=citations)

# TODO match slugs with category names
"""
from unidecode import unidecode
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
    #Generates an ASCII-only slug
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))
"""

"""
@app.route("/path/<query>")
def path(query):
  return graph.lookup(query)
"""

ConspiracyGenerator().verify()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
