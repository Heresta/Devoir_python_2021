from flask import url_for
import datetime

from .. app import db


class Authorship(db.Model):
    __tablename__ = "authorship"
    authorship_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    authorship_plat_id = db.Column(db.Integer, db.ForeignKey('plat.plat_id'))
    authorship_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', back_populates="authorships")
    plat = db.relationship('Plat', back_populates="authorships")

    def author_to_json(self):
        return {
            "author": self.user.to_jsonapi_dict(),
            "on": self.authorship_date
        }


class Composition(db.Model):
    __tablename__ = "composition"
    composition_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    composition_plat_id = db.Column(db.Integer, db.ForeignKey('plat.plat_id'))
    composition_ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.ingredient_id'))
    composition_ingredient = db.relationship('Ingredient', back_populates="composition")
    composition_plat = db.relationship('Plat', back_populates="composition")
    quantite = db.Column(db.String)


class Plat(db.Model):
    plat_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    plat_nom = db.Column(db.Text)
    plat_recette = db.Column(db.VARCHAR(100))
    plat_type = db.Column(db.String(45))
    plat_nombre_convives = db.Column(db.Integer)
    authorships = db.relationship("Authorship", back_populates="plat")
    composition = db.relationship("Composition", back_populates="composition_plat")

    def to_jsonapi_dict(self):
        return {
            "type": "place",
            "id": self.plat_id,
            "attributes": {
                "name": self.plat_nom,
                "type": self.plat_type,
                "nombre_convives": self.plat_nombre_convives,
                "lien_recette": self.plat_recette
            },
            "links": {
                "self": url_for("plat", plat_id=self.plat_id, _external=True),
                "json": url_for("api_plats_single", plat_id=self.plat_id, _external=True)
            },
            "relationships": {
                "editions": [
                    author.author_to_json()
                    for author in self.authorships
                ]
            }
        }


class Ingredient(db.Model):
    ingredient_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True, nullable=False)
    ingredient_nom = db.Column(db.Text)
    ingredient_type = db.Column(db.Text)
    composition = db.relationship("Composition", back_populates="composition_ingredient")
