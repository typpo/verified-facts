#!/usr/bin/env python
from flask import Flask, request, redirect, session, url_for, render_template
from conspiracy import ConspiracyGenerator
import json
import random

app = Flask(__name__)
app.secret_key = 'not a secret key'

@app.route("/")
def index():
  cg = ConspiracyGenerator()
  subject, paragraph, imgurl = cg.generate_paragraph()
  paragraph = paragraph.replace('\n', '<br><br>')
  citations = cg.generate_citations()
  return render_template('index.html', subject=subject, text=paragraph,\
      imgurl=imgurl, citations=citations)

@app.route("/verification")
def verification():
  return render_template('verification.html')

@app.route("/directory")
def directory():
  return render_template('directory.html', \
      subjects=ConspiracyGenerator().get_all_subjects())

"""
@app.route("/path/<query>")
def path(query):
  return graph.lookup(query)
"""

ConspiracyGenerator().verify()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
