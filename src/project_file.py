import requests
from bs4 import BeautifulSoup as bs 
import pandas as pd
import html
import numpy as np
from urllib.parse import urljoin
import logging
import streamlit as st
logging.basicConfig(filename="extract_data.log",level=logging.DEBUG,format="%(asctime)s:%(levelname)s:%(message)s")

class FetchElectronicDetails:
    def __init__(self, product):
        self.product = product
        self.url = f"https://www.flipkart.com/search?q={self.product}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off&page=1"

    def processing_link(self):
        try:
            self.response = requests.get(self.url)
            if self.response.status_code == 200:
                self.data1 = bs(self.response.content, 'html.parser')
                self.df = self.data1.select('._1YokD2._2GoDe3 > ._1YokD2._3Mn1Gg > ._1AtVbE.col-12-12')
                self.page = self.data1.select('._10Ermr')[0].text
                self.products_page_length = int(self.page[self.page.index('1') + 3: self.page.index('of')].replace(',', '').strip())
                self.total_product_count = int(self.page[self.page.index('of') + 3: self.page.index('results')].replace(',', '').strip())
                self.no_pages = int(np.ceil(self.total_product_count / self.products_page_length))
                return True
        except Exception as e:
            logging.debug("Failed to process the link. Error: %s", str(e))
            return False

    def all_product_links(self):
        self.pages_links = []
        self.product_links = []
        try:
            if self.processing_link():
                
                for i in range(1, self.no_pages + 1):
                    self.new_page_url = urljoin(self.url, f"&page={i}")
                    self.pages_links.append(self.new_page_url)

                for link in self.pages_links:
                    self.url = link
                    self.lf1 = 'https://www.flipkart.com'
                    for j in range(min(len(self.df), len(self.df) - 2)):
                        self.href = self.df[j].find_all('a')
                        if self.href:
                            self.href1 = self.href[0].get('href')
                            self.href_final = self.lf1 + self.href1
                            self.product_links.append(self.href_final)
                logging.info("succesfully fetched all the links")
                return self.product_links
        except Exception as e:
            logging.debug("unable to fetch page links Error: %s", str(e))
            return []

#for few products/in few links  in collecting reviews and rating the order follows  class='_3_L3jD>.gUuXy- _16VRIQ>._2_R_DZ' not the otherway.

class ProductDetails:
    def __init__(self, product_links):
        self.product_links = product_links
        self.data_products = []
        self.product_descriptions = []
        self.resulted=None
        self.keys=['RAM&STORAGE', 'DISPLAY', 'CAMERA', 'BATTERY','PROCESSOR','Additional_info']
        self.data_dict={self.key:[] for self.key in self.keys}
        self.temp_dict={}
        self.highlight_data=pd.DataFrame()
        
    def process_1a(self, url1):
        try:
            self.response1 = requests.get(url1)
            if self.response1.status_code == 200:
                logging.info("successfully fetched Response Object")
                self.referenced_data = bs(self.response1.content, 'html.parser').body.select('#container')[0]
                self.rd = self.referenced_data.find_all('div')
                self.rd1 = self.rd[0].select('._2c7YLP.UtUXW0._6t1WkM._3HqJxg ')
                self.rd2 = self.rd1[0].select('._1YokD2._3Mn1Gg.col-8-12 ')
                self.rd3 = self.rd1[0].select('.aMaAEs')
                self.rd4 = self.rd1[0].select('._1AtVbE.col-12-12>.col.JOpGWq')
                self.highlights = self.rd1[0].select_one('._1AtVbE.col-6-12>._2cM9lP>._2418kt')
                self.hl1 = self.highlights.find_all('li')
                logging.info("successfully pulled the process_1a elements")
                return self.rd1, self.rd3, self.rd4, self.hl1
            else:
                logging.debug("Error loading the link {url1}. Status code: {self.response1.status_code}")
                return None
        except Exception as e:
            logging.debug("unable to fetch elements: %s",str(e))
            return None
    
    def highlight_info(self):
        try:
            temp_dict = {key: None for key in self.keys}
            for i, tag in enumerate(self.hl1):
                value = tag.text if tag else None
                temp_dict[self.keys[i]] = value  

            for key in self.keys:
                self.data_dict[key].append(temp_dict[key])
            logging.info("Successfully fetched data_dict dictionary variable")
            return self.data_dict
        except Exception as e:
            logging.debug("unable to fetch data_dict dictionary variable:: %s",str(e))
            


    def extract_product_details(self):
        for i, v1 in enumerate(self.product_links[:400]):
            self.highlight_data = {}
            self.r1 = self.process_1a(v1)
          
            
            if self.r1 is not None:
                logging.info(" r1 element is found")
                self.rd1, self.rd3, self.rd4, self.hl1=self.r1
                if self.rd3 is not None :
                    logging.info("rd3 element is found")
                    try:
                        self.title = self.rd3[0].select('h1')[0].text
                        self.a1 = self.rd3[0].select_one('.CEmiEU>._25b18c').find_all('div')
                        self.offer_price = self.a1[0].text if self.a1[0] else None
                        self.actual_price = self.a1[1].text if self.a1[1] else None
                        self.offer_rate = self.a1[2].text if self.a1[2] else None
                        self.rr_ = self.rd3[0].select('._3_L3jD>.gUuXy-._16VRIQ')[0].select('._2_R_DZ')[0].text
                        self.Rating = self.rr_[:self.rr_.index('Ratings')]
                        self.Reviews = self.rr_[self.rr_.index('&') + 2:]
                        
                        
                        self.product_description = {
                            'Model name': self.title,
                            'Actual Price': self.actual_price,
                            'Offer Price': self.offer_price,
                            'NRating': self.Rating,
                            'NReviews': self.Reviews
                        }

                        self.product_descriptions.append(self.product_description)
                        
                        if self.hl1:
                            self.data_dict1=self.highlight_info()
                        logging.info("successfully fetched data_dict1 data")
                    except Exception as e:
                        logging.debug("Error extracting product details {v1}: {e}")
                        continue


        return self.product_descriptions,self.data_dict1


    def result1(self):
        try:
            data1, data2 = self.extract_product_details()
            self.df = pd.DataFrame(data1)
            self.highlight_data = pd.DataFrame(data2)
            self.resulted = pd.concat([self.df, self.highlight_data], axis=1, ignore_index=True)
            self.resulted.columns=['Model name', 'Actual Price','Offer Price','NRating','NReviews','RAM&STORAGE','DISPLAY','CAMERA','BATTERY','PROCESSOR','Additional_info']
        except Exception as e:
            logging.debug("unable to fetch result: %s",str(e))
            
        return self.resulted
        

def page1():
    """This function returns Data files containing .csv,.json files from Webscraping package"""
    st.title("ECOMMERCE MOBILE DATA SCRAPER")
    link_data_list=None
    product_name=''
    product_name = st.text_input("Provide an product name to scrape")
    
    if st.button("Fetch Data"):
        with st.spinner("Please wait.Scraper might take a moment......."):
            
            ft = FetchElectronicDetails(product_name)
            link_data_list = ft.all_product_links()

            va1 = ProductDetails(link_data_list)
            result = va1.result1()

        st.success("Data successfully scraped!")
        
        st.dataframe(result)
        
        # Create download buttons for CSV and JSON files
        st.download_button('Download Csv file',result.to_csv(),file_name=f"{product_name}.csv")
        st.download_button('Download Json file',result.to_json(),file_name=f"{product_name}.json")
        

def main():
    if getattr(st.session_state, 'page', 1) == 1:
        page1()

if __name__ == "__main__":
    main()
