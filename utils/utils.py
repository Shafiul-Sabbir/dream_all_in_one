import re
import requests


def upload_to_cloudflare(thumbnail_image):
    """
    Upload an image to Cloudflare and return the URL of the uploaded image.
    """
    endpoint = 'https://api.cloudflare.com/client/v4/accounts/f8b413899d5239382d13a2665326b04e/images/v1'
    headers = {
        'Authorization': 'Bearer Ook1HC9KydDm4YfqkmVH5KnoNsSugDDqgLFj4QHi',
    }
    files = {
        'file': thumbnail_image.file
    }
    print("creating response from Cloudflare")
    response = requests.post(endpoint, headers=headers, files=files)
    print("Response status code:", response.status_code)
    response.raise_for_status()
    json_data = response.json()
    variants = json_data.get('result', {}).get('variants', [])
    if variants:
        cloudflare_image = variants[0]  # Use the first variant URL
        print("Cloudflare image URL from response:", cloudflare_image)
        return cloudflare_image
    else:
        print("No variants found in the Cloudflare response")
        return None
    
def generate_slug(name):
    clean_name = re.sub(r'[^A-Za-z0-9\s-]', '-', name)

    # Replace spaces with hyphens
    clean_name = re.sub(r'\s+', '-', clean_name)

    # Convert to lowercase
    clean_name = clean_name.lower()

    # Replace multiple consecutive hyphens with a single hyphen
    clean_name = re.sub(r'-{2,}', '-', clean_name)

    # Strip leading and trailing hyphens
    clean_name = clean_name.strip('-')

    slug = clean_name
    return slug

def reformed_head_or_name(given_string):
    # lower case
    lower_case = given_string.lower()
    
    # removing with guide or without guide
    cleaned = re.sub(r'\b(without guide|with guide)\b', '', lower_case)

    # convert extra spaces into a single space
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # converting space into '-' but without replacing '(' or ')'
    cleaned = re.sub(r'\s', '-', cleaned)

    return cleaned

def get_image_upload_folder(subfolder):
    def wrapper(instance, filename):
        # Company: 1 = IT, 2 = UK, 3 = Ziarah
        # folder_map = {
        #     1: 'IT',
        #     2: 'UK',
        #     3: 'Ziarah'
        # }

        company_name = getattr(instance, "company", None)
        print("Company name:", company_name)
        folder_name = company_name

        return f'{folder_name}/{subfolder}/{filename}'
    return wrapper