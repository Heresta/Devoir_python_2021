from flask import render_template, request, flash, redirect
from flask_login import login_user, current_user, logout_user

from ..app import app, login, db
from ..modeles.donnees import Plat, Ingredient, Composition
from ..modeles.users import User
from ..constantes import PLAT_PAR_PAGE


@app.route("/", methods=["GET", "POST"])
def accueil():
    """permet d'afficher la page d'accueil de l'application.

            Returns
            -------
            Template
                correspondant à la page d'accueil de l'application
            """
    return render_template("pages/accueil.html")


@app.route("/plat", methods=["GET", "POST"])
def plat() -> list:
    """permet d'afficher la page avec la liste de tous les plats de la base de données.

        Returns
        -------
        Template
            correspondant à la page des plats de l'application

        List
            correspondant aux informations sur les plats qui ont été récupérées
        """
    plats = Plat.query.order_by(Plat.plat_nom).all()
    return render_template("pages/plat/plat.html", plats=plats)


@app.route("/plats/<int:plat_id>", methods=["GET", "POST"])
def plat_info(plat_id: int) -> list:
    """permet d'intégrer à la base de données les informations sur la composition des recettes.

            Paramètres
            ----------
            plat_id :
                récupère l'id de de la recette qui a été récupéré au préalable dans ./templates/pages/plat/plat.html
                dans la fonction url_for.

            Returns
            -------
            Template
                correspondant à la page d'un plat selon son id

            list
                correspondant aux informations sur le plat qui ont été récupérées
            """
    unique_plat = Plat.query.get(plat_id)
    i = []
    for ingredien in Plat.query.get(plat_id).composition:
        i.append([ingredien.quantite, ingredien.composition_ingredient])
    return render_template("pages/plat/plat_info.html", plat=unique_plat, i=i)


