from flask import render_template, request, flash, redirect

from .app import app, login
from .modeles.donnees import Plat, Ingredient, Composition
from .modeles.users import User
from .constantes import PLAT_PAR_PAGE
from flask_login import login_user, current_user, logout_user


@app.route("/")
def accueil():
    plats = Plat.query.all()
    return render_template("pages/accueil.html", plats=plats)


@app.route("/plats/<int:plat_id>")
def plat(plat_id):
    unique_plat = Plat.query.get(plat_id)
    for composition in Composition.query.get(Composition.composition_plat_id):
        if composition == plat_id:
            compositions = Composition.query.get(Composition.composition_ingredient_id)
    for ingre in compositions:
        if ingre == Ingredient.query.get(Ingredient.ingredient_id):
            ingredi = Ingredient.query.get(Ingredient.ingredient_id)
    return render_template("pages/plat.html", plat=unique_plat, ingredients=ingredi)


@app.route("/ingredients/all")
def ingredients():
    ingr = Ingredient.query.all()
    return render_template("pages/ingredient.html", ingredients=ingr)


@app.route("/ingredients/<int:ingredient_id>")
def ingredient(ingredient_id):
    unique_ingredient = Ingredient.query.get(ingredient_id)
    return render_template("pages/ingredient_info.html", ingredient=unique_ingredient)


@app.route("/recherche_plat")
def recherche_plat():
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

    return render_template("pages/recherche_plat.html", resultats=resultats, titre=titre, keyword=motclef)


@app.route("/recherche_ingredient")
def recherche_ingredient():
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

    return render_template("pages/recherche_ingredient.html", resultats=resultats, titre=titre)


@app.route("/register", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        statut, donnees = User.creer(
            log=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            prenom=request.form.get("prenom", None),
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


@app.route("/connexion")
def connexion():
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté(e)", "info")
        return redirect("/")
    if request.method == "POST":
        utilisateur = User.identification(
            log=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None),
        )
        if utilisateur:
            flash("Connexion effectuée", "success")
            login_user(utilisateur)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")
    return render_template("pages/connexion.html")


login.login_view = "connexion"


@app.route("/deconnexion")
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté(e)", "info")
    return redirect("/")
