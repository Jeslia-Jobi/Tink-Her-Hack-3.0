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
app.config['SESSION_COOKIE_NAME'] = 'echomood session'

# Spotify OAuth setup
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-top-read user-library-read playlist-modify-public playlist-read-private"
)

# Create a Spotipy client instance
sp = spotipy.Spotify(auth_manager=sp_oauth)
emotion_keywords = {
        "Happy":{"genres": ["upbeat", "dance", "pop"],"target_valence": 0.7, "target_energy": 0.6},
        "Relaxed":{"genres" : ["soft", "jazz", "indie"],"target_valence": 0.3, "target_energy": 0.3},
        "Angry": {"genres" : ["rock", "metal", "intense"], "target_valence": 0.8, "target_energy": 0.8},
        "Neutral":{"genres" : ["chill", "ambient"], "target_valence": 0.5, "target_energy": 0.4},
        "Sad":{ "genres": ["melancholy", "acoustic", "ballad"],"target_valence": 0.1, "target_energy": 0.2}
    }
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
    
# Emotion-based Spotify recommendations
def get_personalized_recommendations(sp, emotion):
    # Emotion-based keyword mapping
    emotion_params = emotion_keywords.get(emotion, emotion_keywords["Neutral"])
    try:
            # Fetch user's top tracks and artists
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')
        top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')

        # Extract seed values
        seed_tracks = [track['id'] for track in top_tracks['items']]
        seed_artists = [artist['id'] for artist in top_artists['items']]
        seed_genres = emotion_params['genres']

        # Ensure at least one seed is provided
        if not seed_tracks and not seed_artists and not seed_genres:
            raise ValueError("No valid seeds available for recommendations.")

        # Call Spotify recommendations API
        recommendations = sp.recommendations(
            seed_tracks=seed_tracks[:5],  # Spotify allows a max of 5 seeds
            seed_artists=seed_artists[:5],
            seed_genres=seed_genres[:5],
            limit=30,
            target_valence=emotion_params['target_valence'],
            target_energy=emotion_params['target_energy']
        )

        # Process recommendations
        return [
            {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'url': track['external_urls']['spotify']
            }
            for track in recommendations['tracks']
        ]
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return []

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
    emotion = session.get('emotion', 'Neutral') 
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info
    sp = spotipy.Spotify(auth=token_info['access_token'])
    try:
        # Reinitialize Spotify client with the token
        
        recommendations = get_personalized_recommendations(sp, emotion)
        # Retrieve emotion from the session
    

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