@app.route("/recherche_plat", methods=["GET", "POST"])
def recherche_plat() -> list:
    """permet d'afficher la page avec la liste de tous les plats de la base de données.

            Returns
            -------
            Template
                correspondant à la page de résultat de recherche de plats de l'application

            List
                correspondant aux informations sur les plats, le titre, le motclef qui ont été récupérées
            """
    motclef = request.args.get("keyword", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    resultats = []

    titre = "Recherche parmi les plats"

    if motclef:
        resultats = Plat.query.filter(Plat.plat_nom.like("%{}%".format(motclef))
                                      ).paginate(page=page, per_page=PLAT_PAR_PAGE)
        titre = "Résultat pour la recherche '" + motclef + "'"

    return render_template("pages/plat/recherche_plat.html", resultats=resultats, titre=titre, keyword=motclef)


@app.route("/recherche_plat_type")
def recherche_plat_type() -> list:
    """permet d'afficher la page avec la liste de tous les plats de la base de données selon le type du plat.

            Returns
            -------
            Template
                correspondant à la page de résultat de recherche de plats de l'application

            List
                correspondant aux informations sur les différentes typologies de plats qui ont été récupérées
            """
    resultats_plat_principal = Plat.query.filter(Plat.plat_type == "Plat principal").order_by(Plat.plat_nom).all()
    resultats_dessert = Plat.query.filter(Plat.plat_type == "Dessert").order_by(Plat.plat_nom).all()
    resultats_entree = Plat.query.filter(Plat.plat_type == "Entrée").order_by(Plat.plat_nom).all()
    resultats_accompagnement = Plat.query.filter(Plat.plat_type == "Accompagnement").order_by(Plat.plat_nom).all()
    resultats_autre = Plat.query.filter(Plat.plat_type == "Autre").order_by(Plat.plat_nom).all()
    return render_template("pages/plat/recherche_plat_type.html", resultats_pp=resultats_plat_principal,
                           resultats_dessert=resultats_dessert, resultats_entree=resultats_entree,
                           resultats_accompagnement=resultats_accompagnement, resultats_autre=resultats_autre)


@app.route("/recherche_plat_convives", methods=["GET", "POST"])
def recherche_plat_convives() -> list:
    """permet d'afficher la page avec la liste de tous les plats de la base de données selon le nombre de convives
    pour la recette.

            Returns
            -------
            Template
                correspondant à la page de résultat de recherche de plats par nombre de convives

            List
                correspondant aux informations sur les plats, le titre, le motclef qui ont été récupérées
            """
    motclef = request.args.get("keyword", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    resultats = []

    titre = "Recherche de plats par nombre de convives"

    if motclef:
        resultats = Plat.query.filter(Plat.plat_nombre_convives.like("%{}%".format(motclef))
                                      ).paginate(page=page, per_page=PLAT_PAR_PAGE)
        titre = "Résultats pour la recherche : '" + motclef + "' convive(s)"

    return render_template("pages/plat/recherche_plat_convives.html", resultats=resultats, titre=titre, keyword=motclef)


@app.route("/ajout_recette", methods=["GET", "POST"])
def ajout_recette():
    """permet de récupérer les informations à envoyer à la méthode ajout() dans ./modeles/donnees.py et ainsi ajouter
    une recette à la base de données.

            Returns (si cela n'a pas fonctionné)
            -------
            Template
                correspondant à la page d'ajout_recette de l'application pour permettre à l'utilisateur de recommencer
                si besoin
            """
    if request.method == "POST":
        statut, donnees = Plat.ajout(
            nom=request.form.get("nom", None),
            recette=request.form.get("recette", None),
            typologie=request.form.get("type", None),
            nombre=request.form.get("nombre", None)
        )

        if statut is True:
            flash("Enregistrement effectué.", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/crud/ajout_recette.html")
    else:
        flash("Ca ne fonctionne pas", "error")
        return render_template("pages/crud/ajout_recette.html")


@app.route("/plats/<int:plat_id>/adding_ingredients", methods=["GET", "POST"])
def adding_ingredient(plat_id: int) -> str:
    """permet de afficher tous les ingrédients de la base de données pour préparer à la fonction add_ingredients() et
    ainsi ajouter des ingrédients à une recette de la base de données.

        Returns (si cela n'a pas fonctionné)
        -------
        Template
            correspondant à la page d'add_ingredient de l'application pour préparer à la fonction add_ingredients()

        list
            correspond la liste complète des ingrédients de la base de données et au plat auquel on veut les ajouter
                """
    ingredi = Ingredient.query.order_by(Ingredient.ingredient_nom).all()
    unique_plat = Plat.query.get(plat_id)
    return render_template("pages/crud/add_ingredients.html", ingredients=ingredi, plat=unique_plat)


@app.route("/add_ingredients", methods=["GET", "POST"])
def add_ingredients():
    """permet de récupérer les informations à envoyer à la méthode ajout_ingr() dans ./modeles/donnees.py et ainsi
    ajouter des ingrédient à une recette de la base de données.

            Returns (si cela n'a pas fonctionné)
            -------
            Template
                correspondant à la page d'add_ingredients de l'application pour permettre à l'utilisateur de recommencer
                si besoin
            """
    if request.method == "POST":
        quantity = []
        for info in request.form.get("quantity", None):
            quantity.append(info)

        if quantity:
            print(quantity)

        n = 0

        for ingred in request.form.get("ingredient", None):
            statut, donnees = Composition.ajout_compo(
                ingredient=ingred,
                plat=request.form.get("keyword", None),
                dosage=quantity[n]
            )
            n += 1

        if statut is True:
            flash("Enregistrement effectué.", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return redirect("//")
    else:
        flash("Ca ne fonctionne pas", "error")
        return render_template("pages/crud/add_ingredients.html")


@app.route("/editer_recette", methods=["GET", "POST"])
def editer_recette():
    """permet de récupérer les informations pour éditer une recette de la base de données.

            Returns (si cela n'a pas fonctionné)
            -------
            Template
                correspondant à la page d'accueil ou au plat lui-même
                """
    id = request.form.get("keyword", None)
    if id:
        if request.method == "POST":
            nouveau_nom = request.form.get("nom", None)
            nouvelle_recette = request.form.get("recette", None)
            nouvelle_typologie = request.form.get("type", None)
            nouveau_nombre = request.form.get("nombre", None)
            modifications = []
            if request.form.get("nom", None):
                update_nom = Plat.query.filter(Plat.plat_id == id).first()
                update_nom.plat_nom = nouveau_nom
                db.session.commit()
                modifications.append("Le nom de la recette a bien été modifié. ")
            elif request.form.get("recette", None):
                update_recette = Plat.query.filter(Plat.plat_id == id).first()
                update_recette.plat_recette = nouvelle_recette
                db.session.commit()
                modifications.append("Le lien vers la recette a bien été modifié. ")
            elif request.form.get("type", None):
                update_typologie = Plat.query.filter(Plat.plat_id == id).first()
                update_typologie.plat_type = nouvelle_typologie
                db.session.commit()
                modifications.append("Le type de la recette a bien été modifié. ")
            elif request.form.get("nombre", None):
                update_nombre = Plat.query.filter(Plat.plat_id == id).first()
                update_nombre.plat_nombre_convives = nouveau_nombre
                db.session.commit()
                modifications.append("Le nombre de convives de la recette a bien été modifié. ")
            return redirect("/")
        else:
            flash("L'application n'a pas réussi à modifier la/les information(s) de ce plat", "error")
            return redirect("/")
    else:
        return redirect("/plat")


@app.route("/edition_recette/<int:plat_id>", methods=["GET", "POST"])
def edition_recette(plat_id: int) -> str:
    """permet de préparer la fonction editer_recette() pour éditer les informations concernant une recette

            Paramètres
            ----------
            plat_id :
                récupère l'id de de la recette qui a été récupéré au préalable dans ./templates/pages/plat/plat.html
                dans la fonction url_for.

            Returns
            -------
            Template
                correspondant à la page edition_recette d'un plat selon son id

            list
                correspondant aux informations sur le plat qui ont été récupérées
            """
    unique_plat = Plat.query.get(plat_id)
    return render_template("pages/crud/edition_recette.html", plat=unique_plat)


@app.route("/supprimer", methods=["GET", "POST"])
def supprimer():
    """permet de supprimer toutes les informations concernant une recette de la base de données
            """
    motclef = request.args.get("keyword", None)
    if motclef:
        id = Plat.query.filter(Plat.plat_id == motclef).first()
        db.session.delete(id)
        db.session.commit()
        for each in Composition.query.filter(Composition.composition_plat_id == motclef).all():
            db.session.delete(each)
            db.session.commit()
        flash("Le plat a bien été supprimé", "success")
        return redirect("/")
    else:
        flash("L'application n'a pas réussi à supprimer ce plat", "error")
        return redirect("/")


@app.route("/supprimer/<int:ids>", methods=["GET", "POST"])
def suppression(ids: int) -> int:
    """permet de préparer la fonction editer_recette() pour éditer les informations concernant une recette

            Paramètres
            ----------
            ids :
                récupère l'id de la recette qui a été récupéré au préalable dans
                ./templates/pages/crud/suppression.html

            Returns
            -------
            Template
                correspondant à la page suppression d'un plat selon son id

            list
                correspondant aux informations sur le plat qui ont été récupérées
            """
    unique_plat = Plat.query.get(ids)
    return render_template("pages/crud/suppression.html", plat=unique_plat)


@app.route("/ingredients/all")
def ingredients() -> list:
    """permet de faire une liste de tous les ingrédients dans la base de données

            Returns
            -------
            Template
                correspondant à la page qui fait la liste des ingredients de la base de données

            list
                correspondant aux informations sur les ingrédients qui ont été récupérées
            """
    ingr = Ingredient.query.order_by(Ingredient.ingredient_nom).all()
    return render_template("pages/ingredient/ingredient.html", ingredients=ingr)


@app.route("/ingredients/<int:ingredient_id>")
def ingredient(ingredient_id: int) -> list:
    """permet de donner toutes les informations concernant un ingrédient de la base de données

            Paramètres
            ----------
            ingredient_id :
                récupère l'id de l'ingrédient qui a été récupéré au préalable dans
                ./templates/pages/ingredient/ingredient.html

            Returns
            -------
            Template
                correspondant à la page donnant des informations sur un ingrédient selon son id

            list
                correspondant aux informations sur l'ingrédient qui ont été récupérées
            """
    unique_ingredient = Ingredient.query.get(ingredient_id)
    p = []
    for pla in Ingredient.query.get(ingredient_id).composition:
        p.append(pla.composition_plat)
    return render_template("pages/ingredient/ingredient_info.html", ingredient=unique_ingredient, p=p)


@app.route("/recherche_ingredient")
def recherche_ingredient() -> list:
    """permet de faire une recherche parmi les ingrédients

            Returns
            -------
            Template
                correspondant aux résultats de la recherche parmi tous les ingrédients

            list
                correspondant aux informations sur les ingrédients qui ont été récupérées
            """
    motclef = request.args.get("keyword", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    resultats = []

    titre = "Recherche parmi les ingrédients"

    if motclef:
        resultats = Ingredient.query.filter(Ingredient.ingredient_nom.like("%{}%".format(motclef))
                                            ).paginate(page=page, per_page=PLAT_PAR_PAGE)
        titre = "Résultat pour la recherche '" + motclef + "'"

    return render_template("pages/ingredient/recherche_ingredient.html", resultats=resultats, titre=titre)


@app.route("/recherche_ingredient_type")
def recherche_ingredient_type() -> list:
    """permet de faire une recherche parmi les ingrédients selon leur type

            Returns
            -------
            Template
                correspondant aux résultats de la recherche parmi tous les ingrédients

            list
                correspondant aux informations sur les ingrédients qui ont été récupérées
            """
    resultats_alcool = Ingredient.query.filter(Ingredient.ingredient_type == "Alcool"
                                               ).order_by(Ingredient.ingredient_nom).all()
    resultats_aromate = Ingredient.query.filter(Ingredient.ingredient_type == "Aromate"
                                                ).order_by(Ingredient.ingredient_nom).all()
    resultats_condiment = Ingredient.query.filter(Ingredient.ingredient_type == "Condiment"
                                                  ).order_by(Ingredient.ingredient_nom).all()
    resultats_eau = Ingredient.query.filter(Ingredient.ingredient_type == "Eau"
                                            ).order_by(Ingredient.ingredient_nom).all()
    resultats_epice = Ingredient.query.filter(Ingredient.ingredient_type == "Epice"
                                              ).order_by(Ingredient.ingredient_nom).all()
    resultats_fromage = Ingredient.query.filter(Ingredient.ingredient_type ==
                                                "Fromage").order_by(Ingredient.ingredient_nom).all()
    resultats_fruit = Ingredient.query.filter(Ingredient.ingredient_type == "Fruit"
                                              ).order_by(Ingredient.ingredient_nom).all()
    resultats_fruit_mer = Ingredient.query.filter(Ingredient.ingredient_type ==
                                                  "Fruit de mer").order_by(Ingredient.ingredient_nom).all()
    resultats_feculent = Ingredient.query.filter(Ingredient.ingredient_type ==
                                                 "Féculent").order_by(Ingredient.ingredient_nom).all()
    resultats_ingredient_prepare = Ingredient.query.filter(Ingredient.ingredient_type ==
                                                           "Ingrédient préparé").order_by(
        Ingredient.ingredient_nom).all()
    resultats_laitage = Ingredient.query.filter(Ingredient.ingredient_type ==
                                                "Laitage").order_by(Ingredient.ingredient_nom).all()
    resultats_legume = Ingredient.query.filter(Ingredient.ingredient_type ==
                                               "Légume").order_by(Ingredient.ingredient_nom).all()
    resultats_oeuf = Ingredient.query.filter(Ingredient.ingredient_type ==
                                             "Oeuf").order_by(Ingredient.ingredient_nom).all()
    resultats_viande = Ingredient.query.filter(Ingredient.ingredient_type ==
                                               "Viande").order_by(Ingredient.ingredient_nom).all()
    return render_template("pages/ingredient/recherche_ingredient_type.html", resultats_alcool=resultats_alcool,
                           resultats_aromate=resultats_aromate, resultats_condiment=resultats_condiment,
                           resultats_eau=resultats_eau, resultats_epice=resultats_epice,
                           resultats_fromage=resultats_fromage, resultats_fruit=resultats_fruit,
                           resultats_fruit_mer=resultats_fruit_mer, resultats_feculent=resultats_feculent,
                           resultats_ingredient_prepare=resultats_ingredient_prepare,
                           resultats_laitage=resultats_laitage, resultats_legume=resultats_legume,
                           resultats_oeuf=resultats_oeuf, resultats_viande=resultats_viande)


@app.route("/vers_ajout_ingredient", methods=["GET", "POST"])
def vers_ajout_ingredient():
    """prépare la fonction d'ajout d'ingrédient (ajout_ingredient())

            Returns
            -------
            Template
                correspondant aux résultats de la recherche parmi tous les ingrédients
            """
    return render_template("pages/crud/ajout_ingredient.html")


@app.route("/ajout_ingredient", methods=["GET", "POST"])
def ajout_ingredient():
    """permet de récupérer les informations à envoyer à la méthode ajout_ingre() dans ./modeles/donnees.py et ainsi
    ajouter des ingrédients à la base de données.

            Returns (si cela n'a pas fonctionné)
            -------
            Template
                correspondant à la page d'ajout_ingredient de l'application pour permettre à l'utilisateur de
                recommencer si besoin
            """
    if request.method == "POST":
        statut_ingredient, donnees = Ingredient.ajout_ingr(
            ingredient=request.form.get("ingredient", None),
            t=request.form.get("typologie", None)
        )
        if statut_ingredient is True:
            flash("Enregistrement effectué.", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/crud/ajout_ingredient.html")
    return render_template("pages/crud/ajout_ingredient.html")


@app.route("/register", methods=["GET", "POST"])
def inscription():
    """permet de récupérer les informations à envoyer à la méthode creer() dans ./modeles/users.py et ainsi
    ajouter des utilisateurs à la base de données.

            Returns (si cela n'a pas fonctionné)
            -------
            Template
                correspondant à la page d'inscription de l'application pour permettre à l'utilisateur de
                recommencer si besoin
            """
    if request.method == "POST":
        statut, donnees = User.creer(
            log=request.form.get("login", None),
            nom=request.form.get("nom", None),
            prenom=request.form.get("prenom", None),
            email=request.form.get("email", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if statut is True:
            flash("Enregistrement effectué. Identifiez-vous maintenant", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/inscription.html")
    else:
        return render_template("pages/inscription.html")


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    """permet de récupérer les informations à envoyer à la méthode identification() dans ./modeles/users.py et ainsi
    connecter des utilisateurs à l'application.

            Returns (si cela n'a pas fonctionné)
            -------
            Template
                correspondant à la page de connexion de l'application pour permettre à l'utilisateur de
                recommencer si besoin
                    """
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté(e)", "info")
        return redirect("/")
    if request.method == "POST":
        utilisateur = User.identification(
            log=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if utilisateur:
            flash("Connexion effectuée", "success")
            login_user(utilisateur)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")
    return render_template("pages/connexion.html")


login.login_view = connexion


@app.route("/deconnexion", methods=["GET", "POST"])
def deconnexion():
    """permet de déconnecter un utilisateur.
        """
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté(e)", "info")
    return redirect("/")
