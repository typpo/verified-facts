from flask import Flask, request, redirect, session, url_for, render_template
import json
import conspiracy

app = Flask(__name__)
app.secret_key = 'not a secret key'

@app.route("/")
def index():
  paragraph = conspiracy.generate_paragraph()
  paragraph = paragraph.replace('\n', '<br><br>')
  return render_template('index.html', text=paragraph)

"""
@app.route("/path/<query>")
def path(query):
  return graph.lookup(query)
"""

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
