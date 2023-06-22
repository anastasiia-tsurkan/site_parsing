import csv
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://webscraper.io/"
LAPTOP_URL = urljoin(BASE_URL, "test-sites/e-commerce/allinone/computers/laptops")

PRODUCT_OUTPUT_CSV_PATH = "products.csv"


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int


PRODUCT_FIELDS = [field.name for field in fields(Product)]


def parse_single_product(product_soup: BeautifulSoup) -> Product:
    return Product(
        title=product_soup.select_one(".title")["title"],
        description=product_soup.select_one(".description").text,
        price=float(product_soup.select_one(".price").text.replace("$", "")),
        rating=int(product_soup.select_one("p[data-rating]")["data-rating"]),
        num_of_reviews=int(product_soup.select_one(
            ".ratings > p.pull-right"
        ).text.split()[0])
    )


def get_num_pages(page_soup: BeautifulSoup) -> int:
    pagination = page_soup.select_one(".pagination")

    if pagination is None:
        return 1

    return int(pagination.select("li")[-2].text)  # "a.page-link"


def get_single_page_products(page_soup: BeautifulSoup) -> [Product]:
    products = page_soup.select(".thumbnail")

    return [parse_single_product(product_soup) for product_soup in products]


def get_laptop_products() -> [Product]:
    page = requests.get(LAPTOP_URL).content
    first_page_soup = BeautifulSoup(page, "html.parser")

    # get num of pages
    num_pages = get_num_pages(first_page_soup)

    all_products = get_single_page_products(first_page_soup)

    for page_num in range(2, num_pages + 1):
        page = requests.get(LAPTOP_URL, {"page": page_num}).content
        soup = BeautifulSoup(page, "html.parser")
        all_products.extend(get_single_page_products(soup))

    return all_products


def write_products_to_csv(products: [Product]) -> None:
    with open(PRODUCT_OUTPUT_CSV_PATH, "w") as file:
        writer = csv.writer(file)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([astuple(product) for product in products])


def main():
    products = get_laptop_products()
    write_products_to_csv(products)


if __name__ == '__main__':
    main()
