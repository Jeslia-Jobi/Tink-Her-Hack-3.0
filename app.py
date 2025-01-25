from flask import Flask, request, jsonify
import librosa
import numpy as np
import pandas as pd
from textblob import TextBlob

app = Flask(__name__)

# Load your dataset (music data with features)
music_data = pd.read_csv('music_data.csv')

# Function to extract audio features
def extract_audio_features(audio_file):
    y, sr = librosa.load(audio_file)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    energy = np.mean(librosa.feature.rms(y=y))
    return {"tempo": tempo, "energy": energy}

# Emotion detection based on audio features
def detect_emotion(features):
    if features["energy"] > 0.5 and features["tempo"] > 120:
        return "Happy"
    elif features["energy"] < 0.3 and features["tempo"] < 90:
        return "Sad"
    else:
        return "Calm"

# Song recommendations based on emotion
def recommend_songs(emotion):
    recommendations = music_data[music_data['emotion'] == emotion]
    return recommendations[['title', 'artist']].to_dict(orient='records')

# Route for emotion prediction from uploaded audio
@app.route('/predict_emotion', methods=['POST'])
def predict_emotion():
    audio_file = request.files['audio']
    features = extract_audio_features(audio_file)
    emotion = detect_emotion(features)
    return jsonify({'emotion': emotion})

# Route for getting song recommendations based on emotion
@app.route('/recommend', methods=['GET'])
def recommend():
    emotion = request.args.get('emotion')
    recommendations = recommend_songs(emotion)
    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True)
