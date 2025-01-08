import json
import time
import urllib.parse
from flask import Flask, render_template, jsonify, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_courses():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the WebDriver (make sure to specify the correct path to your WebDriver)
    service = Service('C:/Users/ASUS/Downloads/chromedriver-win64 (2)/chromedriver-win64/chromedriver.exe')  # Update with your WebDriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    urls = [
        "https://www.geeksforgeeks.org/courses/android-by-kotlin?itm_source=geeksforgeeks&itm_medium=main_header&itm_campaign=courses",
        "https://www.geeksforgeeks.org/courses/mastering-generative-ai-and-chat-gpt?itm_source=geeksforgeeks&itm_medium=main_header&itm_campaign=courses",
        "https://www.geeksforgeeks.org/courses/mastering-django-framework-beginner-to-advance?itm_source=geeksforgeeks&itm_medium=main_header&itm_campaign=courses",
        "https://www.geeksforgeeks.org/courses/search?query=AWS&itm_source=geeksforgeeks&itm_medium=main_header&itm_campaign=courses"
    ]
    
    courses = []

    for url in urls:
        driver.get(url)
        time.sleep(3) 

        try:
            title = driver.find_element(By.TAG_NAME, 'h1').text.strip()
        except Exception as e:
            title = "No Title"
            print(f"Error fetching title: {e}")

        try:
            first_image = driver.find_element(By.CLASS_NAME, 'courseCard_thumbnail__2PaZJ')
            src = first_image.get_attribute('src')
            image = None
            
            if src and '/_next/image?url=' in src:
                
                parsed_url = urllib.parse.urlparse(src)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                image = query_params.get('url', [None])[0]
                if image:
                    print("Extracted Image URL:", image)
            else:
                
                noscript_tag = first_image.find_element(By.XPATH, '..').find_element(By.TAG_NAME, 'noscript')
                if noscript_tag:
                    noscript_img = BeautifulSoup(noscript_tag.get_attribute('innerHTML'), 'html.parser').find('img')
                    noscript_src = noscript_img.get('src')
                    if noscript_src and '/_next/image?url=' in noscript_src:
                    
                        parsed_url = urllib.parse.urlparse(noscript_src)
                        query_params = urllib.parse.parse_qs(parsed_url.query)
                        image = query_params.get('url', [None])[0]
                        if image:
                            print("Extracted Image URL from noscript:", image)
                    else:
                        print("Valid URL not found in noscript.")
                else:
                    print("Noscript tag not found.")
        except Exception as e:
            image = "No Image"
            print(f"Error fetching image: {e}")

        try:
            description = driver.find_element(By.CLASS_NAME, 'courseCard_container__NZCtf').text.strip()
        except Exception as e:
            description = "No Description"
            print(f"Error fetching description: {e}")

        try:
            overview = driver.find_element(By.CLASS_NAME, 'courseOverview_content__QcPah').text.strip()
        except Exception as e:
            overview = "No Overview"
            print(f"Error fetching overview: {e}")

        try:
            course_content = driver.find_element(By.CLASS_NAME, 'coursesSlug_course_content_container__4GwEh').text.strip()
        except Exception as e:
            course_content = "No Content"
            print(f"Error fetching course content: {e}")

        try:
            instructor_name = driver.find_element(By.CLASS_NAME, 'courseInstructor_name__C1NfR').text.strip()
        except Exception as e:
            instructor_name = "No Instructor Name"
            print(f"Error fetching instructor name: {e}")

        try:
            instructor_designation = driver.find_element(By.CLASS_NAME, 'courseInstructor_achievements__jQP23').find_element(By.TAG_NAME, 'p').text.strip()
        except Exception as e:
            instructor_designation = "No Instructor Designation"
            print(f"Error fetching instructor designation: {e}")

        try:
            testimonials_section = driver.find_element(By.CLASS_NAME, 'courseReviewRating_cardContainer__DZw5h')
            testimonials_count = len(testimonials_section.find_elements(By.TAG_NAME, 'div')) if testimonials_section else 0
        except Exception as e:
            testimonials_count = 0
            print(f"Error fetching testimonials count: {e}")

        try:
            feedback_average_text = driver.find_element(By.CLASS_NAME, 'courseCard_rating__iWp7_').text.strip()
            feedback_average = float(feedback_average_text.split('/')[0]) if feedback_average_text else 0.0
        except Exception as e:
            feedback_average = 0.0
            print(f"Error fetching feedback average: {e}")

        courses.append({
            'title': title,
            'image': image,
            'description': description,
            'overview': overview,
            'course_content': course_content,
            'instructor_name': instructor_name,
            'instructor_designation': instructor_designation,
            'testimonials_count': testimonials_count,
            'feedback_average': feedback_average
        })

    with open('courses_data.json', 'w') as f:
        json.dump(courses, f)

    driver.quit()  
    return courses

@app.route('/')
def index():
    try:
        with open('courses_data.json') as f:
            courses = json.load(f)
    except FileNotFoundError:
        courses = []
    return render_template('index.html', courses=courses)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    try:
        with open('courses_data.json') as f:
            courses = json.load(f)
        course = courses[course_id]
        return render_template('course_detail.html', course=course, course_id=course_id)
    except (IndexError, FileNotFoundError):
        return "Course not found", 404

@app.route('/course/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    try:
        with open('courses_data.json') as f:
            courses = json.load(f)

        if request.method == 'POST':
            
            courses[course_id]['title'] = request.form['title']
            courses[course_id]['description'] = request.form['description']
            courses[course_id]['overview'] = request.form['overview']
            courses[course_id]['course_content'] = request.form['course_content']
            courses[course_id]['instructor_name'] = request.form['instructor_name']
            courses[course_id]['instructor_designation'] = request.form['instructor_designation']
            courses[course_id]['testimonials_count'] = request.form['testimonials_count']
            courses[course_id]['feedback_average'] = request.form['feedback_average']

            with open('courses_data.json', 'w') as f:
                json.dump(courses, f)

            return redirect(url_for('course_detail', course_id=course_id))

        course = courses[course_id]
        return render_template('edit_course.html', course=course, course_id=course_id)

    except (IndexError, FileNotFoundError):
        return "Course not found", 404

if __name__ == '__main__':
    scrape_courses() 
    app.run(debug=True)