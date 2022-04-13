#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "cs3858"
DB_PASSWORD = "3049"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":" + \
    DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute(
    """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request

    The variable g is globally accessible
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)

    #
    # example of a database query
    #

    cursor = g.conn.execute("SELECT recipe_id, title FROM Recipe_Created")
    list1 = []
    list2 = []
    recipes = {"recipe_id": [], "title": []}
    for recipe_id, title in cursor:
        # can also be accessed using result[0]
        list1.append(recipe_id)
        list2.append(title)
    cursor.close()

    mylist = zip(list1, list2)

    context = dict(recipes=mylist)

    return render_template("index.html", **context)


@app.route('/another')
def another():

    return render_template("anotherfile.html")


@app.route('/recipe/<n>')
def recipe(n):

    print(n)

    query = "SELECT Recipe_Created.aid, title, recipe_id, description, time_posted, username FROM Recipe_Created, Accounts WHERE Recipe_Created.aid=Accounts.aid AND recipe_id = '" + n + "'"

    cursor = g.conn.execute(query)
    aid = []
    title = []
    recipe_id = []
    description = []
    time_posted = []
    recipe_user = []
    for result in cursor:
        # can also be accessed using result[0]
        title.append(result['title'])
        recipe_id.append(result['recipe_id'])
        aid.append(result['aid'])
        description.append(result['description'])
        time_posted.append(result['time_posted'])
        recipe_user.append(result['username'])
    cursor.close()

    query2 = "SELECT Recipe_contains.aid, comment_id, comment, username FROM Recipe_contains, Accounts where Recipe_contains.aid=Accounts.aid AND recipe_id = " + n

    cursor = g.conn.execute(query2)
    comment_aid = []
    comment_id = []
    comment = []
    username = []

    for a, c_id, c, u in cursor:
        # can also be accessed using result[0]
        comment_aid.append(a)
        comment_id.append(c_id)
        comment.append(c)
        username.append(u)
    cursor.close()

    print(query2)

    query3 = "SELECT Has_tags.tag_id, tags.category FROM Has_tags, Recipe_Created, tags WHERE Has_tags.recipe_id =Recipe_Created.recipe_id AND Has_tags.tag_id = Tags.tag_id AND Has_tags.recipe_id =" + n

    cursor = g.conn.execute(query3)
    tag_id = []
    category = []

    for t, cat in cursor:
        # can also be accessed using result[0]
        tag_id.append(t)
        category.append(cat)
    cursor.close()

    recipe = zip(title, recipe_id, aid,
                 description, time_posted, recipe_user)

    comment = zip(comment_aid, comment_id, comment, username)

    tag = zip(tag_id, category)

    context = dict(recipe=recipe, comment=comment, tag=tag)

    return render_template("recipe.html", **context)


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    print(name)
    cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)'
    g.conn.execute(text(cmd), name1=name, name2=name)
    return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()