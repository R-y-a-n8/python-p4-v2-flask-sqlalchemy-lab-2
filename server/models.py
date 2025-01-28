from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# MetaData configuration for naming conventions
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# Customer Model
class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    
    # Relationship to Review model
    reviews = db.relationship('Review', back_populates='customer')
    
    # Association proxy to access items directly through reviews
    items = association_proxy('reviews', 'item')

    # Avoid recursion by excluding reviews' customer field from serialization
    serialize_rules = ('-reviews.customer',)  # Exclude customer from reviews

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'reviews': [review.to_dict() for review in self.reviews]  # Manually include reviews
        }

# Item Model
class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    # Relationship to Review model
    reviews = db.relationship('Review', back_populates='item')

    # Avoid recursion by excluding reviews' item field from serialization
    serialize_rules = ('-reviews.item',)  # Exclude item from reviews

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'reviews': [review.to_dict() for review in self.reviews]  # Manually include reviews
        }

# Review Model
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(255))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    
    # Relationships to Customer and Item models
    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.id}, Comment: {self.comment}>'

    def to_dict(self):
        return {
            'id': self.id,
            'comment': self.comment,
            'customer': {
                'id': self.customer.id,
                'name': self.customer.name
            } if self.customer else None,  # Avoid full customer serialization
            'item': {
                'id': self.item.id,
                'name': self.item.name,
                'price': self.item.price
            } if self.item else None,  # Avoid full item serialization
        }
