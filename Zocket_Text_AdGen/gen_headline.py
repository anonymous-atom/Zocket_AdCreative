from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
import os
from openai import OpenAI, Client

app = FastAPI()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Get the absolute path of the directory of the current script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Construct the absolute path of the text files
heading_prompt_file_path = os.path.join(dir_path, 'few_shot_headline_prompt.txt')
subheading_prompt_file_path = os.path.join(dir_path, 'few_shot_subheading_prompt.txt')

# Now you can open your files using the absolute paths
with open(heading_prompt_file_path, 'r') as file:
    heading_prompt = file.read()

with open(subheading_prompt_file_path, 'r') as file:
    subheading_prompt = file.read()


class GenerateRequest(BaseModel):
    brand_name: str
    product_name: str
    product_description: str


@app.post('/generate')
async def generate_headline_subheading(data: GenerateRequest):
    brand_name = data.brand_name
    product_name = data.product_name
    product_description = data.product_description

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
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system",
                 "content": """You are an expert Digital marketing professional, now you have to generate A HOOKING 
                 HEADLINE of Just 4 to 5 Words Maximum for a product that will be used in a Facebook ad and other 
                 social media platforms. It should be a single continuous sentence, DO NOT USE "-" AND ":" IN THE 
                 HEADLINE.Please refrain from using hyphens and colons."""
                 },

                {"role": "user", "content": h_prompt}
            ]
        )

    head = completion.choices[0].message.content if completion else None
    completion = None

    if subheading_prompt_tuple[1]:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system",
                 "content": """You are an expert Digital marketing professional, now you have to generate A HOOKING 
                 SUB-HEADLINE of Just 10 to 15 Words Maximum for a product that will be used in a Facebook ad and 
                 other social media platforms. DO NOT USE "-" AND ":" Until and unless used in product name or brand 
                 name. Please refrain from using hyphens and colons , they can be only used for words provided in
                 product name and brand name. Also don't use words that use "-" or ":" as a part of the word.
                  For example,"high-performance" is not allowed as it uses "-". """
                 },

                {"role": "user", "content": sub_prompt}
            ]
        )

    subhead = completion.choices[0].message.content if completion else None

    return {'headline': head, 'subheading': subhead}