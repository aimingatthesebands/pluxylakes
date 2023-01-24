# -*- coding: utf-8 -*-
import os
import random
import db
import keyboards as kb
import aiogram.utils.exceptions
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
import configparser
import db
import datetime
import technical as tech


print(f"==================================\n\n adminPanel \n\n ======================================")

data = configparser.ConfigParser()
data.read("setting.ini", encoding='utf-8')
adminbot = Bot(token=data['bot']['admintoken'], parse_mode=types.ParseMode.HTML)
childBot = Bot(token=data['bot']['token'], parse_mode=types.ParseMode.HTML)
admindp = Dispatcher(adminbot, storage=MemoryStorage())

async def mainMenu():
    msg = """
[ADMINKA 228]

Команды:

/rep - <b>Пополнить баланс</b> 
использование:<b> /rep @username или ID 500 (@username/username можно без @)</b>


/wdr - <b>Выполнить заявку на вывод</b> 
использование: <b> /wdr номер заявки</b> 

/wdrlist - spisok zayavok

/stats - количество юзеров

<b> Сюда будут приходить все заявки на пополнение/вывод </b>
    """
    return msg
async def getAllWRRequestInText(reqsRaw):
    msgText = "Вы получили только 10 последних заявок, полный отчет отправлен в файле: \n\n\n"
    for i in range(len(reqsRaw)):
        username = await db.getUsernameByID(reqsRaw[i][0])
        msgText = msgText + f"-----------------" \
                            f"\nID: <b> {reqsRaw[i][1]} </b>\n\n" \
                            f"создана: {f'@{username}' if username != 'noUsername' else reqsRaw[i][0]}\n" \
                            f"Кош для вывода:    <b>{reqsRaw[i][3]}</b>\n" \
                            f"Сумма:    <b>{round(float(reqsRaw[i][2]))}</b>\n" \
                            f"Тип баланса:    <b>{data['txt']['walletBalance'] if reqsRaw[i][4] == 'WalletBalanceDraw' else data['txt']['refBalance']}</b>\n" \
                            f"Монета:    <b>{data['vendors'][reqsRaw[i][5]]}</b>\n" \
                            f"Дата:    <b>{reqsRaw[i][6]}</b>\n" \
                            f"{data['txt']['isPayed']}:    {'🟩' if int(reqsRaw[i][7]) == 1 else '🟥'}\n" \
                            f"-----------------\n\n"
    return msgText


@admindp.message_handler(commands=['start'], state="*")
async def startProcessing(msg: types.Message):
    cid = msg.chat.id
    if data['bot']['adminPass'] in msg.text.split(" ") or msg.text == data['bot']['adminPass']:  # пароль в ссылrt?
        if not await db.checkifAdminExists(cid):
            if await db.checkifAdminExists(cid) == 0: # Новый админ
                if await db.regAdminStageOne(id=cid, logged=1, status="1",
                                             regtime=str(datetime.datetime.now()).split(".")[0],
                                             name=f"{msg.from_user.first_name} {msg.from_user.last_name if not 'None' else ''}",
                                             username=msg.from_user.username):
                    await msg.bot.send_message(cid, text="👍authorized")
                    await msg.bot.send_message(cid, text=await mainMenu())
            else: # Старый админ
                if not await db.checkIfAdminLogged(cid):
                    await msg.bot.send_message(cid, '⚠️ Авторизуйтесь')
                else:
                    await msg.bot.send_message(cid, text=await mainMenu())

        else:
            await db.logAdmin(cid)
            await msg.bot.send_message(cid, text="👍authorized")
    else:
        await msg.bot.send_message(cid, text=await mainMenu())


