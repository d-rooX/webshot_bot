import io

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import numpy as np
from PIL import Image

from config import WEBDRIVER_PATH


def hide_fixed(driver, depth, element):
	"""
	Search fixed elements on a page and hide them

	:param driver: webdriver
	:param depth: recursion depth
	:param element: element from need to start crawling. i.e body
	:return:
	"""
	if depth == 0:
		return

	res = driver.execute_script('return arguments[0].children', element)
	for el in res:
		if el.value_of_css_property('position') == 'fixed':
			hide_element(driver, el)

		hide_fixed(driver, depth - 1, el)


def hide_element(driver, element):
	"""
	Hide element from the page

	:param driver: webdriver
	:param element: element to hide
	:return:
	"""
	driver.execute_script("arguments[0].style.display = 'none' ", element)


def smooth_scroll(driver: webdriver.Chrome, current_y, scroll_to_y):
	"""
	Smoothly scroll page from current_y to scroll_to_y

	:param driver: webriver
	:param current_y:
	:param scroll_to_y:
	:return:
	"""
	while current_y < scroll_to_y:
		current_y += 20
		driver.execute_script(f"window.scrollTo(0, {current_y})")


def init_driver():
	"""
	Create and initialise driver

	:return: webdriver
	"""
	options = Options()
	options.add_argument('--headless')
	driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH, options=options)
	driver.set_window_size(1920, 1080)
	return driver


def load_page(driver, url):
	"""
	Get page and load all animated objects by scrolling it
	:param driver: webdriver
	:param url:
	:return:
	"""
	driver.get(url=url)
	driver.implicitly_wait(2)

	scroll_height = driver.execute_script("return document.body.scrollHeight")
	smooth_scroll(driver, 0, scroll_height)  # scrolling to load all animated objects
	driver.execute_script("window.scrollTo(0, 0)")  # going back


def do_screenshot(driver: webdriver.Chrome) -> io.BytesIO:
	"""
	Takes full-height screenshot of page

	:param driver: webdriver
	:return: BytesIO object
	"""
	images = []

	window_height = driver.execute_script('return window.innerHeight')
	current_Y = 0

	to_crop_pixels = None
	while True:
		# searching and hiding fixed elements on page
		try:
			hide_fixed(driver, 3, driver.find_element(by='css selector', value='body'))
		except Exception as e:
			type(e)
			continue

		# сreating in-memory buffer for picture
		filename = f'out{current_Y}.png'
		fp = io.BytesIO()
		fp.name = filename

		# saving picture in buffer
		fp.write(driver.get_screenshot_as_png())

		# cropping image with pil
		im = Image.open(fp)
		width, height = im.size
		cropped_height = window_height - to_crop_pixels if to_crop_pixels else 0
		im = im.crop((0, cropped_height, width - 20, height))
		im.save(fp)
		im.save('test.png')
		images.append(im)

		# scrolling one page down
		driver.execute_script("window.scrollBy(0, window.innerHeight)")
		old_Y = current_Y
		current_Y = driver.execute_script("return window.scrollY")
		if old_Y == current_Y:
			break

		# check if we need to crop next frame
		if (next_frame_height := current_Y - old_Y) < window_height:
			to_crop_pixels = next_frame_height

	vertical_image = Image.fromarray(np.vstack(images))

	fp = io.BytesIO()
	fp.name = 'out.png'
	vertical_image.save(fp)
	fp.seek(0)

	return fp
