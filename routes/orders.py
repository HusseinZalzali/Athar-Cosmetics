from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Order, OrderItem, Product, User
from decimal import Decimal

orders_bp = Blueprint('orders', __name__)

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

@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or not data.get('items') or not data.get('shipping'):
            return json_response(False, message='Missing required fields', errors=['items and shipping are required'], status_code=400)
        
        shipping = data['shipping']
        required_shipping = ['name', 'phone', 'city', 'street']
        if not all(shipping.get(field) for field in required_shipping):
            return json_response(False, message='Missing shipping fields', errors=[f'{field} is required' for field in required_shipping if not shipping.get(field)], status_code=400)
        
        items = data['items']
        if not items:
            return json_response(False, message='Order must have at least one item', status_code=400)
        
        total = Decimal('0.00')
        order_items = []
        
        for item_data in items:
            product = Product.query.get(item_data['product_id'])
            if not product:
                return json_response(False, message=f'Product {item_data["product_id"]} not found', status_code=400)
            
            if product.stock < item_data['quantity']:
                return json_response(False, message=f'Insufficient stock for {product.name_en}', status_code=400)
            
            unit_price = Decimal(str(product.price))
            line_total = unit_price * item_data['quantity']
            total += line_total
            
            order_item = OrderItem(
                product_id=product.id,
                quantity=item_data['quantity'],
                unit_price=unit_price,
                line_total=line_total
            )
            order_items.append(order_item)
            
            # Update stock
            product.stock -= item_data['quantity']
        
        order = Order(
            user_id=user_id,
            status='pending',
            total=total,
            payment_method=data.get('payment_method', 'cash_on_delivery'),
            shipping_name=shipping['name'],
            shipping_phone=shipping['phone'],
            shipping_city=shipping['city'],
            shipping_street=shipping['street'],
            shipping_notes=shipping.get('notes', '')
        )
        
        order.items = order_items
        
        db.session.add(order)
        db.session.commit()
        
        return json_response(True, data=order.to_dict(), message='Order created', status_code=201)
    
    except Exception as e:
        db.session.rollback()
        return json_response(False, message='Failed to create order', errors=[str(e)], status_code=500)

@orders_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_orders():
    try:
        user_id = int(get_jwt_identity())
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
        
        return json_response(True, data=[order.to_dict() for order in orders])
    
    except Exception as e:
        return json_response(False, message='Failed to fetch orders', errors=[str(e)], status_code=500)

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_all_orders():
    try:
        if not admin_required():
            return json_response(False, message='Admin access required', status_code=403)
        
        orders = Order.query.order_by(Order.created_at.desc()).all()
        
        return json_response(True, data=[order.to_dict() for order in orders])
    
    except Exception as e:
        return json_response(False, message='Failed to fetch orders', errors=[str(e)], status_code=500)

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    try:
        if not admin_required():
            return json_response(False, message='Admin access required', status_code=403)
        
        order = Order.query.get(order_id)
        if not order:
            return json_response(False, message='Order not found', status_code=404)
        
        data = request.get_json()
        if not data or not data.get('status'):
            return json_response(False, message='Status is required', status_code=400)
        
        valid_statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']
        if data['status'] not in valid_statuses:
            return json_response(False, message='Invalid status', errors=[f'Status must be one of: {", ".join(valid_statuses)}'], status_code=400)
        
        order.status = data['status']
        db.session.commit()
        
        return json_response(True, data=order.to_dict(), message='Order status updated')
    
    except Exception as e:
        db.session.rollback()
        return json_response(False, message='Failed to update order status', errors=[str(e)], status_code=500)