@admindp.message_handler(commands=['rep'], state="*")
async def rep(msg: types.Message):
    cid = msg.chat.id
    if await db.checkIfAdminLogged(cid):
        try:
            paySum, usernameorid = msg.text.split(" ")[2], msg.text.split(" ")[1]
            if not usernameorid.isdigit():
                if await db.getUserByUsername(usernameorid):
                    idFromUsername = await db.getUserByUsername(usernameorid)
                    await db.replAdminFunc(idFromUsername, paySum)
                    await tech.replenishNotification(idFromUsername, paySum)
                    refMasterOfID = await db.getMasterRefID(idFromUsername)
                    if refMasterOfID:
                        refIncome = int(paySum)/10
                        await db.refMasterIncomeEnroll(refMasterOfID, refIncome)
                        await tech.refMasterIncomeNotify(refMasterOfID, refIncome)
                    await msg.bot.send_message(cid, text=f"✅ Пополнение: <b> {paySum} </b> для <b>@{usernameorid}</b> зачислено успешно.\n"
                                                         f"🔔 Юзер получил уведомление. \n\n{f'🔔Реферал <b> {refMasterOfID}/@{await db.getUsernameByID(refMasterOfID)} </b> получил <b>{int(paySum)/10} USD</b>' if refMasterOfID else ''}\n"
                                                         )
                else:
                    await msg.bot.send_message(cid, text=f"Username not found. Try use ID")
            else:
                if await db.checkifExists(usernameorid):
                    id = usernameorid
                    unFromId = await db.getUsernameByID(id)
                    refMasterOfID = await db.getMasterRefID(id)
                    await db.replAdminFunc(id, paySum)
                    await tech.replenishNotification(id, paySum)
                    if refMasterOfID:
                        refIncome = int(paySum) / 10
                        await db.refMasterIncomeEnroll(refMasterOfID, refIncome)
                        await tech.refMasterIncomeNotify(refMasterOfID, refIncome)
                    await msg.bot.send_message(cid,
                                               text=f"✅ Пополнение: <b> {paySum} USD</b> для <b>{id}/@{unFromId if unFromId != 'None' else ''}</b> зачислено успешно.\n"
                                                    f"🔔 Юзер получил уведомление. \n\n{f'🔔Пригласивший <b> {refMasterOfID}/@{await db.getUsernameByID(refMasterOfID)} </b> получил <b>{int(paySum) / 10} USD</b>' if refMasterOfID else ''}\n"
                                               )
                else:
                    await msg.bot.send_message(cid, text=f"ID not found")
        except IndexError:
            await msg.bot.send_message(cid, text=f"Formattingfucked")

    else:
        await msg.bot.send_message(cid, '⚠️ Авторизуйтесь')

@admindp.message_handler(commands=['wdr'], state="*")
async def wdr(msg: types.Message):
    reqNum = msg.text.split(" ")[1]
    response = await db.getWithdrawRequestByNumber(reqNum)
    if response:
        await tech.withdrawNotify(response[0], response[1])
        await db.markWRasPayed(reqNum)
        await msg.bot.send_message(msg.chat.id, "+")
        await db.markWRasPayed(reqNum)
    else:
        await msg.bot.send_message(msg.chat.id, text="zayavka ne naidena")

@admindp.message_handler(commands=['wdrlist'])
async def admgetreqs(msg: types.Message):
    reqsRawFull = await db.getAllWithdrawRequests()
    reqsRawLast =   await db.getLast10WithdrawRequests()
    txt = await getAllWRRequestInText(reqsRawLast)
    filehash = random.randint(100000, 99999999)
    columns = ['from ID', 'Request Number', 'Summa', 'Wallet', 'Balance type', 'Coin', 'Date', 'is Payed?']
    await msg.bot.send_message(msg.chat.id, reply_markup=kb.close(), text=txt)
    await tech.compileCSV(rndhash=filehash, columns=columns, reqsRaw=reqsRawFull)
    try:
        await msg.bot.send_document(chat_id=msg.chat.id, document=open(f'{filehash}.csv', 'rb'))
        path = os.getcwd()
        os.remove(f'{path}/{filehash}.csv')
    except FileNotFoundError:
        pass


@admindp.callback_query_handler(text=['admin_open_reqslist'])
async def admgetreqs(call: types.CallbackQuery):
    reqsRaw = await db.getAllWithdrawRequests()
    txt = await getAllWRRequestInText(reqsRaw)
    await call.bot.send_message(call.message.chat.id, reply_markup=kb.close(), text=txt)

@admindp.callback_query_handler(text=["close"], state="*")
async def closeMsg(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.message.chat.id
        await call.bot.delete_message(cid, call.message.message_id)
    except: pass

@admindp.message_handler(commands=['stats'])
async def cmdstat(msg: types.Message):
    await msg.bot.send_message(msg.chat.id, text=f'Количество юзеров: <b> {await db.getAllUsrsCount()} </b>')

executor.start_polling(admindp)
