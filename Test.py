from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from BaseData import db, Test, Question, Answer
import services
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'секретный_ключ'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
    tests = services.get_all_tests()
    return render_template('index.html', tests=tests)

@app.route('/create_test', methods=['GET', 'POST'])
def create_test():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('Название теста обязательно!')
            return redirect(url_for('create_test'))
        
        new_test = services.create_test(title, description)
        return redirect(url_for('edit_test', test_id=new_test.id))
    
    return render_template('create_test.html')

@app.route('/edit_test/<int:test_id>', methods=['GET', 'POST'])
def edit_test(test_id):
    test = services.get_test_by_id(test_id)
    return render_template('edit_test.html', test=test)

@app.route('/add_question/<int:test_id>', methods=['POST'])
def add_question(test_id):
    question_text = request.form.get('question_text')
    image_file = request.files.get('question_image')
    
    new_question = services.create_question(test_id, question_text, image_file)
    
    # Добавляем варианты ответов
    answer_count = int(request.form.get('answer_count', 4))
    labels = request.form.getlist('answer_label[]')
    texts = request.form.getlist('answer_text[]')
    is_correct_list = request.form.getlist('is_correct[]')
    
    services.add_answers_to_question(new_question.id, answer_count, labels, texts, is_correct_list)
    
    return redirect(url_for('edit_test', test_id=test_id))

@app.route('/view_test/<int:test_id>')
def view_test(test_id):
    test = services.get_test_by_id(test_id)
    return render_template('view_test.html', test=test)

@app.route('/delete_test/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    services.delete_test(test_id)
    return redirect(url_for('home'))

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = services.get_question_by_id(question_id)
    test_id = question.test_id
    
    if request.method == 'POST':
        # Обновляем данные вопроса
        question_text = request.form.get('question_text')
        image_file = request.files.get('question_image')
        remove_image = request.form.get('remove_image')
        
        services.update_question(question_id, question_text, image_file, remove_image)
        
        # Удаляем существующие ответы и добавляем новые
        services.delete_answers_for_question(question_id)
        
        # Добавляем обновленные ответы
        answer_count = int(request.form.get('answer_count', 4))
        labels = request.form.getlist('answer_label[]')
        texts = request.form.getlist('answer_text[]')
        is_correct_list = request.form.getlist('is_correct[]')
        
        services.add_answers_to_question(question_id, answer_count, labels, texts, is_correct_list)
        
        flash('Вопрос успешно обновлен')
        return redirect(url_for('edit_test', test_id=test_id))
    
    return render_template('edit_question.html', question=question, test_id=test_id)

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    test_id = services.delete_question(question_id)
    flash('Вопрос успешно удален')
    
    return redirect(url_for('edit_test', test_id=test_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
