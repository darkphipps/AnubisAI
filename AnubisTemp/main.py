import anpu_talk
import anpu_speak

if __name__ == "__main__":
    while True:
        # Get input from user using speech recognition
        user_input = anpu_speak.listen()

        # Pass the user input to the AnpuTalk function and get the response
        response = anpu_talk.anpu_talk(user_input, return_output=True)

        # Speak the response using speech synthesis
        anpu_speak.speak(response)

        # Print the response to the console
        print("Anubis: " + response)
