import os
import requests

# Confluence settings
base_url = 'https://your-confluence-url.com'
username = 'your-username'
password = 'your-password'
space_key = 'your-space-key'
parent_page_id = 'your-parent-page-id'

base_url = base_url + '/wiki'

# Directory and image file tree settings
directory_path = './img'
image_extensions = ['.png']

# Login to Confluence
auth = (username, password)
session = requests.Session()
session.auth = auth

session.headers.update({'X-Atlassian-Token': 'no-check'})

# Create Confluence pages for each image file
for root, dirs, files in os.walk(directory_path):
    for file in files:
        file_path = os.path.join(root, file)
        if os.path.splitext(file_path)[1].lower() in image_extensions:
            # Create Confluence page for image
            page_title = os.path.splitext(file)[0]
            url = f'{base_url}/rest/api/content/'
            data = {
                'title': page_title,
                'type': 'page',
                'ancestors': [{'id': parent_page_id}],
                'space': {'key': space_key},
                'body': {'storage': {'value': '<p>Here is my image:</p>', 'representation': 'storage'}}
            }
            response = session.post(url, json=data)

            if response.status_code == 200:
                page_id = response.json()['id']
                print(f'Page "{page_title}" created successfully! ID: {page_id}')
            else:
                print(f'Error creating page "{page_title}":', response.content)

            # Upload image file to Confluence as attachment and include in page body
            url = f'{base_url}/rest/api/content/{page_id}/child/attachment'
            files = {'file': (file, open(file_path, 'rb'))}
            response = session.post(url, files=files)
            if response.status_code == 200:
                attachment_id = response.json()['results'][0]['id']
                print(f'Attachment uploaded successfully! ID: {attachment_id}')
            else:
                print('Error uploading attachment:', response.content)
            
            # Update page body to include image attachment
            url = f'{base_url}/rest/api/content/{page_id}'
            data = {
                'id': page_id,
                'title': page_title,
                'type': 'page',
                'version': {'number': 2},
                'body': {
                    'storage': {
                        'value': f'<p><ac:image><ri:attachment ri:filename=\"{file}\" /></ac:image></p>',
                        'representation': 'storage'
                    }
                }
            }
            response = session.put(url, json=data)
            if response.status_code == 200:
                print(f'Image attachment {attachment_id} inserted into page body successfully!')
            else:
                print('Error inserting image attachment into page body:', response.content)