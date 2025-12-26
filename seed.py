from app import app, db
from models import User, Category, Product, ProductImage

def seed_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@athar.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create test customer
        customer = User(
            name='Test Customer',
            email='customer@athar.com',
            role='customer'
        )
        customer.set_password('customer123')
        db.session.add(customer)
        
        # Create categories
        categories_data = [
            {'name_en': 'Body Care', 'name_ar': 'العناية بالجسم', 'slug': 'body-care'},
            {'name_en': 'Scrubs', 'name_ar': 'مقشرات', 'slug': 'scrubs'},
            {'name_en': 'Oils', 'name_ar': 'زيوت', 'slug': 'oils'},
            {'name_en': 'Splashes', 'name_ar': 'رشاشات', 'slug': 'splashes'}
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.session.add(category)
            db.session.flush()
            categories[cat_data['slug']] = category
        
        # Create products
        products_data = [
            {
                'name_en': 'Hydrating Body Scrub',
                'name_ar': 'مقشر الجسم المرطب',
                'description_en': 'A luxurious body scrub enriched with natural ingredients to exfoliate and hydrate your skin, leaving it soft and smooth.',
                'description_ar': 'مقشر جسم فاخر غني بالمكونات الطبيعية لتقشير وترطيب بشرتك، تاركاً إياها ناعمة وسلسة.',
                'price': 45.00,
                'stock': 50,
                'sku': 'ATH-BS-001',
                'category_slug': 'scrubs',
                'ingredients_en': 'Sugar, Coconut Oil, Shea Butter, Vitamin E, Natural Fragrance',
                'ingredients_ar': 'سكر، زيت جوز الهند، زبدة الشيا، فيتامين E، عطر طبيعي',
                'usage_en': 'Apply to wet skin in circular motions. Rinse thoroughly. Use 2-3 times per week.',
                'usage_ar': 'ضع على البشرة الرطبة بحركات دائرية. اشطف جيداً. استخدم 2-3 مرات في الأسبوع.',
                'is_featured': True
            },
            {
                'name_en': 'Creamy Body Scrub',
                'name_ar': 'مقشر الجسم الكريمي',
                'description_en': 'A rich, creamy body scrub that gently exfoliates while deeply moisturizing your skin with nourishing oils.',
                'description_ar': 'مقشر جسم كريمي غني يقشر بلطف بينما يرطب بشرتك بعمق بالزيوت المغذية.',
                'price': 48.00,
                'stock': 45,
                'sku': 'ATH-BS-002',
                'category_slug': 'scrubs',
                'ingredients_en': 'Brown Sugar, Sweet Almond Oil, Cocoa Butter, Oatmeal, Honey',
                'ingredients_ar': 'سكر بني، زيت اللوز الحلو، زبدة الكاكاو، الشوفان، العسل',
                'usage_en': 'Massage onto damp skin. Leave for 2 minutes, then rinse. Best used in shower.',
                'usage_ar': 'دلك على البشرة الرطبة. اترك لمدة دقيقتين ثم اشطف. يُفضل استخدامه في الحمام.',
                'is_featured': True
            },
            {
                'name_en': 'Body Splash - Fresh',
                'name_ar': 'رشاش الجسم - منعش',
                'description_en': 'A refreshing body splash with a light, invigorating fragrance. Perfect for daily use to feel fresh and energized.',
                'description_ar': 'رشاش جسم منعش برائحة خفيفة ومنشطة. مثالي للاستخدام اليومي للشعور بالانتعاش والحيوية.',
                'price': 35.00,
                'stock': 60,
                'sku': 'ATH-BSP-001',
                'category_slug': 'splashes',
                'ingredients_en': 'Purified Water, Aloe Vera, Witch Hazel, Natural Fragrance, Glycerin',
                'ingredients_ar': 'ماء منقى، الصبار، عشبة الويتش هازل، عطر طبيعي، الجلسرين',
                'usage_en': 'Spray on clean skin after shower or throughout the day. Avoid contact with eyes.',
                'usage_ar': 'رش على البشرة النظيفة بعد الاستحمام أو طوال اليوم. تجنب ملامسة العينين.',
                'is_featured': True
            },
            {
                'name_en': 'Body Splash - Floral',
                'name_ar': 'رشاش الجسم - زهري',
                'description_en': 'A delicate floral body splash that leaves a subtle, elegant scent. Ideal for special occasions.',
                'description_ar': 'رشاش جسم زهري رقيق يترك رائحة خفيفة وأنيقة. مثالي للمناسبات الخاصة.',
                'price': 35.00,
                'stock': 55,
                'sku': 'ATH-BSP-002',
                'category_slug': 'splashes',
                'ingredients_en': 'Purified Water, Rose Water, Jasmine Extract, Natural Fragrance, Glycerin',
                'ingredients_ar': 'ماء منقى، ماء الورد، مستخلص الياسمين، عطر طبيعي، الجلسرين',
                'usage_en': 'Spray on pulse points and body. Reapply as needed for lasting fragrance.',
                'usage_ar': 'رش على نقاط النبض والجسم. أعد التطبيق حسب الحاجة لرائحة دائمة.',
                'is_featured': False
            },
            {
                'name_en': 'Nourishing Body Oil',
                'name_ar': 'زيت الجسم المغذي',
                'description_en': 'A luxurious blend of nourishing oils that deeply moisturizes and softens your skin. Absorbs quickly without greasy residue.',
                'description_ar': 'مزيج فاخر من الزيوت المغذية التي ترطب وتنعم بشرتك بعمق. يمتص بسرعة دون بقايا دهنية.',
                'price': 55.00,
                'stock': 40,
                'sku': 'ATH-BO-001',
                'category_slug': 'oils',
                'ingredients_en': 'Jojoba Oil, Argan Oil, Sweet Almond Oil, Vitamin E, Lavender Essential Oil',
                'ingredients_ar': 'زيت الجوجوبا، زيت الأرغان، زيت اللوز الحلو، فيتامين E، زيت اللافندر العطري',
                'usage_en': 'Apply to slightly damp skin after shower. Massage gently until absorbed. Use daily for best results.',
                'usage_ar': 'ضع على البشرة الرطبة قليلاً بعد الاستحمام. دلك برفق حتى الامتصاص. استخدم يومياً للحصول على أفضل النتائج.',
                'is_featured': True
            },
            {
                'name_en': 'Body Splash - Citrus',
                'name_ar': 'رشاش الجسم - الحمضيات',
                'description_en': 'An energizing citrus body splash with zesty notes of lemon and orange. Perfect for morning routines.',
                'description_ar': 'رشاش جسم منعش بالحمضيات بنوتات منعشة من الليمون والبرتقال. مثالي لروتين الصباح.',
                'price': 35.00,
                'stock': 50,
                'sku': 'ATH-BSP-003',
                'category_slug': 'splashes',
                'ingredients_en': 'Purified Water, Lemon Extract, Orange Extract, Natural Fragrance, Glycerin',
                'ingredients_ar': 'ماء منقى، مستخلص الليمون، مستخلص البرتقال، عطر طبيعي، الجلسرين',
                'usage_en': 'Spray on clean skin. Perfect for a quick refresh. Can be used multiple times daily.',
                'usage_ar': 'رش على البشرة النظيفة. مثالي للانتعاش السريع. يمكن استخدامه عدة مرات يومياً.',
                'is_featured': False
            },
            {
                'name_en': 'Gentle Body Scrub',
                'name_ar': 'مقشر الجسم اللطيف',
                'description_en': 'A mild body scrub suitable for sensitive skin. Gently removes dead skin cells while soothing and calming.',
                'description_ar': 'مقشر جسم خفيف مناسب للبشرة الحساسة. يزيل خلايا الجلد الميتة بلطف بينما يهدئ ويهدئ.',
                'price': 42.00,
                'stock': 48,
                'sku': 'ATH-BS-003',
                'category_slug': 'scrubs',
                'ingredients_en': 'Fine Sea Salt, Apricot Kernel Oil, Chamomile Extract, Calendula, Aloe Vera',
                'ingredients_ar': 'ملح البحر الناعم، زيت نواة المشمش، مستخلص البابونج، الآذريون، الصبار',
                'usage_en': 'Use gently on sensitive areas. Rinse with warm water. Use once or twice per week.',
                'usage_ar': 'استخدم برفق على المناطق الحساسة. اشطف بالماء الدافئ. استخدم مرة أو مرتين في الأسبوع.',
                'is_featured': False
            },
            {
                'name_en': 'Luxury Body Oil Blend',
                'name_ar': 'مزيج زيت الجسم الفاخر',
                'description_en': 'An indulgent blend of premium oils for ultimate skin nourishment. Leaves skin silky smooth with a subtle golden glow.',
                'description_ar': 'مزيج فاخر من الزيوت المميزة لتغذية البشرة القصوى. يترك البشرة حريرية ناعمة بتوهج ذهبي خفيف.',
                'price': 65.00,
                'stock': 35,
                'sku': 'ATH-BO-002',
                'category_slug': 'oils',
                'ingredients_en': 'Argan Oil, Rosehip Oil, Marula Oil, Vitamin E, Frankincense Essential Oil',
                'ingredients_ar': 'زيت الأرغان، زيت الورد، زيت المارولا، فيتامين E، زيت اللبان العطري',
                'usage_en': 'Apply to clean, dry skin. Massage in upward motions. Best used in the evening for overnight absorption.',
                'usage_ar': 'ضع على البشرة النظيفة والجافة. دلك بحركات صاعدة. يُفضل استخدامه في المساء للامتصاص طوال الليل.',
                'is_featured': True
            }
        ]
        
        for prod_data in products_data:
            category_slug = prod_data.pop('category_slug')
            category = categories[category_slug]
            
            product = Product(
                category_id=category.id,
                **prod_data
            )
            db.session.add(product)
            db.session.flush()
            
            # Add placeholder image URL (in production, these would be actual uploaded images)
            image = ProductImage(
                product_id=product.id,
                url='/api/uploads/placeholder.jpg',
                alt_text=prod_data['name_en']
            )
            db.session.add(image)
        
        db.session.commit()
        print('Database seeded successfully!')
        print('Admin credentials: admin@athar.com / admin123')
        print('Customer credentials: customer@athar.com / customer123')

if __name__ == '__main__':
    seed_database()




