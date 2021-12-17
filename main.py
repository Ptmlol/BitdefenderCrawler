import optparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv


class Search:
    global driver

    def __init__(self, url):
        self.product_title = None
        self.product_price = None
        self.product_code_link = None
        self.product_code_list = []
        self.product_title_list = []
        self.product_price_list = []
        driver.get(url)

    def search_all_products(self):
        try:
            ul_products = driver.find_elements(By.TAG_NAME, "ul")
            for prod in ul_products:
                li_products = prod.find_elements(By.CLASS_NAME, "Products-item")
                for li_a in li_products:
                    self.product_title = li_a.find_element(By.CLASS_NAME, "Product-nameHeading")
                    self.product_price = li_a.find_element(By.CLASS_NAME, "Price-current")
                    self.product_code_link = li_a.find_element(By.CLASS_NAME, "Product").get_attribute('href')
                    self.product_title_list.append(self.product_title.text)
                    self.product_price_list.append(self.product_price.text)
                    self.write_code()

        except Exception as e:
            print(e)
            pass

    def write_code(self):
        self.product_code_link = str(self.product_code_link[::-1])
        i = 1
        x = ''
        while self.product_code_link[i] != '/':
            x = x + self.product_code_link[i]
            i += 1
        self.product_code_list.append(x)

    def write_to_csv(self):
        file = open('data.csv', 'w', newline='')
        with file:
            header = ['Product Name', 'Product Price', 'Product Code', 'New Price', 'New Price 2', 'Biggest Price '
                                                                                                   'Difference',
                      'Removed']
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            for i in range(len(self.product_price_list)):
                writer.writerow({'Product Name': self.product_title_list[i],
                                 'Product Price': self.product_price_list[i],
                                 'Product Code': self.product_code_list[i],
                                 'New Price': '',
                                 'New Price 2': '',
                                 'Biggest Price Difference': '',
                                 'Removed': ''
                                 })
        file.close()

    @staticmethod
    def read_from_csv():
        old_products = []
        old_prices = []
        old_product_code = []
        with open('data.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                old_products.append(row['Product Name'])
                old_prices.append(row['Product Price'])
                old_product_code.append(row['Product Code'])
        file.close()
        return old_products, old_prices, old_product_code

    @staticmethod
    def compare_title_lists_added(csv_product_name, product_name_last_check):
        added_products = []
        product_index = []
        i = 0
        for item in product_name_last_check:
            if item not in csv_product_name:
                added_products.append(item)
                product_index.append(i)
            i += 1
        return added_products, product_index

    @staticmethod
    def compare_title_lists_removed(csv_product_name, product_name_last_check):
        removed_products = []
        product_index = []
        i = 0
        for item in csv_product_name:
            if item not in product_name_last_check:
                removed_products.append(item)
                product_index.append(i)
            i += 1
        return removed_products, product_index

    def add_to_csv(self):
        old_products_titles, old_prices, old_product_code = self.read_from_csv()
        to_add_titles, to_add_indexes = self.compare_title_lists_added(old_products_titles, self.product_title_list)
        with open(r'data.csv', 'a', newline='') as file:
            header = ['Product Name', 'Product Price', 'Product Code', 'New Price', 'New Price 2', 'Biggest Price '
                                                                                                   'Difference',
                      'Removed']

            writer = csv.DictWriter(file, fieldnames=header)
            for i in range(len(to_add_indexes)):
                writer.writerow({'Product Name': to_add_titles[i],
                                 'Product Price': self.product_price_list[to_add_indexes[i]],
                                 'Product Code': self.product_code_list[to_add_indexes[i]],
                                 'New Price': '',
                                 'New Price 2': '',
                                 'Biggest Price Difference': '',
                                 'Removed': ''
                                 })
        file.close()

    def update_csv(self):
        old_products_titles, old_prices, old_product_code = self.read_from_csv()
        to_remove_list, to_remove_index = self.compare_title_lists_removed(old_products_titles, self.product_title_list)
        header = ['Product Name', 'Product Price', 'Product Code', 'New Price', 'New Price 2', 'Biggest Price ',
                  'Difference', 'Removed']

        lines = list()
        with open('data.csv', 'r') as read_file:
            reader = csv.reader(read_file)
            for row in reader:
                for field in row:
                    if field not in header:
                        lines.append(row)
                        break
            read_file.close()
        for i in range(len(to_remove_index)):
            lines[to_remove_index[i]][6] = 'X'
        print(lines)
        with open('data.csv', 'w') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(lines)
        write_file.close()


def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-u", "--url", dest="url_parsed", help="The URL that is to be searched")
    parser.add_option("-i", "--interval", dest="interval_h", help="The interval between searches")
    (switch_opt, arguments) = parser.parse_args()
    if not switch_opt.url_parsed:
        parser.error("You need to specify the URL! Use -h for help.")
    elif not switch_opt.interval_h:
        parser.error("You need to specify the interval! Use -h for help.")
    else:
        return switch_opt


if __name__ == '__main__':
    # options_sw = get_arguments()
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 ' \
                 'Safari/537.36 '
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options, executable_path='chromedriver/chromedriver')
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                                         'Chrome/85.0.4183.102 Safari/537.36'})
    # URL = options_sw.url_parsed
    URL = "https://altex.ro/telefoane/cpl/"
    Driv
    i = 0
    # seconds = float(options_sw.interval_h) * 60 * 60
    while True:
        time.sleep(10)
        Driver = Search(URL)
        Driver.search_all_products()
        Driver.add_to_csv()
        Driver.update_csv()
        i += 1
        print("Done " + str(i) + " step(s)...\n")
