import os

from flask import Flask, abort, request, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker

import models
from models import Base

DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base.query = db_session.query_property()

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 404

    def __init__(self, error, status_code=None, payload=None):
        super().__init__(self)
        self.error = error
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.error
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# Zad5.2
# Stwórz endpoint /longest_tracks, który zwróci listę 10 wierszy z tabeli (reprezentowanych jako słowniki) `track`
# w formacie json, który reprezentują top 10 najdłuższych utworów w bazie w kolejności od najdłuższego do najkrótszego
# (pole milliseconds).
#
# UWAGA: podczas konstruowania słownika z bazodanowego obiektu należy zrzutować wszystkie wartości pól do stringa.
#
# Przykładowy format odpowiedzi:
#
# [{"album_id":"1","bytes":"11170334","composer":"Angus Young, Malcolm Young, Brian Johnson","genre_id":"1",
# "media_type_ id":"1","milliseconds":"343719","name":"For Those About To Rock (We Salute You)","track_id":"1",
# "unit_price":"0.99"}, {"album_id":"2","bytes":"5510424","composer":"None","genre_id":"1","media_type_id":"2",
# "milliseconds":"342562", "name":"Balls to the Wall","track_id":"2","unit_price":"0.99"},{"album_id":"3",
# "bytes":"3990994", "composer":"F. Baltes, S. Kaufman, U. Dirkscneider & W. Hoffman","genre_id":"1",
# "media_type_id":"2", "milliseconds":"230619","name":"Fast As a Shark","track_id":"3","unit_price":"0.99"},
# {"album_id":"3", "bytes":"4331779","composer":"F. Baltes, R.A. Smith-Diesel, S. Kaufman, U. Dirkscneider & W.
# Hoffman","genre_id":"1", "media_type_id":"2","milliseconds":"252051","name":"Restless and Wild","track_id":"4",
# "unit_price":"0.99"}, {"album_id":"3","bytes":"6290521","composer":"Deaffy & R.A. Smith-Diesel","genre_id":"1",
# "media_type_id":"2", "milliseconds":"375418","name":"Princess of the Dawn","track_id":"5","unit_price":"0.99"},
# {"album_id":"1","bytes":"6713451","composer":"Angus Young, Malcolm Young, Brian Johnson","genre_id":"1",
# "media_type_id":"1","milliseconds":"205662","name":"Put The Finger On You","track_id":"6","unit_price":"0.99"},
# {"album_id":"1","bytes":"7636561","composer":"Angus Young, Malcolm Young, Brian Johnson","genre_id":"1",
# "media_type_id":"1","milliseconds":"233926","name":"Let's Get It Up","track_id":"7","unit_price":"0.99"},
# {"album_id":"1","bytes":"6852860","composer":"Angus Young, Malcolm Young, Brian Johnson","genre_id":"1",
# "media_type_id":"1","milliseconds":"210834","name":"Inject The Venom","track_id":"8","unit_price":"0.99"},
# {"album_id":"1","bytes":"6599424","composer":"Angus Young, Malcolm Young, Brian Johnson","genre_id":"1",
# "media_type_id":"1","milliseconds":"203102","name":"Snowballed","track_id":"9","unit_price":"0.99"},
# {"album_id":"1","bytes":"8611245","composer":"Angus Young, Malcolm Young, Brian Johnson","genre_id":"1",
# "media_type_id":"1","milliseconds":"263497","name":"Evil Walks","track_id":"10","unit_price":"0.99"}]
@app.route("/longest_tracks")
def longest_tracks():
    tracks = db_session.query(models.Track).order_by(models.Track.milliseconds.desc()).limit(10)
    print(tracks)
    result_dict = []
    for u in tracks.all():
        result_dict.append(u.__dict__)
    for i in result_dict:
        del i['_sa_instance_state']
        dic = list(i.keys())
        for di in dic:
            i[di] = str(i[di])
    return jsonify(result_dict)


