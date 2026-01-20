import os
import requests
from bs4 import BeautifulSoup
import ssl
import urllib3
from urllib.parse import urlparse

# Disable SSL warnings for corporate networks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WEB_DIR = "backend/data/webs"
os.makedirs(WEB_DIR, exist_ok=True)

def fetch_and_clean_website(url: str):
    """
    Fetch and clean website content with SSL handling and bot detection evasion
    """
    try:
        # Enhanced headers to better mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Charset': 'UTF-8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Create session with retries and delays
        session = requests.Session()
        
        # Add a delay to avoid being detected as a bot
        import time
        time.sleep(2)
        
        # Try multiple approaches for both SSL and bot detection
        response = None
        
        # First try: Normal request with enhanced headers
        try:
            response = session.get(url, timeout=15, headers=headers, allow_redirects=True)
            response.raise_for_status()
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            print(f"SSL issue with {url}, trying without SSL verification...")
            # Second try: Disable SSL verification
            try:
                response = session.get(url, timeout=15, headers=headers, verify=False, allow_redirects=True)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    # Third try: Even more realistic headers for 403 errors
                    headers.update({
                        'Referer': 'https://www.google.com/',
                        'Origin': 'https://www.google.com'
                    })
                    time.sleep(3)  # Longer delay
                    response = session.get(url, timeout=15, headers=headers, verify=False, allow_redirects=True)
                    response.raise_for_status()
                else:
                    raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                # Handle 403 error with different approach
                print(f"Website blocking access to {url}. Trying alternative approach...")
                headers.update({
                    'Referer': 'https://www.google.com/',
                    'Origin': 'https://www.google.com'
                })
                time.sleep(3)  # Add delay
                response = session.get(url, timeout=15, headers=headers, verify=False, allow_redirects=True)
                response.raise_for_status()
            else:
                raise
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unnecessary elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript"]):
            tag.decompose()

        # Extract text content
        text = soup.get_text(separator="\n")
        cleaned_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        
        # Filter out very short lines that are likely navigation/UI elements
        lines = cleaned_text.split('\n')
        filtered_lines = [line for line in lines if len(line) > 10]  # Keep lines with more than 10 chars
        cleaned_text = '\n'.join(filtered_lines)
        
        # Limit text length to avoid very large documents
        if len(cleaned_text) > 50000:  # Limit to ~50KB of text
            cleaned_text = cleaned_text[:50000] + "\n[Content truncated due to length]"

        # Save to file
        parsed_url = urlparse(url)
        filename = f"{parsed_url.netloc}_{parsed_url.path.replace('/', '_')}.txt"
        # Clean filename
        filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        file_path = os.path.join(WEB_DIR, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"Successfully fetched {len(cleaned_text)} characters from {url}")
        return cleaned_text
        
    except Exception as e:
        error_msg = f"Error fetching URL {url}: {str(e)}"
        print(error_msg)
        
        # If all else fails, return a helpful message
        fallback_content = f"""
Unable to fetch content from {url} due to website restrictions.

This website appears to be blocking automated requests. This is common with sites like GeeksforGeeks that have bot protection.

Alternative suggestions:
1. Try a different URL from the same site
2. Use a simpler URL structure  
3. Copy and paste the content manually into a text file and upload as PDF
4. Try other educational websites that are more accessible

Common accessible alternatives for programming tutorials:
- https://docs.python.org/3/tutorial/
- https://realpython.com/
- https://www.w3schools.com/python/
"""
        return fallback_content
