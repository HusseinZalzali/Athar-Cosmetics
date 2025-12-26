from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db, app
from models import Category, Product, ProductImage, User
import os
from decimal import Decimal, InvalidOperation

catalog_bp = Blueprint('catalog', __name__)

def json_response(success=True, data=None, message=None, errors=None, status_code=200):
    response = {'success': success}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code

def admin_required():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return False
    return True

@catalog_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        lang = request.args.get('lang', 'en')
        categories = Category.query.all()
        return json_response(True, data=[cat.to_dict(lang) for cat in categories])
    except Exception as e:
        return json_response(False, message='Failed to fetch categories', errors=[str(e)], status_code=500)

@catalog_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    try:
        if not admin_required():
            return json_response(False, message='Admin access required', status_code=403)
        
        data = request.get_json()
        if not data or not data.get('name_en') or not data.get('name_ar') or not data.get('slug'):
            return json_response(False, message='Missing required fields', errors=['name_en, name_ar, and slug are required'], status_code=400)
        
        if Category.query.filter_by(slug=data['slug']).first():
            return json_response(False, message='Category slug already exists', status_code=400)
        
        category = Category(
            name_en=data['name_en'],
            name_ar=data['name_ar'],
            slug=data['slug']
        )
        
        db.session.add(category)
        db.session.commit()
        
        return json_response(True, data=category.to_dict(), message='Category created', status_code=201)
    
    except Exception as e:
        db.session.rollback()
        return json_response(False, message='Failed to create category', errors=[str(e)], status_code=500)

@catalog_bp.route('/products', methods=['GET'])
def get_products():
    try:
        lang = request.args.get('lang', 'en')
        search = request.args.get('search', '')
        category_id = request.args.get('category')
        min_price = request.args.get('minPrice')
        max_price = request.args.get('maxPrice')
        sort = request.args.get('sort', 'newest')
        featured = request.args.get('featured')
        
        query = Product.query
        
        if search:
            query = query.filter(
                db.or_(
                    Product.name_en.ilike(f'%{search}%'),
                    Product.name_ar.ilike(f'%{search}%'),
                    Product.description_en.ilike(f'%{search}%'),
                    Product.description_ar.ilike(f'%{search}%')
                )
            )
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if min_price:
            query = query.filter(Product.price >= Decimal(min_price))
        
        if max_price:
            query = query.filter(Product.price <= Decimal(max_price))
        
        if featured == 'true':
            query = query.filter(Product.is_featured == True)
        
        if sort == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort == 'price_desc':
            query = query.order_by(Product.price.desc())
        else:  # newest
            query = query.order_by(Product.created_at.desc())
        
        # Eager load images to avoid N+1 queries
        from sqlalchemy.orm import joinedload
        products = query.options(joinedload(Product.images)).all()
        
        return json_response(True, data=[p.to_dict(lang) for p in products])
    
    except Exception as e:
        return json_response(False, message='Failed to fetch products', errors=[str(e)], status_code=500)

@catalog_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        lang = request.args.get('lang', 'en')
        product = Product.query.get(product_id)
        
        if not product:
            return json_response(False, message='Product not found', status_code=404)
        
        return json_response(True, data=product.to_dict(lang))
    
    except Exception as e:
        return json_response(False, message='Failed to fetch product', errors=[str(e)], status_code=500)

