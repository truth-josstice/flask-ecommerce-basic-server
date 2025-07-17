def test_get_products_returns_empty_list(client):
    response = client.get('/products')
    assert response.status_code == 200
    assert response.get_json() == []

def test_create_product_success(client):
    new_product = {
        "name": "test product",
        "price": 19.99
    }

    response = client.post("/products", json=new_product)
    assert response.status_code == 201
    product = response.get_json()
    assert 'id' in product
    assert product['name'] == 'test product'

def test_get_products_success(client):
    response = client.get("/products")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_update_product_success(client):
    new_product = {
        "name": "old product",
        "description": "this product's name will be changed",
        "price": 19.99
    }

    response = client.post('/products', json=new_product)
    product = response.get_json()
    product_id = product["id"]

    #update the new product
    update_data = {
        "name": "new product value"
    }

    response = client.patch(f"/products/{product_id}", json=update_data)

    assert response.status_code == 200
    updated = response.get_json()
    assert updated["name"] == "new product value"

def test_update_nonexistant_product(client):
    fake_id = 99999
    update_data = {
        "name": "ghost product",
        "price": 49.99
    }

    response = client.patch(f"/products/{fake_id}", json=update_data)
    assert response.status_code == 404
    assert "does not exist" in response.get_json()["message"]

def test_update_product_invalid_data(client):
    product_data ={
        "name": "Typo product",
        "description": "Bad price",
        "price": 5.0,
        "stock": 2
    }

    response = client.post('/products', json=product_data)
    product_id = response.get_json()["id"]

    # set invalid price
    updated_data = {
        "price": "not a number"
    }

    response = client.patch(f"/products/{product_id}", json=updated_data)
    assert response.status_code == 400
    assert "denied" in response.get_json()["message"]