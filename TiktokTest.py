from openai import OpenAI
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json
import re
import time



# Initialize fastAPI
app = FastAPI()

# Pydantic Models
# Use to structure the data and convert the json sent
class ProductLink(BaseModel):
    url: str

class ProductData(BaseModel):
    title: str
    price: str
    description: str
    images: List[str]

class ScrapeAndCleanResponse(BaseModel):
    listing: ProductData
    script: str


# Setup Chrome
service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)

# Wait object for explicit waits
wait = WebDriverWait(driver, 10) # wait up to 10 seconds
def get_image():
    images = wait.until(EC.presence_of_all_elements_located(( By.CSS_SELECTOR, "img.object-cover.max-w-full.max-h-full.aspect-square.rounded-4.cursor-pointer" )))
    count = 1
    for img in images:
        print("Image " + str(count) + ": " + img.get_attribute("src"))
        count += 1
    return [img.get_attribute("src") for img in images]

def get_description():
    while True:
        try:
            # Wait a short time for a "View more" to appear
            viewMore = WebDriverWait(driver, .5).until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "span.Headline-Semibold.text-color-UIText1.rounded-8.background-color-UIShapeNeutral4.px-24.py-13"
            )))

            # Scroll to and click it
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", viewMore)
            viewMore.click()
            time.sleep(0.2)  # allow new content to load
        except:
            break  # no more View more buttons, exit loop

    # Grab all spans with the description class
    description = driver.find_elements(
        By.CSS_SELECTOR,
        "span.font-sans.font-normal.text-color-UIText1.mb-8.break-words.whitespace-normal"
    )

    # Combine all text parts
    fullDescription = " ".join([desc.text for desc in description])

    print("\nProduct Description:")
    print(fullDescription)
    return fullDescription

def get_price():
    # Find all elements with the price class
    prices = driver.find_elements(By.CSS_SELECTOR, "span.flex.flex-row.items-baseline")

    # Initialize an empty string to store the full price
    fullPrice = ""

    # Loop through each element and clean its text
    for p in prices:
        # Get the text of the element
        text = p.text

        # Remove spaces and newlines
        text = text.replace(" ", "").replace("\n", "")

        # Add it to the fullPrice string
        fullPrice += text

    # Print the label
    print("\nProduct Price:")

    # Print the combined price text
    print(fullPrice)
    return fullPrice

def get_title():
    classElements = driver.find_elements(By.CSS_SELECTOR, "span.H2-Semibold.text-color-UIText1Display")
    fullTitle = classElements[1].text
    print("\nProduct Title:")
    print(fullTitle)
    return fullTitle

# Setup AI Client (OpenRouter / DeepSeek)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")  # set your key in env
)


def clean_with_ai(title: str, price: str, description: str, images: list[str]):
    # Construct prompt
    prompt = f"""
                Clean and format the following product details into a JSON object ready for a marketplace listing.
                Return **only valid JSON**. Do not include extra text.
                
                Title: {title}
                Price: {price}
                Description: {description}
                Images: {', '.join(images)}
                
                Required JSON format:
                {{
                    "title": "Product Title",
                    "price": "$20",
                    "description": "Catchy, clear description",
                    "images": ["url1", "url2"]
                }}
                """

    # Call AI
    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3.1:free",
        messages=[{"role": "user", "content": prompt}]
    )

    completion_text = completion.choices[0].message.content

    # Try to extract JSON using regex
    match = re.search(r"\{.*\}", completion_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Fallback: return original scraped data if AI fails
    return {
        "title": title,
        "price": price,
        "description": description,
        "images": images
    }

# Function used to generate script
def generate_script(cleaned_listing: dict):
    # cleaned_listing has "title", "price", "description", "images"
    # get dictionary value from the cleaned listing
    prompt = f"""
    Write a short script for a video or voiceover using the following product info.
    Make it catchy and engaging.

    Title: {cleaned_listing['title']} 
    Price: {cleaned_listing['price']}
    Description: {cleaned_listing['description']}
    Images: {', '.join(cleaned_listing['images'])}
    """

    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat-v3.1:free",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content




# Our endpoint for our api

# 1. Scrape raw product data and clean to return a cleaned json
@app.post("/scrape_and_clean/", response_model=ScrapeAndCleanResponse)
def scrape_and_clean(product: ProductLink):
    driver.get(product.url)
    driver.refresh()
    time.sleep(1)

    # Scrape product
    title = get_title()
    price = get_price()
    images = get_image()
    description = get_description()

    # Call AI to clean & format
    cleaned = clean_with_ai(title, price, description, images)

    # Generate script
    script_text = generate_script(cleaned)

    return ScrapeAndCleanResponse(
        listing=ProductData(
            title=cleaned.get("title", title),
            price=cleaned.get("price", price),
            description=cleaned.get("description", description),
            images=cleaned.get("images", images)
        ),
        script=script_text
    )


# Need this so the fast api server always runs
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

