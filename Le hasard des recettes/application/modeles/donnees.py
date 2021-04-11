from flask import url_for
import datetime

from .. app import db


class Authorship(db.Model):
    """
        C'est une classe qui désigne la paternité des actions par utilisateur sur l'application.
        ...

        Attributs
        ----------
        db.Model :
            permet de lier la classe à la base de données initiée dans .. app.py

        Méthodes
        -------
        author_to_json(self)
            permet d'intégrer à l'api les informations sur la paternité des actions d'un utilisateur sur l'application
        """
    __tablename__ = "authorship"
    authorship_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True, unique=True)
    authorship_plat_id = db.Column(db.Integer, db.ForeignKey('plat.plat_id'))
    authorship_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    authorship_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', back_populates="authorships")
    plat = db.relationship('Plat', back_populates="authorships")

    def author_to_json(self):
        """permet d'intégrer à l'api les informations sur la paternité des actions d'un utilisateur sur l'application

                Paramètres
                ----------
                self :
                    récupère la ligne qui vient d'être créée dans la table
        """
        return {
            "author": self.user.to_jsonapi_dict(),
            "on": self.authorship_date
        }


class Composition(db.Model):
    """
        C'est une classe qui désigne la composition des recettes de la base de données.
        ...

        Attributs
        ----------
        db.Model :
            permet de lier la classe à la base de données initiée dans .. app.py.

        Méthodes
        -------
        ajout_compo(ingredient, plat, dosage)
            permet d'intégrer à la base de données les informations sur la composition des recettes.
        """
    __tablename__ = "composition"
    composition_id = db.Column(db.Integer, nullable=True, autoincrement=True, primary_key=True)
    composition_plat_id = db.Column(db.Integer, db.ForeignKey('plat.plat_id'))
    composition_ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.ingredient_id'))
    composition_ingredient = db.relationship('Ingredient', back_populates="composition")
    composition_plat = db.relationship('Plat', back_populates="composition")
    quantite = db.Column(db.String)

    @staticmethod
    def ajout_compo(ingredient: int, plat: int, dosage: str) -> bool:
        """permet d'intégrer à la base de données les informations sur la composition des recettes.

                Paramètres
                ----------
                ingredient :
                    récupère l'ingredient qui a été récupéré au préalable dans ./routes/generic.py dans
                    la fonction add_ingredient.

                plat :
                    récupère le plat qui a été récupéré au préalable dans ./routes/generic.py dans
                    la fonction add_ingredient.

                dosage :
                    récupère le dosage qui a été récupéré au préalable dans ./routes/generic.py dans
                    la fonction add_ingredient.

                Returns
                -------
                Booleen
                    en fonction du if qui précède les "returns"

                list
                    une liste d'erreurs s'il y a eu une erreur plus haut dans la fonction
                """
        erreurs = []
        if not ingredient:
            erreurs.append("L'ingrédient est manquant")
        if not plat:
            erreurs.append("L'id de la recette est manquant")
        if not dosage:
            erreurs.append("La quantité de l'ingrédient est manquante")

        if len(erreurs) > 0:
            return False, erreurs

        composition = Composition(
            composition_ingredient_id=ingredient,
            composition_plat_id=plat,
            quantite=dosage
        )

        try:
            db.session.add(composition)
            db.session.commit()
            return True, composition
        except Exception as erreur:
            return False, [str(erreur)]


