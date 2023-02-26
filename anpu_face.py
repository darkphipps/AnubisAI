import pyttsx3
import os
import pygame
import time
import anpu_talk

# Initialize the TTS engine
engine = pyttsx3.init()

# Set the voice to use
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # Use the second voice (index 1)

# Set the speech rate
rate = engine.getProperty('rate')
engine.setProperty('rate', 180) # Increase the rate to speed up the speech

# Define a function to speak the text using the TTS engine
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Define a function to synthesize speech using the speech synthesis engine
def synthesize_speech(text, filename):
    # Set the speech synthesis command
    command = f"espeak -w {filename} '{text}'"

    # Call the speech synthesis command
    os.system(command)

# Define a function to play the audio file and animate the virtual character's mouth
def play_audio(filename, image, x, y):
    # Load the audio file
    pygame.mixer.init()
    sound = pygame.mixer.Sound(filename)

    # Play the audio file and animate the virtual character's mouth
    sound.play()
    for i in range(10):
        image.blit(mouth_images[i], (x, y))
        pygame.display.flip()
        time.sleep(0.1)
    sound.stop()

# Load the images for the virtual character and mouth animation
character_image = pygame.image.load("FatesMouthClosed.png")
mouth_images = [pygame.image.load(f"FatesMouthOpen.png") for i in range(10)]

# Set the screen resolution and display the character image
pygame.init()
screen = pygame.display.set_mode((800, 600))
screen.blit(character_image, (0, 0))
pygame.display.flip()

# Get input from the user and speak the response
while True:
    # Get input from the user
    user_input = input("Enter your message: ")

    # Generate the AI response
    response = anpu_talk.anpu_talk(user_input, return_output=True)

    # Speak the response using the TTS engine
    speak(response)

    # Synthesize the speech and play the audio file with mouth animation
    synthesize_speech(response, "output.wav")
    play_audio("output.wav", character_image, 300, 200)
