import requests
from bs4 import BeautifulSoup

from models import objects, LastPost


class Parsing:

    def __init__(self, url: str, head_url: str):
        self.url = url
        self.head_url = head_url

    @staticmethod
    async def is_new_post(post_url: str) -> bool:
        """
        :param post_url:
        :return: возвращает булево значение новый ли пост
        """
        status = await objects.get(LastPost, url=post_url)
        return False if status else True

    @staticmethod
    def get_soup(url: str, encoding: str = None) -> BeautifulSoup:
        page = requests.get(url)
        if encoding:
            page.encoding = encoding
        soup = BeautifulSoup(page.text, 'html.parser')
        return soup

    def parse(self):
        if self.head_url == 'https://www.newsru.co.il':
            return self.__parse_site_1()
        elif self.head_url == 'https://news.israelinfo.co.il':
            return self.__parse_site_2()
        elif self.head_url == 'https://mignews.com':
            return self.__parse_site_3()

        elif self.head_url == 'https://www.jpost.com':
            return self.__parse_site_4()
        elif self.head_url == 'https://en.globes.co.il':
            return self.__parse_site_5()
        elif self.head_url == 'https://www.timesofisrael.com':
            return self.__parse_site_6()

        elif self.head_url == 'https://news.walla.co.il':
            return self.__parse_site_7()
        elif self.head_url == 'https://www.ynet.co.il':
            return self.__parse_site_8()
        elif self.head_url == 'https://www.mako.co.il':
            return self.__parse_site_9()

    def __parse_site_1(self):
        soup = self.get_soup(self.url)
        posts = soup.find('div', {'class': 'topic-list-column'}).find_all('div', {'class': 'topic-list-container'})

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = self.head_url + post.find('a').get('href')

            # проверяем является ли пост новым
            if self.is_new_post(post_url):
                return parsed_posts

            title = post.find('a', {'class': 'news_list_title'}).text.replace('\n', '').strip()
            preview_text = post.find('a', {'class': 'news_list_anons'}).text

            soup = self.get_soup(post_url)

            image = soup.find('div', {'class': 'images'}).find('img')

            content = ''
            if image:
                image = image.get('src').replace('/m/', '/l/')
                content = f'<img src={image}>'

            all_p = soup.find('article', {'class': 'text'}).find_all('p')
            for p in all_p:
                text = p.get_text(strip=True)
                if 'Telegram NEWSru.co.il: самое важное за день' in text:
                    continue
                if text in content:
                    continue
                content += f'<p>{text}</p>'
            parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts

    def __parse_site_2(self):
        soup = self.get_soup(self.url)
        posts = soup.find('div', {'class': 'inner-seller'}).find_all('article', {'class': 'news-bgrnd-img'})

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = self.head_url + post.find('a').get('href')

            # проверяем является ли пост новым
            if self.is_new_post(post_url):
                return parsed_posts

            title = post.find('span', {'itemprop': 'name'}).text.replace('\n', '').strip()
            preview_text = post.find('span', {'itemprop': 'articleBody'}).text

            soup = self.get_soup(post_url)
            image = soup.find('div', {'class': 'news-image photoswipe-img'}).get('data-originalimage')
            all_p = soup.find('div', {'class': 'big-article-content'}).find_all('p')

            del(all_p[-1])

            content = f'<img src="{image}">'

            for p in all_p:
                class_ = p.get('class')
                if class_:
                    if 'copyrights-all-list' in class_:
                        all_p.remove(p)
                p = p.text.replace('\xa0\xa0', ' ').replace('\xa0', '')
                content += f'<p>{p}</p>'

            content_gallery = soup.find('div', {'id': 'contentGallery'})
            if content_gallery:
                images = content_gallery.find_all('li')
                if images:
                    for i in images:
                        image = i.find('img')
                        if image:
                            image_url = image.get('src').replace('/s', '/')
                            content += f'<img src="{image_url}">'

            parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts

    def __parse_site_3(self):
        soup = self.get_soup(self.url)
        posts = soup.find('div', {'class': 'videorubrika'}).find_all('div', {'class': 'pad2'})

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = self.head_url + post.find('h1').find('a').get('href')

            # проверяем является ли пост новым
            if self.is_new_post(post_url):
                return parsed_posts

            title = post.find('h1').find('a').text.replace('\n', '').strip()
            preview_text = post.text

            soup = self.get_soup(post_url)
            text = soup.find('div', {'class': 'textnews'}).text.split('\n')
            del(text[text.index('Поделиться'):])
            del(text[:4])

            try:
                image = self.head_url + post.find('div', {'class': 'overphoto'}).find('img').get('src')
                content = f'<img src={image}>'
            except AttributeError:
                content = ''

            twitter_post = soup.find('blockquote', {'class': 'twitter-tweet'})

            for i in text:
                i = i.replace('\r', '')
                if twitter_post:
                    twitter_post_urls = twitter_post.find_all('a')
                    for x in twitter_post_urls:
                        i = i.replace(x.text, f'<a href="{x.get("href")}">{x.text}</a>')
                content += f'<p>{i}</p>'

            parsed_posts.append([title, content, preview_text, post_url.replace('\xa0', '')])
        return parsed_posts

    # https://www.jpost.com
    def __parse_site_4(self):
        soup = self.get_soup(self.url)
        posts = soup.find_all('div', {'class': 'itc'})[6:8]

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = post.find('a').get('href')

            # проверяем является ли пост новым
            if self.is_new_post(post_url):
                return parsed_posts

            soup = self.get_soup(post_url)  # пост-detail
            title = soup.find('h1', {'class': 'g-row article-title'}).text
            preview_text = soup.find('h2', {'class': 'g-row article-subtitle'}).text
            text = soup.find('div', {'class': 'article-inner-content'}).get_text(strip=True)
            text = text.replace('Read more from Cybertech News:https://www.israeldefense.co.il/en/categories/cybertech', '')
            text = text.replace('.', '. ').replace('  ', ' ')

            blockquote_tweeter = soup.find('blockquote', {'class': 'twitter-tweet'})

            try:
                image = soup.find('div', class_='article-image').find('img', class_='lazy').get('data-original')
                content = f'<img src="{image}">' + f'{text}'
            except AttributeError:  # если не нашли image
                content = text

            if blockquote_tweeter:
                blockquote_tweeter_links = blockquote_tweeter.find_all('a')
                for i in blockquote_tweeter_links:
                    content = content.replace(i.text, f'<a href="{i.get("href")}">{i.text}</a>')

            parsed_posts.append([title, content, preview_text, post_url])
            print(post_url, title)
        return parsed_posts

    # https://en.globes.co.il/en
    def __parse_site_5(self):
        soup = self.get_soup(self.url)
        posts = []

        for x in range(1, 4):
            posts.extend(soup.find_all("div", {"class": f"element el{x}"}))

        # спаршенные посты
        parsed_posts = []

        for post in posts:

            try:
                post_url = self.head_url + post.find('a').get('href')
            except AttributeError:
                continue

            # проверяем является ли пост новым
            if self.is_new_post(post_url):
                return parsed_posts

            preview_text = post.find('p').text

            soup = self.get_soup(post_url)
            title = soup.find('h1', {'id': 'F_Title'}).text
            text = soup.find('article', ).get_text(strip=True)

            try:
                image = soup.find('picture', ).find('img', ).get('src')
                content = f'<img src={image}>{text}'
            except AttributeError:
                content = text

            parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts

    # https://www.timesofisrael.com
    def __parse_site_6(self):
        soup = self.get_soup(self.url)
        posts = soup.find('section', class_='cols4 block items sticky-sidebar-relative').find_all(
            'div', class_='item template1 news')

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = post.find('a').get('href')

            # проверяем является ли пост новым
            if self.is_new_post(post_url):
                return parsed_posts

            soup = self.get_soup(post_url, 'utf-8')
            image = soup.find('div', class_='media').find('a').find('img', ).get('src')
            title = soup.find('h1', class_='headline').text
            preview_text = post.find('div', class_='underline').find('a').text

            content = f'<img src="{image}>'

            all_p = soup.find('div', class_='the-content').find_all('p')
            for p in all_p:
                list_of_classes = p.get('class')
                if not list_of_classes:
                    content += f'<p>{p.text}</p>'

            parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts

    # https://news.walla.co.il
    def __parse_site_7(self):
        soup = self.get_soup(self.url)
        posts = soup.find('section', class_='category-content').find_all('li')

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            tries = 1
            post_url = post.find('a').get('href')

            if self.is_new_post(post_url):
                return parsed_posts

            preview_text = post.find('div', {'class': 'content'}).find('p')

            while tries < 3:
                soup = self.get_soup(post_url)

                try:
                    images = soup.find('div', class_='item-main-content').find_all('picture',
                                                                                   class_='desktop-4-3 mobile-4-3')

                    image = images[0].find('img').get('src')
                    del(images[0])

                    title = soup.find('div', class_='item-main-content').find('h1').text
                    sub_title = soup.find('div', class_='item-main-content').find('p').text

                    sections = soup.find('section', class_='article-content').find_all('section')
                except AttributeError:
                    tries += 1
                    continue

                content = f'<img src="{image}"><h4>{sub_title}</h4>'

                for section in sections:
                    list_of_classes = section.get('class')
                    if list_of_classes:
                        if 'undefined' not in list_of_classes:
                            p = section.find('p')
                            if p:
                                content += f'<p>{p.text}</p>'

                for image in images:
                    image = image.find('img').get('src')
                    content += f'<img src={image}'

                content += f'<a href={post_url}>Ссылка на источник</a>'

                parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts

    # https://www.ynet.co.il
    def __parse_site_8(self):
        soup = self.get_soup(self.url)
        posts = soup.find('div', class_='slotList').find_all('div', class_='slotView')

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = post.find('a').get('href')

            if post_url.endswith('html'):
                print('html - ' + post_url)
                continue

            # проверяем является ли пост новым
            if self.is_new_post(post_url):
                return parsed_posts

            soup = self.get_soup(post_url)
            preview_text = post.find('div', class_='slotSubTitle').find('a').text

            title = soup.find('h1').text
            sub_title = soup.find('h2', class_='subTitle').text

            content_body = soup.find('div', {'class': 'layoutItem article-body'}).find('div', {'data-contents': True})

            content = f'<h4>{sub_title}</h4>'

            for tag in content_body:
                image = tag.find('img')

                if tag.find('div', {'class': 'videoInfo'}):
                    continue

                if image:
                    classes = image.get('class')
                    if not classes:
                        content += f'<img src="{image.get("src")}">'

                if tag.name == 'ul':  # если список с ссылками, то пропускаем
                    if tag.find('a'):
                        continue

                    content += '<ul>'
                    for li in tag:
                        content += f'<li>{li.text}</li>'
                    content += '</ul>'

                if tag.get('class') == 'text_editor_contact_us_link':  # если "связаться с нами"
                    continue

                if tag.name == 'ol':
                    content += '<ol>'
                    for li in tag:
                        content += f'<li>{li.text}</li>'
                    content += '</ol>'

                if tag.find('span', {'class': 'data-offset-key'}):
                    if tag.find('span', {'class': 'data-offset-key'}).get('data-offset-key').startswith('olit'):
                        continue

                content += f'<p>{tag.text}</p>'

            parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts

    # https://www.mako.co.il
    def __parse_site_9(self):
        soup = self.get_soup(self.url)
        posts = soup.find('section', class_='content').find_all('li')

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = self.head_url + post.find('a').get('href')

            # проверяем является ли пост новым
            if self.is_new_post(post_url):
                return parsed_posts

            try:
                image = post.find('figure').find('img').get('src')
                content = f'<img src="{image}">'
            except AttributeError:
                content = ''

            soup = self.get_soup(post_url)

            title = soup.find('article').find('h1').get_text()
            sub_title = soup.find('h2')
            preview_text = soup.find('h2', ).text

            all_p = soup.find('section', class_='article-body').find_all('p')

            if sub_title:
                content += f'<h4>{sub_title.text}</h4>'

            for p in all_p:
                strong = p.find('strong')
                style = p.get('style')

                if p.find_parent('blockquote'):
                    continue
                if style:
                    continue
                if strong:
                    continue

                content += f'<p>{p.get_text(strip=True)}</p>'

            second_photo = soup.find('section', class_='article-body').find('figure')
            if second_photo:
                second_photo_url = second_photo.find('img').get('src')
                content += f'<img src="{second_photo_url}">'

            parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts


# a = Parsing(
#     'https://www.ynet.co.il/wheels/news',
#     'https://www.ynet.co.il'
# #     'https://news.israelinfo.co.il/events/', 'https://news.israelinfo.co.il'
# #     # 'https://www.newsru.co.il/health', 'https://www.newsru.co.il'
# #     # 'https://www.jpost.com/international', 'https://www.jpost.com'
# #     # 'https://www.jpost.com/israel-news/arabisrael/',
# #     # 'https://www.jpost.com'
# #     # 'https://mignews.com/news/arabisrael/',
# #     # 'https://mignews.com'
# # )
# # #     # 'https://www.timesofisrael.com/topic/crime-in-israel',
# # #     # 'https://www.timesofisrael.com'
# # #     'https://www.jpost.com/cybertech',
# # #     'https://www.jpost.com'
# # #     'https://www.mako.co.il/news-digital?partner=NewsNavBar',
# # #     'https://www.mako.co.il'
# )
# posts = a.parse()
# # # # # # print(posts)
# # # # # #
# # # # # #
# from create_article import create_article
#
# for post in posts:
#     page = create_article(post[0], post[1])
#     print(page)
