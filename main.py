import anpu_talk
import anpu_speak
import textwrap

# Prompt the user to select a mode of input
while True:
    mode = input("Enter 's' to use speech recognition, or 't' to type your input: ")
    if mode == "s" or mode == "t":
        break
    else:
        print("Invalid input. Please enter 's' or 't'.")

if mode == "s":
    def get_user_input():
        return anpu_speak.listen()

    def speak_response(response):
        anpu_speak.speak(response)

    output_format = "voice"
else:
    def get_user_input():
        return input("Enter your message: ")

    def speak_response(response):
        print("Anubis: " + textwrap.fill(response, width=100))

    output_format = "text"

if __name__ == "__main__":
    while True:
        # Get input from user using the selected input mode
        user_input = get_user_input()

        # Pass the user input to the AnpuTalk function and get the response
        response = anpu_talk.anpu_talk(user_input, return_output=True)

        # Speak or print the response based on the selected output format
        if response is None:
            print("Anubis: Sorry, I couldn't understand what you said.")
        elif output_format == "voice":
            speak_response(response)
        else:
            print("Anubis: " + textwrap.fill(response, width=100))
