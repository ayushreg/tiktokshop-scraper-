from google import genai
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# Set up gemini

client = genai.Client(api_key="AIzaSyCUe_dhPi99QWdi18N80xlGirbPlChjOrc")

def format_information(title, price, description, images):
    content = f"""
        Rewrite the following product details into a Facebook Marketplace style listing.
        Make it catchy, clear, and ready to post. Keep it short but persuasive.
        
        Product Title: {title}
        Price: {price}
        Description: {description}
        Image URLs: {", ".join(images)}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=content
    )

    # Return the text output
    return response.text.strip()


# Our endpoints for our api

# 1. Scrape raw product data
@app.post("/scrape/", response_model=ProductData)
def scrape_product(product: ProductLink):
    driver.get(product.url)  #product = ProductLink(url="https://example.com/product-page")
    driver.refresh()
    time.sleep(1)

    title = get_title()
    price = get_price()
    images = get_image()
    description = get_description()

    return ProductData(title=title, price=price, description=description, images=images)

# 2. Clean up product data using Gemini
@app.post("/format/")
def format_product(product: ProductData):
    cleaned = format_information(product)  #We need to call the scrape functions first
    return {"formatted_listing": cleaned}


