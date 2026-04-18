from flask import Flask, request, jsonify
from models import db, Advertisement
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///advertisements.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def validate_advertisement_data(data, is_update=False):
    """Валидация данных объявления"""
    if data is None:
        return False, "No JSON data provided"
    
    if not is_update:
        required_fields = ['title', 'description', 'owner']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
            if not isinstance(data[field], str):
                return False, f"Field '{field}' must be a string"
            if not data[field].strip():
                return False, f"Field '{field}' cannot be empty"
        
        if len(data['title']) > 200:
            return False, "Field 'title' must be less than 200 characters"
        if len(data['owner']) > 100:
            return False, "Field 'owner' must be less than 100 characters"
    
    return True, None


@app.route('/advertisements', methods=['POST'])
def create_advertisement():
    """Создание объявления - возвращает 201"""
    try:
        data = request.get_json(silent=True)
        
        is_valid, error = validate_advertisement_data(data, is_update=False)
        if not is_valid:
            return jsonify({'error': error}), 400

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
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/advertisements/<int:ad_id>', methods=['GET'])
def get_advertisement(ad_id):
    """Получение объявления - возвращает 200 или 404"""
    try:
        advertisement = db.session.get(Advertisement, ad_id)
        
        if not advertisement:
            return jsonify({'error': f'Advertisement with id {ad_id} not found'}), 404

        return jsonify(advertisement.to_dict()), 200

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/advertisements/<int:ad_id>', methods=['PUT'])
def update_advertisement(ad_id):
    """Редактирование объявления - возвращает 200 или 404"""
    try:
        advertisement = db.session.get(Advertisement, ad_id)
        
        if not advertisement:
            return jsonify({'error': f'Advertisement with id {ad_id} not found'}), 404

        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400

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
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/advertisements/<int:ad_id>', methods=['DELETE'])
def delete_advertisement(ad_id):
    """Удаление объявления - возвращает 204 БЕЗ ТЕЛА ОТВЕТА"""
    try:
        advertisement = db.session.get(Advertisement, ad_id)
        
        if not advertisement:
            return jsonify({'error': f'Advertisement with id {ad_id} not found'}), 404

        db.session.delete(advertisement)
        db.session.commit()
        
        # ВАЖНО: 204 No Content - пустой ответ без тела
        return '', 204

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@app.route('/advertisements', methods=['GET'])
def get_all_advertisements():
    """Получение всех объявлений"""
    try:
        advertisements = Advertisement.query.order_by(Advertisement.created_at.desc()).all()
        return jsonify([ad.to_dict() for ad in advertisements]), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# Создание таблиц
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
