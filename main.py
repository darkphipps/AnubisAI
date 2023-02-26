import anpu_talk
import anpu_listen
import textwrap
import anpu_speak

def get_user_input():
    """
    Gets user input either through speech recognition or text input,
    depending on the current mode.
    """
    global mode

    if mode == "s":
        # Listen for speech input
        while True:
            user_input = anpu_listen.listen()
            if user_input is None:
                # If no speech is detected, return an empty string
                return ""
            elif "type" in user_input:
                # Switch to text input mode if the user says "type"
                print("Switching to text input mode...")
                mode = "t"
                return input("Enter your message: ")
            else:
                return user_input
    else:
        # Get input from the user using text input
        return input("Enter your message: ")


def speak_response(response):
    """
    Speaks the response out loud or prints it to the console,
    depending on the current output mode.
    """
    global mode

    if mode == "s":
        print("Anubis: " + textwrap.fill(response, width=100))
        anpu_speak.speak(response)
    else:
        print("Anubis: " + textwrap.fill(response, width=100))


# Prompt the user to select a mode of input
while True:
    mode = input("Enter 's' to use speech recognition, or 't' to type your input: ")
    if mode == "s" or mode == "t":
        break
    else:
        print("Invalid input. Please enter 's' or 't'.")

if mode == "s":
    output_format = "voice"
else:
    output_format = "text"

if __name__ == "__main__":
    while True:
        # Get input from user using the selected input mode
        user_input = get_user_input()

        # Pass the user input to the AnpuTalk function and get the response
        response = anpu_talk.anpu_talk(user_input, return_output=True)

        # Speak or print the response based on the selected output format
        if not user_input:
            # If user_input is empty, skip the response and ask for input again
            continue
        elif not response:
            print("Anubis: Sorry, I couldn't understand what you said.")
        else:
            speak_response(response)
