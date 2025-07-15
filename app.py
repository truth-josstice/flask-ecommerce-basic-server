from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema



app = Flask(__name__)

# database+driver://username:password@server:port/databasename => "postgresql+psycopg2://mar_user:123456@localhost:5432/mar_ecommerce"

app.config['SQLALCHEMY_DATABASE_URI']="postgresql+psycopg2://mar_user:123456@localhost:5432/mar_ecommerce"

#must be defined after database uri
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Product(db.Model):
    # define table name
    __tablename__ = "products"
    # define primary key
    id = db.Column(db.Integer, primary_key=True)
    # define non key attributes
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

    def __init__(self, name, description, price, stock):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock


# Create a class for ProductSchema
class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


@app.route('/')
def show_products():
    products = app
    return products

@app.cli.command("create")
def create_table():
    db.create_all()
    print("Tables created!")

@app.cli.command("drop")
def drop_table():
    db.drop_all()
    print("Tables dropped!")

@app.cli.command("seed")
def seed_table():
    # Create instance of products
    product1 = Product(
        name = "Product 1",
        description = "This is product 1",
        price = 12.99,
        stock = 5
    )

    product2 = Product()
    product2.name = "Product 2"
    product2.price = 15
    product2.stock = 0
    
    #need to add and commit to the session
    db.session.add(product1)
    db.session.add(product2)
    db.session.commit()

    print("Tables seeded!")

# CRUD operations on the Products Table
# GET, POST, PUT, PATCH, DELETE
# READ operation - GET method

@app.route('/products')
def get_products():
    # Statement: SELECT * FROM products;
    products_list = Product.query.all()

    # Convert object to JSON format - Serialise
    data = products_schema.dump(products_list)
    return jsonify(data)

# READ specific product from the products list
# GET /products/id
@app.route('/products/<int:product_id>')
def get_a_product(product_id):
    #Statement: SELECT * FROM products WHERE id=product_id
    product = Product.query.get(product_id)

    if product:
        data = product_schema.dump(product)
        return jsonify(data)
    else:
        return jsonify({"message": f'Product with id {product_id} does not exist'}), 404