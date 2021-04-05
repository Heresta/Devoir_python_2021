from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from ..app import db, login


class User(UserMinxin, db.Model):
    user_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    user_nom = db.Column(db.Text, nullable=False)
    user_prenom = db.Column(db.Text, nullable=False)
    user_login = db.Column(db.String(45), nullable=False)
    user_email = db.Column(db.Text, nullable=False)
    user_password = db.Column(db.String(64), nullable=False)
    authorships = db.relationship("Authorship", back_populates="user")

    @staticmethod
    def identification(log, motdepasse):
        utilisateur = User.query.filter(User.user_id == log).first()
        if utilisateur and check_password_hash(utilisateur.user_password, motdepasse):
            return utilisateur
        return None

    @staticmethod
    def creer(log, nom, prenom, email, motdepasse):
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


def get_id(self):
    return self.user_id


def to_jsonapi_dict(self):
    return {
        "type": "people",
        "attributes": {
            "name": self.user_nom
        }
    }


@login.user_loader
def trouver_utilisateur_via_id(identifiant):
    return User.query.get(int(identifiant))
