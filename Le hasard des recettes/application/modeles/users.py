from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from ..app import db, login


class User(UserMixin, db.Model):
    """
        C'est une classe qui désigne les utilisateurs sur l'application.
        ...

        Attributs
        ----------
        db.Model :
            permet de lier la classe à la base de données initiée dans .. app.py

        Méthodes
        -------
        identification(log, motdepasse)
            permet d'identifier un utilisateur sur l'application

        creer(log, nom, prenom, email, motdepasse)
            permet de créer un nouvel utilisateur sur l'application
        """
    user_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    user_nom = db.Column(db.Text, nullable=False)
    user_prenom = db.Column(db.String, nullable=False)
    user_login = db.Column(db.String(45), nullable=False)
    user_email = db.Column(db.Text, nullable=False)
    user_password = db.Column(db.String(64), nullable=False)
    authorships = db.relationship("Authorship", back_populates="user")

    @staticmethod
    def identification(log, motdepasse) -> None:
        """permet d'identifier un utilisateur sur l'application.

                Paramètres
                ----------
                log :
                    récupère l'identifiant de l'utilisateur qui a été récupéré au préalable dans
                    ./templates/pages/connexion.html.

                motdepasse :
                    récupère le mot de passe de l'utilisateur qui a été récupéré au préalable dans
                    ./templates/pages/connexion.html.

                Returns
                -------
                None
                    Si cela ne fonctionne pas

                list
                    correspondant aux informations sur l'utilisateur qui ont été récupérées
                """
        utilisateur = User.query.filter(User.user_login == log).first()
        if utilisateur and check_password_hash(utilisateur.user_password, motdepasse):
            return utilisateur
        return None

    @staticmethod
    def creer(log, nom, prenom, email, motdepasse) -> bool:
        """permet de créer un utilisateur sur l'application dans la base de données.

                Paramètres
                ----------
                log :
                    récupère l'identifiant de l'utilisateur qui a été récupéré au préalable dans
                    ./templates/pages/inscription.html.

                motdepasse :
                    récupère le mot de passe de l'utilisateur qui a été récupéré au préalable dans
                    ./templates/pages/inscription.html.

                nom :
                    récupère le nom de l'utilisateur qui a été récupéré au préalable dans
                    ./templates/pages/inscription.html.

                prenom :
                    récupère le prenom de l'utilisateur qui a été récupéré au préalable dans
                    ./templates/pages/inscription.html.

                email :
                    récupère l'email de l'utilisateur qui a été récupéré au préalable dans
                    ./templates/pages/inscription.html.

                Returns
                -------
                Booleen :
                    indique si cela fonctionne ou non
                """
        erreurs = []
        if not log:
            erreurs.append("L'identifiant est manquant")
        if not email:
            erreurs.append("L'email est manquant")
        if not nom:
            erreurs.append("Le nom est manquant")
        if not prenom:
            erreurs.append("Le prenom est manquant")
        if not motdepasse:
            erreurs.append("Le mot de passe est manquant")

        uniques = User.query.filter(db.or_(User.user_email == email, User.user_login == log)).count()
        if uniques > 0:
            erreurs.append("L'email et/ou le login sont déjà inscrits dans notre base de données.")

        if len(erreurs) > 0:
            return False, erreurs

        utilisateur = User(
            user_nom=nom,
            user_prenom=prenom,
            user_login=log,
            user_email=email,
            user_password=generate_password_hash(motdepasse)
        )

        try:
            db.session.add(utilisateur)
            db.session.commit()
            return True, utilisateur
        except Exception as erreur:
            return False, [str(erreur)]


def get_id(self) -> int:
    """permet de récupérer un id d'utilisateur.

            Returns
            -------
            Int :
                id de l'utilisateur en cours
       """
    return self.user_id


def to_jsonapi_dict(self):
    """permet de récupérer des informations sur l'utilisateur en cours.

            Returns
            -------
            json :
                informations sur l'utilisateur en cours
           """
    return {
        "type": "people",
        "attributes": {
            "name": self.user_nom
        }
    }


@login.user_loader
def trouver_utilisateur_via_id(identifiant):
    """permet de trouver par un identifiant un utilisateur.

            Paramètres
            ----------
            identifiant :
                correspond à un id de User

            Returns
            -------
            Int :
                id de l'utilisateur en cours
           """
    return User.query.get(int(identifiant))
