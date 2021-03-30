from flask import render_template, request, url_for, jsonify
from urllib.parse import urlencode

from ..app import app
from ..constantes import PLAT_PAR_PAGE, API_ROUTE
from ..modeles.donnees import Plat


def json_404():
    response = jsonify({"erreur": "Impossible d'accéder à la requête"})
    response.status_code = 404
    return response


@app.route(API_ROUTE+"/plats/<plat_id>")
def api_places_single(plat_id):
    try:
        query = Plat.query.get(plat_id)
        return jsonify(query.to_jsonapi_dict())
    except:
        return json_404()


@app.route(API_ROUTE+"/plats")
def api_plats_browse():
    motclef = request.args.get("q", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    if motclef:
        query = Plat.query.filter(Plat.plat_nom.like("%{}%".format(motclef)))
    else:
        query = Plat.query

    try:
        resultats = query.paginate(page=page, per_page=PLAT_PAR_PAGE)
    except Exception:
        return json_404()

    dict_resultats = {
        "links": {
            "self": request.url
        },
        "data": [
            plat.to_jsonapi_dict()
            for plat in resultats.items
        ]
    }

    if resultats.has_next:
        arguments = {
            "page": resultats.next_num
        }
        if motclef:
            arguments["q"] = motclef
        dict_resultats["links"]["next"] = url_for("api_plats_browse", _external=True)+"?"+urlencode(arguments)

    if resultats.has_prev:
        arguments = {
            "page": resultats.prev_num
        }
        if motclef:
            arguments["q"] = motclef
        dict_resultats["links"]["prev"] = url_for("api_plats_browse", _external=True)+"?"+urlencode(arguments)

    response = jsonify(dict_resultats)
    return response
