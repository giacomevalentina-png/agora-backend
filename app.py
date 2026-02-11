from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agora.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email, 'isAdmin': self.is_admin}

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    excerpt = db.Column(db.String(500))
    content = db.Column(db.Text)
    category = db.Column(db.String(50))
    access = db.Column(db.String(20))
    author = db.Column(db.String(100))
    date = db.Column(db.String(20))
    chart_data = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'excerpt': self.excerpt,
            'content': self.content, 'category': self.category,
            'access': self.access, 'author': self.author, 'date': self.date,
            'chartData': json.loads(self.chart_data) if self.chart_data else None
        }

class NewsletterSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Agora API is running'})

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email exists'}), 400
    user = User(name=data['name'], email=data['email'],
                password_hash=generate_password_hash(data['password']),
                is_admin=(data['email'] == 'admin@agora.com'))
    db.session.add(user)
    db.session.commit()
    return jsonify({'user': user.to_dict()}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    return jsonify({'user': user.to_dict()})

@app.route('/api/articles')
def get_articles():
    articles = Article.query.order_by(Article.id.desc()).all()
    return jsonify([a.to_dict() for a in articles])

@app.route('/api/articles', methods=['POST'])
def create_article():
    data = request.json
    article = Article(
        title=data['title'], excerpt=data['excerpt'],
        content=data['content'], category=data['category'],
        access=data['access'], author=data['author'],
        date=datetime.now().strftime('%Y-%m-%d'),
        chart_data=json.dumps(data.get('chartData')) if data.get('chartData') else None
    )
    db.session.add(article)
    db.session.commit()
    return jsonify(article.to_dict()), 201

@app.route('/api/newsletter/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    if NewsletterSubscriber.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Already subscribed'})
    sub = NewsletterSubscriber(email=data['email'])
    db.session.add(sub)
    db.session.commit()
    return jsonify({'message': 'Subscribed'}), 201

@app.route('/api/newsletter/subscribers')
def get_subscribers():
    subs = NewsletterSubscriber.query.all()
    return jsonify([{'email': s.email} for s in subs])

def init_db():
    with app.app_context():
        db.create_all()
        if Article.query.count() == 0:
            samples = [
                Article(title="Understanding Global Trade Wars", excerpt="How trade policies shape markets",
                       content="Trade wars have become increasingly common...", category="markets",
                       access="free", author="agora Team", date="2026-02-05"),
                Article(title="The Rise of Populism", excerpt="Analyzing populist movements",
                       content="Populist movements have reshaped politics...", category="politics",
                       access="members", author="agora Team", date="2026-02-03")
            ]
            for a in samples:
                db.session.add(a)
            db.session.commit()
        print("✅ Database initialized!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)