import argparse
import json
import logging
import random
from datetime import datetime
from time import sleep

import requests

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s.%(msecs)03d %(process)d:%(processName)s line:%(lineno)d - %(levelname)s === %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

parser = argparse.ArgumentParser(description='manual to this script')

parser.add_argument("-xh", type=str, default="MYTQ3CH/A", dest="型号")
parser.add_argument("-dq", type=str, default="广东-深圳-南山区", dest="地区")
parser.add_argument(
    "-bk", type=str, default="ELvJ9NHnM7cqvUtuyeS8c6", dest="bark_api_key")
parser.add_argument(
    "-bs", type=str, default="https://api.day.app/", dest="bark_server")
parser.add_argument("-mz", type=str, default="Max", dest="名字")
parser.add_argument("-ys", type=str, default=None, dest="颜色")
parser.add_argument("-rl", type=str, default=None, dest="容量")
parser.add_argument("-cs", type=str, default="深圳,广州", dest="城市")
parser.add_argument("-dp", type=str, default=None, dest="店铺")
parser.add_argument("-qdsj", type=str,
                    default="2024-09-15 00:00:00", dest="启动时间")
parser.add_argument("-tzsj", type=str,
                    default="2024-10-01 00:00:00", dest="停止时间")
parser.add_argument("-bark", type=str,
                    default="1", dest="bark")
parser.add_argument("-wxpush", type=str,
                    default="1", dest="wxpush")
parser.add_argument("-wxpushtoken", type=str,
                    default="AT_uhjpnxvzuzqWRJj9YsDrqdFJwpCxa38L", dest="wxpushAppToken")
parser.add_argument("-wxpushuids", type=str,
                    default="", dest="wxpushuids")
parser.add_argument("-wxpushtopicIds", type=str,
                    default="", dest="wxpushtopicIds")


args = parser.parse_args()

url = "https://www.apple.com.cn/shop/fulfillment-messages"

uer_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
headers = {
    "User-Agent": uer_agent}


# 你的Bark服务器地址和密钥
bark_server = args.bark_server  # 替换为你的Bark服务器地址
bark_api_key = args.bark_api_key  # 替换为你的Bark API密钥
storeNumber = "R484"

# 发送Bark通知的函数


def send_bark_notification(title, message):
    url = f'{bark_server}{bark_api_key}/{title}/{message}?level=active&url=applestore://'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info(f"Bark通知已发送成功！{message}")
        else:
            logging.error(f"Bark通知发送失败，状态码：{response.status_code}")
    except Exception as e:
        logging.error(f"发送Bark通知时出错：{str(e)}")


# 替换成你的appToken和uids
appToken = args.wxpushAppToken
uids = str(args.wxpushuids).split(",")
topicIds = str(args.wxpushtopicIds).split(",")


def send_wxpusher_message(app_token, topicIds, uids, content, summary=""):
    # 设置API URL
    url = "https://wxpusher.zjiecode.com/api/send/message"

    # 构建消息内容和参数
    message = {
        "appToken": app_token,
        "content": content,
        "summary": summary,
        "contentType": 3,  # 文本消息类型
        "uids": uids,
        "topicIds": topicIds
    }

    # 发送HTTP POST请求
    response = requests.post(url, json=message)

    # 检查响应
    if response.status_code == 200:
        logging.info("wxpusher消息发送成功")
    else:
        logging.error("wxpusher消息发送失败，HTTP响应代码:", response.status_code)
        logging.error("wxpusher响应内容:", response.text)


def getProductList(product):
    k = {
        "mts.0": "regular",
        "mts.1": "compact",
        "searchNearby": "true",
        "product": product,
        "store": storeNumber
    }
    logging.debug("参数: %s", k)
    u = "https://www.apple.com.cn/shop/pickup-message-recommendations"
    response_body = requests.get(u, headers=headers, params=k)
    if response_body.status_code == 200:
        context = response_body.content.decode("utf-8")
        context_json = json.loads(context)
        PickupMessage = context_json['body']['PickupMessage']
        if PickupMessage is not None:
            products = []
            if 'recommendedProducts' in PickupMessage:
                products = PickupMessage['recommendedProducts']
                logging.info("products: %s", products)
            return products
    return list()


