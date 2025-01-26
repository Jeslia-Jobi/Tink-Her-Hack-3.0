# Tink-Her-Hack-3.0
# EchoMood 🎯


## Basic Details
### Team Name: Tech Divas


### Team Members
- Member 1: Nandana P A- Muthoot Institute of Technology and Science 
- Member 2: Jeslia Jobi- Muthoot Institute of Technology and Science 
- Member 3: Parvathi Krishna- Muthoot Institute of Technology and Science 

### Project Description
EchoMood is a web app that recommends music based on your emotions. It uses Flask for the backend and TextBlob for sentiment analysis. Users type a sentence describing their mood, and the app suggests songs from a local database or Spotify. Personalized recommendations are available via Spotify login.

### The Problem statement
Traditional music recommendation systems lack the ability to adapt dynamically to a user’s real-time emotional state. They often rely on historical listening patterns, which may not align with how the user currently feels. This limitation creates a gap for users seeking emotionally resonant music in the moment.

### The Solution
This project offers an Emotion-Based Music Recommendation System, a web application that detects a user’s mood through text input and recommends songs tailored to their emotions. By integrating a local music dataset and Spotify’s API, the system delivers personalized playlists dynamically matched to the user’s detected emotional state (e.g., Happy, Sad, Neutral, Angry). It provides a seamless user experience and bridges the gap between emotional needs and music discovery.

## Technical Details
### Technologies/Components Used
For Software:
- **Languages used :** Python, HTML, CSS
- **Frameworks used :** Flask
- **Libraries used :** Spotipy, TextBlob, Pandas, os, jsonify, Session
- **Tools used :** Sotipy Developer Dashboard, Text Editor/IDE, Python Package Manager


### Implementation
1.**Emotion Detection :**

-Analyzes user input text using TextBlob for sentiment analysis.
-Detects emotions such as Happy, Sad, Neutral, and Angry.

2.**Music Recommendation :** 

-Uses a local music dataset (music_data.csv) to recommend songs based on emotions.
-Integrates with the Spotify API to fetch personalized playlists dynamically.

3.**Web Application :**

-Developed using Flask to provide a seamless user interface for input, authentication, and recommendations.
-Renders dynamic HTML templates (index.html, recommendations.html).

4.**Spotify Integration :**

-Implements OAuth 2.0 authentication to log in users via Spotify.
-Retrieves personalized song recommendations through Spotify's API.

4.**Session Handling :**

-Stores detected emotions and user authentication details in the Flask session for streamlined flow across routes.

# Installation
1. pip install flask spotipy textblob pandas
2. music_data.csv
3. Client ID, Client Secret, and configure the Redirect URI from Spotify Development Dashboard


# Run
python app.py 

# Screenshots (Add at least 3)
![Screenshot1](Add screenshot 1 here with proper name)
Add caption explaining what this shows

![Screenshot2](Add screenshot 2 here with proper name)
Add caption explaining what this shows

![Screenshot3](Add screenshot 3 here with proper name)
Add caption explaining what this shows

# File Structure
![Workflow](Add your workflow/architecture diagram here)


# Build Photos
![Team](Add photo of your team here)


![Components](Add photo of your components here)
List out all components shown

![Build](Add photos of build process here)
Explain the build steps

![Final](Add photo of final product here)
Explain the final build

### Project Demo
# Video
[Add your demo video link here]
Explain what the video demonstrates

# Additional Demos
[Add any extra demo materials/links]



---
Made with ❤ at TinkerHub
