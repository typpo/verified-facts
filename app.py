#!/usr/bin/env python
from flask import Flask, request, redirect, session, url_for, render_template
from generator.conspiracy import ConspiracyGenerator
from id_manager import IdManager
import urllib
import urlparse
import json
import random
import base64
import re
from unidecode import unidecode

app = Flask(__name__)
app.secret_key = 'not a secret key'

page_cache = IdManager()

@app.route("/")
def index():
  return generate_conspiracy_page()

@app.route("/verification")
def verification():
  return render_template('verification.html')

@app.route("/search")
def search():
  return render_template('lookup.html')

@app.route("/report")
def report():
  return render_template('report.html')

@app.route("/directory")
def directory():
  links = []
  for x in ConspiracyGenerator().get_all_subjects():
    val = (x[0], urllib.quote(x[0].encode('utf-8').replace('/', '|')),\
        urllib.quote(base64.b64encode(x[1])))
    links.append(val)
  return render_template('directory.html', \
      links=links)

@app.route("/s/<subject>")
def path(subject):
  subject_category = base64.b64decode(urllib.unquote(request.args.get('c')))
  subject_unescaped = urllib.unquote(subject).replace('|', '/')   # ghetto escaping

  # put it in twice so it's used more
  preset_mappings = {}
  preset_mappings[subject_category] = [subject_unescaped, subject_unescaped]

  page_id, args = generate_conspiracy_args(preset_mappings)

  return redirect('/i/%s/%s' % (subject, page_id), 302)


@app.route("/i/<subject>/<page_id>")
def id_path(subject, page_id):
  try:
    args = page_cache.get_kwargs(page_id)
    return render_template('index.html', **args)
  except:
    return "bad id"

def generate_conspiracy_page(preset_mappings={}):
  page_id, args = generate_conspiracy_args(preset_mappings)
  return render_template('index.html', **args)

def generate_conspiracy_args(preset_mappings):
  cg = ConspiracyGenerator()
  subject, paragraph, imgurl = cg.generate_paragraph(preset_mappings)
  paragraph_lines = paragraph.split('\n')
  imgpos = random.randint(1, 2)
  citations = cg.generate_citations()

  slug = slugify(subject)
  page_id = page_cache.get_next_id()

  permalink = 'http://verifiedfacts.org/i/%s/%s' % (slug, page_id)

  args = {
      'subject': subject,
      'permalink': permalink,
      'text': paragraph_lines,
      'imgurl': imgurl,
      'imgpos': imgpos,
      'citations': citations,
      'page_id': page_id,
  }
  page_cache.save(page_id, args)
  return page_id, args

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))

def initialize():
  print 'Verifying and generating initial pages...'
  cg = ConspiracyGenerator()
  cg.verify()
  if page_cache.first_time:
    # generate slugged pages for everything ahead of time
    for x in ConspiracyGenerator().get_all_subjects():
      obj = {x[1]: [x[0], x[0]]}
      generate_conspiracy_args(obj)

initialize()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', use_reloader=False)