class Plat(db.Model):
    """
        C'est une classe qui désigne les recettes de la base de données.
        ...

        Attributs
        ----------
        db.Model :
            permet de lier la classe à la base de données initiée dans .. app.py.

        Méthodes
        -------
        to_jsonapi_dict(self)
            permet d'intégrer à l'api les informations sur la paternité des actions d'un utilisateur sur l'application

        ajout(nom, recette, typologie, nombre)
            permet d'intégrer à la base de données les informations sur une recette.
        """
    plat_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    plat_nom = db.Column(db.Text)
    plat_recette = db.Column(db.VARCHAR(100))
    plat_type = db.Column(db.String(45))
    plat_nombre_convives = db.Column(db.Integer)
    authorships = db.relationship("Authorship", back_populates="plat")
    composition = db.relationship("Composition", back_populates="composition_plat")

    def to_jsonapi_dict(self):
        """permet d'intégrer à la base de données les informations sur la composition des recettes.

                Paramètres
                ----------
                self :
                    récupère la ligne qui vient d'être créée dans la table.

                Returns
                -------
                json
                    json rempli en fonction des informations fournies dans la classe.
                """
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

    @staticmethod
    def ajout(nom: str, recette: str, typologie: str, nombre: int) -> bool:
        """permet d'intégrer à la base de données les informations sur la composition des recettes.

                Paramètres
                ----------
                nom :
                    récupère le nom de la recette qui a été récupéré au préalable dans ./routes/generic.py dans
                    la fonction ajout_plat.

                recette :
                    récupère l'url de la recette qui a été récupéré au préalable dans ./routes/generic.py dans
                    la fonction ajout_plat.

                typologie :
                    récupère la typologie de la recette qui a été récupérée au préalable dans ./routes/generic.py dans
                    la fonction ajout_plat.

                Returns
                -------
                Booleen
                    en fonction du if qui précède les "returns"

                list
                    une liste d'erreurs s'il y a eu une erreur plus haut dans la fonction
                """
        erreurs = []
        if not nom:
            erreurs.append("Le nom de la recette est manquant")
        if not recette:
            erreurs.append("Le lien vers la recette est manquant")
        if not typologie:
            erreurs.append("Le type de la recette est manquant")
        if not nombre:
            erreurs.append("L'indication du nombre de convives est manquant")

        uniques = Plat.query.filter(db.or_(Plat.plat_recette == recette, Plat.plat_nom == nom)).count()
        if uniques > 0:
            erreurs.append("Le lien vers cette recette ou cette recette est déjà inscrit dans "
                           "notre base de données.")

        if len(erreurs) > 0:
            return False, erreurs

        plat = Plat(
            plat_nom=nom,
            plat_recette=recette,
            plat_type=typologie,
            plat_nombre_convives=nombre
        )

        try:
            db.session.add(plat)
            db.session.commit()
            return True, plat
        except Exception as erreur:
            return False, [str(erreur)]


class Ingredient(db.Model):
    """
        C'est une classe qui désigne les ingrédients des recettes de la base de données.
        ...

        Attributs
        ----------
        db.Model :
            permet de lier la classe à la base de données initiée dans .. app.py.

        Méthodes
        -------
        ajout_ingr(ingredient, t)
            permet d'intégrer à la base de données les informations sur un ingrédient.
        """
    ingredient_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True, nullable=False)
    ingredient_nom = db.Column(db.Text)
    ingredient_type = db.Column(db.Text)
    composition = db.relationship("Composition", back_populates="composition_ingredient")

    @staticmethod
    def ajout_ingr(ingredient: str, t: str) -> bool:
        """permet d'intégrer à la base de données les informations sur la composition des recettes.

                Paramètres
                ----------
                ingredient :
                    récupère le nom de l'ingrédient qui a été récupéré au préalable dans ./routes/generic.py dans
                    la fonction ajout_ingredient.

                t :
                    récupère le type de l'ingrédient qui a été récupéré au préalable dans ./routes/generic.py dans
                    la fonction ajout_ingredient.

                Returns
                -------
                Booleen
                    en fonction du if qui précède les "returns"

                list
                    une liste d'erreurs s'il y a eu une erreur plus haut dans la fonction
                """
        erreurs = []
        if not ingredient:
            erreurs.append("Le nom de l'ingrédient est manquant")
        if not t:
            erreurs.append("Le type de l'ingrédient est manquant")

        uniques = Ingredient.query.filter(Ingredient.ingredient_nom == ingredient).count()
        if uniques > 0:
            erreurs.append("Cet ingrédient est déjà inscrit dans notre base de données.")

        if len(erreurs) > 0:
            return False, erreurs

        ingredient = Ingredient(
            ingredient_nom=ingredient,
            ingredient_type=t
        )

        try:
            db.session.add(ingredient)
            db.session.commit()
            return True, ingredient
        except Exception as erreur:
            return False, [str(erreur)]
