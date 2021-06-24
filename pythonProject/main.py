import csv
import time

from bs4 import BeautifulSoup
import requests
import rpa as r


class RpaProject(object):
    """
    This RPA(Robotic process automation) enters a metalmarket.eu to get information about each 1oz silver coin in the
    website and saves the data to csv file.
    """
    def __init__(self):
        self.coins_data = []
        self.headers = ["Nazwa", "Cena", 'Nominał', 'Stop', 'Rant', 'Producent', 'Waga', 'Średnica']

    def get_coin_data(self, url):
        """
        Gets the information about each coin and saves the data to a list
        :param url: A coin web address
        :type url: str
        :return: None
        """
        # Make a GET request to fetch the raw HTML content
        # This function waits for each new http request so that it wont give errors that too much requests where made
        time.sleep(5)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML,'
                                 ' like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
        html_content = requests.get(url, headers=headers).text
        coin_info = {}
        soup = BeautifulSoup(html_content, "lxml")
        table = soup.find("table", attrs={"class": "n54117_dictionary"})
        coin_info["Nazwa"] = soup.find("h1").text
        coin_info["Cena"] = soup.find("strong", attrs={"class": "projector_price_value"}).text
        coin_data = table.find_all("span")[::2]
        coin_data_names = []
        for data in coin_data:
            coin_data_names.append(data.text.replace('\n', '').strip())
        for td, th in zip(coin_data_names, table.find_all("div")):
            if td in self.headers:
                coin_info[td] = th.text.replace('\n', '').strip()
        self.coins_data.append(coin_info)

    def get_a_list_of_coins(self, url):
        """
        Gets a list of coins website to get the info about it
        :param url: A website with a list of coins
        :return:None
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML,'
                                 ' like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
        html_content = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html_content, "lxml")
        list_of_coin_pages = soup.find("ul", attrs={"class": "pagination pull-right"})
        list_of_coins = soup.find("div", attrs={"id": "search"})
        for t in list_of_coins.find_all(attrs={"class": "product-name"}, href=True):
            self.get_coin_data(f'http://metalmarket.eu/{t["href"]}')
        pages = list_of_coin_pages.find_all("a", href=True)
        for page in range(1, len(pages)):
            print(f'http://metalmarket.eu/{pages[page]["href"]}')
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML,'
                                     ' like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
            html_content = requests.get(f'http://metalmarket.eu/{pages[page]["href"]}', headers=headers).text
            soup = BeautifulSoup(html_content, "lxml")
            list_of_coins = soup.find("div", attrs={"id": "search"})
            for t in list_of_coins.find_all(attrs={"class": "product-name"}, href=True):
                self.get_coin_data(f'http://metalmarket.eu/{t["href"]}')

    def save_to_csv(self):
        """
        Saves the data to csv file
        :return: None
        """
        # Create csv file
        with open("output.csv", 'w', newline='', encoding="utf-8") as out_file:
            writer = csv.DictWriter(out_file, self.headers)
            writer.writeheader()
            for row in self.coins_data:
                if row:
                    writer.writerow(row)

    def execute(self):
        """
        Executes the program
        :return: None
        """
        r.init()
        print("Running...")
        r.url('https://www.metalmarket.eu/sw/menu/monety/1-uncjowe-monety-802.html')
        r.click('//*[@id="filter_traits1_val367"]')
        r.click('//*[@id="filter_traits510_val481"]')
        r.click('//*[@id="filters_submit"]')
        self.get_a_list_of_coins(r.url())
        r.close()
        self.save_to_csv()
        print("Finished")


if __name__ == '__main__':
    RpaProject().execute()
