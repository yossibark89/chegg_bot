import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# chrome_options.add_experimental_option('debuggerAddress','127.0.0.1:any-port-you-want') #set port
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from urllib.parse import urlparse
import re
import random
import requests
from bs4 import BeautifulSoup
import time
import os
import warnings
import json, base64

warnings.filterwarnings("ignore", category=DeprecationWarning)

PROXY = '138.197.162.125:8080'
chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)
opts = webdriver.ChromeOptions()
opts.binary_location = chrome_bin

#chrome_driver = r'C:\Program Files\webdriver\chromedriver'  # set path to chromedriver

opts.headless = True
opts.add_argument('--proxy-server=%s' % PROXY)
# opts.add_argument("--no sandbox")
# opts.add_argument("--disable-gpu")


def chrome_takeFullScreenshot(driver):
    def send(cmd, params):
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        return response.get('value')

    def evaluate(script):
        response = send('Runtime.evaluate', {'returnByValue': True, 'expression': script})
        return response['result']['value']

    metrics = evaluate( \
        "({" + \
        "width: Math.max(window.innerWidth, document.body.scrollWidth, document.documentElement.scrollWidth)|0," + \
        "height: Math.max(innerHeight, document.body.scrollHeight, document.documentElement.scrollHeight)|0," + \
        "deviceScaleFactor: window.devicePixelRatio || 1," + \
        "mobile: typeof window.orientation !== 'undefined'" + \
        "})")
    send('Emulation.setDeviceMetricsOverride', metrics)
    screenshot = send('Page.captureScreenshot', {'format': 'png', 'fromSurface': True})
    send('Emulation.clearDeviceMetricsOverride', {})

    return base64.b64decode(screenshot['data'])


def virtual_click(browser, click_object, use_random=True):
    try:
        size = click_object.size
    except StaleElementReferenceException:
        print("StaleElementReferenceException")
        return False
    size_list = list(size.values())
    height = int(size_list[0]) - 1
    width = int(size_list[1]) - 1
    if use_random:
        try:
            height_rand = random.randint(1, height)
        except ValueError:
            height_rand = 1
        try:
            width_rand = random.randint(1, width)
        except ValueError:
            width_rand = 1
    if not use_random:
        height_rand = height
        width_rand = width
    action = webdriver.common.action_chains.ActionChains(browser)
    try:
        action.move_to_element_with_offset(click_object, width_rand, height_rand)
    except StaleElementReferenceException:
        return False
    action.click()
    try:
        action.perform()
    except MoveTargetOutOfBoundsException:
        return False
    except StaleElementReferenceException:
        return False
    return True


try:
    os.mkdir('./screens')
except FileExistsError:
    pass

request_queue = []
flag = False
client = commands.Bot(command_prefix='!')

_2captcha_key = 'cb319d881ccd6998c30ae4a94c9cc666'
bot_token = 'NjUxNzk4MDM0Mzc5NzAyMjgz.XfarEA.KbHfalMvK13ZIiwaXeeW1lBK3sc'


@client.event
async def on_ready():
    print('Chegg-bot is ready! :D')


@client.command()
async def chegg(ctx, chegg_url):
    global request_queue
    global process_queue
    global flag

    """check if url is valid and whether the chegg site is working"""
    if urlparse(
            chegg_url).hostname != 'www.chegg.com' or ctx.message.channel.name != "general":  # channel ID you want the bot to work in
        await ctx.send(f'{ctx.author.mention} Invalid link. Please try again.')
        return

    else:
        """confirmed that url domain is chegg and the channel is correct"""
        request_object = {'user': ctx, 'url': chegg_url}
        await ctx.send(f'{ctx.author.mention} Your request is in the queue. Please wait while it gets processed.')
        if request_object not in request_queue:
            time.sleep(random.uniform(2, 6))
            request_queue.append(request_object)
            if not flag:
                li = take_screenshot(request_object)
                if li[0] == 0:
                    new_ctx = li[1]
                    await new_ctx.send(f'{new_ctx.author.mention} Invalid Chegg URL. Please check again.')
                file_name, new_ctx = li
                message = f'{new_ctx.author.mention} Be sure to click \'open original\' to view the full size image.\nLink: ' + chegg_url
                fp = open('./screens/' + file_name, 'rb')
                try:
                    await new_ctx.author.send(content=message, file=discord.File(fp))
                    await new_ctx.send(content=f'{ctx.author.mention}Check your DMs!')
                except:
                    await new_ctx.send(
                        content=f'{ctx.author.mention} Unable to send answer!\nEither your DMs aren\'t open or the request was too large!')

                fp.close()
                os.remove('./screens/' + file_name)  # set your path to the screenshot
                time.sleep(random.uniform(5, 8))
                if request_queue:
                    take_screenshot(request_queue[0])
                else:
                    return


        ##hereeee
        else:
            await ctx.send(f'{ctx.author.mention} Unknown Error!')
            return


