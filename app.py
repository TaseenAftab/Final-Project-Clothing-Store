from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

from funcs import login_required

app = Flask(__name__)

# Configure the database to use
store=SQL("sqlite:///store.db")
products=SQL("sqlite:///products.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route('/')
def index():
    logincheck=1
    if login_required()==False:
        logincheck=0
    categories=products.execute("SELECT * FROM categories")
    if not login_required():
        print ("not logged in!")
    return render_template("index.html",categories=categories,logincheck=logincheck) 

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    
# Route for categories (e.g., /Shirts or /Pants)
@app.route('/<category>')
def show_category(category):
    
    prolist=products.execute("SELECT * FROM categories")
    
    
    exists = any(item['tag'] == category for item in prolist)
    if exists==False:
        return "not a valid directory"
    
    items = products.execute("SELECT name,price FROM products WHERE id IN (SELECT id FROM prod_tags WHERE tag = ?);",category)
    return render_template('category.html', category=category, items=items)      
            

# Route for specific items within a category (e.g., /Shirts/shirt1)
@app.route('/<category>/<item>')
def show_item(category, item):
    prolist=products.execute("SELECT * FROM categories")
    exists = any(prod['tag'] == category for prod in prolist)

    if exists==False:
        return "invalid address"
    
    items = products.execute("SELECT * FROM products WHERE id IN (SELECT id FROM prod_tags WHERE tag = ?);",category)
    exists=any(itemlist['name'] == item for itemlist in items)

    if exists==False:
        return "invalid address"
    

    realitem = next(val for val in items if val['name'] == item)
    return render_template('item.html', category=category, item=realitem)


@app.route("/register", methods=["GET","POST"])
def register():


    # For accessing route for registering
    if request.method=='GET':
        return render_template ("register.html")
    
    username=request.form.get('username')
    if not username or (len(username)<7):
        return "enter a username, atleast 8 characters long"
    password=request.form.get('password')
    if not password or len(password)<7:
         return "Enter a password, atleast 8 characters long"
    confirmation=request.form.get('confirmation')
    if not confirmation:
        return "Enter password again"   
    if confirmation!=password:
            return "Passwords do not match"


    if len(store.execute("SELECT id FROM users WHERE username=?",username))==0:
        store.execute("INSERT INTO users (username, hash) VALUES(?,?)",username,generate_password_hash(password))
        rows = store.execute("SELECT * FROM users WHERE username=(?)", username)
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return "Username already in use"
        


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=='GET':
        return render_template ("login.html")
    
    username=request.form.get('username')
    if not username or (len(username)<7):
        return "enter a valid username."
    password=request.form.get('password')
    if not password or len(password)<7:
         return "Enter a valid password."

    user=store.execute("SELECT * FROM users WHERE username=?",username)
    if len(user)==0:
        return "user does not exist"
    if check_password_hash(user[0]["hash"],password)==False:
        return "Invalid Password"
    
    #successfully logged in
    session['user_id']=user[0]["id"]
    return redirect("/")
    


@app.route("/profile",methods=["GET","POST"])
def profile():
    if not login_required():
        print ("not logged in!")
        return "log in first"

    user=store.execute("SELECT * FROM users WHERE id=?",session['user_id'])
    if not (user[0]['username']):
        return "username not found"
    

    if request.method=="GET":
        if not (user[0]['username']):
            return "username not found"
        username=user[0]['username']
        contact=user[0]['contact']
        address=user[0]['address']
        con_check,add_check=1,1
        if contact==0:
            con_check=0
        if address=='None':
            add_check=0;
        return render_template("profile.html",add_check=add_check,con_check=con_check,username=username,contact=contact,address=address)

    if request.method=="POST":
        if request.form.get('contact'):
            contact=request.form.get('contact')
            try:
                contact=int(contact) 
            except ValueError:
                return "Invalid Number"
            store.execute("UPDATE users SET contact=? WHERE id=?",contact,session['user_id'])
            return redirect('/profile')
        

        if request.form.get('address'):
            address=request.form.get('address')
            store.execute("UPDATE users SET address=? WHERE id=?",address,session['user_id'])
            return redirect('/profile')
        

        if request.form.get('old_password') or request.form.get('new_password'):
            if not request.form.get('old_password') or not request.form.get('new_password'):
                return "Enter the password"
            old=request.form.get('old_password')
            new=request.form.get('new_password')


            user_pass=store.execute("SELECT hash FROM users WHERE id=?",session['user_id'])[0]['hash']
            if check_password_hash(user_pass,old)==False:
                return "Invalid Password"
            else:
                store.execute("UPDATE users SET hash =? WHERE id=?",generate_password_hash(new),session['user_id'])
                return redirect('/')


@app.route("/cart", methods=["GET",'POST'])
def cart():
    if request.method=="GET":
        cartitems=store.execute("SELECT * FROM cart WHERE userid=?",session['user_id'])
        return render_template("cart.html",cartitems=cartitems)
    
    if request.method=="POST":
        itemid=request.form.get('product_id')
        quantity=request.form.get('quantity')
        item=products.execute("SELECT * FROM products WHERE id=?",itemid)

        cartitem=store.execute("SELECT * FROM cart WHERE itemid=? AND userid=?",itemid,session['user_id'])
        if len(cartitem)==0:
            category=products.execute("SELECT tag FROM prod_tags WHERE id=?",itemid)
            
            store.execute("INSERT INTO cart (userid,itemid,itemname,price,quantity,category) VALUES(?,?,?,?,?,?)",session['user_id'],itemid,item[0]["name"],item[0]["price"],quantity,category[0]['tag'])

        else:
            old_quantity=int(cartitem[0]["quantity"])
            quantity=old_quantity+int(quantity)
            store.execute("UPDATE cart SET quantity=? WHERE userid=? AND itemid=?",quantity,session['user_id'],itemid)
        cartitems=store.execute("SELECT * FROM cart WHERE userid=?",session['user_id'])
        return render_template('cart.html',cartitems=cartitems) 





if __name__ == '__main__':
    app.run(debug=True)
