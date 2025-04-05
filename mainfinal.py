from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from bs4 import BeautifulSoup
import json

test_answers={}
def setup_selenium():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    return driver

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

def navigate_to_test_series_details(driver, url):
    driver.get(url)
    time.sleep(5)

def extract_test_names_and_links(driver):
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product_inner")))
    scroll_to_bottom(driver)
    time.sleep(20)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    tests = []
    test_elements = soup.find_all('div', class_='product_inner')
    for element in test_elements:
        test_name = element.find('h2', class_='product_title').get('title')
        last_attempt = element.find('a', href=True, string='Last Attempt')
        if last_attempt:
            last_attempt_link = last_attempt['href']
            tests.append({'test_name': test_name, 'last_attempt_link': last_attempt_link})
    print(len(tests))        
    return tests

def extract_accordion_elements(driver):
    # Wait for test page to load
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".accordion")))

    # Extract accordion elements
    accordions = driver.find_elements(By.CSS_SELECTOR, ".btn-accordion-header")
    print(len(accordions))
    return accordions

def extract_correct_answers_from_accordion(driver, accordions):
    test_correct_answers = []
    i=0
    for accordion in accordions:
        # ans=""
        # Click on the accordion to expand it
        button = accordion#.find_element(By.CSS_SELECTOR, ".btn-accordion-header")
        actions = ActionChains(driver)
        if(i!=0):
            actions.move_to_element(button).click().perform()
        full_question_element = driver.find_element(By.CSS_SELECTOR, ".qqq")
        full_question = full_question_element.text.strip()
        
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".selection")))

        # Get the HTML content of the page
        html = driver.page_source
        
        # Create a BeautifulSoup object
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all selection elements
        selection_elements = soup.find_all('div', class_='selection')
        
        # Iterate through the selection elements and find the one with the green class
        for selection_element in selection_elements:
            if selection_element.find('span', class_='checkmark text-center mt-0 green'):
                # Extract the correct answer value
                correct_answer_element = selection_element.find('div', class_='mathjax-container').find('p')
                if correct_answer_element:
                    correct_answer = correct_answer_element.text
                    #print("Qustion:", full_question)
                    #print("Correct Answer:", correct_answer)
                    break
        i+=1        
        test_correct_answers.append((full_question, correct_answer))
    return test_correct_answers

def extract_correct_answers(driver, test):
    correct_answers=[]
    driver.get('https://lpu.myperfectice.com'+test['last_attempt_link'])
    time.sleep(5)
    accordions = extract_accordion_elements(driver)
    correct_answers = extract_correct_answers_from_accordion(driver, accordions)
    test_id = test['last_attempt_link'].split('/')[-1]
    test_answers[test_id] = {}
    #print(f"Test {test_id}:")  
    #print("Correct answers:")        
    for question, answer in correct_answers:
    #    print(f"  Question {question}: {answer}")
        test_answers[test_id][question] = answer


def main():
    driver = setup_selenium()
    login_to_website(driver, '12322566', 'LPU@70849')
    navigate_to_test_series_details(driver, 'https://lpu.myperfectice.com/student/testSeries/details/5da2351f42e6085038581567')
    tests = extract_test_names_and_links(driver)
    i=1
    for test in tests:
        print(i,"=",end=" ")
        extract_correct_answers(driver, test)
        #break
    # extract_correct_answers(driver, '/student/attemptSummary/66630514ab44c896ee127863')
    driver.quit()
    with open("answer_key.json", "w") as f:
        json.dump(test_answers, f, indent=4)

if __name__ == "__main__":
    main()