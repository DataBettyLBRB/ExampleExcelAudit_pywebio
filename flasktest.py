import flask

app = flask.Flask(__name__)
app.config["DEBUG"] = True


def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

app.add_url_rule('/', 'home', home)
app.run()
