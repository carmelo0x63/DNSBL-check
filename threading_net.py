import threading  
import requests  
  
def download_file(url):  
    response = requests.get(url)  
    print(f'Downloaded {url}, status code = {response.status_code}')  
  
#urls = ["http://example.com/file1", "http://example.com/file2"]  
urls = ["https://www.cisco.com/c/dam/en/us/td/docs/security/esa/esa15-5-1/release_notes/Secure_Email_15-5_Release_Notes.pdf", "https://www.cisco.com/c/dam/en/us/td/docs/security/esa/esa15-5-1/release_notes/Secure_Email_15-5-1_HP_Release_Notes.pdf"]  

threads = [threading.Thread(target = download_file, args = (url,)) for url in urls]  
  
for thread in threads:  
    thread.start()  
#for thread in threads:  
    thread.join()

