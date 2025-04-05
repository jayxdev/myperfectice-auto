from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import json
import re
import random

# Load answer key from JSON file
with open('answer_key.json') as f:
    answer_key = json.load(f)

with open('test_key.json') as f:
    test_key = json.load(f)

def setup_selenium():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    return driver

def login_to_website(driver, username, password):
    driver.get('https://lpu.myperfectice.com/')
    username_field = driver.find_element(By.NAME, 'email')
    password_field = driver.find_element(By.NAME, 'password')
    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
    )
# Click the login button
    login_button.click()
    time.sleep(5)


# Automate test series
def automate(driver):
    print(f"Automating test series:")
    # Find the test series title element on the page
    driver.set_window_size(896, 768)
    #driver.set_window_size(1024, 768)
    start = driver.find_element(By.XPATH,"//*[@id=\"page-wrapper\"]/p-student/app-test-series-details/div/div/div/div[2]/div/div[1]/a")
    actions = ActionChains(driver)
    actions.move_to_element(start).click().perform()
    time.sleep(5)
    driver.set_window_size(1024, 768)
    take_assessment_btn = driver.find_element(By.XPATH,"//*[@id=\"wrapper\"]/section[3]/div/div/div/div[2]/div/div/div[1]/div/a")

    if take_assessment_btn:
        print("Take Assessment button found, clicking on it")
        take_assessment_btn.click()
        attempt_test(driver)
    else:
        print("Take Assessment button not found")




    # if test_h4:
    #     print("Test series title found, clicking on it")
    #     test_h4.click()
    #     # Wait for the page to load and then call the resume_test function
    #     resume_test()
    # else:
    #     print("Test Series title not found")

# Resume test
def resume_test(driver):
    print("Resuming test")
    # Wait for 2 seconds to allow the page to load
    time.sleep(2)
    # Find the resume button element on the page
    resume_btn = driver.find_element(By.CSS_SELECTOR,"a.btn.btn-primary.btn-block.mt-2")
    if resume_btn:
        print("Resume button found, clicking on it")
        resume_btn.click()
    else:
        print("Congratulations! You have completed test series")

# Inner resume test
def inner_resume(driver):
    print("Inner resume test")
    # Wait for 2 seconds to allow the page to load
    time.sleep(2)
    # Get the current URL
    url = driver.current_url
    # Extract the test ID from the URL
    id = url.split("id=")[1]
    if id:
        # Construct the test URL
        test_url = f"https://lpu.myperfectice.com/student/learning-test/{id}"
        print(f"Navigating to test URL: {test_url}")
        # Navigate to the test URL
        driver.get(test_url)
    else:
        print("Navigating to dashboard")
        # Find the dashboard link element on the page
        dashboard = driver.find_element(By.CSS_SELECTOR,"li.nav-item.ng-star-inserted > a.nav-link.p-0")
        if dashboard:
            # Click on the dashboard link element
            dashboard.click()
        else:
            print("Dashboard link not found")

