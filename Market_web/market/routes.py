from market import app
from flask import render_template, flash, redirect, url_for, request
from market.models import Item, User
from .helpers import usd 
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, PostForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user




# Custom filter
app.jinja_env.filters["usd"] = usd

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():

    purchase_form = PurchaseItemForm()

    selling_form = SellItemForm()
    
    # same as form.validate_on_submit but it avoid the resubmittion of the form when the refresh
    if request.method == 'POST':
        # getting the purchase item
        purchase_item = request.form.get('purchase_item')
       
        item_verif = Item.query.filter_by(name=purchase_item).first()
       
         
        if item_verif:
            # Puchassing an item
            # verifiying if the user can buy the item
            if current_user.can_purchase(item_verif):
                
                # credit_user = User.query.get(item_verif.owner)
                
                # credit_user.budget += item_verif.price
                
                
                # db.session.commit()


                # item_verif.owner = current_user.id
                # current_user.budget -= item_verif.price
                # db.session.commit()
     
                item_verif.buy(current_user)
                
                flash(f'Successful! You purchased {item_verif.name} for {usd(item_verif.price)}', category='success')
            else:
                flash(f"Insuffisant cash! you don't have enough money to purchase {item_verif.name}", category='danger')
        
        # Selling item
        # getting the sold item 
        sold_item = request.form.get('sold_item')
       
        item_verif = Item.query.filter_by(name=sold_item).first()
       
         
        if item_verif:
            # selling an item
            # verifiying if the user has the item
            if current_user.can_sell(item_verif):
                
                # item_verif.owner = current_user.id
                # current_user.budget -= item_verif.price
                # db.session.commit()
     
                item_verif.sell(current_user)
                
                flash(f'Successful! You sold {item_verif.name} back to market for {usd(item_verif.price)}', category='success')
            else:
                flash(f"Error Error! something went wrong with the selling of {item_verif.name}", category='danger')

        return redirect(url_for('market_page'))
    
    if request.method == 'GET':
        # querying the items available
        items = Item.query.order_by(Item.date.desc()).filter_by(possesion=None)
        
        # getting user owns
        user_owns = Item.query.filter_by(possesion=current_user.id)       
        
        return render_template('market.html', items=items, purchase_form=purchase_form, user_owns=user_owns, selling_form=selling_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():

    form = RegisterForm()

    # check if the user has submit the form, same as if request.method == 'POST'
    # and updating the user table
    if form.validate_on_submit():
        username = (form.username.data).title()
        email = form.email_address.data
        password1 = form.password1.data

        new_user = User(username=username, email=email, password=password1)
        db.session.add(new_user)
        db.session.commit()

        # acts as a session (login_user)
        # and this allow the user to be directed to market page
        login_user(new_user)

        flash(f'Account created successfully! You are now logged in as {username}', category='success')

        return redirect(url_for('market_page'))
   
    # checking for errors
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')


    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login_page():

    form = LoginForm()

    # check if the user has submit the form, same as if request.method == 'POST'
    # and checking if the user has an existing account
    if form.validate_on_submit():
        username = (form.username.data).title()
        password = form.password.data
        
        attempted_user = User.query.filter_by(username=username).first()

        if attempted_user and attempted_user.check_password(attempted_password=password):

            login_user(attempted_user)

            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')

            return redirect(url_for('market_page'))

        else:
            flash('Username and password are not match! Please try again', category='danger')


    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!', category='info')

    return redirect(url_for('home_page'))


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def post():

    form = PostForm()

    if request.method == 'POST':
        product_name = request.form.get('product_name').title()
        product_price = request.form.get('product_price')
        barcode = request.form.get('barcode')
        description = request.form.get('description')

        barcode_verif = Item.query.filter_by(barcode=barcode).first()

        if not product_name:
            flash('Missing product name! Please fill the product name.', category='danger')
            
            return redirect(url_for('post'))
        elif not product_price or not product_price.isnumeric() or int(product_price) < 1:
            flash('Missing product price! Please type again the product price.', category='danger')

            return redirect(url_for('post'))
        elif not barcode or not barcode.isnumeric() or int(barcode) < 1 or len(barcode) != 12 or barcode_verif:
            flash('Invalid Barcode! Please type a new barcode or generate.', category='danger')

            return redirect(url_for('post'))
        else:
            product_price = int(product_price)

        try:
            new_item = Item(name=product_name, price=product_price, barcode=barcode, description=description, owner=current_user.id)
            db.session.add(new_item)
            db.session.commit()

            flash(f"{product_name} has been added in the market for a price of {usd(product_price)}.", category='success')
            
            
            return redirect(url_for('market_page'))
        except Exception as error:
            flash('Something went wrong! Please try again', category='danger')

            return redirect(url_for('post'))

    return render_template('post.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

     # getting user owns
    user_owns = Item.query.order_by(Item.date.desc()).filter_by(owner=current_user.id)
    
    selling_form = SellItemForm()

    return render_template('profile.html', user_owns=user_owns, selling_form=selling_form)



@app.route('/post/update/<int:post_id>', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    
    edit_post = Item.query.get_or_404(post_id)

    if edit_post.owner == current_user.id and request.method == 'GET':

        form = PostForm()
        form.description.data = edit_post.description
    
        return render_template('updatePost.html', form=form, edit_post=edit_post)

    if request.method == 'POST':
        
        product_name = request.form.get('product_name').title()
        product_price = request.form.get('product_price')
        barcode = request.form.get('barcode')
        description = request.form.get('description')
        print(barcode)
        if barcode != None:
            flash('The barcode cannot change!!', category='danger')

            return redirect(url_for('market_page'))
        if not product_name:
            flash('Missing product name! Please fill the product name.', category='danger')
            
            return redirect(url_for('market_page'))
        elif not product_price or not product_price.isnumeric() or int(product_price) < 1:
            flash('Missing product price! Please type again the product price.', category='danger')

            return redirect(url_for('market_page'))
        else:
            product_price = int(product_price)

        try:
            edit_post.name=product_name
            edit_post.price=product_price
            edit_post.description=description

            db.session.commit()

            flash(f"{product_name} has been updated in the market for a price of {usd(product_price)}.", category='success')
            
            
            return redirect(url_for('market_page'))
        except Exception as error:
            flash('Something went wrong! Please try again', category='danger')

            return redirect(url_for('market_page'))

    flash('You do not have an authorisation to access this Item!!!', category='danger')
    return redirect(url_for('market_page'))