import logging

import requests

from bs4 import BeautifulSoup

from typing import Optional

from utils.db_api.article.last_post import is_new_post


logging.basicConfig(level=logging.INFO)


class Parsing:
    def __init__(self, url: str, head_url: str):
        self.url = url
        self.head_url = head_url

    @staticmethod
    def get_soup(url: str, encoding: str = None) -> Optional[BeautifulSoup]:
        try:
            page = requests.get(url)
        except requests.exceptions.ConnectionError:
            return None
        if encoding:
            page.encoding = encoding
        soup = BeautifulSoup(page.text, 'html.parser')
        return soup

    async def parse(self):
        try:
            if self.head_url == 'https://www.newsru.co.il':
                return await self.__parse_site_1()
            elif self.head_url == 'https://news.israelinfo.co.il':
                return await self.__parse_site_2()
            elif self.head_url == 'https://mignews.com':
                return await self.__parse_site_3()

            elif self.head_url == 'https://www.jpost.com':
                return await self.__parse_site_4()
            elif self.head_url == 'https://en.globes.co.il':
                return await self.__parse_site_5()
            elif self.head_url == 'https://www.globes.co.il':
                return await self.__parse_site_13()
            elif self.head_url == 'https://www.timesofisrael.com':
                return await self.__parse_site_6()

            elif self.head_url == 'https://news.walla.co.il':
                return await self.__parse_site_7()
            elif self.head_url == 'https://www.ynet.co.il':
                return await self.__parse_site_8()
            elif self.head_url == 'https://www.mako.co.il':
                return await self.__parse_site_9()

            elif self.head_url == 'https://passportnews.co.il':
                return await self.__parse_site_10()
            elif self.head_url == 'https://mobile.mako.co.il':
                return await self.__parse_site_11()
            elif self.head_url == 'https://www.ynetnews.com':
                return await self.__parse_site_12()
        except Exception as e:
            logging.info(e)
            return []

    async def __parse_site_1(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find('div', {'class': 'topic-list-column'}).find_all('div', {'class': 'topic-list-container'})

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = self.head_url + post.find('a').get('href')

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            title = post.find('a', {'class': 'news_list_title'}).text.replace('\n', '').strip()
            preview_text = post.find('a', {'class': 'news_list_anons'}).text

            soup = self.get_soup(post_url)
            if not soup:
                continue

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

    async def __parse_site_2(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find('div', {'class': 'inner-seller'}).find_all('article', {'class': 'news-bgrnd-img'})

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = self.head_url + post.find('a').get('href')

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            title = post.find('span', {'itemprop': 'name'}).text.replace('\n', '').strip()
            preview_text = post.find('span', {'itemprop': 'articleBody'}).text

            soup = self.get_soup(post_url)
            if not soup:
                continue
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

    async def __parse_site_3(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find('div', {'class': 'videorubrika'}).find_all('div', {'class': 'pad2'})

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = self.head_url + post.find('h1').find('a').get('href')

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            title = post.find('h1').find('a').text.replace('\n', '').strip()
            preview_text = post.text

            soup = self.get_soup(post_url)
            if not soup:
                continue
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
    async def __parse_site_4(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find_all('div', {'class': 'itc'})[6:8]

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = post.find('a').get('href')

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            soup = self.get_soup(post_url)
            if not soup:
                continue  # пост-detail
            title = soup.find('h1', {'class': 'g-row article-title'}).text
            preview_text = soup.find('h2', {'class': 'g-row article-subtitle'}).text
            text = soup.find('div', {'class': 'article-inner-content'}).get_text(strip=True)
            text = text.replace('Read more from Cybertech News:https://www.israeldefense.co.il/en/categories/cybertech',
                                '')
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
        return parsed_posts

    # https://en.globes.co.il/en
    async def __parse_site_5(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
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
            if await is_new_post(post_url):
                return parsed_posts

            preview_text = post.find('p').text

            soup = self.get_soup(post_url)
            if not soup:
                continue
            title = soup.find('h1', {'id': 'F_Title'}).text
            text = soup.find('article', ).get_text(strip=True).replace('<p>', '')

            try:
                image = soup.find('picture', ).find('img', ).get('src')
                content = f'<img src={image}>{text}'
            except AttributeError:
                content = text

            parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts

    # https://www.timesofisrael.com
    async def __parse_site_6(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find('section', class_='cols4 block items sticky-sidebar-relative').find_all(
            'div', class_='item template1 news')

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = post.find('a').get('href')

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            soup = self.get_soup(post_url, 'utf-8')
            if not soup:
                continue
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
    async def __parse_site_7(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find('section', class_='category-content').find_all('li')

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            tries = 1
            post_url = post.find('a').get('href')

            if await is_new_post(post_url):
                return parsed_posts

            preview_text = post.find('div', {'class': 'content'}).find('p')

            while tries < 3:
                soup = self.get_soup(post_url)
            if not soup:
                continue

            try:
                self.all = soup.find('div', class_='item-main-content').find_all('picture',
                                                                                 class_='desktop-4-3 mobile-4-3')
                images = self.all

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
    async def __parse_site_8(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find('div', class_='slotList').find_all('div', class_='slotView')

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = post.find('a').get('href')

            if post_url.endswith('html'):
                print('html - ' + post_url)
                continue

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            soup = self.get_soup(post_url)
            if not soup:
                continue
            preview_text = post.find('div', class_='slotSubTitle').find('a').text
            try:
                title = soup.find('h1').text
            except AttributeError:
                title = ''
            try:
                sub_title = soup.find('h2', class_='subTitle').text
            except AttributeError:
                sub_title = ''
            try:
                content_body = soup.find('div', {'class': 'layoutItem article-body'}).find('div',
                                                                                           {'data-contents': True})
            except AttributeError:
                continue

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
    async def __parse_site_9(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find('section', class_='content').find_all('li')

        # спаршенные посты
        parsed_posts = []

        for post in posts:
            post_url = self.head_url + post.find('a').get('href')

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            try:
                image = post.find('figure').find('img').get('src')
                content = f'<img src="{image}">'
            except AttributeError:
                content = ''

            soup = self.get_soup(post_url)
            if not soup:
                continue

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

    # https://passportnews.co.il
    async def __parse_site_10(self):
        soup = self.get_soup(self.url)
        posts = soup.find('div', {
            'class': 'elementor-posts-container elementor-posts elementor-passport-skin elementor-grid'}).find_all(
            'article')[:5]

        # спарсенные посты
        parsed_posts = []

        for post in posts:
            post_url = post.find('a', {'class': 'elementor-post__thumbnail__link'}).get('href')

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            title = post.find('h2', {'class': 'passport_title'}).text.replace('\n', '').strip()
            preview_text = post.find('h2', {'class': 'passport_title'}).text

            soup = self.get_soup(post_url)
            if not soup:
                continue
            soup = BeautifulSoup(str(soup).replace('<br/>', 'BRTEXT'), 'html.parser')

            content_body = soup.find('div', {'data-id': '6aed723'}).find('div', {'class': 'elementor-widget-wrap'})
            content = ''

            for tag in content_body:
                if tag.__dict__.get('attrs'):
                    if tag.__dict__.get('attrs').get('data-widget_type') == 'theme-post-excerpt.default':
                        content += f'<h4>{tag.find("div").get_text()}</h4>'

                if tag.name:
                    element = tag.find('div', {'class': 'elementor-widget-container'})
                    image = tag.find('figure')

                    if element:

                        for tag in element:
                            if tag.name in ['figure', 'p']:
                                if tag.name == 'figure':
                                    content += f'<img src="{tag.find("img").get("src")}">'
                                    image = False
                                    continue

                                if tag.find('a'):
                                    if tag.find('a').get('href').startswith('https://www.facebook.com'):
                                        continue

                                text = tag.get_text(strip=True)

                                if text in content:
                                    continue

                                content += f"<p>{text.replace('BRTEXT', '<br/>')}</p>"

                    if image:
                        image = image.find('img')
                        content += f'<img src="{image.get("src")}">'

            parsed_posts.append([title, content, preview_text, post_url])

        return parsed_posts

    # https://mobile.mako.co.il
    async def __parse_site_11(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find('ol').find_all('li')[:5]

        # спарсенные посты
        parsed_posts = []

        for post in posts:
            if post.find('a'):
                post_url = self.head_url + post.find('a').get('href')
            else:
                continue

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            soup = self.get_soup(post_url)
            if not soup:
                continue

            title = soup.find('article').find('h1').get_text()
            sub_title = soup.find('h2')
            preview_text = soup.find('h2', ).text

            content_body = soup.find('section', {'class': 'article-body'})

            content = ''

            if sub_title:
                content += f'<h4>{sub_title.text}</h4>'

            if soup.find('figure'):
                content += f"<img src={soup.find('figure').find('img').get('src')}>"

            for tag in content_body:
                image = tag.find('img')
                a = tag.find('a')

                if image and image != -1:  # в переменную иногда прилетает "-1"
                    image = image.get('src')
                    content += f'<img src={image}>'

                if tag.name == 'p':
                    try:
                        content += f"<p>{tag.get_text()}</p>"
                    except Exception as e:
                        print(e)
                        pass

                if a and a != -1:  # в переменную иногда прилетает "-1"
                    try:
                        for link in tag.find_all('a'):
                            if link.get('href'):
                                if link.get('href').startswith('https://twitter'):
                                    content += f'<a href="{link.get("href")}">Twitter</a> '
                                    break
                                elif link.get('href').startswith('https://www.instagram.com'):
                                    content += f'<a href="{link.get("href")}">Instagram</a> '
                                    break
                    except Exception as e:
                        print(e)
                        pass

            content += f'<a href="{post_url}">ССЫЛКА НА СТАТЬЮ</a>'
            parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts

    async def __parse_site_12(self):
        soup = self.get_soup(self.url)
        posts = soup.find('div', {'class': 'slotList'}).find_all('div', {'class': 'slotView'})[:5]

        # спарсенные посты
        parsed_posts = []

        for post in posts[:1]:
            post_url = post.find('a').get('href')

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            title = post.find('div', {'class': 'slotTitle'}).find('a').text.replace('\n', '').strip()
            preview_text = post.find('div', {'class': 'slotSubTitle'}).find('a').text

            soup = self.get_soup('https://www.ynetnews.com/article/By21SLrNP')
            if not soup:
                continue
            content_body = soup.find('div', {'data-contents': True})

            content = ''

            for tag in content_body:
                image = tag.find('img')

                if tag.name == 'figure':
                    if tag.find('li'):
                        continue
                    if tag.find_all('a'):
                        if tag.find_all("a")[-1].get("href"):
                            content += f'<a href="{tag.find_all("a")[-1].get("href")}">Twitter</a>'

                if tag.find('div', {'class': 'taboola-taboola-mid-page'}):
                    continue

                if image:
                    classes = image.get('class')
                    if not classes:
                        content += f'<img src="{image.get("src")}">'
                    content += f"<p>{image.get('alt')}</p>"

                if tag.name == 'figure':  # если список с ссылками, то пропускаем
                    if tag.find('img'):
                        continue

                if tag.find('span', {'data-text': True}):
                    if not tag.find('span', {'data-text': True}).text.startswith('Reprinted courtesy of '):
                        content += f"<p>{tag.find('span', {'data-text': True}).text}</p>"

            parsed_posts.append([title, content, preview_text, post_url])
        return parsed_posts

    async def __parse_site_13(self):
        soup = self.get_soup(self.url)
        if not soup:
            return []
        posts = soup.find_all('div', {'class': 'tagit'})[:5]

        # спарсенные посты
        parsed_posts = []

        for post in posts:
            post_url = self.head_url + post.find('a', {'class': 'tagit__link'}).get('href')

            # проверяем является ли пост новым
            if await is_new_post(post_url):
                return parsed_posts

            title = post.find('h3', {'class': 'tagit__title'}).text.replace('\n', '').strip()

            preview_text = post.find('p', {'class': 'tagit__subtitle'}).text

            soup = self.get_soup(post_url)
            if not soup:
                continue
            try:
                image = soup.find('picture', {'class': 'artBigImage'}).find('img')
            except AttributeError:
                image = ''

            content = ''
            if image:
                image = image.get('src').replace('/m/', '/l/')
                content = f'<img src={image}>'

            content_body = soup.find('div', {'class': 'articleInner'})

            for tag in content_body:
                if tag.find('img') and tag.find('img') != -1:
                    classes = tag.find('img').get('class')
                    if not classes:
                        content += f'<img src="{tag.find("img").get("src")}">'
                    continue

                if tag.name == 'p':
                    content += f"<p>{tag.get_text()}</p>"
                if tag.name == 'h3':
                    content += f"<h3>{tag.get_text()}</h3>"

            parsed_posts.append([title, content, preview_text, post_url])

        return parsed_posts
