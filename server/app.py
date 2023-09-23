from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        messages_serialized = [message.to_dict() for message in messages]
        return jsonify(messages_serialized), 200
    elif request.method == 'POST':
        post = Message(
            body=request.form.get('body'),
            username=request.form.get('username'),
        )
        db.session.add(post)
        db.session.commit()

        post_dict = post.to_dict()
        response = make_response(
            jsonify(post_dict), 201
        )
        return response

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def update_or_delete_message(id):
    message = Message.query.get(id)

    if not message:
        response_body = {
            'error': 'Message not found',
        }
        return jsonify(response_body), 404

    if request.method == 'PATCH':
        new_body = request.form.get('body')
        message.body = new_body
        db.session.commit()

        updated_message = message.to_dict()

        response = make_response(
            jsonify(updated_message), 200
        )
        return response
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response_body = {
            'delete_successful': True,
            'message': 'Message deleted.',
        }
        response = make_response(
            jsonify(response_body), 200
        )
        return response

if __name__ == '__main__':
    app.run(port=5555)
