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
    # List of keywords to trigger specific emotions
    sad_keywords = ['sad', 'down', 'unhappy', 'blue','lonely','fell','break']
    angry_keywords = ['angry', 'mad', 'furious', 'rage','frustrated','irritated','annoyed']
    happy_keywords = ['happy', 'joyful', 'cheerful', 'excited','love']
    
    # Convert text to lowercase to make keyword matching case-insensitive
    text_lower = text.lower()
    
    # Check for specific keywords in the text first
    if any(keyword in text_lower for keyword in sad_keywords):
        return "Sad"
    elif any(keyword in text_lower for keyword in angry_keywords):
        return "Angry"
    elif any(keyword in text_lower for keyword in happy_keywords):
        return "Happy"
    
    # If no specific keywords found, perform sentiment analysis
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity  # Returns a float between -1 and 1
    
    # Sentiment classification based on polarity
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
@app.route('/recommend_spotify')
@app.route('/recommend_spotify')
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

        songs = []
        for track in search_results['tracks']['items']:
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            song_url = track['external_urls']['spotify']

            # Append the song details to the list
            songs.append({
                'name': song_name,  # Add song name here
                'artist': artist_name,  # Add artist name here
                'url': song_url
            })

        # Render the recommendations template with songs
        return render_template('recommendations.html', songs=songs, emotion=emotion)
    except Exception as e:
        return f"Error fetching Spotify recommendations: {e}"




# Route to get song recommendations based on emotion
@app.route('/recommend_emotion/<emotion>', methods=['GET'])
@app.route('/recommend_emotion/<emotion>', methods=['GET'])
def recommend_emotion(emotion):
    # Get song recommendations for the detected emotion
    recommendations = recommend_songs(emotion)
    
    # Ensure the recommendation includes both song name and artist
    songs = [
        {'name': song['title'], 'artist': song['artist'], 'url': song['url']}
        for song in recommendations
    ]
    
    # Return the list of recommended songs to the user, passing the emotion to the template
    return render_template('recommendations.html', songs=songs, emotion=emotion)

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
@app.route("/callback")
def callback():
    try:
        # Get the token from the URL parameter 'code'
        token_info = sp_oauth.get_access_token(request.args.get('code'))
        if not token_info:
            return "Error fetching token from Spotify", 400
        
        # Store token info in the session
        session["token_info"] = token_info
        print("Token received:", token_info)  # Debug: print token

        # Redirect to the recommend_spotify route after successful login
        return redirect(url_for("recommend_spotify"))
    except Exception as e:
        return f"Error during Spotify login: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
