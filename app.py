from flask import Flask, request, jsonify
from models import db, Advertisement
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///advertisements.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)


def validate_advertisement_data(data, is_update=False):
    """
    Валидация данных объявления
    Возвращает (is_valid, error_message)
    """
    if not data:
        return False, "No JSON data provided"
    
    if not is_update:
        # Для создания проверяем все обязательные поля
        required_fields = ['title', 'description', 'owner']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Проверка типов
        if not isinstance(data.get('title'), str):
            return False, "Field 'title' must be a string"
        if not isinstance(data.get('description'), str):
            return False, "Field 'description' must be a string"
        if not isinstance(data.get('owner'), str):
            return False, "Field 'owner' must be a string"
        
        # Проверка длины
        if len(data['title']) > 200:
            return False, "Field 'title' must be less than 200 characters"
        if len(data['owner']) > 100:
            return False, "Field 'owner' must be less than 100 characters"
    
    return True, None


@app.route('/advertisements', methods=['POST'])
def create_advertisement():
    """
    Создание нового объявления
    Ожидает JSON: {"title": "...", "description": "...", "owner": "..."}
    """
    try:
        data = request.get_json(silent=True)
        
        # Валидация данных
        is_valid, error_message = validate_advertisement_data(data, is_update=False)
        if not is_valid:
            return jsonify({'error': error_message}), 400

        # Создание объявления
        advertisement = Advertisement(
            title=data['title'].strip(),
            description=data['description'].strip(),
            owner=data['owner'].strip()
        )

        db.session.add(advertisement)
        db.session.commit()

        return jsonify(advertisement.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/advertisements/<int:ad_id>', methods=['GET'])
def get_advertisement(ad_id):
    """
    Получение объявления по ID
    """
    try:
        advertisement = Advertisement.query.get(ad_id)

        if not advertisement:
            return jsonify({'error': f'Advertisement with id {ad_id} not found'}), 404

        return jsonify(advertisement.to_dict()), 200

    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/advertisements/<int:ad_id>', methods=['PUT'])
def update_advertisement(ad_id):
    """
    Редактирование объявления
    Ожидает JSON с любыми полями для обновления
    """
    try:
        advertisement = Advertisement.query.get(ad_id)

        if not advertisement:
            return jsonify({'error': f'Advertisement with id {ad_id} not found'}), 404

        data = request.get_json(silent=True)

        if not data:
            return jsonify({'error': 'No JSON data provided for update'}), 400

        # Обновление только переданных полей с валидацией
        if 'title' in data:
            if not isinstance(data['title'], str) or not data['title'].strip():
                return jsonify({'error': "Field 'title' must be a non-empty string"}), 400
            if len(data['title']) > 200:
                return jsonify({'error': "Field 'title' must be less than 200 characters"}), 400
            advertisement.title = data['title'].strip()
            
        if 'description' in data:
            if not isinstance(data['description'], str) or not data['description'].strip():
                return jsonify({'error': "Field 'description' must be a non-empty string"}), 400
            advertisement.description = data['description'].strip()
            
        if 'owner' in data:
            if not isinstance(data['owner'], str) or not data['owner'].strip():
                return jsonify({'error': "Field 'owner' must be a non-empty string"}), 400
            if len(data['owner']) > 100:
                return jsonify({'error': "Field 'owner' must be less than 100 characters"}), 400
            advertisement.owner = data['owner'].strip()

        db.session.commit()

        return jsonify(advertisement.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/advertisements/<int:ad_id>', methods=['DELETE'])
def delete_advertisement(ad_id):
    """
    Удаление объявления
    Возвращает статус 204 No Content при успешном удалении
    """
    try:
        advertisement = Advertisement.query.get(ad_id)

        if not advertisement:
            return jsonify({'error': f'Advertisement with id {ad_id} not found'}), 404

        db.session.delete(advertisement)
        db.session.commit()

        # Возвращаем 204 No Content без тела ответа
        return '', 204

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


# Дополнительный эндпоинт для получения всех объявлений
@app.route('/advertisements', methods=['GET'])
def get_all_advertisements():
    """
    Получение списка всех объявлений
    """
    try:
        advertisements = Advertisement.query.order_by(
            Advertisement.created_at.desc()
        ).all()

        return jsonify([ad.to_dict() for ad in advertisements]), 200

    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


# Безопасное создание таблиц при запуске
def init_db():
    """Инициализация базы данных безопасным способом"""
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
