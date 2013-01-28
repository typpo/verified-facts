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
  subject, paragraph = cg.generate_paragraph()
  paragraph = paragraph.replace('\n', '<br><br>')
  imgurl = random.choice([
    "http://img703.imageshack.us/img703/5281/doent.gif",
    "http://upload.wikimedia.org/wikipedia/commons/thumb/2/28/70-%D0%BC_%D0%B0%D0%BD%D1%82%D0%B5%D0%BD%D0%BD%D0%B0_%D0%9F-2500_(%D0%A0%D0%A2-70).jpg/220px-70-%D0%BC_%D0%B0%D0%BD%D1%82%D0%B5%D0%BD%D0%BD%D0%B0_%D0%9F-2500_(%D0%A0%D0%A2-70).jpg",
    "http://www.windows2universe.org/sun/images/sunspots_max_min_sm.jpg",
    "http://www.handsonuniverse.org/activities/whatisit/w-img/SolSysFig.gif",
    "http://alexis.m2osw.com/images/plaque_pioneer.jpg",
  ])
  citations = cg.generate_citations()
  return render_template('index.html', subject=subject, text=paragraph,\
      imgurl=imgurl, citations=citations)

"""
@app.route("/path/<query>")
def path(query):
  return graph.lookup(query)
"""

ConspiracyGenerator().verify()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
