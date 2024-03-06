# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
# pylint: disable=trailing-whitespace

class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_a_product(self):
        """test a product is found
        """
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(product.id, found_product.id)
        self.assertEqual(product.name, found_product.name)
        self.assertEqual(product.price, found_product.price)
        self.assertEqual(product.description, found_product.description)
        self.assertEqual(product.category, found_product.category)
        self.assertEqual(product.available, found_product.available)

    def test_update_a_product(self):
        """Test create and update a product
        """
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Update the product description and check
        new_description = "This a new description"
        product.description = new_description
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, new_description)
        # Fetch it back and make the id hasn't change but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, new_description)

    def test_delete_a_product(self):
        """Test create single product and verify
            that only single product exist and then, delete the product
        """
        c_product = ProductFactory()
        c_product.id = None
        c_product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        c_product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_product(self):
        """Test it should list all products in the database
        """
        products = Product.all()
        self.assertEqual(len(products), 0)
        for _ in range(5):
            product = ProductFactory()
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """it should find a product by name
        """
        gen_products = ProductFactory.create_batch(5)
        for product in gen_products:
            product.create()
        product_name = gen_products[0].name
        count = len([product for product in gen_products if product_name == product.name])
        found = Product.find_by_name(product_name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product_name, product.name)

    def test_find_product_by_availability(self):
        """it should find product by availablity
        """
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_product_category(self):
        """it should find a product by categry
        """
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_update_without_product_id(self):
        """it should raise a DataValidiation Error if product id is ommitted"""
        product = ProductFactory()
        product.create()
        product.id = None
        new_text = "should not change balbalba"
        product.description = new_text
        self.assertIsNone(product.id)
        self.assertRaises(DataValidationError, product.update)

    def test_product_serialized(self):
        """it should return seriliazed data
        """
        product = ProductFactory()
        product.create()
        found = Product.all()
        # assert product saved to the database
        self.assertEqual(len(found), 1)
        # assert serialize return type dictionary
        serial_product = product.serialize()
        self.assertIsInstance(serial_product, dict)
        self.assertEqual(serial_product['id'], product.id)
        self.assertEqual(serial_product['name'], product.name)
        self.assertEqual(serial_product['description'], product.description)

    def test_product_deserialized(self):
        """it should create an instance Product from dictionary data
        """
        product = ProductFactory()
        product_data = product.serialize()
        # assert product_data is dictionary
        self.assertIsInstance(product_data, dict)
        # pass product_data to deserialize method this shouldn't change anything...
        # ...since product_data dictionary contains properties of product
        new_product = product.deserialize(product_data)
        self.assertEqual(new_product.id, product_data['id'])
        self.assertEqual(new_product.name, product_data['name'])
        self.assertEqual(new_product.description, product_data['description'])
        self.assertAlmostEqual(Decimal(new_product.price), Decimal(product_data['price']))

    def test_product_deserialize_avialble_not_bool(self):
        """it should raise DataValidation error when...
            ...non boolean value is passed available attribute
        """
        product = ProductFactory()
        product_data = product.serialize()
        # assert product_data is dictionary
        self.assertIsInstance(product_data, dict)
        product_data['available'] = "true"
        self.assertRaises(DataValidationError, product.deserialize, product_data)
        product_data['available'] = 2032
        self.assertRaises(DataValidationError, product.deserialize, product_data)
        product_data['available'] = False
        new_product = product.deserialize(product_data)
        self.assertEqual(new_product.id, product_data['id'])
        self.assertEqual(new_product.name, product_data['name'])
        self.assertEqual(new_product.description, product_data['description'])

    def test_raises_datavalidation_keyerror(self):
        """it should raise Datavalidation error due to KeyError
        """
        product = ProductFactory()
        product_data = product.serialize()
        # assert product_data is dictionary
        self.assertIsInstance(product_data, dict)
        del product_data['name']
        self.assertRaises(DataValidationError, product.deserialize, product_data)

    def test_raises_datavalidation_typeerror(self):
        """it should riase AttributeError
        """
        product = ProductFactory()
        product_data = product.serialize()
        # assert product_data is dictionary
        self.assertIsInstance(product_data, dict)
        product_data['category'] = 7887
        self.assertRaises(DataValidationError, product.deserialize, product_data)
        product_data['category'] = 2312.3123
        self.assertRaises(DataValidationError, product.deserialize, product_data)
        product_data['category'] = 'some text'
        self.assertRaises(DataValidationError, product.deserialize, product_data)
        product_data['category'] = True
        self.assertRaises(DataValidationError, product.deserialize, product_data)

    def test_find_product_by_price(self):
        """it should find product by price
        """
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        price = products[0].price
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)

    def test_find_product_by_price_str(self):
        """it should find product by string price
        """
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        price = products[0].price
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(str(price))
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)
