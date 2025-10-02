import re
from bs4 import BeautifulSoup

def match_filters(item : dict, filters: dict):
    print(f"\n--- Filtering Item: {item['title']} ---")
    print(f"Item data: {item}")
    print(f"Filters: {filters}")
    try:
        # Year filter
        if "year_min" in filters and item["year"] < filters["year_min"]:
            print(f"Filter failed: Year (min) - {item['year']} < {filters['year_min']}")
            return False
        if "year_max" in filters and item["year"] > filters["year_max"]:
            print(f"Filter failed: Year (max) - {item['year']} > {filters['year_max']}")
            return False

        # Price filter
        if "price_min" in filters and item["price"] < filters["price_min"]:
            print(f"Filter failed: Price (min) - {item['price']} < {filters['price_min']}")
            return False
        if "price_max" in filters and item["price"] > filters["price_max"]:
            print(f"Filter failed: Price (max) - {item['price']} > {filters['price_max']}")
            return False

        # KM filter
        if "km_min" in filters and item["km"] < filters["km_min"]:
            print(f"Filter failed: KM (min) - {item['km']} < {filters['km_min']}")
            return False
        if "km_max" in filters and item["km"] > filters["km_max"]:
            print(f"Filter failed: KM (max) - {item['km']} > {filters['km_max']}")
            return False

        # Engine size filter
        if "engine_size_min" in filters and item["engine_size"] < filters["engine_size_min"]:
            print(f"Filter failed: Engine Size (min) - {item['engine_size']} < {filters['engine_size_min']}")
            return False
        if "engine_size_max" in filters and item["engine_size"] > filters["engine_size_max"]:
            print(f"Filter failed: Engine Size (max) - {item['engine_size']} > {filters['engine_size_max']}")
            return False

        # Engine type filter
        if "engine_type" in filters:
            matched_engine_type = False
            item_engine_type_lower = item["engine_type"].lower()
            for et_filter in filters["engine_type"]:
                if et_filter.lower() == item_engine_type_lower.lower():
                    matched_engine_type = True
                    break
            if not matched_engine_type:
                print(f"Filter failed: Engine Type - {item['engine_type']} not in {filters['engine_type']}")
                return False

        # Location filter
        if "location" in filters:
            matched_location = False
            item_location_lower = item["location"].lower()
            for loc_filter in filters["location"]:
                if loc_filter.lower() in item_location_lower:
                    matched_location = True
                    break
            if not matched_location:
                print(f"Filter failed: Location - '{item['location']}' does not contain any of {filters['location']}")
                return False

        print(f"Item {item['title']} PASSED all filters.")
        return True
    except (KeyError, TypeError) as e:
        print(f"Error during filtering: {e} for item: {item} and filters: {filters}")
        return False

def scrape_listings(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    listings = []
    listing_data = soup.find(id="listingData")
    if not listing_data:
        print("No listing data found on the page.")
        return listings

    ads = listing_data.select("div.product-card")
    for ad in ads:
            title_element = ad.select_one(".product-card__title")
            title = title_element.get_text(strip=True) if title_element else "N/A"

            price_element = ad.select_one(".product-card__price-main")
            price_text = price_element.get_text(strip=True) if price_element else "0"
            price_cleaned = re.sub(r'[\s€]', '', price_text)
            price = int(price_cleaned) if price_cleaned.isdigit() else 0

            link_element = ad.select_one("a.product-card-link__tricky-link")
            link = link_element.get("href") if link_element else "N/A"

            image_element = ad.select_one("img.img-object-fit-cover")
            image = image_element.get("src") if image_element else "N/A"

            location_element = ad.select_one(".product-card__address")
            location = location_element.get_text(strip=True) if location_element else "N/A"

            sub_info = ad.select_one(".product-card__sub-title")
            engine_size_text = sub_info.get_text(strip=True) if sub_info else "0.0"
            engine_size_match = re.search(r"\d+[.,]\d+", engine_size_text)
            engine_size = float(engine_size_match.group().replace(',', '.')) if engine_size_match else 0.0

            basic_info = ad.select_one(".product-card__basic-info-list")
            if basic_info:
                year_text = basic_info.find_all("span")[0].get_text(strip=True)
                year = int(year_text) if year_text.isdigit() else 0

                km_text = basic_info.find_all("span")[1].get_text(strip=True)
                km_cleaned = re.sub(r'[^\d]', '', km_text)
                km = int(km_cleaned) if km_cleaned.isdigit() else 0
                
                engine_type = basic_info.find_all("span")[2].get_text(strip=True).replace('●', '').strip()
            else:
                year, km, engine_type = 0, 0, "N/A"


            if link and not link.startswith("https://"):
                link = f"https://www.nettiauto.com{link}"

            listings.append({
                'title': title, 
                'price': price, 
                'link': link,
                'image': image,
                'location': location,
                'year': year,
                'km': km,
                'engine_size': engine_size,
                'engine_type': engine_type
            })
    return listings

