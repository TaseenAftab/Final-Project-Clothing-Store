# CS50 Final Project - Taseen's Store
This is my final project for CS50 and in this project I aim to make a clothing store, an e-commerce store essentially. As I have had experience of using HTML, CSS, and Bootstrap to make websites in the past, I decided to make a web application with these but this time also add Flask and Python into the mix and make a store which is not only functional but also responsive. Yes this web application is responsive.

Technologies used:
  HTML
  CSS
  BOOTSTRAP
  JavaScript
  SQLite3
  Python
  Flask framerwork

## How the web application works?
The idea behind this web application is simple: there is an e-commerce store called Taseen's store and on this store there are three types of products that are available, which are:
1. Sneakers
2. Shirts
3. Pants

Now not only can viewers view these products, they can also register, login, add those items to their carts and then place their orders, basically simulating an actual e-commerce store. You will first of all be asked to register. You can add a username and you will have to add password twice in order to register. The criteria for password and username both is at least 8 characters, if this criteria is met the password will be encoded with werkzeug.security.  Once you have successfully registered, you can go on to login. 
Once you have logged in, you can add products to your card and you can also view your profile. In your profile, you can add your contact number and your house address and there is also an option to change your password.
If you go into the product categories, You can add products to your cart directly from categories or you can go into further detail on the products from the individual product pages and you can add to cart from there. 
In your cart, you can change the quantities of each products. You can choose to totally remove an item or increase their quantity. After which you can proceed to checkout and be given a subtotal. Following which your order can be placed.

### Pages/Files used
The web application utilizes a lot of pages/files. From those pages are:
- app.py: contains the main logic of the code, utilizes python language and the flask framework.
- funcs.py: contains a few funtions which are needed in the code.
- apology.html : Shows error message.usually rendered when user gives a misinput or doesnt fill the form as per the requirements. 
- cart.html : Shows the user their cart.
- category.html : Shows the many categories of products avilaible (only 3 in this case). 
- checkout.html : displays final list of products and their subtotal before placing order.
- footer.html : is the footer of the page.
- index.html : is the main page, where all of the categories are.
- item.html : shows individual items,their price, description, and an option to add them to cart while also an option to choose how many to add to cart.
- layout.html : Is the main layout used by all pages.
- login.html : Is used to log the user in.
- order completed.html : shows a final congrulatory message after order is placed.
- profile.html : allows user to view their profile, change their password, add an address or contact number or update either.
- register.html: lets user register requiring a valid unused username and an 8 character+ password to be entered twice.

### Routing and Sessions
Each and every route checks if the user is logged in or not. If the user is not logged in within the header, they will not be shown the options to go into card, into profile or rather they will only be shown the option to log in and register.Once the user has logged in, their session will be created (serialized and deserialized) and stored in the cookies.

### Databases
Two databases have been used in this project:
1. products.db - Contains information on all of the individual products and of the product categories.
2. store.db - Contains a record of all of the users, their cards, their information, and their profile.
Both of these contain multiple tables in order to properly utilize the information.

## Help taken
Since this is my first project of this scale, I have utilized help from a multitude of sources. Mainly in this regard, ChatGPT. I've used it for some of my Python code and some of my Bootstrap code.
