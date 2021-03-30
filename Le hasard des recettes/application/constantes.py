from warnings import warn

PLAT_PAR_PAGE = 5

SECRET_KEY = "Je suis un secret !"

API_ROUTE = "/api"

if SECRET_KEY == "Je suis un secret !":
    warn("Le secret par défaut n'a pas été changé, vous devriez le faire", Warning)
