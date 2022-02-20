# NTNU-Course-Queuing-Website-BackEnd
NTNU Course Queuing Website Back-End / 師大課程排隊網站後端

## Setup tutorial

In this project, I decided to install on Windows, which is much more friendly to all students.

Accordingly, this tutorial is write for Windows users.

For Linux users, I bet you are familiar to programs.

It should be easy for you to setup this project without detailed procedures.

For Mac users... Sorry. XD

1. Database

   I used MySQL in this project, you can download and install it from [here](https://dev.mysql.com/downloads/installer/).

2. Validation code cracking
   
   Download the weights file [val_loss.h5](https://drive.google.com/file/d/16YL-915VVvY0bSMr2FiKhVnV19ipYF59/view?usp=sharing) and put it in directory `validation`.

3. Selenium (爬蟲)

   Check the version of your Google Chrome, download the relative version of [chromedriver.exe](https://chromedriver.chromium.org/downloads) and put it in directory `ntnu/chromedriver_win32`

4. Environment

   Before installing environment, check that your computer has installed [Python](https://www.python.org/downloads/).
   
   (I prefer using [`virtualenv`](https://pypi.org/project/virtualenv/), you can use your preference.)
   > 1. Open CMD. (Windows+R --> type "cmd" --> confirm)
   > 2. Move to the directory of this project.
   > 3. Enter command `virtualenv ENV_NAME_YOU_WANT`.
   
   (If `virtualenv` is not installed, enter command `pip install virtualenv` to install it, then try the third step again.)
   
   After succcessfully created an virtual enviroment, we can activate it and install required packages.
   > 4. Enter command `ENV_NAME_YOU_WANT\Script\activate` to activate your virtual enviroment.
   > 
   >    (Using powershell instead of CMD might face some unexpected problems.)
   > 5. Enter command `pip install -r requirements.txt` to install required packages.

5. Configuration files

   There is a directory named `.config_example`. Rename it to `.config`.
   
   Open files in it, fill all "???" and delete all "(SOME_EXPLAIN)".

   For the `robot.env`, you will have to register LINE LOGIN and LINE Message API at [LINE Developers](https://developers.line.biz/zh-hant/) to get LINE_CLIENT_SECRET and LINE_BEARER.
   
   There are plenty tutorials on the Internet, you can follow those to register LINE bot.
   
   1. LINE LOGIN offical tutorial: https://developers.line.biz/zh-hant/docs/line-login/getting-started/
   2. LINE Message API offical tutorial: https://developers.line.biz/zh-hant/docs/messaging-api/getting-started/

   Beware! You have to finish the setting of your domain first, so that you can verify Webhook URL in Message API.
   
6. Start the Back-End: Enter command `python app.py`!
