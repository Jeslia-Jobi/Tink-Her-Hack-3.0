from flask import Flask, request, redirect, url_for, session, jsonify, render_template
import os
import librosa
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from textblob import TextBlob
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'

# Spotify OAuth setup
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-library-read playlist-modify-public"
)

# Create a Spotipy client instance
sp = spotipy.Spotify(auth_manager=sp_oauth)

# Sample song database (for demonstration)
music_data = pd.DataFrame({
    'title': ['Song A', 'Song B', 'Song C', 'Song D'],
    'artist': ['Artist 1', 'Artist 2', 'Artist 3', 'Artist 4'],
    'emotion': ['Happy', 'Sad', 'Calm', 'Happy'],
    'genre': ['Pop', 'Rock', 'Jazz', 'Pop'],
})

# Function to extract audio features
def extract_audio_features(audio_file):
    y, sr = librosa.load(audio_file)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    energy = np.mean(librosa.feature.rms(y=y))
    return {"tempo": tempo, "energy": energy}

# Emotion prediction based on audio features
def detect_emotion(features):
    if features["energy"] > 0.5 and features["tempo"] > 120:
        return "Happy"
    elif features["energy"] < 0.3 and features["tempo"] < 90:
        return "Sad"
    else:
        return "Calm"

# Function to recommend songs based on emotion
def recommend_songs(emotion):
    recommendations = music_data[music_data['emotion'] == emotion]
    return recommendations[['title', 'artist']].to_dict(orient='records')

# Route to handle emotion prediction
@app.route('/predict_emotion', methods=['POST'])
def predict_emotion():
    audio_file = request.files['audio']
    features = extract_audio_features(audio_file)
    emotion = detect_emotion(features)
    return jsonify({'emotion': emotion})

# Route to get song recommendations based on emotion
@app.route('/recommend', methods=['GET'])
def recommend():
    emotion = request.args.get('emotion')
    recommendations = recommend_songs(emotion)
    return jsonify({'recommendations': recommendations})

# Route to start Spotify authentication
@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Callback route after user grants permission on Spotify
@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect(url_for('recommend_spotify'))

# Route to recommend songs from Spotify
@app.route('/recommend_spotify')
def recommend_spotify():
    if not session.get("token_info"):
        return redirect(url_for("login"))

    token_info = session.get("token_info")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    # Use Spotify API to recommend songs based on the detected emotion (e.g., "Happy")
    emotion = "Happy"  # For demonstration
    if emotion == "Happy":
        results = sp.search(q='happy', type='track', limit=5)
    elif emotion == "Sad":
        results = sp.search(q='sad', type='track', limit=5)
    else:
        results = sp.search(q='calm', type='track', limit=5)

    tracks = results['tracks']['items']
    song_list = [{'name': track['name'], 'artist': track['artists'][0]['name'], 'url': track['external_urls']['spotify']} for track in tracks]

    return render_template('recommendations.html', songs=song_list)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
