import requests
import os
from bs4 import BeautifulSoup
import time

def download_sklearn_docs():
    """Download sklearn documentation pages"""
    
    # Create directory for sklearn docs
    os.makedirs('sklearn_docs', exist_ok=True)
    
    # List of sklearn documentation URLs
    base_url = "https://scikit-learn.org/stable/"
    doc_pages = [
        "user_guide.html",
        "modules/classes.html",
        "modules/linear_model.html",
        "modules/ensemble.html",
        "modules/tree.html",
        "modules/svm.html",
        "modules/neural_networks.html",
        "modules/clustering.html",
        "modules/decomposition.html",
        "modules/preprocessing.html",
        "modules/model_selection.html",
        "modules/metrics.html"
    ]
    
    all_text = []
    
    for page in doc_pages:
        try:
            print(f"Downloading: {page}")
            response = requests.get(base_url + page)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text = soup.get_text()
            # Clean up the text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            all_text.extend(lines)
            
            time.sleep(1)  # Be respectful to the server
            
        except Exception as e:
            print(f"Error downloading {page}: {e}")
    
    # Save to file
    with open('sklearn_docs.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_text))
    
    print(f"Downloaded sklearn docs: {len(all_text)} lines")

if __name__ == "__main__":
    download_sklearn_docs()