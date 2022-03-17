from re import search
import feedparser
import re

moet_rss_url = "https://moet.gov.vn/rss/Pages/index.aspx?ItemID=54"
answer = ""
feed = feedparser.parse(moet_rss_url)


def main():
    for i in range(10):
        if re.search("(H|h)ọc sinh giỏi quốc gia", feed.entries[i].title):
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
