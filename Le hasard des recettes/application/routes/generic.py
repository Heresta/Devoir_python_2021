from flask import render_template, request, flash, redirect
from flask_login import login_user, current_user, logout_user

from ..app import app, login, db
from ..constantes import PLAT_PAR_PAGE
from ..modeles.donnees import Plat, Ingredient
from ..modeles.users import User


@app.route("/", methods=["GET", "POST"])
def accueil():
    return render_template("pages/accueil.html")


@app.route("/plat", methods=["GET", "POST])
def plat():
    plats = Plat.query.order_by(Plat.plat_nom).all()
    return render_template("pages/plat/plat.html", plats=plats)


@app.route("/plats/<int:plat_id>", methods=["GET", "POST"])
def plat(plat_id):
    unique_plat = Plat.query.get(plat_id)
    i = []
    for ingredient in Plat.query.get(plat_id).composition:
        i.append([ingredient.quantite, ingredient.composition_ingredient])
    return render_template("pages/plat/plat_info.html", plat=unique_plat, i=i)
          
                             
@app.route("/recherche_plat", methods=["GET", "POST"])
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

    return render_template("pages/plat/recherche_plat.html", resultats=resultats, titre=titre, keyword=motclef)                            


@app..route("/recherche_plat_type")
def recherche_plat_type():
    resultats_plat_principal = Plat.query.filter(Plat.plat_type == "Plat principal").order_by(Plat.plat_nom).all()
    resultats_dessert = Plat.query.filter(Plat.plat_type == "Dessert").order_by(Plat.plat_nom).all()
    resultats_entree = Plat.query.filter(Plat.plat_type == "Entrée").order_by(Plat.plat_nom).all()
    resultats_accompagnement = Plat.query.filter(Plat.plat_type == "Accompagnement").order_by(Plat.plat_nom).all()
    resultats_autre = Plat.query.filter(Plat.plat_type == "Autre").order_by(Plat.plat_nom).all()
    return render_template("pages/plat/recherche_plat_type.html", resultats_pp=resultats_plat_principal,
                           resultats_dessert=resultats_dessert, resultats_entree=resultats_entree,
                           resultats_accompagnement=resultats_accompagnement, resultats_autre=resultats_autre)


@app.route("/recherche_plat_convives", methods=["GET", "POST"])
def recherche_plat_convives():
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
            return render_template("pages/ajout_recette.html")
    return render_template("pages/crud/ajout_recette.html")


@app.route("/editer_recette", methods=["GET", "POST"])
def editer_recette():
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
            flash("L'application n'a pas réussi à modifier la/les information(s) de ce plat")
            return redirect("/")
    else:
        return redirect("/plat")


@app.route("/edition_recette/<int:plat_id>", methods=["GET", "POST"])
def edition_recette(plat_id):
    unique_plat = Plat.query.get(plat_id)
    return render_template("pages/crud/edition_recette.html", plat=unique_plat) 


@app.route("/supprimer", methods=["GET", "POST"])
def supprimer():
    motclef = request.args.get("keyword", None)
    if motclef:
        id = Plat.query.filter(Plat.plat_id == motclef).first()
        db.session.delete(id)
        db.session.commit()
        flash("Le plat a bien été supprimé")
        return redirect("/")
    else:
        flash("L'application n'a pas réussi à supprimer ce plat")
    return redirect("/")


@app.route("/supprimer/<int:ids>", methods=["GET", "POST"])
def suppression(ids):
    unique_plat = Plat.query.get(ids)
    return render_template("pages/plat/suppression.html", plat=unique_plat)

                             
@app.route("/ingredients/all")
def ingredients():
    ingr = Ingredient.query.all()
    return render_template("pages/ingredient/ingredient.html", ingredients=ingr)


@app.route("/ingredients/<int:ingredient_id>")
def ingredient(ingredient_id):
    unique_ingredient = Ingredient.query.get(ingredient_id)
    p = []
    for plat in Ingredient.query.get(ingredient_id).composition:
        p.append(plat.composition_plat)
    return render_template("pages/ingredient/ingredient_info.html", ingredient=unique_ingredient, p=p)
                             
                             
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

    return render_template("pages/ingredient/recherche_ingredient.html", resultats=resultats, titre=titre)

                             
@app.route("/recherche_ingredient_type")
def recherche_ingredient_type():
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
    resultats_ingredient_prepare = Ingredient.query.filter(Ingredient.ingredient_type == "Ingrédient préparé"
                                              ).order_by(Ingredient.ingredient_nom).all()
    resultats_laitage = Ingredient.query.filter(Ingredient.ingredient_type == "Laitage"
                                              ).order_by(Ingredient.ingredient_nom).all()
    resultats_legume = Ingredient.query.filter(Ingredient.ingredient_type == "Légume"
                                              ).order_by(Ingredient.ingredient_nom).all()
    resultats_oeuf = Ingredient.query.filter(Ingredient.ingredient_type == "Oeuf"
                                              ).order_by(Ingredient.ingredient_nom).all()
    resultats_viande = Ingredient.query.filter(Ingredient.ingredient_type == "Viande"
                                              ).order_by(Ingredient.ingredient_nom).all()
    return render_template("pages/ingredient/recherche_ingredient_type.html", resultats_alcool=resultats_alcool,
                           resultats_aromate=resultats_aromate, resultats_condiment=resultats_condiment,
                           resultats_eau=resultats_eau, resultats_epice=resultats_epice,
                           resultats_fromage=resultats_fromage, resultats_fruit=resultats_fruit,
                           resultats_fruit_mer=resultats_fruit_mer, resultats_feculent=resultats_feculent,
                           resultats_ingredient_prepare=resultats_ingredient_prepare,
                           resultats_laitage=resultats_laitage, resultats_legume=resultats_legume,
                           resultats_oeuf=resultats_oeuf, resultats_viande=resultats_viande)
                            
                             
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


@app.route("/connexion", methods=["GET", "POST"])
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
