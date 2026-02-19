import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class WebScraper:
    
    #init method to initialize the class with headless option and set up variables for driver and coins data
    
    def __init__(self, headless=True ):
        self.headless = headless
        self.driver = None
        self.coins_data=[]

    def initialize_driver(self):
        
        # set the web driver options
        
        chrome_options = webdriver.ChromeOptions()
        if self.headless:
            chrome_options.add_argument("--headless")  
            chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # initialize the web driver
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("✓ Chrome WebDriver initialized successfully")
    def top_Coins(self):
        self.driver.get("https://coinmarketcap.com/")
        try:
            # Wait until the table is loaded
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME,"tbody"))
            )
            
            # Find the top 10 coins
            
            coins = self.driver.find_elements(By.TAG_NAME,"tr")[2:12]  # Skip the header row and get the top 10 rows
            print("✓ Successfully found the top 10 coins")
            
            for coin in coins:
                
                #If the name has a specific class like <p class="coin-name">
                # Find the table cell, then the link, then the paragraph
                # Get all 'p' tags inside the coin row
                #find the Coin_name
                
                paragraphs = coin.find_elements(By.TAG_NAME, "p")
                
                # Usually:
                # paragraphs[0] is the Rank (e.g., "1")
                # paragraphs[1] is the Name (e.g., "Bitcoin")
                
                if len(paragraphs) > 1:
                    coin_name = paragraphs[1].text
                
                # Find the Coin Price
                # 1. Get all table cells in the current coin row
                
                cells = coin.find_elements(By.TAG_NAME, "td")
                
                # 2. On CoinMarketCap, the price is usually in the 4th cell (index 3)
                # It is often wrapped in a <span> tag
                
                price_cell = cells[3]
                price_text = price_cell.find_element(By.TAG_NAME, "span").text
                
                #Find the market Cap in coins between 
                
                cell = coin.find_elements(By.TAG_NAME, "td")
                
                if len(cells) > 7:
                    Market_cell = cell[7]
                    try:
                        market_cap = Market_cell.find_element(By.TAG_NAME, "p").text
                    except:
                        # Fallback if it's directly in a span
                        market_cap = Market_cell.text
                       
                #24 hours volume in the coins
                
                cell1 = coin.find_elements(By.TAG_NAME, "td")
                hours= cell1[5]
                hours_value = hours.find_element(By.TAG_NAME, "span").text
                
                # data will e append to the coins_data variable
                
                self.coins_data.append({
                    "name": coin_name, 
                    "price": price_text,
                    "market_cap": market_cap,
                    "24h_volume": hours_value                  
                })
                print(f"✓ Scraped {len(self.coins_data)} coins.")
        except Exception as e:
            print(f"Error while scraping: {e}")
        finally:
            self.driver.quit()
    
    # save the data to a csv file
    def save_to_csv(self, filename="crypto_data.csv"):
        if not self.coins_data:
            print("No data available to save.")
            return

        # 1. Convert the list of dictionaries into a DataFrame
        
        df = pd.DataFrame(self.coins_data)

        # 2. Save the DataFrame to a CSV file
        # index=False prevents Pandas from adding a row number column
        
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"✓ Data saved to {filename} using Pandas.")
       
# Main function to run the scraper

def main():
    scraper = WebScraper(headless=True)
    scraper.initialize_driver()
    scraper.top_Coins()
    scraper.save_to_csv(filename="crypto_data.csv")

# Run the main function

if __name__ == "__main__":
    main()