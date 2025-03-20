from BaseData import db, Test, Question, Answer
import base64

def get_all_tests():
    """Получить все тесты"""
    return Test.query.all()

def get_test_by_id(test_id):
    """Получить тест по ID"""
    return Test.query.get_or_404(test_id)

def get_question_by_id(question_id):
    """Получить вопрос по ID"""
    return Question.query.get_or_404(question_id)

def create_test(title, description):
    """Создать новый тест"""
    new_test = Test(title=title, description=description)
    db.session.add(new_test)
    db.session.commit()
    return new_test

def delete_test(test_id):
    """Удалить тест по ID"""
    test = get_test_by_id(test_id)
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