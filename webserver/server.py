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
from wsgiref.util import request_uri
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for
from datetime import datetime

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
#engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
# );""")
# engine.execute(
#    """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


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


@app.route('/')
def index():
    # DEBUG: this is debugging code to see what request looks like
    print(request.args)

    cursor = g.conn.execute("SELECT recipe_id, title FROM Recipe_Created")
    list1 = []
    list2 = []

    for recipe_id, title in cursor:
        list1.append(recipe_id)
        list2.append(title)
    cursor.close()

    queryfav = "SELECT list_id, name, aid FROM create_list WHERE favorite = True"

    cursor = g.conn.execute(queryfav)

    listid = []
    name = []
    aid = []

    for a, b, c in cursor:
        listid.append(a)
        name.append(b)
        aid.append(c)
    cursor.close()

    queryGeneral = "SELECT list_id, name, aid FROM create_list WHERE favorite = False"

    cursor = g.conn.execute(queryGeneral)

    gen_listid = []
    gen_name = []
    gen_aid = []

    for a, b, c in cursor:
        gen_listid.append(a)
        gen_name.append(b)
        gen_aid.append(c)
    cursor.close()

    print(list1)
    print(list2)
    mylist = zip(list1, list2)
    mylist2 = zip(list1, list2)
    favoriteList = zip(listid, name, aid)
    genList = zip(gen_listid, gen_name, gen_aid)

    context = dict(recipes2=mylist2, recipes=mylist,
                   favoriteList=favoriteList, genList=genList)

    return render_template("index.html", **context)


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
        tag_id.append(t)
        category.append(cat)
    cursor.close()

    recipe = zip(title, recipe_id, aid,
                 description, time_posted, recipe_user)

    comment = zip(comment_aid, comment_id, comment, username)

    tag = zip(tag_id, category)

    context = dict(recipe=recipe, comment=comment, tag=tag, recipeid=recipe_id)

    return render_template("recipe.html", **context)


@app.route('/list/<n>')
def list(n):

    print(n)

    query = "SELECT has_recipe.list_id, has_recipe.recipe_id, title FROM has_recipe, recipe_created WHERE list_id = " + \
        n + " AND has_recipe.recipe_id = recipe_created.recipe_id"

    cursor = g.conn.execute(query)
    list_id = []
    recipe_id = []
    title = []

    for a, b, c in cursor:
        list_id.append(a)
        recipe_id.append(b)
        title.append(c)

    cursor.close()

    listnameQuery = "SELECT name FROM create_list WHERE list_id = " + n
    cursor = g.conn.execute(listnameQuery)
    name = []
    for x in cursor:
        name.append(x)

    list = zip(list_id, recipe_id, title)
    print(title)
    print(name)

    context = dict(list=list, name=name)

    return render_template("listPages.html", **context)

# FOLLOWINGS QUERY THINGY


@app.route('/followings')
def followings():

    query5 = "SELECT Accounts.username, Follow.aid_2 FROM Accounts, Follow WHERE Accounts.aid = Follow.aid_1"

    cursor = g.conn.execute(query5)
    # cursor.execute(query)
    # row = cursor.fetchone()
    account = []
    follower = []
    # parse through favorite variable
    # if favorite == false
    for aUsername, f_aid in cursor:
        # can also be accessed using result[0]
        account.append(aUsername)
        follower.append(f_aid)

    cursor.close()
    print(account)
    print(follower)

    list = zip(account, follower)
    context = dict(list=list)

    return render_template("followings.html", **context)


@app.route('/login/addUser',  methods=['POST'])
def addUser():
    name = request.form['hi']
    print(name)

    cmd = 'INSERT INTO Accounts VALUES (:name1), (:name2)'

    g.conn.execute(text(cmd), name1=100, name2=name)
    return render_template("login.html")

# Example of adding new data to the database


@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    print(name)
    cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)'
    g.conn.execute(text(cmd), name1=name, name2=name)
    return redirect('/')


@app.route('/addRecipe', methods=['POST'])
def addRecipe():
    name = request.form['recipeName']
    description = request.form['description']
    print(name)
    print(description)

    count = 0
    cursor = g.conn.execute("SELECT count(*) FROM Recipe_Created")
    for n in cursor:
        print(n[0])  # count of recipes
        count = n[0]

    time = datetime.now()

    # default user is 1 (wendy)

    g.conn.execute(text(
        "INSERT INTO Recipe_Created VALUES (1, (:c), (:title), (:descript), (:timenow))"), c=count+1, title=name, descript=description, timenow=time)

    return redirect('/')


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/recipe/<n>/addComment', methods=['POST', 'GET'])
def addComment(n):
    comment = request.form['comment']
    print(comment)

    count = 0
    query = "SELECT count(*) FROM Recipe_contains"
    cursor = g.conn.execute(query)
    for num in cursor:
        print(num[0])  # count of recipes
        count = num[0]

    # default user is 1 (wendy)

    g.conn.execute(text(
        "INSERT INTO Recipe_contains VALUES (1, (:r), (:c), (:com))"), r=n, c=count+1, com=comment)

    return redirect(url_for('recipe', n=n))


@app.route('/addList', methods=['POST'])
def addList():
    name = request.form['listName']
    type = request.form['listtype']
    recipes = request.form.getlist('recipes')
    print(name)
    print(type)
    print(recipes)

    isfavorite = False

    if type == "favorite":
        isfavorite = True
    else:
        isfavorite = False

    print(isfavorite)

    count = 0
    cursor = g.conn.execute("SELECT count(*) FROM Create_list")
    for n in cursor:
        print(n[0])  # count of lists
        count = n[0]

    # default user is 1 (wendy)

    count = count+1

    g.conn.execute(text(
        "INSERT INTO Create_list VALUES ((:c), (:title), (:fav), 1)"), c=count, title=name, fav=isfavorite)

    for i in recipes:
        print(i)
        g.conn.execute(text(
            "INSERT INTO Has_recipe VALUES ((:list_id), (:recipe_id))"), list_id=count, recipe_id=i)

    return redirect(url_for('index'))


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
