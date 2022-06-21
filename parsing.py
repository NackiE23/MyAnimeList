import requests
from bs4 import BeautifulSoup


def main():
    text = requests.get('https://myanimelist.net/anime/season').text
    soup = BeautifulSoup(text, "lxml")

    title = soup.title.text.strip()
    print(f"{title=}")

    current_season = soup.select(".season_nav")[0].text.strip()
    print(f"{current_season=}")

    genres = soup.find_all('li', {'class': "js-btn-sort-order btn-sort-order fa-stack"})
    genres = [genre.text.strip() for genre in genres]
    print(f"{genres=}")

    anime = soup.select(".h2_anime_title .link-title")
    anime = [a.text.strip() for a in anime]
    print(f"{anime=}")

    anime_blocks = soup.select("div.js-anime-type-1")
    anime_blocks_date = [a.select(".info .item")[0].text.strip() for a in anime_blocks]
    anime_blocks_series = ["".join(
        (a.select(".info .item:nth-child(2) span:nth-child(1)")[0].text.strip(),
         ", ",
         a.select(".info .item:nth-child(2) span:nth-child(2)")[0].text.strip()
         )
    ) for a in anime_blocks]
    print(f"{anime_blocks_date=} \n"
          f"{anime_blocks_series=}")


if __name__ == "__main__":
    main()
