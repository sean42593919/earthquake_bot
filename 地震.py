from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import discord
import time
import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # 載入 .env 檔案
token=os.getenv("DISCORD_TOKEN")# 讀取 Token
channel=int(os.getenv("channel"))

chrome_options=Options() 
chrome_options.add_argument('--headless')#不開啟視窗
chrome_options.add_argument('--disable-gpu')#不開啟GPU以免錯誤
chrome_options.add_argument('--log-level=3')#只跑出重要訊息
href='https://www.cwa.gov.tw/V8/C/E/index.html'
info=[]
values=[]
color=[0x1fff4b,0xf0ff1f,0xff0a0a]
color_ball=["🟢","🟡","🔴"]
while True:
    #地震資料收集
    driver=webdriver.Chrome(options=chrome_options)
    driver.get('https://www.cwa.gov.tw/V8/C/E/index.html')
    data=driver.find_element(By.XPATH,'//*[@id="eq-1"]/td[3]/div/a')
    href_text=data.get_attribute('href')
    if href!=href_text:#判斷是否有資料更新
        href=data.get_attribute('href')
        driver.get(href)
        data=driver.find_element(By.XPATH,'/html/body/div[3]/main/div/div/div[2]/ul')#這個是抓出地震資訊
        img=driver.find_element(By.XPATH,'/html/body/section/div/div[1]/div/div[2]/div/div/a/div[2]/img')#這個是抓出震央
        src=img.get_attribute('src')
        for i in range(5):
            info.append(data.text.split("\n")[i])
        info[1]=info[1]+info[2]
        del info[2]
        for i in range(4):
            values.append(info[i].split("：")[1])

        #discord機器人操作
        intents=discord.Intents.default()
        intents.message_content=True
        client=discord.Client(intents=intents)

        @client.event
        async def on_ready():#讓機器人啟動
            print('目前登入身份：',client.user)
            await send_message()
            await client.close()

        async def send_message():#讓機器人傳地震訊息和震央圖片
            if float(values[3])<4:
                color_select=0
            elif 4<=float(values[3])<5:
                color_select=1
            else:
                color_select=2
            channel_eq=client.get_channel(channel)
            embed=discord.Embed(title="⚠️⚠️地震速報⚠️⚠️",url=href,description="最近最新地震消息",color=color[color_select],timestamp=datetime.datetime.now())
            embed.set_author(name="中央氣象署地震觀測網", url="https://www.cwa.gov.tw/V8/C/E/index.html")
            embed.add_field(name="發震時間：",value=values[0],inline=False)
            embed.add_field(name="位置：",value=values[1],inline=False)
            embed.add_field(name="地震深度：",value=values[2],inline=False)
            embed.add_field(name="芮氏規模：",value=color_ball[color_select]+" "+values[3],inline=False)
            embed.add_field(name="本報告係中央氣象署地震觀測網即時地震資料地震速報之結果。",value="",inline=False)
            embed.set_image(url=src)
            await channel_eq.send(embed=embed)

        client.run(token)
        info=[]
        values=[]
        time.sleep(60)
    else:
        time.sleep(60)
        continue