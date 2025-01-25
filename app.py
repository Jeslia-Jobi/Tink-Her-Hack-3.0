from flask import Flask, request, redirect, url_for, session, jsonify, render_template
import os
import pandas as pd
from textblob import TextBlob
import spotipy
from spotipy.oauth2 import SpotifyOAuth
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

# Load the music data dynamically
music_data = pd.read_csv('music_data.csv')  # Ensure music_data.csv is in the same directory

# Sentiment analysis function
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity  # Returns a float between -1 and 1
    
    if sentiment > 0.2:
        return "Happy"  # Positive sentiment
    elif -0.2 <= sentiment <= 0.2:
        return "Neutral"  # Neutral to slight positive sentiment
    elif sentiment < -0.2 and sentiment > -0.5:
        return "Sad"  # Moderate negative sentiment
    elif sentiment <= -0.5:
        return "Angry"  # Strong negative sentiment
    else:
        return "Relaxed"  # Default for uncertain cases

# Function to recommend songs based on emotion
def recommend_songs(emotion):
    recommendations = music_data[music_data['emotion'].str.lower() == emotion.lower()]
    return recommendations[['title', 'artist', 'url']].to_dict(orient='records')

# Route to handle sentiment analysis based on text input
@app.route('/predict_emotion', methods=['POST'])
def predict_emotion():
    text_input = request.form['text']  # Get text input from form
    emotion = analyze_sentiment(text_input)
    return render_template('index.html', emotion=emotion)  # Pass emotion to the same page

@app.route('/recommend_spotify')
def recommend_spotify():
    # Check if the user has a valid Spotify session
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))

    try:
        # Reinitialize Spotify client with the token
        sp = spotipy.Spotify(auth=token_info['access_token'])

        # Retrieve emotion from the session
        emotion = session.get('emotion', 'Happy')  # Default to "Happy" if emotion is missing

        # Use Spotify API to search songs based on emotion
        search_results = sp.search(q=emotion.lower(), type='track', limit=10)
        songs = [
            {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'url': track['external_urls']['spotify']
            }
            for track in search_results['tracks']['items']
        ]

        # Render the recommendations template with songs
        return render_template('recommendations.html', songs=songs, emotion=emotion)
    except Exception as e:
        return f"Error fetching Spotify recommendations: {e}"


# Route to get song recommendations based on emotion
@app.route('/recommend_emotion/<emotion>', methods=['GET'])
def recommend_emotion(emotion):
    # Get song recommendations for the detected emotion
    recommendations = recommend_songs(emotion)
    
    # Return the list of recommended songs to the user, passing the emotion to the template
    return render_template('recommendations.html', songs=recommendations, emotion=emotion)

@app.route('/login')
def login():
    try:
        emotion = request.args.get('emotion', '')
        auth_url = sp_oauth.get_authorize_url()
        session['emotion'] = emotion  # Save emotion for use after Spotify login
        return redirect(auth_url)
    except Exception as e:
        return f"Error initiating Spotify login: {e}"
# Home route
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/callback")
def callback():
    try:
        token_info = sp_oauth.get_access_token(request.args.get('code'))
        session["token_info"] = token_info
        return redirect(url_for("recommend_spotify"))
    except Exception as e:
        return f"Error during Spotify login: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
