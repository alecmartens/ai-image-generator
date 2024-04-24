import os
from PIL import Image
import requests
from datetime import datetime
import time

REQUESTS_PER_MINUTE_LIMIT = 3

def fetch_image_from_dalle(prompt, api_key):
    """Fetch an image from an API based on a text prompt."""
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
    """Save image to a file."""
    with open(path, 'wb') as f:
        f.write(image_content)

def convert_image_format(source_path, output_format):
    if output_format == 'heic':
        heif_file = pyheif.read(source_path)
        img = Image.frombytes(
            heif_file.mode, 
            heif_file.size, 
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        output_path = source_path.replace('.png', '.heic')
        img.save(output_path, format='heic')
    else:
        img = Image.open(source_path)
        output_path = source_path.replace('.png', f'.{output_format}')
        img.save(output_path, format=output_format.upper())

def generate_and_save_images(food_names, output_dir, api_key):
    """Generate and save images for a list of food names."""
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
    
    formats = ['png', 'jpg', 'heic']
    selected_format = input("Enter the file type to generate (png or jpg): ").lower() # note heic is not currently supported
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
        convert_image_format(base_path, selected_format)
