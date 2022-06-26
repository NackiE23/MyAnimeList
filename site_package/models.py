from site_package import db


class Anime(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=60), nullable=False)
    alternative_name = db.Column(db.String(length=60), nullable=True)
    release = db.Column(db.Date(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=True)
    grade = db.Column(db.Integer(), nullable=True)
    img = db.Column(db.LargeBinary)

    def __repr__(self):
        return self.name
