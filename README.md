# AI Image Generator

This Python script generates images based on prompts provided by the user. It utilizes the DALL·E 3 OpenAI API to generate images and saves them to the local filesystem.

## Usage

1. Ensure you have set up your OpenAI API key (`OPENAI_API_KEY`) in your environment variables.
2. Clone or download this repository.
3. Install the required dependencies by running `pip install -r requirements.txt`.
4. Run the script `generate_images.py`.
5. Enter a list of prompts (separated by commas) when prompted.
6. Choose the file type for generated images (PNG or JPG).
7. Images will be generated based on the prompts and saved to the `/generated_images` folder.

## Note

- Ensure your OpenAI API key has sufficient permissions and is not rate-limited.
- This script was originally intended to generate images of various foods, but it can generate any image supported by the OpenAI API.
