from flask import Flask

from blueprint.sub_reviews.sub_reviews import sub_reviews_bp
from blueprint.auth.auth import auth_bp
from blueprint.reviews.reviews import reviews_bp

app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(sub_reviews_bp)


if __name__ == '__main__':
    app.run(debug=True)