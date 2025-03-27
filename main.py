from flask import Flask, jsonify, request
from flask.views import MethodView
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from models import Session, Posters
from schema import UpdatePost

app = Flask("poster_portal")

class HttpError(Exception):

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


def validate(schema_cls, json_data):
    try:
        schema_cls(**json_data).dict(exclude_unset=True)
    except ValidationError:
        raise HttpError(400, "some data is incorrect")


@app.errorhandler(HttpError)
def error_handler(HttpError):
    response = jsonify({'error': HttpError.message})
    response.starus_code = 409
    return response

@app.before_request
def before_requests():
    session = Session()
    request.session = session

@app.after_request
def after_request(http_response):
    request.session.close()
    return http_response

def get_post_by_id(poster_id):
    poster = request.session.get(Posters, poster_id)
    if poster is None:
            raise HttpError(404, f'post with {poster_id} id does not exist')
    return poster


class PostersView(MethodView):

    def get(self):
        raw_posters = request.session.query(Posters).all()
        posters = [raw_poster.dict for raw_poster in raw_posters]
        return jsonify(posters)
        
    def post(self):
        json_data = request.json
        poster = Posters(Title=json_data['Title'],
                        Description=json_data['Description'],
                        Owner=json_data['Owner'])
        request.session.add(poster)
        try: 
            request.session.commit()
        except IntegrityError:
            raise HttpError(409, 'post already exists')
        return jsonify(poster.dict)

posters_view = PostersView.as_view('posters')
app.add_url_rule('/posters/', view_func=posters_view, methods=['GET', 'POST',])

class OnePosterView(MethodView):

    def get(self, poster_id: int):
        poster = get_post_by_id(poster_id)
        return jsonify(poster.dict)
    
    def patch(self, poster_id: int):
        json_data = validate(UpdatePost, request.json)
        poster = get_post_by_id(poster_id)
        for field, value in json_data.items():
            setattr(poster, field, value)
            request.session.add(poster)
        try: 
            request.session.commit()
        except IntegrityError:
            raise HttpError(409, 'post already exists')
        return poster.dict

    def delete(self, poster_id: int):
        poster = get_post_by_id(poster_id)
        request.session.delete(poster)
        request.session.commit()
        return jsonify({'status': 'deleted'})

one_poster_view = OnePosterView.as_view('one_poster')
app.add_url_rule('/one_poster/<poster_id>/', view_func=one_poster_view, methods=['GET', 'PATCH', 'DELETE',])


if __name__ == '__main__':
    app.run()