@catalog_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    try:
        print("=== PRODUCT CREATION REQUEST ===")
        print(f"Content-Type: {request.content_type}")
        print(f"Method: {request.method}")
        print(f"Has JSON: {request.is_json}")
        print(f"Raw data length: {len(request.data) if request.data else 0}")
        
        if not admin_required():
            print("Admin check failed")
            return json_response(False, message='Admin access required', status_code=403)
        
        print("Admin check passed")
        
        # Try to get JSON data with better error handling
        data = None
        try:
            if request.is_json:
                data = request.get_json()
            else:
                # Try to force parse
                data = request.get_json(force=True, silent=True)
            print(f"Parsed JSON: {data}")
        except Exception as json_error:
            print(f"JSON parsing error: {json_error}")
            import traceback
            traceback.print_exc()
            return json_response(False, message='Invalid JSON format', errors=[str(json_error)], status_code=400)
        
        if not data:
            print("No data in request")
            print(f"Request data: {request.data}")
            print(f"Request form: {request.form}")
            return json_response(False, message='No JSON data provided', errors=['Request body must contain JSON'], status_code=400)
        
        print(f"Processing data: {data}")
        print(f"Data type: {type(data)}")
        print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        print(f"Data type: {type(data)}")
        print(f"Data keys: {list(data.keys()) if data else 'None'}")
        
        required_fields = ['name_en', 'price', 'sku', 'category_id']
        missing_fields = []
        for field in required_fields:
            value = data.get(field)
            print(f"Field {field}: {value} (type: {type(value)})")
            if value is None or value == '' or (field == 'category_id' and (value == 'null' or str(value).lower() == 'null')):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"Missing fields: {missing_fields}")
            return json_response(False, message='Missing required fields', errors=[f'{field} is required' for field in missing_fields], status_code=400)
        
        # Auto-fill Arabic fields with English values if not provided
        name_ar = data.get('name_ar') or data['name_en']
        description_ar = data.get('description_ar') or data.get('description_en', '')
        ingredients_ar = data.get('ingredients_ar') or data.get('ingredients_en', '')
        usage_ar = data.get('usage_ar') or data.get('usage_en', '')
        
        # Validate category_id is not null/empty
        category_id = data.get('category_id')
        print(f"Category ID raw: {category_id} (type: {type(category_id)})")
        
        if category_id is None or category_id == '' or str(category_id).lower() == 'null':
            print("Category ID is null or empty")
            return json_response(False, message='Invalid category', errors=['category_id is required and cannot be null'], status_code=400)
        
        # Convert to int if it's a string
        try:
            category_id = int(category_id)
            print(f"Category ID converted to int: {category_id}")
        except (ValueError, TypeError) as e:
            print(f"Category ID conversion error: {e}")
            return json_response(False, message='Invalid category', errors=[f'category_id must be a valid number. Got: {category_id}'], status_code=400)
        
        # Validate category exists
        category = Category.query.get(category_id)
        if not category:
            print(f"Category {category_id} not found in database")
            return json_response(False, message='Invalid category', errors=[f'Category with id {category_id} does not exist'], status_code=400)
        
        print(f"Category found: {category.name_en}")
        
        # Check if SKU already exists
        if Product.query.filter_by(sku=data['sku']).first():
            return json_response(False, message='SKU already exists', errors=[f'Product with SKU {data["sku"]} already exists'], status_code=400)
        
        # Validate price is a valid number
        try:
            price = Decimal(str(data['price']))
            if price <= 0:
                return json_response(False, message='Invalid price', errors=['Price must be greater than 0'], status_code=400)
        except (ValueError, TypeError, InvalidOperation):
            return json_response(False, message='Invalid price format', errors=['Price must be a valid number'], status_code=400)
        
        # Validate stock is a non-negative integer
        stock = data.get('stock', 0)
        try:
            stock = int(stock)
            if stock < 0:
                return json_response(False, message='Invalid stock', errors=['Stock must be a non-negative integer'], status_code=400)
        except (ValueError, TypeError):
            return json_response(False, message='Invalid stock format', errors=['Stock must be a valid integer'], status_code=400)
        
        product = Product(
            name_en=data['name_en'],
            name_ar=name_ar,
            description_en=data.get('description_en', ''),
            description_ar=description_ar,
            price=price,
            stock=stock,
            sku=data['sku'],
            category_id=category_id,
            ingredients_en=data.get('ingredients_en', ''),
            ingredients_ar=ingredients_ar,
            usage_en=data.get('usage_en', ''),
            usage_ar=usage_ar,
            is_featured=data.get('is_featured', False)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return json_response(True, data=product.to_dict(), message='Product created', status_code=201)
    
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return json_response(False, message='Failed to create product', errors=[str(e)], status_code=500)

@catalog_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    try:
        if not admin_required():
            return json_response(False, message='Admin access required', status_code=403)
        
        product = Product.query.get(product_id)
        if not product:
            return json_response(False, message='Product not found', status_code=404)
        
        data = request.get_json()
        
        if 'name_en' in data:
            product.name_en = data['name_en']
            # Auto-update Arabic name if not provided
            if 'name_ar' not in data or not data.get('name_ar'):
                product.name_ar = data['name_en']
            else:
                product.name_ar = data['name_ar']
        if 'description_en' in data:
            product.description_en = data['description_en']
            # Auto-update Arabic description if not provided
            if 'description_ar' not in data or not data.get('description_ar'):
                product.description_ar = data['description_en']
            else:
                product.description_ar = data['description_ar']
        if 'price' in data:
            product.price = Decimal(str(data['price']))
        if 'stock' in data:
            product.stock = data['stock']
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'ingredients_en' in data:
            product.ingredients_en = data['ingredients_en']
        if 'ingredients_ar' in data:
            product.ingredients_ar = data['ingredients_ar']
        if 'usage_en' in data:
            product.usage_en = data['usage_en']
        if 'usage_ar' in data:
            product.usage_ar = data['usage_ar']
        if 'is_featured' in data:
            product.is_featured = data['is_featured']
        
        db.session.commit()
        
        return json_response(True, data=product.to_dict(), message='Product updated')
    
    except Exception as e:
        db.session.rollback()
        return json_response(False, message='Failed to update product', errors=[str(e)], status_code=500)

@catalog_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    try:
        if not admin_required():
            return json_response(False, message='Admin access required', status_code=403)
        
        product = Product.query.get(product_id)
        if not product:
            return json_response(False, message='Product not found', status_code=404)
        
        db.session.delete(product)
        db.session.commit()
        
        return json_response(True, message='Product deleted')
    
    except Exception as e:
        db.session.rollback()
        return json_response(False, message='Failed to delete product', errors=[str(e)], status_code=500)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@catalog_bp.route('/products/<int:product_id>/images', methods=['POST'])
@jwt_required()
def upload_product_image(product_id):
    try:
        if not admin_required():
            return json_response(False, message='Admin access required', status_code=403)
        
        product = Product.query.get(product_id)
        if not product:
            return json_response(False, message='Product not found', status_code=404)
        
        if 'image' not in request.files:
            return json_response(False, message='No image file provided', status_code=400)
        
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return json_response(False, message='Invalid file', status_code=400)
        
        filename = secure_filename(file.filename)
        # Create unique filename
        import uuid
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Store relative URL
        image_url = f"/api/uploads/{unique_filename}"
        
        image = ProductImage(
            product_id=product_id,
            url=image_url,
            alt_text=request.form.get('alt_text', product.name_en)
        )
        
        db.session.add(image)
        db.session.commit()
        
        return json_response(True, data=image.to_dict(), message='Image uploaded', status_code=201)
    
    except Exception as e:
        db.session.rollback()
        return json_response(False, message='Failed to upload image', errors=[str(e)], status_code=500)

@catalog_bp.route('/products/<int:product_id>/images/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_product_image(product_id, image_id):
    try:
        if not admin_required():
            return json_response(False, message='Admin access required', status_code=403)
        
        product = Product.query.get(product_id)
        if not product:
            return json_response(False, message='Product not found', status_code=404)
        
        image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first()
        if not image:
            return json_response(False, message='Image not found', status_code=404)
        
        # Delete the file from filesystem
        try:
            filename = image.url.split('/')[-1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Warning: Could not delete file {filepath}: {e}")
        
        db.session.delete(image)
        db.session.commit()
        
        return json_response(True, message='Image deleted')
    
    except Exception as e:
        db.session.rollback()
        return json_response(False, message='Failed to delete image', errors=[str(e)], status_code=500)

@catalog_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