# Attempt test
def attempt_test(driver):
    ready=driver.find_element(By.XPATH,"//*[@id=\"page-wrapper\"]/p-student/app-test-term/section[2]/div/div/div[2]/a[2]")
    ready.click()
    print("Starting to attempt test")
    time.sleep(20)
    # Set an interval to attempt each question
    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the relevant <ul> element
        question_info_ul = soup.find('ul', {'class': ['nav', 'info', 'pl-0', 'mb-3']})
        
        # Extract the question number and total from the <span> elements
        current = question_info_ul.find_all('span')[0].text.strip()
        total = question_info_ul.find_all('span')[2].text.strip()

        print(f"Current question: {current}, Total questions: {total}")

        # Get the question ID
        question_id = get_question_id(driver)
        print(question_id)

        # Get the test ID
        test_id = get_test_id()

        # Get the question element
        question_element = driver.find_element(By.CSS_SELECTOR,".question-item span mathjax-renderer div.mathjax-container p")
        print(question_element.text)

        # Get the answer from the answer key
        answer = answer_key[test_id][question_element.text]
        print(answer)
        if not answer:
            print(f"No answer found for question {current} in test {test_id}")
            # Click a random checkbox
            checkboxes = driver.find_elements(By.CSS_SELECTOR,"input[type='checkbox']")
            if not checkboxes:
                print("No checkboxes found")
                break
           
            random_number = random.randint(0, 3)
            print(random_number)
            random_checkbox = checkboxes[0]
            print("Clicking a random checkbox")
            random_checkbox.click()
            break
        else:
            # Find the options elements on the page
            options = driver.find_elements(By.CSS_SELECTOR,"input[type='checkbox']")

            # Find the correct option element
            answer_options = driver.find_elements(By.CSS_SELECTOR,".answer-checkbox input[type='checkbox']")

            # Get the answer text elements
            answer_texts = driver.find_elements(By.CSS_SELECTOR,".answer-text p")

            # The answer you want to select
            correct_answer = answer
            print(correct_answer)

            # Loop through the answer elements
            for answer_element in answer_texts:
                if answer_element.text == correct_answer:
                    print("Correct answer found")
                    # Click the correct answer checkbox
                    answer_element.find_element(By.XPATH,"./../input").click()
                    break
                else:
                    print("Correct answer not found")

                # Find the "Save and Next" button element on the page
                save_and_next = driver.find_element(By.CSS_SELECTOR,"a.btn.btn-primary.btn-block")
                if save_and_next:
                    print("Clicking 'Save and Next' button")
                    save_and_next.click()
                else:
                    print("No 'Save and Next' button found")
    
                # Check if it's the last question
                if current == total:
                    print("Last question, clicking 'Finish' button")
                    # Find the "Finish" button element on the page
                    finish_btn = driver.find_element(By.CSS_SELECTOR,"#page-wrapper > p-student > app-learning-test > div.adaptive-question > div > div > div.ng-star-inserted > div.d-block.d-lg-none.fixed-bottom.ng-star-inserted > div > div > a")
                    if finish_btn:
                        finish_btn.click()
                    else:
                        print("No 'Finish' button found")
    
# Get question ID
def get_question_id(driver):
    # Find the question header element on the page
    question_header = driver.find_element(By.CSS_SELECTOR,"#page-wrapper > p-student > app-learning-test > div.adaptive-question > div > div > div.heading > div > div:nth-child(1) > div > ul > li.count.text-white.clearfix > span:nth-child(1)")
    if question_header:
        # Extract the question ID from the question header element
        question_id_regex = r"\d+"
        question_id_match = re.search(question_id_regex, question_header.text)
        if question_id_match:
            return question_id_match.group(0)
    return None

# Get test ID
def get_test_id(driver):
    # Find the test name element on the page
    test_name_element = driver.find_element(By.CSS_SELECTOR,"h3.f-16.bold")
    if test_name_element:
        # Extract the test ID from the test name element
        test_name = test_name_element.text.strip()
        test_id = test_key[test_name]
        if test_id:
            return test_id
    return None

def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Set a limit for maximum number of scrolls to avoid infinite loops
    max_scrolls = 10
    scroll_count = 0
    
    # Loop to scroll down and wait for content to load
    while scroll_count < max_scrolls:
        # Get current height
        current_height = driver.execute_script("return document.body.scrollHeight")
        
        # Scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new content to load
        time.sleep(3)  # Adjust based on content load time
        
        # Get new height
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Break the loop if no new content is loaded
        if new_height == current_height:
            break
        
        scroll_count += 1
    
    # Optionally, you can wait for some time to ensure all content is fully loaded
    time.sleep(5)
def navigate_to_test_series_details(driver, url):
    driver.get(url)
    time.sleep(5)

def main():
    driver = setup_selenium()
    login_to_website(driver, '12322566', 'LPU@70849')
    navigate_to_test_series_details(driver, 'https://lpu.myperfectice.com/student/testSeries/details/5da2351f42e6085038581567')
    
   # scroll_to_bottom(driver)
    automate(driver)
    #driver.quit()

if __name__ == "__main__":
    main()


