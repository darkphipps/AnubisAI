import pyttsx3
import sqlite3
from dotenv import load_dotenv
import os
import textwrap
import speech_recognition as sr
import anpu_think


def speak(text, speaker_name=None):
    # Use pyttsx3 library to speak the text
    engine = pyttsx3.init()
    if speaker_name:
        voices = engine.getProperty('voices')
        for voice in voices:
            if speaker_name.lower() in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
    engine.say(text)
    engine.runAndWait()


def create_database():
    # Create or connect to the anpu_speech.db database
    conn = sqlite3.connect('anpu_speech.db')
    c = conn.cursor()

    # Create the 'voice_samples' table if it does not exist
    c.execute('''CREATE TABLE IF NOT EXISTS voice_samples (id INTEGER PRIMARY KEY AUTOINCREMENT, sample TEXT)''')

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()


def store_voice_sample(sample):
    # Connect to the anpu_speech.db database
    conn = sqlite3.connect('anpu_speech.db')
    c = conn.cursor()

    # Create the 'voice_samples' table if it does not exist
    c.execute('''CREATE TABLE IF NOT EXISTS voice_samples (id INTEGER PRIMARY KEY AUTOINCREMENT, sample TEXT)''')

    # Insert the voice sample into the 'voice_samples' table
    c.execute('INSERT INTO voice_samples (sample) VALUES (?)', (sample,))

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()


def train_voice_recognition():
    # Connect to the anpu_speech.db database
    conn = sqlite3.connect('anpu_speech.db')
    c = conn.cursor()

    # Retrieve all voice samples from the 'voice_samples' table
    c.execute('SELECT sample FROM voice_samples')
    samples = c.fetchall()

    # Create a new Recognizer instance and train it using the voice samples
    r = sr.Recognizer()
    for sample in samples:
        r.dynamic_energy_threshold = False
        r.adjust_for_ambient_noise(sr.AudioData(sample[0], sample_rate=44100, sample_width=2))
        r.dynamic_energy_threshold = True
        with sr.AudioFile(sample[0]) as source:
            audio = r.record(source)
        r.recognize_google(audio)

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()


def get_input():
    # Create or connect to the anpu_speech.db database
    conn = sqlite3.connect('anpu_speech.db')
    c = conn.cursor()

    # Retrieve the user's voice sample with the highest ID
    c.execute('SELECT sample FROM voice_samples ORDER BY id DESC LIMIT 1')
    result = c.fetchone()

    # Close the database connection
    conn.close()

    return result[0] if result else None


def speak_response(response, persona_name="Anubis", mode="text", wrap_length=80, speaker_name=None):
    """
    Speak the response using text-to-speech or print it to the console.

    :param response: The response to be spoken or printed

    :param response: The response to be spoken or printed.
    :param persona_name: The name of the persona to use when speaking.
    :param mode: The mode to use when responding. Either "text" or "voice".
    :param wrap_length: The maximum length of each line when wrapping text.
    """
    if mode == "text":
        wrapped_response = textwrap.fill(response, wrap_length)
        print(f"{persona_name}: {wrapped_response}")
    elif mode == "voice":
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        speaker_name = persona_name
        for voice in voices:
            if persona_name.lower() in voice.name.lower():
                speaker_name = voice.name
                engine.setProperty('voice', voice.id)
                break
        wrapped_response = textwrap.fill(response, wrap_length)
        engine.say(wrapped_response)
        engine.runAndWait()


if __name__ == "__main__":
    # Load environment variables from a .env file
    load_dotenv()

    # Set the Google Speech Recognition API key


    # Set the Google Speech Recognition API key
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    # Create the 'voice_samples' table if it doesn't exist
    create_database()

    while True:
        user_input = listen()

        # Use Google Speech Recognition to convert the audio to text
        try:
            # Store the user's voice sample in the database for future training
            store_voice_sample(user_input)

            # Do the necessary processing based on user input
            # ...

        except Exception as e:
            print(f"Sorry, there was an error processing your input: {e}")
