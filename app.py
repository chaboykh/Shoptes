import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_admin import Admin, BaseView, expose
from flask_admin.form import BaseForm
from wtforms import StringField, FloatField, TextAreaField, HiddenField, validators
from jinja2 import Markup

# --- Configuration & Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'panha_mall_json_db_secure_key_456'
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'

# Define the JSON file path
JSON_DB_PATH = 'products_db.json'
admin = Admin(app, name=Markup('ផ្សារទំនើបបញ្ញា (Admin)'), template_mode='bootstrap3')

# --- JSON Database Functions ---

def load_products():
    """Reads all product data from the JSON file."""
    if not os.path.exists(JSON_DB_PATH):
        return []
    with open(JSON_DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_products(products):
    """Writes the entire list of products back to the JSON file."""
    with open(JSON_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=4, ensure_ascii=False)

def get_next_id(products):
    """Calculates the next available product ID."""
    return max([p['id'] for p in products] + [0]) + 1

# --- WTForms for Product Input ---

class ProductForm(BaseForm):
    """Form used for creating and editing products in the Admin."""
    id = HiddenField() # Used for editing existing products
    name_kh = StringField(Markup('ឈ្មោះ (ខ្មែរ)'), [validators.DataRequired()], render_kw={"placeholder": "ឧទាហរណ៍: អាវយឺត"})
    name_en = StringField('Name (English)', [validators.DataRequired()], render_kw={"placeholder": "Example: T-Shirt"})
    price = FloatField(Markup('តម្លៃ (Price)'), [validators.DataRequired()], render_kw={"placeholder": "Example: 15.50"})
    description_kh = TextAreaField(Markup('ការពិពណ៌នា (Khmer)'), render_kw={"rows": 3})
    store = StringField(Markup('ហាង (Store)'), render_kw={"placeholder": "ឧទាហរណ៍: ហាងសម្លៀកបំពាក់ A"})
    image_url = StringField('Image URL', render_kw={"placeholder": "https://example.com/image.jpg"})

# --- Custom Admin View for JSON Data ---

class ProductJsonView(BaseView):
    """Custom view for managing products using the JSON file."""
    
    @expose('/')
    def index_view(self):
        """Displays the list of products."""
        products = load_products()
        return self.render('admin_list.html', products=products)

    @expose('/new', methods=('GET', 'POST'))
    def create_view(self):
        """Handles creating a new product."""
        form = ProductForm(request.form)
        if request.method == 'POST' and form.validate():
            products = load_products()
            new_product = {
                'id': get_next_id(products),
                'name_kh': form.name_kh.data,
                'name_en': form.name_en.data,
                'price': form.price.data,
                'description_kh': form.description_kh.data,
                'store': form.store.data,
                'image_url': form.image_url.data
            }
            products.append(new_product)
            save_products(products)
            flash(Markup(f'ទំនិញ "{new_product["name_kh"]}" ត្រូវបានបញ្ចូលដោយជោគជ័យ។'), 'success')
            return redirect(url_for('productjson.index_view'))
        
        return self.render('admin_edit.html', form=form, action='create')

    @expose('/edit/<int:product_id>', methods=('GET', 'POST'))
    def edit_view(self, product_id):
        """Handles editing an existing product."""
        products = load_products()
        product = next((p for p in products if p['id'] == product_id), None)

        if not product:
            flash(Markup('រកមិនឃើញទំនិញនេះទេ។'), 'error')
            return redirect(url_for('productjson.index_view'))

        form = ProductForm(request.form, **product) 
        
        if request.method == 'POST' and form.validate():
            # Find and update the product in the list
            product.update({
                'name_kh': form.name_kh.data,
                'name_en': form.name_en.data,
                'price': form.price.data,
                'description_kh': form.description_kh.data,
                'store': form.store.data,
                'image_url': form.image_url.data
            })
            save_products(products)
            flash(Markup(f'ទំនិញ "{product["name_kh"]}" ត្រូវបានកែប្រែដោយជោគជ័យ។'), 'success')
            return redirect(url_for('productjson.index_view'))

        return self.render('admin_edit.html', form=form, action='edit', product_id=product_id)

    @expose('/delete/<int:product_id>', methods=('POST',))
    def delete_view(self, product_id):
        """Handles deleting a product."""
        products = load_products()
        initial_length = len(products)
        # Filter out the product to be deleted
        products[:] = [p for p in products if p['id'] != product_id]
        
        if len(products) < initial_length:
            save_products(products)
            flash(Markup('ទំនិញត្រូវបានលុបដោយជោគជ័យ។'), 'success')
        else:
            flash(Markup('រកមិនឃើញទំនិញដើម្បីលុបទេ។'), 'error')

        return redirect(url_for('productjson.index_view'))

# Add the custom view to the Admin interface
admin.add_view(ProductJsonView(name=Markup('ទំនិញ (Products)'), endpoint='productjson'))

# --- Frontend Route ---

@app.route('/')
def index():
    products = load_products() # Load data directly from JSON
    # Note: We pass the list of dictionaries directly to the template
    return render_template('index.html', products=products)

# --- Execution ---

if __name__ == '__main__':
    # Ensure the JSON file exists on first run
    if not os.path.exists(JSON_DB_PATH):
        save_products([])
        print(f"Created empty JSON database file at: {JSON_DB_PATH}")
    
    print("\n--- JSON-Based PANHA MALL SERVER ---")
    print("Frontend: http://127.0.0.1:5000/")
    print("Admin Panel: http://127.0.0.1:5000/admin")
    print("------------------------------------\n")
    app.run(debug=True)
