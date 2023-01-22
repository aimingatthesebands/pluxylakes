import asyncio
import aiogram.utils.exceptions
import requests
import configparser
from aiogram import Bot,types
from aiogram.dispatcher import FSMContext
import db
import keyboards as kb
import csv

data = configparser.ConfigParser()
data.read("setting.ini", encoding='utf-8')
adminBot = Bot(token=data['bot']['admintoken'], parse_mode=types.ParseMode.HTML)
mainBot = Bot(token=data['bot']['token'], parse_mode=types.ParseMode.HTML)


class AsyncIter:
    def __init__(self, items):
        self.items = items

    async def __aiter__(self):
        for item in self.items:
            yield item

async def convertUSDToCurrency(coin, amount, ratesLink):
    loop = asyncio.get_event_loop()
    futureRate = loop.run_in_executor(None, requests.get, ratesLink)
    if coin == "eth":
        rate = await futureRate
        eth = float(rate.text.split("<br>")[1].split(":")[1])
        return round(amount/eth, 7)
    elif coin == "btc":
        rate = await futureRate
        btc = float(rate.text.split("<br>")[0].split(":")[1])
        return round(amount/btc, 7)
    elif coin == "usdterc" or coin == "usdttrc":
        return amount

async def getNearestRank(x, lvlList):
    fCall = min(lvlList, key=lambda y:abs(y-x))
    if fCall > x:
        return fCall
    else:
        closestIndx = lvlList.index(fCall)
        return lvlList[closestIndx+1]

async def getPreviousRank(x, lvlList):
    fuckedUpLvls = [0, 1, 2, 3, 4]
    fCall = min(lvlList, key=lambda y:abs(y-x))
    if fCall < x:
        return fCall
    elif x not in lvlList and x not in fuckedUpLvls:
        closestIndx = lvlList.index(fCall)
        return lvlList[closestIndx-1]
    elif x in fuckedUpLvls:
        return 0
    else: return x

async def adminReplenishNotify(id, sum, vendor, dt):
    admins = await db.getAllAdmins()
    admins = AsyncIter(admins)
    async for i in admins:
        await adminBot.send_message(chat_id=i[0], disable_notification=True, text=f"Пополнение:\n\n"
                                    f"ID: <b> {id} | @{await db.getUsernameByID(id)}</b>\n"
                                    f"Сумма: <b> {sum} USD </b>\n"
                                    f"Монета пополнения:<b> {vendor}\n</b>"
                                    f"Создана: <b> {dt} </b>\n\n"
                                    f"{f'Реферальная награда <b> {int(sum)/10} USD</b> будет зачислена <b> {await db.getMasterRefID(id)} </b>' if await db.getMasterRefID(id) else ''}\n\n"
                                    f"<b> Проверьте наличие перевода на кошельке, если он есть используйте команду: </b> <code> /rep {id} {sum} </code>")

async def antixss(txtstr):
    s1 = str(txtstr).replace("<", "")
    s2 = str(s1).replace(">", "")
    return s2

async def refMasterIncomeNotify(masterid, sum):
    try:
        await mainBot.send_message(chat_id=masterid, reply_markup=kb.onNewRefNotification(), disable_notification=False, text=data['txt']['refIncome'].format(sum))
    except aiogram.utils.exceptions.BotBlocked:
        pass

async def replenishNotification(id, sum):
    try:
        await mainBot.send_message(chat_id=id, reply_markup=kb.justMainMenu(), disable_notification=False, text=data['txt']['balanceReplenished'].format(sum))
    except aiogram.utils.exceptions.BotBlocked:
        pass


async def adminWithdrawNotification(id, num, sum, wallet, type, coin, date):
    admins = await db.getAllAdmins()
    admins = AsyncIter(admins)
    username = await db.getUsernameByID(id)
    async for i in admins:
        await adminBot.send_message(chat_id=i[0], reply_markup=kb.adminGetAllWithdrawRequests(), disable_notification=True, text=f"Вывод:\n\n"
                                    f"ID заявки: <b> {num} | от юзера {f'@{username}' if username != 'noUsername' else id}</b>\n"
                                    f"💲  Сумма вывода: <b> {sum} USD </b>\n"
                                    f"🪙  Монета:<b> {coin}\n</b>"
                                    f"💼  Кошелек для вывода: <b>{wallet} </b>\n"
                                    f"{'👥  Вывод с <b> реферального баланса </b>' if type == 'RefBalanceDraw' else '❓ Вывод с <b> потокого баланса </b>'}\n"
                                    f"📅  Создана: <b> {date} </b>\n\n"
                                    f"Пометить как выплаченную    <code> /wdr {num}</code>"
                                    )

async def withdrawNotify(id, reqnum): # N
    await mainBot.send_message(id, disable_notification=False, text=data['txt']['withdrawRequestPayedNotif'].format(reqnum))

async def compileCSV(rndhash, columns, reqsRaw):
    with open(f'{rndhash}.csv', mode='w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(columns)
        for i in range(len(reqsRaw)):
            writer.writerow([f"{reqsRaw[i][0]}", f"{reqsRaw[i][1]}", f"{reqsRaw[i][2]}", f"{reqsRaw[i][3]}", f"{reqsRaw[i][4]}", f"{reqsRaw[i][5]}", f"{reqsRaw[i][6]}", f"{reqsRaw[i][7]}"])
