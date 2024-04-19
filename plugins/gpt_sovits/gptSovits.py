import requests
import os

current_module_directory = os.path.dirname(__file__)
output_dir = os.path.join(current_module_directory, "output.wav")

# Endpoint URL
url = "http://127.0.0.1:9880"

# Parameters for the GET request
params = {
    'text': 'English is a West Germanic language in the Indo-European language family, whose speakers, called Anglophones, originated in early medieval England.[4][5][6] The namesake of the language is the Angles, one of the ancient Germanic peoples that migrated to the island of Great Britain.',
    'text_language': 'en'
}

# Sending the GET request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:

    # Open a binary file in write mode and write the contents of the response
    with open(output_dir, 'wb') as file:
        file.write(response.content)
    print("Audio file downloaded successfully:", output_dir)
else:
    print("Failed to download audio file. Status Code:", response.status_code)
