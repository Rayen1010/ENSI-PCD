from red_text_detector_with_Paddle_OCR import RedTextDetector  # Import the original class
from fuzzywuzzy import fuzz  # For fuzzy matching

# Define the list of valid words
VALID_WORDS = ["Spoon", "Bag", "Bottle of Water", "Cup", "Tennis Racket"]

def find_matching_valid_word(word, valid_words=VALID_WORDS, threshold=80):
    """
    Find the valid word that matches the extracted word using fuzzy matching.
    
    Args:
        word (str): The extracted word.
        valid_words (list): List of valid words to compare against.
        threshold (int): Minimum similarity score to consider a match (default: 80).
    
    Returns:
        str or None: The matching valid word if a match is found, otherwise None.
    """
    word_lower = word.lower()
    for valid_word in valid_words:
        valid_word_lower = valid_word.lower()
        # Use partial_ratio for better substring matching
        similarity_score = fuzz.partial_ratio(word_lower, valid_word_lower)
        if similarity_score >= threshold:
            return valid_word  # Return the valid word (not lowercase)
    return None  # No match found

# Update the VALID_WORDS dictionary to include prices
VALID_WORDS = {
    "Spoon": 2,
    "Bag": 50,
    "Bottle of Water": 0.9,
    "Cup": 10,
    "Tennis Racket": 100
}

def get_correct_words():
    """
    Find the first frame with red text, validate the extracted words,
    and return a dictionary of valid words with their prices.
    
    Returns:
        dict: Dictionary of valid words and their prices {item: price}.
    """
    try:
        # Initialize the RedTextDetector
        detector = RedTextDetector(frames_folder="analyze_frames")
        
        # Find the first frame with red text and extract the list of words
        frame_file, extracted_words = detector.find_first_frame_with_red_text()
        
        if not extracted_words:
            print("No red text detected in any frame.")
            return {}
        
        print(f"Extracted words from frame '{frame_file}': {extracted_words}")
        
        # Validate each word and collect the corresponding valid words with prices
        purchased_items = {}
        for word in extracted_words:
            matching_valid_word = find_matching_valid_word(word, VALID_WORDS.keys())
            if matching_valid_word:
                price = VALID_WORDS[matching_valid_word]
                purchased_items[matching_valid_word] = price
                print(f"✅ Correct word: {word} -> Valid word: {matching_valid_word} (Price: {price}dt)")
            else:
                print(f"❌ Incorrect word: {word}")
        
        # Print the final list of valid words with prices
        print(f"\nFinal purchased items: {purchased_items}")
        return purchased_items
    
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        return {}

if __name__ == "__main__":
    try:
        # Get the list of valid words
        valid_words = get_correct_words()
        print(f"Returned valid words: {valid_words}")
    except Exception as e:
        print(f"❌ System initialization failed: {str(e)}")