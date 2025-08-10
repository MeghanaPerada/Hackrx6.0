# src/utils/secret_token.py
"""Secret token handling utilities"""

import requests
import re
from bs4 import BeautifulSoup
from typing import List, Tuple

def check_for_secret_token_url(questions: List[str]) -> Tuple[bool, str]:
    """
    Check if any question contains a secret token URL and extract the token
    Returns (found, token) tuple
    """
    base_url = "@https://register.hackrx.in/utils/get-secret-token?"
    
    for question in questions:
        if base_url in question:
            try:
                # Find the URL in the question
                start_idx = question.find(base_url)
                if start_idx != -1:
                    # Remove the @ symbol and extract the URL
                    url_start = start_idx + 1  # Skip the @
                    # Find the end of the URL (space or end of string)
                    url_end = question.find(' ', url_start)
                    if url_end == -1:
                        url_end = len(question)
                    
                    full_url = question[url_start:url_end]
                    print(f"🔗 Found secret token URL: {full_url}")
                    
                    # Visit the URL and extract the secret token
                    token = fetch_secret_token_from_url(full_url)
                    if token:
                        return True, token
                    else:
                        return True, "Error: Could not retrieve secret token from the URL"
                        
            except Exception as e:
                print(f"❌ Error processing secret token URL: {e}")
                return True, f"Error: Failed to process URL - {e}"
    
    return False, ""

def fetch_secret_token_from_url(url: str) -> str:
    """Fetch secret token from URL by scraping webpage content"""
    try:
        print(f"📥 Fetching secret token from: {url}")
        
        # Add headers to mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        print(f"✅ Successfully fetched webpage (Status: {response.status_code})")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        print(f"📄 Page content preview: {page_text[:200]}...")
        
        # Method 1: Look for hexadecimal tokens in the entire page
        hex_token_pattern = r'\b[a-fA-F0-9]{32,}\b'
        hex_matches = re.findall(hex_token_pattern, page_text)
        if hex_matches:
            token = max(hex_matches, key=len)
            print(f"✅ Found hexadecimal token: {token}")
            return token
        
        # Method 2: Look in HTML elements for tokens
        token_elements = soup.find_all(['div', 'span', 'p', 'code', 'pre'], string=re.compile(r'[a-fA-F0-9]{32,}'))
        for element in token_elements:
            token_match = re.search(r'[a-fA-F0-9]{32,}', element.get_text())
            if token_match:
                token = token_match.group()
                print(f"✅ Found token in HTML element: {token}")
                return token
        
        # Method 3: Look for tokens in specific HTML attributes or data attributes
        for element in soup.find_all(['div', 'span', 'input', 'textarea']):
            for attr in ['data-token', 'value', 'data-value', 'id', 'class']:
                attr_value = element.get(attr, '')
                if isinstance(attr_value, str) and re.match(r'^[a-fA-F0-9]{32,}$', attr_value):
                    print(f"✅ Found token in {attr} attribute: {attr_value}")
                    return attr_value
        
        # Method 4: Look for text after "Your Secret Token" or "Secret Token"
        lines = page_text.strip().split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if "Your Secret Token" in line or "Secret Token" in line:
                print(f"🔍 Found 'Secret Token' text at line {i}")
                # Check the next few lines for the token
                for j in range(i + 1, min(i + 10, len(lines))):
                    potential_token = lines[j].strip()
                    # Check if this looks like a token (long hex string)
                    if len(potential_token) >= 32 and re.match(r'^[a-fA-F0-9]+$', potential_token):
                        print(f"✅ Found structured token: {potential_token}")
                        return potential_token
                    # Also check for tokens within the line
                    token_match = re.search(r'[a-fA-F0-9]{32,}', potential_token)
                    if token_match:
                        token = token_match.group()
                        print(f"✅ Found token in line: {token}")
                        return token
        
        # Method 5: Look for any long alphanumeric strings (fallback)
        general_token_pattern = r'\b[a-zA-Z0-9]{32,}\b'
        general_matches = re.findall(general_token_pattern, page_text)
        if general_matches:
            # Filter for hex-like tokens first
            hex_like = [m for m in general_matches if re.match(r'^[a-fA-F0-9]+$', m)]
            if hex_like:
                token = max(hex_like, key=len)
                print(f"✅ Found hex-like token: {token}")
                return token
            else:
                token = max(general_matches, key=len)
                print(f"✅ Found general alphanumeric token: {token}")
                return token
        
        # Method 4: Return meaningful content if found
        clean_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('🔒')]
        meaningful_content = []
        
        for line in clean_lines:
            if line not in ['Your Secret Token', 'Secret Token', '🔒', '____']:
                meaningful_content.append(line)
        
        if meaningful_content:
            result = ' '.join(meaningful_content)
            print(f"✅ Returning meaningful content: {result}")
            return result
        
        # Method 5: Last resort - return entire cleaned page content
        clean_text = page_text.replace('\n', ' ').strip()
        if clean_text:
            print(f"✅ Returning entire page content: {clean_text[:100]}...")
            return clean_text
        
        print(f"⚠️ Could not find any meaningful content in the webpage")
        return "Error: No content found on the webpage"
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout error fetching URL {url}")
        return "Error: Request timeout while fetching the URL"
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error fetching URL {url}")
        return "Error: Could not connect to the URL"
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error fetching URL {url}: {e}")
        return f"Error: Request failed - {str(e)}"
    except Exception as e:
        print(f"❌ Unexpected error parsing webpage: {e}")
        return f"Error: Failed to parse webpage - {str(e)}"