def take_screenshot(r_obj):
    global flag
    flag = True
    global request_queue
    ctx = r_obj['user']
    url = r_obj['url']
    new_ctx = ctx
    print(f'>>scraping for {ctx.author.name}-{url}')
    """opens chegg question site"""
    time.sleep(random.uniform(2, 4))
    browser.get(url)
    time.sleep(random.uniform(9, 14))
    try:
        test555 = browser.find_element_by_xpath('//*[@id="qna-body"]/main/section[1]/div/a')
        virtual_click(browser, test555)

    except:
        pass
    handle_captcha()
    question_num_ptn = re.compile(r'-q\d+')
    number = random.randint(10000000, 99999999)
    file_name = 'screenshot' + str(number) + '.png'
    png = chrome_takeFullScreenshot(browser)

    with open("./screens/" + file_name, 'wb') as f:
        f.write(png)

    request_queue.remove(r_obj)
    time.sleep(5)
    browser.get('https://www.chegg.com')
    flag = False
    print('>>Saved screenshot')

    return [file_name, new_ctx]


def handle_captcha():  # This isn't really needed in remote debugging non headless, but is essential elsewhere
    if browser.title == 'Access to this page has been denied.':
        print('>>A wild captcha appeared!!!!')
        print(browser.find_element_by_tag_name('h1').text)
        if browser.find_element_by_tag_name('h1').text == 'Please verify you are a human':
            print('CAPTCHAAAAA!')
            """captcha"""
            html = browser.page_source
            soup = BeautifulSoup(html, 'lxml')
            sitekey = soup.find('div', attrs={'class': 'g-recaptcha'})['data-sitekey']
            data_2cap = {'key': _2captcha_key,
                         'method': 'userrecaptcha',
                         'googlekey': sitekey,
                         'pageurl': browser.current_url,
                         'invisible': '0',
                         'json': '0'}
            r = requests.get(
                f'https://2captcha.com/in.php?key={data_2cap["key"]}&method=userrecaptcha&googlekey={data_2cap["googlekey"]}&pageurl={data_2cap["pageurl"]}&invisible=1')
            print(r.text)
            id = r.text.split('|')[1]
            callback = soup.find('div', attrs={'class': 'g-recaptcha'})['data-callback']
            r = requests.get(f'https://2captcha.com/res.php?key={data_2cap["key"]}&action=get&id={id}')
            print(r.text)
            status = r.text.split('|')[0]
            i = 0
            while status != 'OK':
                print(f'{i}-Status is not OK, trying in 5 seconds-{status}')
                r = requests.get(f'https://2captcha.com/res.php?key={data_2cap["key"]}&action=get&id={id}')
                status = r.text.split('|')[0]
                i += 1
                time.sleep(random.uniform(2, 4))
            token_g = r.text.split('|')[1]
            print(token_g)
            js1 = f'document.getElementById("g-recaptcha-response").innerHTML="{token_g}";'
            print(js1)
            browser.execute_script(js1)
            time.sleep(random.uniform(2, 3))
            js2 = f'{callback}("{token_g}");'
            print(js2)
            browser.execute_script(js2)
            time.sleep(random.uniform(3, 5))


def signin():  # Only use this function if you are using new instances of your browser each time
    print('>>signing in!')
    browser.get('https://www.chegg.com/auth?action=login&redirect=https%3A%2F%2Fwww.chegg.com%2F')
    handle_captcha()

    time.sleep(2)
    email_elem = browser.find_element_by_id('emailForSignIn')
    for character in 'alondra_calderon@ymail.com':
        email_elem.send_keys(character)
        time.sleep(0.1)
    time.sleep(2)

    password_elem = browser.find_element_by_id('passwordForSignIn')
    for character in 'Blueyes97':
        password_elem.send_keys(character)
        time.sleep(0.1)
    time.sleep(2)

    browser.find_element_by_name('login').click()

    try:
        if WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div[2]/div[2]/div/div[3]/div/oc-component/div/div/div/div[2]/div[1]/div[1]/div/form/div/div/div/div/div[3]/span"))):
            print('redirecting back to login')
            browser.get('https://www.chegg.com/auth?action=login')
            handle_captcha()
            signin()
            handle_captcha()
    except TimeoutException:
        pass

    if browser.find_element_by_tag_name('h1').text == 'Oops, we\'re sorry!':
        return [0]
    handle_captcha()


if __name__ == '__main__':
    browser = webdriver.Chrome(executable_path="chromedriver", options=opts)
    signin()
    client.run(bot_token)
    # test comment
