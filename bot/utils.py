from bs4 import BeautifulSoup

def match_filters(item : dict, filters: dict):
    try:
        return (
            filters["year_min"] <= item["year"] <= filters["year_max"]
            and filters["price_min"] <= item["price"] <= filters["price_max"]
            and filters["km_min"] <= item["km"] <= filters["km_max"]
            and filters["engine_size_min"] <= item["engine_size"] <= filters["engine_size_max"]
            and item["engine_type"].lower() in [e.lower() for e in filters["engine_type"] ]
        )
    except KeyError:
        return  False

def scrape_listings(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    listings = []
    listing_data = soup.find(id="listingData")
    if listing_data:
        ads = listing_data.select("div.product-card")
        for ad in ads:
            title_element = ad.select_one(".product-card__title")
            title = title_element.get_text(strip=True) if title_element else "N/A"

            price_element = ad.select_one(".product-card__price-main")
            price = price_element.get_text(strip=True) if price_element else "N/A"

            link_element = ad.select_one("a.product-card-link__tricky-link")
            link = link_element.get("href") if link_element else "N/A"

            image_element = ad.select_one("img.img-object-fit-cover")
            image = image_element.get("src") if image_element else "N/A"

            location_element = ad.select_one(".product-card__address")
            location = location_element.get_text(strip=True) if location_element else "N/A"

            sub_info = ad.select_one(".product-card__sub-title")
            engine_size = sub_info.get_text(strip=True) if sub_info else "N/A"

            basic_info = ad.select_one(".product-card__basic-info-list")
            if basic_info:
                year = basic_info.find_all("span")[0].get_text(strip=True)
                km = basic_info.find_all("span")[1].get_text(strip=True)
                engine_type = basic_info.find_all("span")[2].get_text(strip=True)
            else:
                year, km, engine_type = "N/A", "N/A", "N/A"


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

