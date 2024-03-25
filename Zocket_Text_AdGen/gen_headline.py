from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Import prompt from text file
with open('few_shot_headline_prompt.txt', 'r') as file:
    heading_prompt = file.read()

with open('few_shot_subheading_prompt.txt', 'r') as file:
    subheading_prompt = file.read()


@app.route('/generate', methods=['POST'])
def generate_headline_subheading():
    data = request.get_json()

    brand_name = data.get('brand_name')
    product_name = data.get('product_name')
    product_description = data.get('product_description')
    heading_prompt_tuple = (heading_prompt, True)
    subheading_prompt_tuple = (subheading_prompt, True)

    # Replace the placeholders in the prompt with the actual values
    h_prompt = heading_prompt_tuple[0]
    sub_prompt = subheading_prompt_tuple[0]

    h_prompt = h_prompt.replace("{brand_name}", brand_name)
    h_prompt = h_prompt.replace("{product_name}", product_name)
    h_prompt = h_prompt.replace("{product_description}", product_description)

    sub_prompt = sub_prompt.replace("{brand_name}", brand_name)
    sub_prompt = sub_prompt.replace("{product_name}", product_name)
    sub_prompt = sub_prompt.replace("{product_description}", product_description)

    # Initialize completion to None
    completion = None

    # Generate the headline using GPT-3
    if heading_prompt_tuple[1]:
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system",
                 "content": """You are an expert Digital marketing professional, now you have to generate A HOOKING HEADLINE
                 of Just 4 to 5 Words Maximum for a product that will be used in a Facebook ad and other social media platforms.
                 It should be a single continuous sentence, don't use ":" """
                 },

                {"role": "user", "content": h_prompt}
            ]
        )

    head = completion.choices[0].message.content if completion else None
    completion = None

    if subheading_prompt_tuple[1]:
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system",
                 "content": """You are an expert Digital marketing professional, now you have to generate A HOOKING SUB-HEADLINE
                 of Just 10 to 15 Words Maximum for a product that will be used in a Facebook ad and other social media platforms.  """
                 },

                {"role": "user", "content": sub_prompt}
            ]
        )

    subhead = completion.choices[0].message.content if completion else None

    return jsonify({'headline': head, 'subheading': subhead})


if __name__ == '__main__':
    app.run(debug=False)
