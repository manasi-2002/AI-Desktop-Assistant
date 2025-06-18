import re

def extract_yt_term(command):
    # Normalize to lowercase
    command = command.lower() #Converts the entire command to lowercase to make text processing case-insensitive (e.g., "Play" becomes "play").



    # Optional words before 'play', like 'please', 'can you', 'quickly', etc.
    command = re.sub(r'\b(please|can you|could you|quickly|kindly)\b', '', command)#Uses regex to remove polite/filler words that might precede the actual intent.

    # Match different ways of saying "play X on/in/from/at youtube"
    pattern = r'play\s+(.*?)\s+(on|in|from|at)\s+youtube'
    match = re.search(pattern, command)#This line tries to find a match for a regular expression pattern in the given command string.



    if match:
        return match.group(1).strip()#If a match is found, group(1) gives the part between "play" and "youtube" (the actual video name). .strip() removes extra spaces.


    
    # Fallback: if only 'play' and 'youtube' are present
    if "play" in command and "youtube" in command:
        command = command.replace("play", "").replace("youtube", "")
        return command.strip()

    return None
def remove_words(input_string, words_to_remove):#Defines a function that removes specific words (like filler or assistant name) from a sentence.
    words = input_string.split()
    filtered_words = [word for word in words if word.lower() not in words_to_remove]#Creates a new list with only those words that are not in the words_to_remove list.
    result_string=' '.join(filtered_words)
    return result_string
