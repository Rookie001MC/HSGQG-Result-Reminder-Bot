import json
from re import search
import feedparser
import re

# ItemID 54 == Tin tổng hợp [0]
# ItemID 56 == Tin Hoạt động của Bộ [1]

moet_rss_urls = [
    "https://moet.gov.vn/rss/Pages/index.aspx?ItemID=54",
    "https://moet.gov.vn/rss/Pages/index.aspx?ItemID=56",
]
posts = []


def main():
    for url in moet_rss_urls:
        posts.extend(feedparser.parse(url).entries)

    for post in posts:
        if re.search("(H|h)ọc sinh giỏi quốc gia", post.title):
            url = post.link
            found = True
            break
        found = False
    result_file_write(found, url)


def result_file_write(found, url):
    if found == True:
        data = {
            "result": 1,
            "url": url,
        }
    else:
        data = {
            "result": 0,
        }

    with open("result.json", "w") as result_file:
        json.dump(data, result_file)


if __name__ == "__main__":
    main()