# Zad5.3 Stwórz endpoint `/longest_tracks_by_artist` który zachowuje się tak samo jak poprzedni, ale dodatkowo
# przekazuje parametr `?artist=<artist>` i zwraca w jsonie listę z 10cioma najdłuższymi utworami (tj z ich
# reprezentacją w formacie json) danego wykonawcy. Jeśli wykonawcy nie ma bazy proszę zwrócić status 404.
#
# UWAGA: podczas konstruowania słownika z bazodanowego obiektu należy zrzutować wszystkie wartości pól do stringa.
#
# Przykład:
#
# request GET - http://my_heroku_app.com/longest_tracks_by_artist?artist=Aerosmith
#
# response - [{"album_id":"5","bytes":"12374569","composer":"Steven Tyler, Joe Perry, Mark Hudson","genre_id":"1",
# "media_type_id":"1","milliseconds":"381231","name":"Livin' On The Edge","track_id":"37","unit_price":"0.99"},
# {"album_id":"5","bytes":"11616195","composer":"Steven Tyler, Richie Supa","genre_id":"1","media_type_id":"1",
# "milliseconds":"356519","name":"Amazing","track_id":"30","unit_price":"0.99"},{"album_id":"5","bytes":"10869391",
# "composer":"Steven Tyler, Tom Hamilton","genre_id":"1","media_type_id":"1","milliseconds":"330736","name":"Janie's
# Got A Gun","track_id":"28","unit_price":"0.99"},{"album_id":"5","bytes":"10552051","composer":"Steven Tyler,
# Joe Perry","genre_id":"1","media_type_id":"1","milliseconds":"321828","name":"Love In An Elevator","track_id":"24",
# "unit_price":"0.99"},{"album_id":"5","bytes":"10402398","composer":"Steven Tyler, Joe Perry, Desmond Child",
# "genre_id":"1","media_type_id":"1","milliseconds":"316656","name":"Crazy","track_id":"34","unit_price":"0.99"},
# {"album_id":"5","bytes":"10144730","composer":"Steven Tyler, Joe Perry, Desmond Child","genre_id":"1",
# "media_type_id":"1","milliseconds":"310622","name":"What It Takes","track_id":"26","unit_price":"0.99"},
# {"album_id":"5","bytes":"10056995","composer":"Steven Tyler, Joe Perry, Taylor Rhodes","genre_id":"1",
# "media_type_id":"1","milliseconds":"309263","name":"Cryin'","track_id":"29","unit_price":"0.99"},{"album_id":"5",
# "bytes":"9989331","composer":"Steven Tyler, Desmond Child","genre_id":"1","media_type_id":"1",
# "milliseconds":"307617","name":"Angel","track_id":"36","unit_price":"0.99"},{"album_id":"5","bytes":"9719579",
# "composer":"Steven Tyler, Joe Perry, Jack Blades, Tommy Shaw","genre_id":"1","media_type_id":"1",
# "milliseconds":"295680","name":"Walk On Water","track_id":"23","unit_price":"0.99"},{"album_id":"5",
# "bytes":"8679940","composer":"Steven Tyler, Joe Perry, Desmond Child","genre_id":"1","media_type_id":"1",
# "milliseconds":"264855","name":"Dude (Looks Like A Lady)","track_id":"27","unit_price":"0.99"}]
@app.route("/longest_tracks_by_artist")
def longest_tracks_by_artist():
    a = request.args
    if 'artist' in a:
        art = a['artist']
    else:
        abort(404)

    try:
        tracks = db_session.query(models.Track).join(models.Track.album).join(models.Album.artist).filter(
            models.Artist.name == art).order_by(models.Track.milliseconds.desc()).limit(10).all()
        result_dict = []
        for u in tracks:
            result_dict.append(u.__dict__)
        for i in result_dict:
            del i['_sa_instance_state']
            dic = list(i.keys())
            for di in dic:
                i[di] = str(i[di])

        if len(result_dict) == 0:
            abort(404)

    except:
        abort(404)

    return jsonify(result_dict)


# Zad5.4
# Dodaj endpoint `artists` wg poniższej specyfikacji:
#
# - możliwość dodawania nowych artystów (POST JSON)
# - stworzenie nowego obiektu powinno objawić się zwróconym kodem 200
# - niestworzenie obiektu powinno objawić się zwróconym kodem 400
#
# UWAGA: podczas konstruowania słownika z bazodanowego obiektu należy zrzutować wszystkie wartości pól do stringa.
#
# Przykładowy POST:
# {
#     "name": "Madonna"
# }
# Przykładowa odpowiedź z sukcesem:
# {
#     "artist_id": "1488",
#     "name": "Madonna"
# }
#
# Protip: zamiast pisać ify sprawdzające czy json na pewno zawiera to co trzeba dużo wygodniej posłużyć się jakimś
# walidatorem - np Schema, Cerberus
#
# linki - http://docs.python-cerberus.org/en/stable/ i https://github.com/keleshev/schema
@app.route("/artists", methods=["POST"])
def artists():
    if request.method == "POST":
        return post_artists()
    abort(404)


def post_artists():
    data = request.json
    new_name = data.get("name")
    if new_name is None:
        abort(400)

    try:
        art = models.Artist(name=new_name)
        db_session.add(art)
        db_session.commit()

        artist = db_session.query(models.Artist).filter(models.Artist.name == new_name).with_for_update().one()
        result_dict = artist.__dict__
        print(result_dict)

        del result_dict['_sa_instance_state']
        dic = list(result_dict.keys())
        for di in dic:
            result_dict[di] = str(result_dict[di])

        return jsonify(result_dict)
    except:
        abort(400)


# Zad5.5
# Dodaj nowy endpoint '/count_songs', który przyjmuje requesty GET z parametrem `artist` i zwraca jsona w którym
# klucz to nazwa artysty lub artystów jeśli podano ich kilku, a wartości to ilość piosenek danego artysty. Więcej niż
# jeden artysta będzie podany w urlu w następujący sposób - `?artist=<artist_1>,<artist_2>,<artist_3>(...)<artist_n>
#
# Przykład:
# `/count_songs?artist=Aerosmith,AC/DC` powinien zwrócić jsona `{"AC/DC":18,"Aerosmith":15}`
#
# W przypadku gdy żadnego z podanych artystów nie ma w bazie lub gdy w querystringu nie podano żadnego artysty należy
# zwrócić 404.
@app.route("/count_songs")
def count_songs():
    a = request.args
    if 'artist' in a:
        art = str(a['artist'])
        art = art.split(",")

    else:
        abort(404)
    try:
        result_dict = {}
        songs = (
            db_session.query(models.Artist.name, func.count(models.Track.name))
                .join(models.Track.album)
                .join(models.Album.artist)
                .filter(models.Artist.name.in_(art))
                .group_by(models.Artist.name)
        )
        if len(songs.all()) == 0:
            abort(404)

        for u in songs.all():
            result_dict[u[0]] = u[1]

        return jsonify(result_dict)
    except:
        abort(404)


if __name__ == "__main__":
    app.run(debug=False)
