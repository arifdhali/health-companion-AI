import os
import base64
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv
from config import client 

load_dotenv()

# STATIC USER PROFILE (can be fetched from DB/frontend in real app)
DEFAULT_PROFILE = {
    "goals": "Lose 10 pounds in 3 months, improve cardiovascular health",
    "conditions": "None",
    "routines": "30-minutes walk 3x/week",
    "preferences": "Vegetarian, prefers low-impact exercises",
    "restrictions": "No high-intensity workouts due to knee pain"
}

# ------------------ PROMPT BUILDERS ------------------

def building_prompt(user_question=None):
 
    prompt = f"""
    You are a Healthy Companion AI.
    Here is the user profile:

    - Goals: {DEFAULT_PROFILE["goals"]}
    - Conditions: {DEFAULT_PROFILE["conditions"]}
    - Routines: {DEFAULT_PROFILE["routines"]}
    - Preferences: {DEFAULT_PROFILE["preferences"]}
    - Restrictions: {DEFAULT_PROFILE["restrictions"]}

    Based on this, provide a helpful response.
    You should give a title like "Health Information By Arif Dhali" at the top.
    """
    if user_question:
        prompt += f"\nUser's Question: {user_question}"
    return prompt

def building_prompt_for_image():
    """
    Builds an AI prompt ONLY for nutrition info from an image.
    """
    return """
    You are a Healthy Companion AI.
    Analyze the provided image and provide ONLY the nutritional information
    such as calories, protein, fat, carbs, vitamins, and other relevant nutrients.
    You should give a title like "Nutritional Information By Arif Dhali" at the top.
    Do NOT include any general advice, goals, or routines.
    """


def image_to_base64(image_path):
  
    with open(image_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode('utf-8')
    return b64


def get_gemini_response(input_prompt, image_path=None, downloadable=False):
 
    model = os.getenv("MODEL_NAME")
    
    content = [
        {
            "role": "user",
            "parts": [{"text": input_prompt}]
        }
    ]

    if image_path:
        base64String = image_to_base64(image_path)
        ext = os.path.splitext(image_path)[1].lower()
        if ext in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif ext == ".png":
            mime_type = "image/png"
        else:
            mime_type = "image/*"

        content[0]["parts"].append({
            "inline_data": {"data": base64String, "mime_type": mime_type}
        })

    try:
        response = client.models.generate_content(model=model, contents=content)
        response_data = response.candidates[0].content
        text_response = response_data.parts[0]
        print("\nAI Response:\n", text_response.text)

        if downloadable and text_response:
            isFileGenerated = download_response(text_response.text)
            print(f"Is file generated? {isFileGenerated}")

        return text_response.text

    except Exception as e:
        print("Error:", e)
        return "Sorry, I am unable to process your request at the moment."

def get_gemini_nutrition(image_path):

    prompt = building_prompt_for_image()
    return get_gemini_response(prompt, image_path=image_path, downloadable=True)



def download_response(response_text):
  
    file_name = datetime.today().strftime("%d-%m-%y") + "_ai_response.txt"
    with open(file_name, "w") as download_file:
        download_file.write(response_text)
    return True



def main():
    print("Choose an option:\n1. General health/fitness question\n2. Nutrition analysis from image")
    choice = input("Enter 1 or 2: ")

    if choice == "1":
        userinput = input("Enter your health and fitness question: ")
        build_prompt = building_prompt(userinput)
        get_gemini_response(build_prompt, downloadable=True)

    elif choice == "2":
        image_path = input("Enter the path of the food image: ")
        get_gemini_nutrition(image_path)

    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
