import os
from PIL import Image
import requests
from datetime import datetime
import time

REQUESTS_PER_MINUTE_LIMIT = 3

def fetch_image_from_dalle(prompt, api_key):
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json={'prompt': prompt, 'n': 1})
    # print(response.json())
    if response.status_code == 200:
        try:
            image_url = response.json()['data'][0]['url']
            image_data = requests.get(image_url).content
            return image_data, None
        except (KeyError, IndexError):
            return None, f"Image URL not found or response structure unexpected for prompt: {prompt}"
    elif response.status_code == 402:  # Billing hard limit reached
        return None, prompt
    elif response.status_code == 429:  # Rate limit reached
        print("Rate limit reached. Waiting for a minute...")
        time.sleep(60)  
        return fetch_image_from_dalle(prompt, api_key)  
    else:
        print("Error response JSON:", response.json())
        raise Exception(f"API Error: {response.text}")

def save_image(image_content, path):
    with open(path, 'wb') as f:
        f.write(image_content)

def generate_and_save_images(food_names, output_dir, api_key):
    success_list = []
    failure_list = []
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for food in food_names:
        print(f"Generating image for {food}...")
        try:
            image_data, failed_food = fetch_image_from_dalle(food, api_key)
            if image_data:
                success_list.append(food)
                base_path = os.path.join(output_dir, f"{food}.png")
                save_image(image_data, base_path)
                print(f"Image generated for {food} successfully.")
            elif failed_food:
                failure_list.append(failed_food)
        except Exception as e:
            failure_list.append(failed_food)
            print(f"Error generating image for {food}: {str(e)}")
    return success_list, failure_list

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    input_str = input("Enter a list of food items, separated by commas: ")
    food_names = [name.strip() for name in input_str.split(',')]

    parent_dir = "generated_images"

    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    output_dir = os.path.join(parent_dir, f'generated_images_{timestamp}')
    
    formats = ['png', 'jpg']
    selected_format = input("Enter the file type to generate (png or jpg): ").lower() 
    if selected_format not in formats:
        print("Invalid file type selected. Defaulting to PNG.")
        selected_format = 'png'
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key is None:
        raise ValueError("API key is not set in the environment variables")
    else:
        print("API key found!")

    success, failure = generate_and_save_images(food_names, output_dir, api_key)
    
    if success:
        print("Images successfully generated for:", success)
    if failure:
        failure = [item for item in failure if item is not None]
        if failure:
            print("Images not generated due to billing limit:", failure)

    for food in success:
        base_path = os.path.join(output_dir, f"{food}.png")
        img = Image.open(base_path)
        output_path = base_path.replace('.png', f'.{selected_format}')
        img.save(output_path, format=selected_format.upper())
