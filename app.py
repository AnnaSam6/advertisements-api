from flask import Flask, request, jsonify
from models import db, Advertisement

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///advertisements.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)


@app.route('/advertisements', methods=['POST'])
def create_advertisement():
    """
    Создание нового объявления
    Ожидает JSON: {"title": "...", "description": "...", "owner": "..."}
    """
    try:
        data = request.get_json()

        # Валидация обязательных полей
        if not data or not all(key in data for key in ['title', 'description', 'owner']):
            return jsonify({
                'error': 'Missing required fields. Required: title, description, owner'
            }), 400

        # Создание объявления
        advertisement = Advertisement(
            title=data['title'],
            description=data['description'],
            owner=data['owner']
        )

        db.session.add(advertisement)
        db.session.commit()

        return jsonify(advertisement.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/advertisements/<int:ad_id>', methods=['GET'])
def get_advertisement(ad_id):
    """
    Получение объявления по ID
    """
    try:
        advertisement = Advertisement.query.get(ad_id)

        if not advertisement:
            return jsonify({'error': 'Advertisement not found'}), 404

        return jsonify(advertisement.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/advertisements/<int:ad_id>', methods=['PUT'])
def update_advertisement(ad_id):
    """
    Редактирование объявления
    Ожидает JSON с любыми полями для обновления
    """
    try:
        advertisement = Advertisement.query.get(ad_id)

        if not advertisement:
            return jsonify({'error': 'Advertisement not found'}), 404

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Обновление полей
        advertisement.update_from_dict(data)
        db.session.commit()

        return jsonify(advertisement.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/advertisements/<int:ad_id>', methods=['DELETE'])
def delete_advertisement(ad_id):
    """
    Удаление объявления
    """
    try:
        advertisement = Advertisement.query.get(ad_id)

        if not advertisement:
            return jsonify({'error': 'Advertisement not found'}), 404

        db.session.delete(advertisement)
        db.session.commit()

        return jsonify({'message': 'Advertisement deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Дополнительный эндпоинт для получения всех объявлений
@app.route('/advertisements', methods=['GET'])
def get_all_advertisements():
    """
    Получение списка всех объявлений
    """
    try:
        advertisements = Advertisement.query.order_by(
            Advertisement.created_date.desc()
        ).all()

        return jsonify([ad.to_dict() for ad in advertisements]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Создание таблиц при запуске
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
