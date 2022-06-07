from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from parameter import *
import pandas as pd

class Scrape:
    def get_data_from_category(self, category_name):
        category_url = categories[category_name]['page-1']
        self.driver.get(category_url)
        xpath = '//*[@id="products-inner"]'
        product_list = self.driver.find_element(By.XPATH, xpath)
        page = 1
        
        data_temp = f'data_{category_name}_pg_{page}.txt'
        image_temp = f'img_{category_name}_pg_{page}.txt'

        self.file_text_names[category_name].append(data_temp)
        self.file_img_names[category_name].append(image_temp)

        file = open(data_temp, 'w')
        file.write(product_list.text)
        file.close()

        file = open(image_temp, 'w')
        for i in range(30):
            print(f"Getting {category_name} image {i + 1}!")
            file.write(str(self.get_img_from_category(i + 1) + '\n'))
        file.close()

        page += 1
        # while page < self.max_pages:
            # To go next page, failed :(
            # xpath_page = '//*[@id="catalog-wrapper"]/main/div/div/nav/ul/li[2]/a'
            # self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_page))).click()
            # product_list = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            # data_temp = f'data_ikra_pg_{page}.txt'
            # image_temp = f'img_{category_name}_pg_{page}.txt'
            # self.file_text_names[category_name].append(data_temp)
            # self.file_img_names[category_name].append(image_temp)
            # file = open(data_temp, 'w')
            # file.write(product_list.text)
            # file.close()
            # images = []
            # for i in range(30):
            #     images.append(self.get_image(i + 1))
            # file = open(image_temp, 'w')
            # for image in images:
            #     file.write(str(image))
            # file.close()
            # page += 1

        print("Data have been scraped!")
    
    def get_img_from_category(self, i):
        xpath = f'//*[@id="products-inner"]/div[{i}]/div[1]/div[1]/div/a/img'
        try:
            image_list = self.driver.find_element(By.XPATH, xpath)
            return image_list.get_attribute('src')
        except:
            return "Нет фото"

    def convert_data(self):
        for category in categories:
            data_final = {
                "name": [],
                "price": [],
                "unit": [],
                "image": []
            }
            for file_img_name in self.file_img_names[category]:
                file = open(file_img_name, 'r')
                lines = file.read().splitlines()
                file.close()
                
                for image in lines:
                    data_final['image'].append(image)

            for file_text_name in self.file_text_names[category]:
                file = open(file_text_name, 'r')
                lines = file.read().splitlines()
                file.close()            
                count = 1
                for text in lines:
                    if count % 5 == 1:
                        if self.has_whitespace(text):
                            price = text.replace(' ', '')
                            if self.is_float(price):
                                data_final['price'].append(float(price))
                                count += 1
                        else:
                            data_final['price'].append(float(text))
                            count += 1
                    elif count % 5 == 2:
                        count += 1
                    elif count % 5 == 3:
                        data_final['unit'].append('₽' + text)
                        count += 1
                    elif count % 5 == 4:
                        if self.is_float(text):
                            continue
                        if self.has_whitespace(text):
                            price = text.replace(' ', '')
                            if self.is_float(price):
                                continue
                        if text != ' д':
                            data_final['name'].append(text)
                            count += 1
                        else:
                            continue   
                    elif count % 5 == 0:
                        count += 1
            self.all_data[category] = data_final  

    def save_data(self):
        self.convert_data()
        writer = pd.ExcelWriter(self.data_file, engine='openpyxl')

        for sheet_name in categories:
            df = pd.DataFrame(data=self.all_data[sheet_name])

            print(df)

            df.to_excel(writer, index=False, sheet_name=sheet_name)

        writer.save()
        print(f"Data have been saved to {self.data_file}")

    def has_whitespace(self, s):
        return ' ' in s

    def is_float(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=options, executable_path=path)
        self.url = site_main_url
        self.data_file = 'result.xlsx'
        self.wait = WebDriverWait(self.driver, 10)
        self.max_pages = 2
        self.file_text_names = {
            "ikra": [],
            "coffee_beans": [],
            "bread": []
        }
        self.file_img_names = {
            "ikra": [],
            "coffee_beans": [],
            "bread": []
        }
        self.all_data = {
            "ikra": [],
            "coffee_beans": [],
            "bread": []
        }

s = Scrape()
for category_name in category_names:
    s.get_data_from_category(category_name)
s.save_data()
