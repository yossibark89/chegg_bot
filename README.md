# chegg_bot
A automated chegg answer scraper

This project powers a Discord bot that awaits for the command !chegg <URL> and scrapes Chegg for the expert answer to the passed in URL. 
Once the answer is retrieved, the bot DM's the user the answer as a screenshot. To take screenshots, the code utilized a library called
Selenium that allows me to build a webdriver to automate the opening and navigation of webpages. The code also used 2captcha servies
to solve any reCaptcha's that appear when navigating Chegg. 
