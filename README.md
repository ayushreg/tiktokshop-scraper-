
<div align="center">
  <h1>AI-Powered Marketplace Listing Generator</h1>
  <p>
    A smart Python script that uses Selenium and the Google Gemini API to automatically create catchy Facebook Marketplace listings from a product URL.
  </p>
</div>

---

## Description

This project automates the creation of professional product listings for Facebook Marketplace. It combines:

- **Web scraping with Selenium** to gather product details (title, price, description, images).  
- **AI-powered text generation with Google Gemini API** to create a ready-to-post, persuasive listing.  

> ⚠️ **Note:** This script runs **locally only**. It requires Chrome, ChromeDriver, Python, and internet access to TikTok Shop and Google Gemini API.

---

## Features

- Extract product **title**, **price**, **description**, and **images** from TikTok Shop.  
- Generate **catchy, concise, and ready-to-post listings**.  
- Minimal setup for local execution.  
- Designed for future expansion into a web application.

---

## Local Setup

### Prerequisites

- Python 3.x installed ([Download Python](https://www.python.org/downloads/))  
- Google Chrome browser installed ([Download Chrome](https://www.google.com/chrome/))  
- ChromeDriver that matches your Chrome version ([Download ChromeDriver](https://sites.google.com/chromium.org/driver/))  
- Google Gemini API key  

### Installation Steps

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
````

2. **Install required Python libraries:**

```bash
pip install selenium
pip install google-generativeai
```

3. **Set up ChromeDriver:**

* Check your Chrome version: `chrome://settings/help`
* Download the matching ChromeDriver.
* Place it in your project folder or add it to your system PATH.

4. **Configure API key:**

Open `main.py` and replace the placeholder API key with your own:

```python
client = genai.Client(api_key="YOUR_API_KEY")
```

### Running the Script

```bash
python main.py
```

1. Enter a **TikTok Shop product link** when prompted.
2. The script will output:

* Product title
* Product price
* Product description
* Image URLs
* Formatted Facebook Marketplace listing

---

## Limitations

* Only works **locally** on machines with Chrome and ChromeDriver installed.
* Requires **internet access** to access TikTok Shop and Google Gemini API.
* Does **not currently support bulk scraping** or other e-commerce websites.

---

## Roadmap

* Add support for more e-commerce platforms (Amazon, eBay, etc.)
* Implement better error handling for out-of-stock products or missing data
* Create a simple GUI for easier use
* Explore a web-based version to run in a browser without local setup

---

## Contributing

Contributions are welcome! Open an issue or submit a pull request if you want to help improve this project.

---

## License

This project is licensed under the MIT License.

```
