import random
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
    synonyms = db.relationship('Synonym', backref='word', lazy=True, cascade="all, delete-orphan")

# 동의어 테이블
class Synonym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    synonym = db.Column(db.String(100), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)

# 데이터베이스 생성
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
    synonyms_text = request.form.get('synonyms', '')

    if word_text and meaning_text:
        new_word = Word(word=word_text, meaning=meaning_text)
        db.session.add(new_word)
        db.session.commit()

        if synonyms_text:
            synonyms_list = [syn.strip() for syn in synonyms_text.split(',')]
            for syn in synonyms_list:
                new_synonym = Synonym(synonym=syn, word_id=new_word.id)
                db.session.add(new_synonym)

        db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_word(id):
    word = Word.query.get_or_404(id)
    db.session.delete(word)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_word(id):
    word = Word.query.get_or_404(id)

    if request.method == 'POST':
        word.word = request.form['word']
        word.meaning = request.form['meaning']
        
        # 기존 동의어 삭제 후 새로운 동의어 추가
        Synonym.query.filter_by(word_id=id).delete()
        synonyms_text = request.form.get('synonyms', '')
        if synonyms_text:
            synonyms_list = [syn.strip() for syn in synonyms_text.split(',')]
            for syn in synonyms_list:
                new_synonym = Synonym(synonym=syn, word_id=word.id)
                db.session.add(new_synonym)

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', word=word)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    words = Word.query.all()
    if len(words) < 1:
        return render_template('quiz.html', message="단어가 부족합니다. 단어를 추가해주세요.")

    # 랜덤으로 단어를 섞어 5개만 뽑아서 퀴즈 문제로 출제
    quiz_words = random.sample(words, min(len(words), 5))

    if request.method == 'POST':
        score = 0
        for word in quiz_words:
            user_answer = request.form.get(f'word_{word.id}')
            if user_answer == word.meaning:
                score += 1
        return render_template('quiz_result.html', score=score, total=len(quiz_words))

    return render_template('quiz.html', words=quiz_words)

if __name__ == '__main__':
    app.run(debug=True)
