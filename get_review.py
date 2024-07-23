import requests
from bs4 import BeautifulSoup
import csv
import re
from concurrent.futures import ThreadPoolExecutor



def fetchCompanyData(row):
    try:
        div1 = row.find("div", class_='tw-order-2')
        divs = div1.find_all("div")
        company_name = divs[0].text.strip() if len(divs) > 0 else "N/A"
        country = divs[1].text.strip() if len(divs) > 1 else "N/A"
        div2 = row.find("div", class_='tw-order-1')
        star_element = div2.find('div', class_='tw-flex tw-relative tw-space-x-0.5 tw-w-[88px] tw-h-md')

# Get the value of the aria-label attribute
        aria_label = star_element.get('aria-label')
        match = re.search(r'(\d+) out of (\d+) stars', aria_label)
        if match:
            star_count = int(match.group(1))
            total_stars = int(match.group(2))
            
        else:
            print("No star count found")
        stars = star_count
        date_element = div2.find('div', class_='tw-text-body-xs tw-text-fg-tertiary')
        date = date_element.text.strip()
        review_element = div2.find('p', class_='tw-break-words')
        review = review_element.text.strip()

        

        return [company_name, review, stars, date,country ]
    except Exception as e:
        print(f"Error fetching company data: {e}")
    return None

def main():
    company_data = []
    # URL of the company search page
    for page in range(1, 259):
        url = 'https://apps.shopify.com/plug-in-seo/reviews?search_id=79ded6de-d3ca-46f7-962c-7e349ff61f95&sort_by=relevance&page=' + str(page)
        try:
            r = requests.get(url)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # Finding all <tr> elements with the class 'ng-star-inserted'
            rows = soup.find_all('div', class_='tw-pb-md')
            print(page,len(rows))
            # print(rows[0])
            # List to store company data
            

            # Use ThreadPoolExecutor to fetch data in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = executor.map(fetchCompanyData, rows[:-1])
                
            for result in results:
                if result:
                    company_data.append(result)
            
           
        except requests.RequestException as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"Error in main function: {e}")
    # print(company_data)
    #  Write the data to a CSV file
    with open('info.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Shop name", "Review", "Stars", "Date", "Country"])
        writer.writerows(company_data)
if __name__ == "__main__":
    main()
