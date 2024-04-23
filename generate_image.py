import os
from PIL import Image
import requests
from datetime import datetime
import time

REQUESTS_PER_MINUTE_LIMIT = 3

def fetch_image_from_dalle(prompt):
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key is None:
        raise ValueError("API key is not set in the environment variables")
    else:
        print("API key found!")
    """Fetch an image from an API based on a text prompt."""
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json={'prompt': prompt, 'n': 1})
    if response.status_code == 200:
        image_data = response.json()['data'][0]['image']
        return image_data, None
    elif response.status_code == 402:  # Billing hard limit reached
        return None, prompt
    elif response.status_code == 429:  # Rate limit reached
        print("Rate limit reached. Waiting for a minute...")
        time.sleep(60)  
        return fetch_image_from_dalle(prompt)  
    else:
        raise Exception(f"API Error: {response.text}")

def save_image(image_content, path):
    """Save image to a file."""
    with open(path, 'wb') as f:
        f.write(image_content)

def convert_image_format(source_path, output_format):
    """Convert image to a different format."""
    img = Image.open(source_path)
    output_path = source_path.replace('.png', f'.{output_format}')
    img.save(output_path, output_format.upper())

def generate_and_save_images(food_names, output_dir, formats=['png', 'jpg', 'heic']):
    """Generate and save images for a list of food names."""
    success_list = []
    failure_list = []
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for food in food_names:
        print(f"Generating image for {food}...")
        try:
            image_data, failed_food = fetch_image_from_dalle(food)
            if image_data:
                base_path = os.path.join(output_dir, f"{food}.png")
                save_image(image_data, base_path)
                for format in formats:
                    if format != 'png':
                        convert_image_format(base_path, format)
                success_list.append(food)
            elif failed_food:
                failure_list.append(failed_food)
                break
        except Exception as e:
            print(f"Error generating image for {food}: {str(e)}")
    return success_list, failure_list

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f'generated_images_{timestamp}'
    input_str = input("Enter a list of food items, separated by commas: ")
    food_names = [name.strip() for name in input_str.split(',')]
    success, failure = generate_and_save_images(food_names, output_dir)
    print("Images successfully generated for:", success)
    print("Images not generated due to billing limit:", failure)
