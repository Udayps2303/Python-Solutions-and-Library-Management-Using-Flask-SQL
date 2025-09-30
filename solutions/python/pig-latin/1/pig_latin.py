def translate(text):
    # 1. Split the input text into a list of individual words.
    words = text.split()
    
    # 2. Create an empty list to store the translated words.
    translated_words = []
    
    # 3. Loop through each word from the input text.
    for word in words:
        vowels = "aeiou"
        
        # --- Rule 1: Check if the word starts with a vowel sound. ---
        if word.startswith(('a', 'e', 'i', 'o', 'u', 'xr', 'yt')):
            # If it does, simply add "ay" to the end.
            translated_word = word + "ay"
        
        # --- Rules 2, 3, 4: The word starts with a consonant sound. ---
        else:
            # We need to find where the first consonant cluster ends.
            first_vowel_position = 0
            
            # Look at each letter to find the first vowel.
            for i, letter in enumerate(word):
                # Is the letter a vowel?
                if letter in vowels:
                    # Special "qu" Rule: If 'u' follows a 'q', it's part of the consonant sound.
                    if letter == 'u' and i > 0 and word[i-1] == 'q':
                        continue # Keep searching.
                    
                    # Otherwise, we've found our split point.
                    first_vowel_position = i
                    break # Stop this inner loop.
                    
                # Special "y" Rule: Treat 'y' as a vowel if it's not the first letter.
                if letter == 'y' and i > 0:
                    first_vowel_position = i
                    break # Stop this inner loop.
            
            # Slice the word into the start (consonants) and end (rest of the word).
            start_part = word[:first_vowel_position]
            end_part = word[first_vowel_position:]
            
            # Build the new Pig Latin word by rearranging the parts.
            translated_word = end_part + start_part + "ay"
        
        # Add the fully translated word to our list.
        translated_words.append(translated_word)
        
    # 4. Join the translated words back into a single string, separated by spaces.
    return " ".join(translated_words)