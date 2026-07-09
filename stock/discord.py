import requests
import time 
url = "https://discord.com/api/webhooks/1518820872335654924/6thiTPwmaubDkaJsZOVNMYQAvnCkVZ48SA1mXdvKe58UUy5GjZaQpo9EApxZroo6j1ko"

def send_message(message):
    data = {
        "content": message
    }
    response = requests.post(url, json=data)
    if response.status_code == 204:
        print("Message sent successfully.")
    else:
        print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    count =1
    while True:
        time.sleep(10)  # Send a message every 10 seconds
        message = "@everyone Hello from the Discord webhook!" + str(count)
        send_message(message)
        count += 1  
