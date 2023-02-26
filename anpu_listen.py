import sqlite3
import speech_recognition as sr
import winsound

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

def listen():
    # Load and play the input_ready.mp3 file to indicate that the microphone is listening
    winsound.PlaySound("input_ready.mp3", winsound.SND_FILENAME)

    # Use speech_recognition library to record audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        audio = r.listen(source)

    # Use Google Speech Recognition to convert the audio to text
    try:
        user_input = r.recognize_google(audio)

        # Store the user's voice sample in the database for future training
        store_voice_sample(user_input)

        return user_input
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Sorry, could not request results from Google Speech Recognition service; {e}")

if __name__ == '__main__':
    while True:
        user_input = listen()
        print(f"You said: {user_input}")
