from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

app = Flask(__name__)

def get_rendered_content(url):
  # Set up headless Chrome options
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  chrome_options.add_argument("--disable-gpu")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-dev-shm-usage")

  selenium_host = os.environ.get('SELENIUM_HOST', 'localhost')
  selenium_port = os.environ.get('SELENIUM_PORT', '4444')

  # Connect to the Selenium server running in the Docker container
  driver = webdriver.Remote(
      command_executor=f'http://{selenium_host}:{selenium_port}/wd/hub',
      options=chrome_options
  )

  try:
    driver.get(url)
    # Wait for JavaScript to load and render
    time.sleep(5)  # Adjust the sleep time if necessary
    rendered_content = driver.page_source
  finally:
    driver.quit()

  return rendered_content

@app.route('/fetch', methods=['GET'])
def fetch_url():
  url = request.args.get('url')
  if not url:
    return jsonify({"error": "URL parameter is missing"}), 400

  try:
    rendered_content = get_rendered_content(url)
    return rendered_content
  except Exception as e:
    return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
