from flask_app import app
from flask import render_template,redirect,request,session,flash
from flask_app.models.user import User
from flask_app.models.recipe import Recipe
from flask_bcrypt import Bcrypt
from flask import jsonify       
bcrypt = Bcrypt(app)
#import datetime to change date format


@app.route("/")
def form():
    return render_template("create.html")

@app.route('/register', methods=["POST"])
def create_user():
    
    pw_hash = bcrypt.generate_password_hash(request.form['pw'])
    
    data = {
        "first_name": request.form["fname"],
        "last_name" : request.form["lname"],
        "email" : request.form["email"],
        "password" : pw_hash
    }
    
    # We pass the data dictionary into the save method from the User class.
    id= User.save(data)
    message={}
    # Don't forget to redirect after saving to the database.
    if id:
        message['ok']= True
        session['user_id'] = id
    else:
        message['ok']= False
        message['content'] = str(id)
    return jsonify(message)

@app.route('/login', methods=["POST"])
def login_user():
    # First we make a data dictionary from our request.form coming from our template.
    # The keys in data need to line up exactly with the variables in our query string.

    data = {
        "email" : request.form["email"],
        "password" : request.form["pw"]
    }

    message= {}

    user= User.login(data)
    if not user:
        message['ok'] = False
        message['content'] = "An error ocurred while logging in"
        return jsonify(message)
    elif not bcrypt.check_password_hash(user['password'], data['password']):
        message['ok'] = False
        message['content'] = "Wrong password. Please enter the correct password"
        return jsonify(message)
    session['user_id'] = user['id']
    message['ok']= True
    return jsonify(message) 


@app.route("/homepage")
def read():

    if not 'user_id' in session:
        flash("Please login to access the site","login")
        return redirect("/")
    recipes= Recipe.get_all_recipes()
    user= User.get_user_info(data={'id':session['user_id']})
    return render_template("read.html", recipes=recipes, user=user)


@app.route("/addRecipe", methods=["POST"])
def sendRecipe():
    if not 'user_id' in session:
        flash("Please login to access the site","login")
        return redirect("/")

    data = {
        "name" : request.form["name"],
        "description" : request.form["description"],
        "instructions": request.form["instructions"],
        "under_30min": request.form["under_30min"],
        "made_on": request.form["made_on"],
        "user_id": session["user_id"]
    }

    message = {}
    log = Recipe.save(data)
    if log:
        message['ok']= True
        data['id'] = log
        message['data'] = data
        return jsonify(message)
    else:
        message['ok']=False
        message['content']= str(log)
        return jsonify(message)

@app.route("/recipes/<int:id>")
def showRecipe(id):
    if not 'user_id' in session:
        flash("Please login to access the site","login")
        return redirect("/")
    
    user= User.get_user_info(data={'id':session['user_id']})
    recipe = Recipe.get_recipe_info(data={'id':id})
    return render_template("show_recipe.html", recipe=recipe, user=user)



@app.route("/recipes/edit/<int:id>")
def editRecipe(id):
    if not 'user_id' in session:
        flash("Please login to access the site","login")
        return redirect("/")

    user= User.get_user_info(data={'id':session['user_id']})
    recipe = Recipe.get_recipe_info(data={'id':id})
    print(recipe)
    return render_template("edit_recipe.html", id = id, recipe=recipe, user=user)

@app.route("/updateRecipe", methods=["POST"])
def updateRecipe():
    if not 'user_id' in session:
        flash("Please login to access the site","login")
        return redirect("/")
    

    data = {
        "name" : request.form["name"],
        "description" : request.form["description"],
        "instructions": request.form["instructions"],
        "under_30min": request.form["under_30min"],
        "made_on": request.form["made_on"],
        "user_id": session["user_id"],
        "id": request.form["id"]
    }

    
    message = {}
    result = Recipe.update(data)
    print(result,type(result))
    if type(result) is not bool:
        message['ok'] = True
        return message
    else:
        message['ok']= False
        return message


@app.route("/deleteRecipe", methods=["POST"])
def deleteRecipe():
    if not 'user_id' in session:
        flash("Please login to access the site","login")
        return redirect("/")
    
    print(request.form)
    log = Recipe.delete_recipe(request.form)
    message = {}
    
    if log!= False:
        message['ok']= True
        return jsonify(message)
    else:
        message['ok']=False
        return jsonify(message)


@app.route("/logout")
def clearsession():
    session.clear()
    return redirect('/')