from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from BaseData import db, Test, Question, Answer, User, Article, ArticleFile
import services
import os
import re

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
    articles = services.get_all_articles()
    return render_template('index.html', tests=tests, articles=articles)

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

# Маршруты для работы со статьями
@app.route('/articles')
@login_required
def articles():
    articles = services.get_all_articles()
    for article in articles:
        # Очистим разметку для предварительного просмотра
        article.preview_content = article.content
    return render_template('articles.html', articles=articles)

@app.route('/create_article', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Название и содержание статьи обязательны!')
            return redirect(url_for('create_article'))
        
        files = request.files.getlist('files')
        new_article = services.create_article(title, content, files)
        
        flash('Статья успешно создана!')
        return redirect(url_for('view_article', article_id=new_article.id))
    
    return render_template('create_article.html')

def format_telegram_text(text):
    """Преобразует разметку Telegram в HTML"""
    # Заменяем переносы строк на <br>
    text = text.replace('\n', '<br>')
    
    # Жирный текст: *текст* -> <strong>текст</strong>
    text = re.sub(r'\*(.*?)\*', r'<strong>\1</strong>', text)
    
    # Курсив: _текст_ -> <em>текст</em>
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
    
    # Подчёркнутый: __текст__ -> <u>текст</u>
    text = re.sub(r'__(.*?)__', r'<u>\1</u>', text)
    
    # Код: `текст` -> <code>текст</code>
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    
    # Блок кода: ```текст``` -> <pre>текст</pre>
    text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text)
    
    return text

def generate_article_toc(text):
    """Генерирует оглавление статьи на основе заголовков"""
    # Разделяем текст на строки
    lines = text.split('\n')
    toc_items = []
    
    # Находим строки, которые выглядят как заголовки
    # 1. Строки, начинающиеся с # (как в Markdown)
    # 2. Строки с *заголовком* (жирный текст в начале строки)
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Markdown-подобные заголовки
        if line.startswith('#'):
            level = 1
            while line.startswith('#'):
                level = min(level + 1, 6)  # h1-h6
                line = line[1:].strip()
            
            # Генерируем уникальный ID для якоря
            item_id = f"heading-{i}"
            toc_items.append({
                'id': item_id,
                'text': line,
                'level': level
            })
        
        # Жирный текст как заголовок (только если вся строка в звездочках)
        elif line.startswith('*') and line.endswith('*') and len(line) > 2:
            heading_text = line[1:-1].strip()
            item_id = f"heading-{i}"
            toc_items.append({
                'id': item_id,
                'text': heading_text,
                'level': 2  # h2 для жирных заголовков
            })
    
    return toc_items

@app.route('/view_article/<int:article_id>')
@login_required
def view_article(article_id):
    article = services.get_article_by_id(article_id)
    
    # Генерируем оглавление
    toc_items = generate_article_toc(article.content)
    
    # Добавляем якоря к заголовкам в тексте
    content_with_anchors = article.content
    for item in toc_items:
        # Заменяем заголовки на якори в зависимости от типа
        if item['level'] == 2:  # Жирные заголовки
            pattern = f"\\*{re.escape(item['text'])}\\*"
            replacement = f"<span id='{item['id']}'></span>*{item['text']}*"
            content_with_anchors = re.sub(pattern, replacement, content_with_anchors, 1)
        else:  # Markdown заголовки
            hashes = '#' * (item['level'] - 1)
            pattern = f"{hashes} {re.escape(item['text'])}"
            replacement = f"<span id='{item['id']}'></span>{hashes} {item['text']}"
            content_with_anchors = re.sub(pattern, replacement, content_with_anchors, 1)
    
    # Форматируем содержимое с якорями
    formatted_content = format_telegram_text(content_with_anchors)
    
    return render_template('view_article.html', article=article, formatted_content=formatted_content, toc_items=toc_items)

@app.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = services.get_article_by_id(article_id)
    
    # Проверка прав доступа
    if article.user_id != current_user.id and current_user.id != 1:
        flash('У вас нет прав для редактирования этой статьи')
        return redirect(url_for('articles'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Название и содержание статьи обязательны!')
            return redirect(url_for('edit_article', article_id=article_id))
        
        files = request.files.getlist('files')
        success, message = services.update_article(article_id, title, content, files)
        
        flash(message)
        if success:
            return redirect(url_for('view_article', article_id=article_id))
    
    return render_template('edit_article.html', article=article)

@app.route('/delete_article/<int:article_id>', methods=['POST'])
@login_required
def delete_article(article_id):
    success, message = services.delete_article(article_id)
    flash(message)
    
    return redirect(url_for('articles'))

@app.route('/delete_article_file/<int:file_id>', methods=['POST'])
@login_required
def delete_article_file(file_id):
    success, message = services.delete_file_from_article(file_id)
    flash(message)
    
    return redirect(request.referrer or url_for('articles'))

@app.route('/add_article_file/<int:article_id>', methods=['POST'])
@login_required
def add_article_file(article_id):
    """Добавить один файл к статье через AJAX"""
    article = services.get_article_by_id(article_id)
    
    # Проверка прав доступа
    if article.user_id != current_user.id and current_user.id != 1:
        return jsonify({'success': False, 'message': 'У вас нет прав для редактирования этой статьи'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Файл не был загружен'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Файл не выбран'})
    
    # Добавляем файл
    try:
        new_file = services.add_file_to_article(article_id, file)
        
        # Создаем HTML для превью файла
        preview_html = render_template('_file_preview.html', file=new_file, article=article)
        
        return jsonify({
            'success': True, 
            'message': 'Файл успешно загружен',
            'file_id': new_file.id,
            'preview_html': preview_html
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
