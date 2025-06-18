import platform #platform: Used to detect the operating system (Windows, macOS, Linux).
import pyttsx3 #pyttsx3: Text-to-speech library that works offline
import speech_recognition as sr #speech_recognition: Captures and converts spoken words to text.
import eel #eel: Bridges Python with a frontend written in HTML/JS (used to update UI from Python).

# Initialize TTS engine based on OS
system_os = platform.system() #Gets the name of the operating system.
if system_os == "Windows": #Checks if the operating system is Windows.
    try: #
        engine = pyttsx3.init("sapi5") # Tries to initialize the pyttsx3 text-to-speech engine using the "sapi5" driver. sapi5 is the built-in Windows speech engine.
    except Exception: 
        print("sapi5 not available") # If "sapi5" is not available or fails, this block handles the error gracefully.
        engine = pyttsx3.init() # If the specified driver ("sapi5") fails, this line initializes the engine with the default driver.
elif system_os == "Darwin": 
    engine = pyttsx3.init("nsss") #On macOS, uses the nsss speech engine.
else:
    engine = pyttsx3.init()  # Linux or fallback

voices = engine.getProperty("voices") #Gets the available voices 
engine.setProperty("voice", voices[0].id) # and sets the first one.
engine.setProperty("rate", 174) # Sets the speaking rate (174 words per minute).

# Speak function with eel display
def speak(text): #
    text = str(text) # Converts text to a string
    eel.DisplayMessage(text) # displays the message in the assistant's chat area 
    engine.say(text) # Passes the text to the pyttsx3 engine for text-to-speech conversion.
    engine.runAndWait() # Starts speaking the prepared text and waits until it’s finished.
    eel.receiverText(text) #shows the spoken text in a different area of the UI 
@eel.expose #
# Speech recognition function
def takecommand(): #Makes this function callable from the frontend using eel.
    recognizer = sr.Recognizer() # Creates a recognizer object.
    try: #
        with sr.Microphone() as source: #Opens the microphone as the input source.
            print("I'm listening...") #
            eel.DisplayMessage("I'm listening...") #
            recognizer.pause_threshold = 1 #The recognizer will wait 1 second of silence before stopping the listening phase and considering the speech input complete.
            recognizer.adjust_for_ambient_noise(source) # Adjusts for background noise.
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8) #Maximum 10 seconds to start speaking.Maximum 8 seconds of speaking time.

        print("Recognizing...") #
        eel.DisplayMessage("Recognizing...") #
        query = recognizer.recognize_google(audio, language='en-US') #Uses Google's API to convert speech to text.
        print(f"User said: {query}") #
        eel.DisplayMessage(query) #
        return query.lower() #Prints, displays, and returns the recognized text in lowercase.


  
    except sr.WaitTimeoutError: # No speech (WaitTimeoutError)
        speak("I didn't hear anything.") #
    except sr.UnknownValueError: #Unclear speech (UnknownValueError)
        speak("Sorry, I didn't catch that.") #
    except Exception as e: #
        print(f"Error: {str(e)}") #
        speak("An error occurred while listening.") #

    return None #Returns None if something goes wrong.

# Main command processing function
@eel.expose 
def takeAllCommands(message=None): #Exposed to the frontend to process input either from voice or text box.
    try:
        query = message.lower() if message else takecommand() #If message is provided (from UI), convert to lowercase.Otherwise, call takecommand() to listen.
        if not query: #
            speak("I didn't catch that.") #
            return "no_query" #✅ Return a fallback response

        print(f"Processing: {query}") #
        eel.senderText(query) #Prints and displays the user's command in the chat UI.


        
        if "open" in query: #
            from backend.feature import openCommand #
            openCommand(query) #If the query includes "open", it calls openCommand() from your feature module to launch an app or URL.

        elif "send message" in query or "video call" in query or "call" in query: #If any one of these phrases is found in the query, the assistant will process it as a WhatsApp interaction.
            from backend.feature import findContact, whatsApp #Imports two helper functions from the backend.feature module:
            flag = "" #flag: To store the type of WhatsApp action (e.g., "message", "call", "video").
            msg = "" #msg: To store the actual message content (if it's a message).

            Phone, name = findContact(query) # Calls findContact() with the user’s query.
            if Phone != 0: #Checks if a valid phone number was returned by findContact(query).
                if "send message" in query: #If the command includes "send message":
                    flag = "message" #Sets flag to "message" to indicate a text message.
                    speak("What message do you want to send?") #Uses speak() to ask the user, “What message do you want to send?”
                    msg = takecommand() #Listens for the user’s reply using takecommand() and stores it in msg.
                elif "video call" in query:#
                    flag = "video" #If the query contains "video call", sets flag to "video".
                elif "call" in query: #
                     flag = 'call' #If the query includes "call" (but not “video call”), sets flag to 'call' for a normal voice call.

                if flag == "message" and not msg: # If the user intended to send a message, but didn’t say anything
                    speak("Message was not received. Cancelling.") 
                    return "message_cancelled"  # ✅ Added return

                whatsApp(Phone, msg, flag, name) #Calls the whatsApp() function to perform the action.

        elif "youtube" in query: #Plays a YouTube video based on the query.
            from backend.feature import playYoutube #
            playYoutube(query) #

        else:
            from backend.feature import chatBot #
            chatBot(query) #If the command doesn’t match known patterns, it is passed to the chatbot.
        return "success"  # ✅ Always return something if no exception

    except Exception as e: #
        print(f"An error occurred: {e}") #
        speak("Sorry, something went wrong.") #Catches any other errors and speaks an error message.


        return "error"  # ✅ Handle error case
    finally:
        eel.ShowHood() #Always call eel.ShowHood() at the end (likely a JS function to show/hide UI components).