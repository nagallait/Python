import requests
import openpyxl
import csv
import time

# API Key for What CMS API 
api_key = "w2y2a94amiw4oqqq1772mvbl71dpcw25c7wz2z4ci60owhi6ifknidah09lrtwr9bfe39f"

#website_names = ["hazel.com.sg", "grunn.sg"]

# fn to read website names from CSV file
def read_website_names_from_csv(file_path):
    website_names = []
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            website_names = [row[0] for row in csv_reader]
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    return website_names


# Read website names from CSV
csv_file_path = "website_names.csv"
website_names = read_website_names_from_csv(csv_file_path)
urls = [f"https://{name}" for name in website_names]


# fn to request
def analyze_website(url):
    api_url = f"https://whatcms.org/API/Tech?key={api_key}&url={url}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check for status 120 limit 10 sec
        if data.get("result", {}).get("code") == 120:  
            retry_in = data.get("retry_in_seconds", 10) 
            print(f"Rate limited. Retrying in {retry_in} seconds...")
            time.sleep(retry_in)
            return analyze_website(url)
        
        # Process the results when 200
        if data.get("result", {}).get("code") == 200:  
            # Initialize n order the columns
            technologies = {
                "Blog_CMS": "",
                "E-Commerce_CMS": "",
                "Programming_Language": "",
                "Database": "",
                "CDN": "",
                "Web_Server": "",
                "Landing_Page_Builder_CMS": "",
                "Operating_System": "",
                "Web_Framework": "",
            }

            # Map technologies to specific columns based on categories
            for tech in data.get("results", []):
                name = tech.get("name", "")
                version = tech.get("version", "")
                categories = ", ".join(tech.get("categories", []))

                # Check and map based on technology type
                if "Blog" in categories or "CMS" in categories:
                    technologies["Blog_CMS"] = f"{name} {version}"
                if "E-commerce" in categories:
                    technologies["E-Commerce_CMS"] = f"{name} {version}"
                if "Programming Language" in categories:
                    technologies["Programming_Language"] = f"{name} {version}"
                if "Database" in categories:
                    technologies["Database"] = f"{name} {version}"
                if "CDN" in categories:
                    technologies["CDN"] = f"{name} {version}"
                if "Web Server" in categories:
                    technologies["Web_Server"] = f"{name} {version}"
                if "Landing Page Builder" in categories or "CMS" in categories:
                    technologies["Landing_Page_Builder_CMS"] = f"{name} {version}"
                if "Operating System" in categories:
                    technologies["Operating_System"] = f"{name} {version}"
                if "Web Framework" in categories:
                    technologies["Web_Framework"] = f"{name} {version}"

            return {
                "url": url,
                "whatcms_link": f"https://whatcms.org/?s={url}",
                "technologies": technologies,
                "whatcms_response": "200 - Success",
            }
        else:
            print(f"Error in API response for {url}: {data.get('result', {}).get('msg', 'Unknown error')}")
            return {
                "url": url,
                "whatcms_link": f"https://whatcms.org/?s={url}",
                "technologies": {
                    "Blog_CMS": "",
                    "E-Commerce_CMS": "",
                    "Programming_Language": "",
                    "Database": "",
                    "CDN": "",
                    "Web_Server": "",
                    "Landing_Page_Builder_CMS": "",
                    "Operating_System": "",
                    "Web_Framework": "",
                },
                "whatcms_response": f"{data.get('result', {}).get('code')} - {data.get('result', {}).get('msg', 'Error')}",
            }
    else:
        print(f"HTTP Error for {url}: {response.status_code}")
        return {
            "url": url,
            "whatcms_link": f"https://whatcms.org/?s={url}",
            "technologies": {
                "Blog_CMS": "",
                "E-Commerce_CMS": "",
                "Programming_Language": "",
                "Database": "",
                "CDN": "",
                "Web_Server": "",
                "Landing_Page_Builder_CMS": "",
                "Operating_System": "",
                "Web_Framework": "",
            },
            "whatcms_response": f"HTTP Error {response.status_code}",
        }

# add all websites and collect results with 10 sec delay each
results = []
for website in urls:
    results.append(analyze_website(website))
    time.sleep(10)  

# Create and save results to an Excel file
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "CMS Analysis"

# Write headers for the Excel
headers = ["url", "whatcms_link", "Blog_CMS", "E-Commerce_CMS", "Programming_Language", 
           "Database", "CDN", "Web_Server", "Landing_Page_Builder_CMS", "Operating_System", 
           "Web_Framework", "whatcms_response"]
sheet.append(headers)

# Write output in rows
for result in results:
    technologies = result["technologies"]
    sheet.append([
        result["url"],
        result["whatcms_link"],
        technologies["Blog_CMS"],
        technologies["E-Commerce_CMS"],
        technologies["Programming_Language"],
        technologies["Database"],
        technologies["CDN"],
        technologies["Web_Server"],
        technologies["Landing_Page_Builder_CMS"],
        technologies["Operating_System"],
        technologies["Web_Framework"],
        result["whatcms_response"]
    ])

# Save the Excel file in path dir
excel_file = "CMS_Analysis.xlsx"
workbook.save(excel_file)

print(f"Results saved in the file: {excel_file}")