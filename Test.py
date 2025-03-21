from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from BaseData import db, Test, Question, Answer, User
import services
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'секретный_ключ_для_разработки')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)

# Инициализация менеджера авторизации
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'welcome'
login_manager.login_message = "Пожалуйста, войдите в систему для доступа к этой странице"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/dashboard')
@login_required
def dashboard():
    tests = services.get_all_tests()
    return render_template('index.html', tests=tests)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not username or not email or not password:
            flash('Все поля обязательны для заполнения')
            return redirect(url_for('register'))
            
        if password != password_confirm:
            flash('Пароли не совпадают')
            return redirect(url_for('register'))
        
        success, message = services.register_user(username, email, password)
        flash(message)
        if success:
            return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Пожалуйста, введите имя пользователя и пароль')
            return redirect(url_for('login'))
        
        success, message = services.login_user_func(username, password)
        flash(message)
        if success:
            return redirect(url_for('dashboard'))
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы')
    return redirect(url_for('welcome'))

@app.route('/create_test', methods=['GET', 'POST'])
@login_required
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
@login_required
def edit_test(test_id):
    test = services.get_test_by_id(test_id)
    
    # Проверяем права доступа
    if test.user_id != current_user.id and current_user.id != 1:
        flash('У вас нет прав для редактирования этого теста')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_test.html', test=test)

@app.route('/add_question/<int:test_id>', methods=['POST'])
@login_required
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
@login_required
def view_test(test_id):
    test = services.get_test_by_id(test_id)
    return render_template('view_test.html', test=test)

@app.route('/delete_test/<int:test_id>', methods=['POST'])
@login_required
def delete_test(test_id):
    success = services.delete_test(test_id)
    if success:
        flash('Тест успешно удален')
    else:
        flash('У вас нет прав для удаления этого теста')
    return redirect(url_for('dashboard'))

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def delete_question(question_id):
    test_id = services.delete_question(question_id)
    flash('Вопрос успешно удален')
    
    return redirect(url_for('edit_test', test_id=test_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
