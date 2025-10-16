import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from jinja2 import Markup

# --- Vercel Note on Database ---
# Vercel's serverless environment doesn't allow SQLite (panhamall.db) 
# for production because it's non-persistent. For a REAL deployment, 
# you MUST switch to a hosted database like PostgreSQL (e.g., Vercel Postgres, Supabase).
# For this demonstration, we'll keep the SQLite configuration, 
# but note that data persistence will be unreliable on Vercel.

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'panha_mall_super_secret_key_12345'
# Vercel will look for this file, but writes will be unreliable/lost.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join('/tmp', 'panhamall.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'flatly' 

db = SQLAlchemy(app)
admin = Admin(app, name=Markup('ផ្សារទំនើបបញ្ញា <span style="font-size: 0.8em;">(Admin)</span>'), template_mode='bootstrap3')


# --- Database Model: Product (ទំនិញ) ---
class Product(db.Model):
    # Model definition remains the same
    id = db.Column(db.Integer, primary_key=True)
    name_kh = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description_kh = db.Column(db.Text, nullable=True) 
    store = db.Column(db.String(100), nullable=True) 
    image_url = db.Column(db.String(255), nullable=True) 

    def __repr__(self):
        return f'<Product {self.name_kh}>'

# --- Flask-Admin Custom View for Product ---
class ProductAdminView(ModelView):
    # ... (Admin view config remains the same)
    column_labels = dict(
        name_kh=Markup('ឈ្មោះ (ខ្មែរ)'),
        name_en='Name (English)',
        price=Markup('តម្លៃ (Price)'),
        description_kh=Markup('ការពិពណ៌នា (Khmer)'),
        store=Markup('ហាង (Store)'),
        image_url='Image URL'
    )
    column_list = ('name_kh', 'price', 'store', 'image_url')
    form_columns = ('name_kh', 'name_en', 'price', 'store', 'description_kh', 'image_url')

    def get_url(self, endpoint, **kwargs):
        if endpoint == 'product.index_view':
            self.name = 'ទំនិញ (Products)'
        return super().get_url(endpoint, **kwargs)

admin.add_view(ProductAdminView(Product, db.session, name='ទំនិញ'))


# --- Vercel Initialization Step: Create tables on first request ---
# We use app.before_first_request to ensure the tables exist 
# when a request hits the serverless function.
@app.before_first_request
def create_tables():
    db.create_all()


# --- Main Application Routes and Templates ---
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


# --- Execution for Vercel (IMPORTANT) ---
# Vercel and Gunicorn look for the 'app' variable, NOT the 'if __name__ == "__main__":' block.
# We've removed the local-only 'flask initdb' command and execution block.
