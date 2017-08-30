import random
import lxml.html
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import requests
import re

# 10秒内每隔500毫秒扫描1次页面变化，当出现指定的元素后结束。
# wait = WebDriverWait(browser, 10)
USER_AGENTS = ['Mozilla/5.0', 'Gecko/20100101', 'Firefox/53.0', 'Windows NT 6.1']


def parser(url):
    # 因为这个网站的弹出广告超多所以建议使用PHANTOMJS方式爬取
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    # 从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
    dcap["phantomjs.page.settings.userAgent"] = (random.choice(USER_AGENTS))
    # 不载入图片，爬页面速度会快很多
    dcap["phantomjs.page.settings.loadImages"] = False
    browser = webdriver.PhantomJS(desired_capabilities=dcap)
    try:
        browser.get(url)
        # 隐式等待5秒，可以自己调节
        browser.implicitly_wait(5)
        # 设置10秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项
        # 以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。
        browser.set_page_load_timeout(10)
        # 之所以放弃这个方式，的确这个方式有bug或者自己遗漏某一点，这样很容易再爬取中中断
        # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, param)))
        html = browser.page_source
        doc = lxml.html.fromstring(html)
        browser.quit()
    except Exception as e:
        browser.quit()
        print(e)
    return doc


def getWeLike():
    print('开始进入网站...')
    for index in range(200):
        if index == 0:
            doc = parser('http://jp.xieav.com/one/LLP/')
        else:
            doc = parser('http://jp.xieav.com/one/LLP/index{}.shtml'.format(index + 2))
        filePics = doc.xpath('/html/body/div[3]/div[1]/div/ul/li/div[1]/a/img/@src')
        fileUrls = doc.xpath('/html/body/div[3]/div[1]/div/ul/li/div[1]/a/@href')
        fileRealNames = doc.xpath('/html/body/div[3]/div[1]/div/ul/li/div[1]/a/img/@alt')
        for i, eachImgName in enumerate(fileRealNames):
            print(eachImgName)
            # ------------------------------创建文件夹-------------------------------
            if not os.path.exists('image\\' + eachImgName):
                print('创建文件夹...')
                os.makedirs('image\\' + eachImgName)
            # ------------------------------下载icon图片-----------------------------
            picurl = 'http://jp.xieav.com' + filePics[i]
            try:
                r = requests.get(picurl)
                filename = 'image\\{}\\'.format(eachImgName) + '1.jpg'
                with open(filename, 'wb') as fo:
                    fo.write(r.content)
                # ------------------------------进入对应网页-----------------------------
                intourl = 'http://jp.xieav.com' + fileUrls[i] + 'player.shtml'
                print(intourl)
                # ------------------------------进入js网页-----------------------------
                videodoc = parser(intourl)
                videojs = videodoc.xpath('//*[@id="ccplay"]/script[1]/@src')
                print('http://jp.xieav.com' + videojs[0])
                jscontent = parser('http://jp.xieav.com' + videojs[0]).xpath('/html/body/pre/text()')
                urlPattern = '.*(xfplay\:\/\/\S+\.(mp4|wmv|rmvb)).*'
                pattern = re.match(urlPattern, jscontent[0])
                if pattern:
                    xfplay = pattern.group(1)
                    print(xfplay)
                f = open('image\\{}\\'.format(eachImgName) + '1.txt', 'w')
                f.write(pattern.group(1))
            except Exception as e:
                print(e)

getWeLike()
