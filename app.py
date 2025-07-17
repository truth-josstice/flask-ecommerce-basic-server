from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow # Not needed with new update of marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

# database+driver://username:password@server:port/databasename

DATABASE_URI = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

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

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))

    # def __init__(self, name, description): #New Marshmallow does not need the init but good to have to create default values etc
    #     self.name = name
    #     self.description = description

# Create a class for ProductSchema
class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

# Create a class for CategorySchema
class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


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

    # this product cannot be created this way once we have initialised the product class with an __init__ method, cli commands should be kept separate for this reason
    product2 = Product(
    name = "Product 2",
    description = "This is product 2",
    price = 15,
    stock = 0,
    )
    
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
    stmt = db.select(Product).where()
    products_list = db.session.scalars(stmt)

    # Convert object to JSON format - Serialise
    data = products_schema.dump(products_list)
    return jsonify(data)

# READ specific product from the products list
# GET /products/id
@app.route('/products/<int:product_id>')
def get_a_product(product_id):
    #Statement: SELECT * FROM products WHERE id=product_id
    stmt = db.select(Product).where(Product.id == product_id)
    product = db.session.scalar(stmt)

    if product:
        data = product_schema.dump(product)
        return jsonify(data)
    else:
        return jsonify({"message": f'Product with id {product_id} does not exist'}), 404
    
# CREATE a product
# POST method - /products/

@app.route("/products", methods=["POST"])
def create_product():
    #Statement INSERT INTO products(*args) VALUES (*values);
    # Get the body JSON data
    body_data = request.get_json()
    # Create product object and pass on values
    new_product = Product(
        name = body_data.get("name"),
        description = body_data.get("description"),
        price = body_data.get("price"),
        stock = body_data.get("stock"),
    )
    # add to session and commit
    db.session.add(new_product)
    db.session.commit()

    #return the newly created product
    data = product_schema.dump(new_product)
    return jsonify(data), 201

# DELETE a product
# DELETE /products/id
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    # DELETE FROM products WHERE id=product_id;
    # Find the product with product_id from db
    # SELECT * FROM products WHERE id=product_id;
        # Method 1
        # stmt = db.select(Product).filter_by(id=product_id)
        # product = db.session.scalar(stmt)
    # product = Product.query.get(product_id)
    stmt = db.select(Product).where(Product.id == product_id)
    product = db.session.scalar(stmt)
    # if exists delete product send message
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f'Product with id {product_id} deleted successfully'})
    # else send acknowledgment message
    else:
        return jsonify({"message": f'Product with id {product_id} does not exist'}), 404
    
#UPDATE method PUT - updates all paramaters in the table, replaces any which have not been included, can create a new row if doesnt exist, PATCH - updates a single value in the table, cannot create new row in table
@app.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    stmt = db.select(Product).where(Product.id == product_id)
    product = db.session.scalar(stmt)
    try:
        if product:
            body_data = request.get_json()
        # update the values - SHORT CIRCUIT
        # product.name = body_data.get("name") or product.name
        # product.description = body_data.get("description") or product.description
        # product.price = body_data.get("price") or product.price
        # product.stock = body_data.get("stock") or product.stock

        # get method can incorporate or implicitly (a little more DRY)
            product.name = body_data.get("name", product.name)
            product.description = body_data.get("description", product.description)
            product.price = body_data.get("price", product.price)
            product.stock = body_data.get("stock", product.stock)

            db.session.commit()
            return jsonify(product_schema.dump(product))
    
    # else:
        else:
            return jsonify({"message": f"Product with {product_id} does not exist"}), 404
    except: 
        return jsonify({"message": "request denied, invalid data type"}), 400

if __name__ == "__main__":
    app.run(debug=True)