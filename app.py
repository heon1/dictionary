from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLite 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vocabulary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 단어 테이블
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), unique=True, nullable=False)
    meaning = db.Column(db.String(255), nullable=False)
    
    # Word와 Synonym을 연결 (1:N 관계)
    synonyms = db.relationship('Synonym', backref='word', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Word {self.word}>'

# 동의어 테이블
class Synonym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    synonym = db.Column(db.String(100), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)  # Word 테이블과 연결

    def __repr__(self):
        return f'<Synonym {self.synonym}>'

# 데이터베이스 초기화
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    words = Word.query.all()
    return render_template('index.html', vocabulary=words)

@app.route('/add', methods=['POST'])
def add_word():
    word_text = request.form['word']
    meaning_text = request.form['meaning']
    synonyms_text = request.form.get('synonyms', '')  # 동의어 입력란이 비어있을 수도 있음

    if word_text and meaning_text:
        new_word = Word(word=word_text, meaning=meaning_text)
        db.session.add(new_word)
        db.session.commit()

        # 동의어 추가 (쉼표로 구분하여 여러 개 입력 가능)
        if synonyms_text:
            synonyms_list = [syn.strip() for syn in synonyms_text.split(',')]
            for syn in synonyms_list:
                new_synonym = Synonym(synonym=syn, word_id=new_word.id)
                db.session.add(new_synonym)
        
        db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