def getInfo(mz, ys, rl, cs, dp, kw, sj=False):
    global storeNumber
    response_body = requests.get(url, headers=headers, params=kw)
    if response_body.status_code == 200:
        context = response_body.content.decode("utf-8")
        context_json = json.loads(context)
        logging.debug(context_json)
        stores = context_json['body']['content']['pickupMessage']['stores']
        for store in stores:
            storeName = store['storeName']
            storeNumber = store['storeNumber']
            city = store['city']
            logging.debug("%s %s", city, storeName)
            # 城市筛选
            if cs is not None and len(cs) > 0 and city not in cs:
                logging.info("%s 跳过", city)
                continue
                # 筛选商店
            if dp is not None and len(dp) > 0 and storeName not in dp:
                logging.info("%s 跳过", storeName)
                continue
            partsAvailability = store["partsAvailability"]
            if len(partsAvailability) == 0:
                logging.info(storeName + "，无货")
                continue
            else:
                for parts in partsAvailability:
                    if len(parts) > 0:
                        pickUp = partsAvailability[parts]
                        storePickupProductTitle = pickUp['messageTypes']['regular']['storePickupProductTitle']
                        apple_prd = storePickupProductTitle.split(" ")
                        color = apple_prd[-1]
                        storeage = apple_prd[-2]
                        name = apple_prd[-3]
                        if ys is not None and len(ys) > 0 and color not in ys:
                            logging.info("%s 跳过", color)
                            continue
                        if rl is not None and len(rl) > 0 and storeage not in rl:
                            logging.info("%s 跳过", storeage)
                            continue
                        if mz is not None and len(mz) > 0 and name != mz:
                            logging.info("%s 跳过", storePickupProductTitle)
                            continue
                        pickupDisplay = pickUp['pickupDisplay']
                        pickupType = pickUp['pickupType']
                        pickupSearchQuote = str(
                            pickUp['pickupSearchQuote']).replace("/", "-")
                        logging.info(
                            "%s,%s,%s", storeName, storePickupProductTitle, pickupSearchQuote)
                        if pickupDisplay == "available" and pickupType == "店内取货":
                            # 通知
                            logging.info(
                                "%s,%s", storeName, pickupSearchQuote)
                            # 调用函数发送消息
                            if wxpush == "1":
                                send_wxpusher_message(
                                    appToken, topicIds, uids, storeName + storePickupProductTitle + pickupSearchQuote, storeName + storePickupProductTitle + pickupSearchQuote)
                            if bark == "1":
                                send_bark_notification(
                                    storeName, storePickupProductTitle+pickupSearchQuote)
        # 商店扫描完
        if sj:
            sleep(random.randint(1, 3))
    else:
        logging.error("访问失败, %s", response_body.status_code)
        sleep(60)


if __name__ == '__main__':
    product = args.型号
    location = args.地区.replace('-', " ")
    mz = args.名字
    ys = args.颜色
    rl = args.容量
    cs = args.城市
    dp = args.店铺
    qdsj = args.启动时间
    tzsj = args.停止时间
    bark = args.bark
    wxpush = args.wxpush

    logging.info(" 名字:%s 颜色:%s 容量:%s 城市:%s 店铺:%s", mz, ys, rl, cs, dp)
    logging.info("bark通知:%s, wxpush通知:%s", bark, wxpush)

    kw = {
        "pl": "true",
        "mts.0": "regular",
        "mts.1": "compact",
        "searchNearby": "true",
        "parts.0": product,
        "location": location,
        "store": "R577"
    }
    flag = True
    while flag:
        # 获取当前时间
        current_time = datetime.now()
        qdsj_time = datetime.strptime(qdsj, "%Y-%m-%d %H:%M:%S")
        tzsj_time = datetime.strptime(tzsj, "%Y-%m-%d %H:%M:%S")
        logging.info("当前时间：%s, 运行时间：%s-%s",
                     current_time, qdsj_time, tzsj_time)
        if tzsj_time < current_time:
            logging.info("停止运行")
            send_bark_notification("警告:停止运行", tzsj_time)
            flag = False
            break
        try:
            if qdsj_time > current_time:
                logging.info("当前时间小于设定时间，不执行操作")
                sleep(1)
                continue
            getInfo(mz, ys, rl, cs, dp, kw)
            parts = getProductList(product)
            if len(parts) != 0:
                for part in parts:
                    kw["parts.0"] = part
                    getInfo(mz, ys, rl, cs, dp, kw)
            sleep(random.randint(1, 2))
        except Exception as err:
            logging.error("error, %s", err)
            send_bark_notification("警告:运行ERROR", err)
            sleep(60)
            continue
            continue
