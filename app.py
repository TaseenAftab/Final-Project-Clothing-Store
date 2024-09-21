from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

from funcs import login_required,usd

app = Flask(__name__)

#configure jinja to show dollar sign
app.jinja_env.filters["usd"] = usd

# Configure the database to use
store=SQL("sqlite:///store.db")
products=SQL("sqlite:///products.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route('/')
def index():

    categories=products.execute("SELECT * FROM categories")
    if not login_required():
        print ("not logged in!")
    
    return render_template("index.html",categories=categories,logincheck=login_required()) 

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    

@app.route('/<category>')
def show_category(category):
    
    prolist=products.execute("SELECT * FROM categories")
    
    
    exists = any(item['tag'] == category for item in prolist)
    if exists==False:
        return "not a valid directory"
    
    items = products.execute("SELECT * FROM products WHERE id IN (SELECT id FROM prod_tags WHERE tag = ?);",category)
    return render_template('category.html', category=category, items=items,logincheck=login_required())    
            


@app.route('/<category>/<item>')
def show_item(category, item):
    prolist=products.execute("SELECT * FROM categories")
    exists = any(prod['tag'] == category for prod in prolist)

    if exists==False:
        return render_template("apology.html",message="invalid address",error="404",logincheck=login_required())
    
    items = products.execute("SELECT * FROM products WHERE id IN (SELECT id FROM prod_tags WHERE tag = ?);",category)
    exists=any(itemlist['name'] == item for itemlist in items)

    if exists==False:
        return render_template("apology.html",message="invalid address",error="404",logincheck=login_required())
    

    realitem = next(val for val in items if val['name'] == item)
    return render_template('item.html', category=category, item=realitem,logincheck=login_required())


@app.route("/register", methods=["GET","POST"])
def register():


    # For accessing route for registering
    if request.method=='GET':
        return render_template ("register.html")
    
    username=request.form.get('username')
    if not username or (len(username)<7):
        return render_template("apology.html",message="Enter a Username atleast 8 characters long",error="404",logincheck=login_required())
    password=request.form.get('password')
    if not password or len(password)<7:
       return render_template("apology.html",message="Enter a password, atleast 8 characters long",logincheck=login_required())
    confirmation=request.form.get('confirmation')
    if not confirmation:
        return render_template("apology.html",message="Incorrect Password",logincheck=login_required())
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
         return render_template("apology.html",message="Enter a valid username",logincheck=login_required())
    password=request.form.get('password')
    if not password or len(password)<7:
         return render_template("apology.html",message="Enter a valid password",logincheck=login_required())

    user=store.execute("SELECT * FROM users WHERE username=?",username)
    if len(user)==0:
         return render_template("apology.html",message="user does not exist",logincheck=login_required())
    if check_password_hash(user[0]["hash"],password)==False:
         return render_template("apology.html",message="Invalid Password",logincheck=login_required())
    
    #successfully logged in
    session['user_id']=user[0]["id"]
    return redirect("/")
    


@app.route("/profile",methods=["GET","POST"])
def profile():
    if not login_required():
        print ("not logged in!")
        return render_template("apology.html",message="log in first")

    user=store.execute("SELECT * FROM users WHERE id=?",session['user_id'])
    if not (user[0]['username']):
        return render_template("apology.html",message="username not found")
    
    #to view profile
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
            add_check=0

        return render_template("profile.html",add_check=add_check,con_check=con_check,username=username,contact=contact,address=address,logincheck=login_required())

    if request.method=="POST":
        
        #if user is adding/changing contact number
        check=request.form.get('reqcheck')
        if check=='con':
            contact=request.form.get('contact')
            if contact=='':
                contact=0
                return render_template("apology.html", message="Enter a valid Number.")
        
            
            try:
                contact=int(contact)
            except ValueError:
                return render_template("apology.html",message="Enter a valid Nu mber.")
                
            store.execute("UPDATE users SET contact=? WHERE id=?",contact,session['user_id'])
            return redirect('/profile')
        
        #if user is adding/changing address
        if check=='add':
            address=request.form.get('address','')
            if address=='':
                address='None'
                return render_template("apology.html", message="Enter a valid Address.")
            
                
            print(address)
            store.execute("UPDATE users SET address=? WHERE id=?",address,session['user_id'])
            return redirect('/profile')
        
        #checking both of the passwords
        if check=='pass':
                old=request.form.get('old_password')
                new=request.form.get('new_password')
                if old=='' or new=='':
                    return render_template("apology.html",message="Enter both passwords.")
        
                #hashing and storing the password
                user_pass=store.execute("SELECT hash FROM users WHERE id=?",session['user_id'])[0]['hash']
                if check_password_hash(user_pass,old)==False:
                    return "Invalid Password"
                else:
                    store.execute("UPDATE users SET hash =? WHERE id=?",generate_password_hash(new),session['user_id'])
                    return redirect('/')


@app.route("/cart", methods=["GET",'POST'])
def cart():
    #to show the cart
    if request.method=="GET":
        cartitems=store.execute("SELECT * FROM cart WHERE userid=? AND quantity <> 0",session['user_id'])
        return render_template("cart.html",cartitems=cartitems,logincheck=login_required())
    
    if request.method=="POST":
        if not login_required():
            print ("not logged in!")
            return render_template("apology.html",message="log in first")
        

        itemid=request.form.get('product_id')
        quantity=request.form.get('quantity')
        try:
            quantity=int(quantity)
        except ValueError:
            if quantity=='':
                quantity=0
                quantity=int(quantity)
            else:
                return render_template("apology.html",message="Not a valid Quantity!")

        updatecheck=int(request.form.get('updatecheck')) #for updating quantity from cart
        print (updatecheck)
        if updatecheck==1:
            if quantity==0:#if updated quantity is zero it will delete the row
                store.execute("DELETE FROM cart WHERE itemid=?",itemid)
            store.execute("UPDATE cart SET quantity=? WHERE userid=? AND itemid=?",quantity,session['user_id'],itemid)


        item=products.execute("SELECT * FROM products WHERE id=?",itemid)
        cartitem=store.execute("SELECT * FROM cart WHERE itemid=? AND userid=?",itemid,session['user_id'])
        
        #if no such item ALREADY exists in cart
        if len(cartitem)==0:
            category=products.execute("SELECT tag FROM prod_tags WHERE id=?",itemid)
            
            store.execute("INSERT INTO cart (userid,itemid,itemname,price,quantity,category) VALUES(?,?,?,?,?,?)",session['user_id'],itemid,item[0]["name"],item[0]["price"],quantity,category[0]['tag'])
        #if item already exists
        elif updatecheck==0 and len(cartitem)!=0:
            old_quantity=int(cartitem[0]["quantity"])
            quantity=old_quantity+int(quantity)
            store.execute("UPDATE cart SET quantity=? WHERE userid=? AND itemid=?",quantity,session['user_id'],itemid)
        cartitems=store.execute("SELECT * FROM cart WHERE userid=? AND quantity <> 0",session['user_id'])
        return render_template('cart.html',cartitems=cartitems,logincheck=login_required()) 



@app.route("/checkout",methods=["GET"])
def checkout():
    if not login_required():
        print ("not logged in!")
        return render_template("apology.html",message="log in first")


    user=store.execute("SELECT * FROM users WHERE id=?",session['user_id'])

    #to view profile
    username=user[0]['username']
    contact=user[0]['contact']
    address=user[0]['address']

    if address=='None' or contact=='0':
        return render_template("apology.html",message=f' Enter your Contact Number and Address in <a href="/profile"> Profile </a>.' )
    cartitems=store.execute("SELECT * FROM cart WHERE userid=? AND quantity <> 0",session['user_id'])
    return render_template("checkout.html",cartitems=cartitems,logincheck=login_required(),username=username,address=address)

@app.route("/order-completed")
def order_completed():
    return render_template("order-completed.html",logincheck=login_required())


if __name__ == '__main__':
    app.run(debug=True)
