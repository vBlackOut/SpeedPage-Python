from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import sys
import requests
import io

class SpeedPage():

    def __init__(self, url):

        self.user_agent = "{} {} {}".format(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3)",
            "AppleWebKit/537.36 (KHTML, like Gecko)",
            "Chrome/35.0.1916.47 Safari/537.36"
        )

        self.headers = {'User-Agent': self.user_agent}

        self.webdriver()
        self.driver.get(url)

        self.get_stat_js()
        self.test_elements()

        for key, value in self.list_big_image.items():

            print("\nconnect to {} downloading...".format(key))
            (max_speed,
             average_speed,
             total_size,
             speed_time) = self.speed_page_url(key)

        self.driver.quit()

    def webdriver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-application-cache')
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def get_stat_js(self):
        navigationStart = self.driver.execute_script(
            "return window.performance.timing.navigationStart"
        )
        responseStart = self.driver.execute_script(
            "return window.performance.timing.responseStart"
        )
        domComplete = self.driver.execute_script(
           "return window.performance.timing.domComplete"
        )

        backendPerformance_calc = responseStart - navigationStart
        frontendPerformance_calc = domComplete - responseStart

        print("Back End: %s sec" % str(backendPerformance_calc/1000))
        print("Front End: %s sec" % str(frontendPerformance_calc/1000))
        print("Total Time Load: %s sec" % str(
           (backendPerformance_calc+frontendPerformance_calc)/1000)
        )

    def get_all_elements(self):

        elements_image = self.driver.execute_script("""
            var imgs = document.getElementsByTagName("img");
            var imgSrcs = [];

            for (var i = 0; i < imgs.length; i++) {
                imgSrcs.push(imgs[i].src);
            }

            return imgSrcs;
        """)

        elements_scripts = self.driver.execute_script("""
            var script = document.getElementsByTagName("script");
            var scriptSrcs = [];

            for (var i = 0; i < script.length; i++) {
                scriptSrcs.push(script[i].src);
            }

            return scriptSrcs;
        """)

        elements_style = self.driver.execute_script("""
            var link = document.getElementsByTagName("link");
            var linkSrcs = [];

            for (var i = 0; i < link.length; i++) {
                linkSrcs.push(link[i].href);
            }

            return linkSrcs;
        """)

        all_list_elements = elements_scripts + elements_style + elements_image
        all_list_elements = set(all_list_elements)

        return all_list_elements

    def test_elements(self):

        self.list_big_image = {}

        for item in self.get_all_elements():

            if hyperlink in item:
                r = requests.get(item, stream=True, headers=self.headers)
                if r.headers.get('content-length') != None:
                    self.list_big_image[item] = r.headers.get('content-length')
                    #print(item, r.headers)
            else:
                r = requests.get(
                    "{}/{}".format(hyperlink,item),
                    stream=True,
                    headers=self.headers
                )
                if (r.headers.get('content-length') != None and
                    r.status_code != 404):
                    self.list_big_image["{}/{}".format(hyperlink, item)] = \
                    r.headers.get('content-length')

        return self.list_big_image

    def Average(self, lst):
        return sum(lst) / len(lst)

    def speed_page_url(self, url):

        url = f"{url}"
        max_download = []
        with io.BytesIO() as f:
            start = time.time()
            r = requests.get(url, headers=self.headers, stream=True)
            total_length = r.headers.get('content-length')
            dl = 0
            if total_length is None: # no content length header
                f.write(r.content)
            else:
                for chunk in r.iter_content(1024):
                    dl += len(chunk)
                    f.write(chunk)
                    done = int(30 * dl / int(total_length))
                    download = round(dl//(time.time() - start) / 100000, 3)
                    max_download.append(download)
                    sys.stdout.write("\r[%s%s] %s Mbps" % ('=' * done,
                                      ' ' * (30-done),
                                      round(dl//(time.time() - start) / 100000,
                                      3))
                    )
        try:
            #print( f"\n{total_length}kb = {(time.time() - start):.2f} seconds")
            print("\n max download speed: {} Mbps avg: {} Mbps".format(
                  max(max_download), round(self.Average(max_download), 3))
            )
            print("{0} kb = {1} seconds".format(
               int(total_length)/1000, round((time.time() - start), 3))
            )

            return (max(max_download),
                    round(self.Average(max_download), 3),
                    int(total_length)/1000,
                    round((time.time() - start), 3))
        except ValueError as e:
            print("Keep passing downloading... {}".format(e))
            return -1, -1, -1, -1

if "__main__" == __name__:
    hyperlink = sys.argv[1]
    SpeedPage(hyperlink)
