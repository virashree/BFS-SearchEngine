from collections import deque
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
from urllib.parse import urlparse,urljoin
import os
from textProcessor import TextProcessor
from index import Index
from operator import itemgetter


class Crawl():

    def __init__(self):
        self.visited_pages = set()
        self.tp = TextProcessor()
        self.inx = Index()
        self.inverted_index = {}
        self.domain = ["k-state.edu", "ksu.edu"]
        self.queue = deque()
        self.stop_words = self.tp.stop_words()
        self.tf_idf = {}

    def crawler(self, url):

        if len(os.listdir("Webpages/")) > 3500:
            return

        if len(self.visited_pages) == 0:
            self.visited_pages.add(url)
            with open('visted_pages.txt', 'a') as f:
                f.writelines(url)
                f.writelines("\n")
        try:
            urlfind = urllib.request.urlopen(url)

            baseurl = url.rstrip('/')
            soup = BeautifulSoup(urlfind)
            urls = soup.find_all('a', href=True)

            for i in urls:
                link = i.get('href')
                complete_url = ""

                if '.pdf' not in link and '.jpg' not in link and '.doc' not in link and '.pptx' not in link  and '.mp4' not in link\
                        and '.png' not in link and '.jpeg' not in link and '.gif' not in link:
                    if link.startswith('https'):
                        complete_url = link
                    elif link.startswith('http'):
                        temp = link.split('http:', 1)[1]
                        complete_url = urljoin("https:", temp)
                    elif link.startswith('//'):
                        complete_url = urljoin("https:", link)
                    elif link.startswith('/'):
                        complete_url = urljoin(baseurl, link)

                    if complete_url != "":
                        complete_url = complete_url.rstrip('/')
                        if self.contains(complete_url) is False and self.has_domain(complete_url) is True:
                            self.visited_pages.add(complete_url)
                            self.queue.append(complete_url)
                            try:
                                self.index_webpage(complete_url)
                                with open('visted_pages.txt','a') as f:
                                    f.writelines(complete_url)
                                    f.writelines("\n")S
                                print(complete_url)
                            except Exception as er:
                                print(er)
                                pass

        except urllib.error.HTTPError as e:
            print(url, e)
            pass

        except Exception as ex:
            print(url, ex)
            pass

        if len(self.queue) == 0:
            return

        url = self.queue.pop()
        self.crawler(url)

    def has_domain(self, url):
        p = urlparse(url)
        if p.hostname.endswith('k-state.edu') or p.hostname.endswith('ksu.edu'):
            return True
        else:
            return False

    def contains(self, url):

        if url in self.visited_pages:
            return True
        else:
            if "k-state.edu" in url:
                url = url.replace("k-state.edu", "ksu.edu")

            elif "ksu.edu" in url:
                url = url.replace("ksu.edu", "k-state.edu")

            if url in self.visited_pages:
                return True
            else:
                return False

    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'meta', '[document]', 'img']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def index_webpage(self, url):
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)

        try:
            if soup.title is not None:
                title_page = soup.title.string.rstrip().strip()
                title_page = ''.join(e for e in title_page if e.isalnum())
            else:
                global count
                count = count + 1
                title_page = "temp" + str(count)
        except:
            global count
            count = count + 1
            title_page = "temp" + str(count)

        content = u" ".join(t.strip() for t in visible_texts)

        tokens = self.tp.tokenize(content)
        tokens = self.tp.remove_stopwords(tokens, self.stop_words)
        tokens = self.tp.stem(tokens)

        f = open("Webpages/" + title_page + ".txt", "w")
        f.writelines(url)
        f.writelines('\n')
        f.writelines(u" ".join(t.strip() for t in tokens))

    def index(self):
        dir_path = "Webpages"

        files = os.listdir(dir_path)
        no_doc = len(files)
        for file in files:
            with open(dir_path + "/" + file, 'r') as f:
                url = f.readline().rstrip()
                body = "\n".join(f.readlines())
                tokens = body.split()
                termFreq = self.inx.term_frequency(tokens)
                doc = {'url': url, 'tokens': termFreq}
                self.inverted_index = self.inx.build_inverted_index(doc, self.inverted_index)

        self.tf_idf = self.inx.tf_idf(self.inverted_index, no_doc)


if __name__ == '__main__':

    newPath = "Webpages/"
    if not os.path.exists(newPath):
        os.makedirs(newPath)

    tp = TextProcessor()
    index = Index()
    crwl = Crawl()

    ## uncomment this code in order to run the crawler

    # count = 0
    # seed = "https://www.cs.ksu.edu"
    # crwl.crawler(seed)


    crwl.index()
    inverted_index = crwl.inverted_index
    tf_idf = crwl.tf_idf
    stop_words = crwl.stop_words

    files = os.listdir("Webpages/")
    no_doc = len(files)

    # cosine similarity
    cos_similarities = {}

    # read queries from file
    with open('queries.txt', 'r') as f:
        lines = f.read()
        queries = {}
        cnt = 1
        for query in lines.split('.'):
            query = query.strip()
            if query is not "":
                queryTokens = tp.tokenize(query)
                queryTokens = tp.remove_stopwords(queryTokens, stop_words)
                queryTokens = tp.stem(queryTokens)
                termFreq = index.term_frequency(queryTokens)
                tf_idf_query = index.tf_idf_query(termFreq, inverted_index, no_doc)
                queries[cnt] = tf_idf_query
                cnt = cnt + 1

    # cosine similarity between queries and documents
    for q_id, query in queries.items():
        cos_similarities[q_id] = []
        for doc_id, doc in tf_idf.items():
            try:
                cos_sim = index.cos_similarity(doc, query)
                cos_similarities[q_id].append((doc_id, cos_sim))
            except:
                print("exception caught")
        cos_similarities[q_id] = sorted(cos_similarities[q_id], key=itemgetter(1), reverse=True)

    top5_q1 = cos_similarities[1][:5]
    top5_q2 = cos_similarities[2][:5]
    top5_q3 = cos_similarities[3][:5]
    top5_q4 = cos_similarities[4][:5]
    top5_q5 = cos_similarities[5][:5]
    print(top5_q1)
    print(top5_q2)
    print(top5_q3)
    print(top5_q4)
    print(top5_q5)



