from BaseData import db, Test, Question, Answer, User
import base64
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user

def get_all_tests():
    """Получить все тесты"""
    tests = Test.query.all()
    # Проверяем существующие тесты и присваиваем им admin, если у них нет user_id
    for test in tests:
        if test.user_id is None:
            test.user_id = 1  # ID администратора по умолчанию
            db.session.add(test)
    
    if tests and any(test.user_id is None for test in tests):
        db.session.commit()
    
    return tests

def get_test_by_id(test_id):
    """Получить тест по ID"""
    return Test.query.get_or_404(test_id)

def get_question_by_id(question_id):
    """Получить вопрос по ID"""
    return Question.query.get_or_404(question_id)

def create_test(title, description):
    """Создать новый тест"""
    new_test = Test(title=title, description=description, user_id=current_user.id)
    db.session.add(new_test)
    db.session.commit()
    return new_test

def delete_test(test_id):
    """Удалить тест по ID"""
    test = get_test_by_id(test_id)
    
    # Проверка, что текущий пользователь - владелец теста
    if test.user_id != current_user.id and current_user.id != 1:  # Не админ и не владелец
        return False
        
    db.session.delete(test)
    db.session.commit()
    return True

def create_question(test_id, question_text, image_file):
    """Создать новый вопрос с изображением (если есть)"""
    test = get_test_by_id(test_id)
    
    # Обработка изображения, если оно есть
    image_data = None
    if image_file and image_file.filename:
        image_binary = image_file.read()
        image_base64 = base64.b64encode(image_binary).decode('utf-8')
        image_data = f"data:{image_file.content_type};base64,{image_base64}"
    
    # Создание вопроса
    new_question = Question(text=question_text, image=image_data, test_id=test.id)
    db.session.add(new_question)
    db.session.commit()
    return new_question

def add_answers_to_question(question_id, answer_count, labels, texts, is_correct_list):
    """Добавить варианты ответов к вопросу"""
    for i in range(answer_count):
        label = labels[i] if i < len(labels) and labels[i] else chr(97 + i)  # a, b, c, d...
        
        # Получаем текст ответа, используем пустую строку, если значение не указано
        text = texts[i] if i < len(texts) else ''
        
        is_correct = str(i) in is_correct_list
        
        new_answer = Answer(
            label=label,
            text=text,
            is_correct=is_correct,
            question_id=question_id
        )
        db.session.add(new_answer)
    
    db.session.commit()
    return True

def update_question(question_id, question_text, image_file, remove_image):
    """Обновить вопрос"""
    question = get_question_by_id(question_id)
    question.text = question_text
    
    # Обработка изображения
    if image_file and image_file.filename:
        image_binary = image_file.read()
        image_base64 = base64.b64encode(image_binary).decode('utf-8')
        question.image = f"data:{image_file.content_type};base64,{image_base64}"
    elif remove_image == 'yes':
        question.image = None
        
    db.session.commit()
    return question

def delete_answers_for_question(question_id):
    """Удалить все ответы для вопроса"""
    Answer.query.filter_by(question_id=question_id).delete()
    db.session.commit()
    return True

def delete_question(question_id):
    """Удалить вопрос"""
    question = get_question_by_id(question_id)
    test_id = question.test_id
    
    db.session.delete(question)
    db.session.commit()
    return test_id

def register_user(username, email, password):
    """Регистрация нового пользователя"""
    # Проверка, существует ли пользователь с таким email или username
    existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        return False, "Пользователь с таким email или именем уже существует"
    
    # Хеширование пароля и создание пользователя
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return True, "Регистрация успешна"

def login_user_func(username, password):
    """Авторизация пользователя"""
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return False, "Неверное имя пользователя или пароль"
    
    login_user(user)
    return True, "Авторизация успешна" 