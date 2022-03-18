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
        print(post.title)
        if re.search("(H|h)ọc sinh giỏi quốc gia", post.title):
            found = True
            break
        found = False
    result_file_write(found)


def result_file_write(found):
    if found == True:
        answer = "Results are in."
    else:
        answer = "Not yet."

    with open("result.txt", "w") as result_file:
        result_file.write(answer)


if __name__ == "__main__":
    main()
