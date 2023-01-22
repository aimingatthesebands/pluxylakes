# -*- coding: utf-8 -*-
# Necessary modules: technical.py as tech, keyboard.py as kb, db.py.
# Needed to work properly: adminpanelBot.py (integrated with main.py), daytimehandler (run 24/7 on VDS)
import asyncio
import collections
import requests
import aiogram.utils.exceptions
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
import configparser
import keyboards as kb
import datetime
import db
import technical as tech

print(f"==================================\n\n {db.getInfo(1604009857)} \n\n ======================================")

data = configparser.ConfigParser()
data.read("setting.ini", encoding='utf-8')
bot = Bot(token=data['bot']['token'], parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
lvlList = [int(lvl) for lvl in data['expsys'].keys()]

class States(StatesGroup):
    menu = State()
    onTaskMarket = State()
    billingDataInputWalletBal = State()
    billingDataInputRefBal = State()
    payWait = State()
    awaitingContact = State()
    readyToCompleteTask = State()
    onRefProgram = State()
    withdrawStage1 = State()
    withdrawStage2 = State()
    withdrawStage3 = State()
    withdrawStage4 = State()
    lookingWithdrawRequests = State()
    replenishStage1 = State()
    replenishStage2 = State()
    replenishSumInputAwaiting = State()
    onAddTaskMarket = State()
    packTaskChosen = State()


# ------------- Чисто текстовые функции для сообщений ----------
async def menumsg(id):
    dbdata = await db.getInfo(id)
    refcount = await db.getRefsCount(id)
    WelcomeMessage = f"""
🧞‍♂ Hola,  <b>{dbdata[14]}</b> 🫡

Nivel: <b>{dbdata[4]}</b>
Experiencia: <b>{dbdata[19]} / {await tech.getNearestRank(int(dbdata[3]), lvlList) - await tech.getPreviousRank(int(dbdata[3]), lvlList)} </b>
Rango: <b> {f"Iron🦾️</b> ({15-int(dbdata[4])} {data['txt']['tillNextRank']})" if int(dbdata[2]) == 1 else f"Bronze🥉</b> ({50-int(dbdata[4])} {data['txt']['tillNextRank']})" if int(dbdata[2]) == 2 else f"Silver🥈</b> ({15-int(dbdata[4])} {data['txt']['tillNextRank']})" if int(dbdata[2]) == 3 else "Gold🏅</b>"}

Saldo: <b>{round(dbdata[6], 3)} USD</b> 
Tareas restantes:  <b>{dbdata[8]}</b>
Límite de misiones diarias: <b>{dbdata[10]}/{dbdata[9]}</b>

Saldo de referencia: <b>{dbdata[7]} USD</b>

Cant. invitados: <b>{refcount}</b>

<b> {data['txt']['mainMenuNews']} </b>
    """
    return WelcomeMessage
async def afterStart(fname, lname):
    msg = f"""
Hola, <b>{fname} {lname if not "None" else " "} 🖐</b> 
Para continuar con el registro, comparte el número (haga clic en el botón de abajo)
    """
    return msg
async def taskMarket():
    msg = """
<b>[BOLSA DE TRABAJO]</b>

️🧞‍♂  Me alegro de verte en la bolsa de trabajo. Completa tareas y obtén dinero 💰

Pagos por tareas completadas por rango:
🦾 <b>Iron</b>   (1lvl+)   0.25-0.3 USD
🥉 <b>Bronze</b>   (15lvl+)   0.35-0.5 USD
🥈 <b>Silver</b>   (50lvl+)   0.6-0.9 USD
🥇 <b>Gold</b>   (100lvl+)   1-4 USD

Elige una categoría y empieza a ganar 👇
    """
    return msg
async def ironTasks(id):
    data = await db.getInfo(id)
    msg = f"""
<b>[MISIONES DE IRON 🦾]</b>

Saldo: <b>{round(data[6], 3)} USD</b>       
Tareas restantes:  <b>{data[8]}</b>
Límite de misiones diarias: <b>{data[10]}/{data[9]}</b>

️🧞‍♂ Completa tareas y obtén dinero. 

Puede obtener 0.25-0.3 USD por tareas completadas con el rango de <b>Iron</b>
    """
    return msg
async def bronzeTasks(id):
    data = await db.getInfo(id)
    msg = f"""
<b>[MISIONES DE BRONZE🥉]</b>

Saldo: <b>{round(data[6], 3)} USD</b>      
Tareas restantes:  <b>{data[8]}</b>
Límite de misiones diarias: <b>{data[10]}/{data[9]}</b>

️🧞‍♂ Completa tareas y obtén dinero. 

Puede obtener 0.4 USD por tareas completadas con el rango de <b>Bronze</b>
    """
    return msg
async def silverTasks(id):
    data = await db.getInfo(id)
    msg = f"""
<b>[MISIONES DE SILVER🥉]</b>

Saldo: <b>{round(data[6], 3)} USD</b>         
Tareas restantes:  <b>{data[8]}</b>
Límite de misiones diarias: <b>{data[10]}/{data[9]}</b>

️🧞‍♂ Completa tareas y obtén dinero. 

Puede obtener 0.6 USD por tareas completadas con el rango de <b>Silver</b>
    """
    return msg
async def goldTasks(id):
    data = await db.getInfo(id)
    msg = f"""
<b>[MISIONES DE GOLD🥉]</b>

Saldo: <b>{round(data[6], 3)} USD</b> 
Tareas restantes:  <b>{data[8]}</b>
Límite de misiones diarias: <b>{data[10]}/{data[9]}</b>

️🧞‍♂ Completa tareas y obtén dinero. 

Puede obtener 1-4 USD por tareas completadas con el rango de <b>Gold</b>
    """
    return msg
async def levelIsTooLow():
    msg = """
<b>[TU NIVEL ES DEMASIADO BAJO]</b>

Te recordamos que a partir del nivel 1 solo está disponible la categoría Hierro. Además, para poder entrar necesitas aumentar tu nivel.

🦾 Hierro: disponible a partir del nivel 1
🥉 Bronce - disponible a partir del nivel 15
🥈 Plata - disponible a partir del nivel 50
🥇 Oro: disponible a partir del nivel 100

Sube algunos niveles y vuelve 💪
    """
    return msg
async def activeTask(type, platform, link, id, addInfo):
    data = await db.getInfo(id)
    msg = f"""
<b>[{type}]</b>

Tarea: <b>{type.lower()}</b>
Plataforma:  <b>{platform}</b>
Recompensa:  <b>{data[12]}$ + {data[11]} EXP + [Tu bono de nivel es : {data[13]} USD]</b>
Enlace:  {link}
Informacion adicional: <b> {addInfo} </b>

️🧞‍♂ No olvides presionar el botón cuando completes la tarea.

🚨INTENTO DE FRAUDE LLEVARÁ AL BLOQUEO DE CUENTA🚨
    """
    return msg
async def acceptedTask(id, type, platform):
    data = await db.getInfo(id)
    msg = f"""
<b>[ASIGNACIÓN ACEPTADA ✅]</b>
‍
Tarea: <b>{type}</b>
Plataforma:  <b>{platform}</b>

Has sido recompensado:
Recompensa:  <b>{data[12]} USD + {data[11]} EXP + [Tu bono de nivel es : {data[13]} USD]</b>

️🧞‍Gracias, la recompensa ha sido otorgada 👍

Saldo: <b>{round(data[6], 3)} USD</b>
Tareas restantes:  <b>{data[8]}</b>
Límite de misiones diarias: <b>{data[10]}/{data[9]}</b>

🚨INTENTO DE FRAUDE LLEVARÁ AL BLOQUEO DE CUENTA 🚨
    
    """
    return msg
async def refProgram(id):
    dbdata = await db.getInfo(id)
    refcount = await db.getRefsCount(id)
    msg = f"""
<b> [PROGRAMA DE REFERENCIA] </b>

Saldo de referencia: <b> {dbdata[7]} </b>  USD
Cant. invitados: <b> {refcount} </b>

Su enlace de referencia
<code>t.me/{data['bot']['username']}?start={dbdata[0]} </code>

Invita personas y gana 🤩
Según los términos de nuestro programa de fidelización, recibirás el 10 % de las ganancias de cada persona a la que hayas invitado 🤑
    """
    return msg
async def myRefList(id):
    dbdata = await db.getInfo(id)
    refcount = await db.getRefsCount(id)
    msg = f"""
<b> [MIS INVITACIONES] </b>

Cant. invitados: <b> {refcount} </b>

Su enlace de referencia:
<code>t.me/{data['bot']['username']}?start={dbdata[0]}</code>

Las últimas personas que invitaste: 
    """
    return msg
async def startWithdraw(id):
    dbdata = await db.getInfo(id)
    withdrawRequestCountText = await db.getActiveWithdrawRequests(id)
    msg = f"""
<b> [RETIRO DE SALDO] </b>

Saldo: <b>{round(dbdata[6], 3)} USD</b>
Saldo de referencia: <b>{dbdata[7]} USD</b>
Monto mínimo de retiro: <b>50 USD</b>
Solicitudes de retiro: <b>{withdrawRequestCountText}/{data['prefs']['maxWithdrawRequests']}</b>

❗️Antes de retirar, lee las condiciones de retiro:
✦ El retiro se produce una vez a la semana (de jueves a domingo)
✦ Puede crear un máximo <b> {data['prefs']['maxWithdrawRequests']} solicitudes </b>de retiro por semana
✦ Cantidad mínima de retiro <b> {data['prefs']['minWithdrawSum']} </b>
✦ El retiro de la transmisión y el saldo de referencia se crean por separado
✦ La tarifa de retiro es pagada por el destinatario
✦ Usted es el único responsable de la exactitud de los datos creados en la solicitud de retiro

    """
    return msg
async def checkingWithdrawRequestsCount():
    msg = f"""
<b> [[CREANDO UNA SOLICITUD DE RETIRO paso 1 de 4] </b>  

Comprobando el número de aplicaciones disponibles esta semana...

❗Puede crear un máximo de{data['prefs']['maxWithdrawRequests']} solicitudes de retiro por semana
    """
    return msg
async def maxRequestsWithdrawDenied(id):
    withdrawRequestCountText = await db.getActiveWithdrawRequests(id)
    msg = f"""
<b> [RECHAZO] </b>

<b> ❌ RECHAZO ❌ </b>
Ya ha creado el número máximo de solicitudes de retiro. Espere a que se completen los antiguos o elimínelos.

Aplicaciones creadas: <b> {withdrawRequestCountText}/{data['prefs']['maxWithdrawRequests']} </b>
❗Puede crear un máximo de 2 solicitudes de retiro por semana
    """
    return msg
async def withdrawStage2():
    msg = """
<b> [CREANDO UNA SOLICITUD DE RETIRO paso 2 de 4] </b>

Para comenzar, elija el método con el que desea retirar dinero
    """
    return msg
async def withdrawStage3(id):
    data = await db.getInfo(id)
    msg =  f"""
<b> [CREANDO UNA SOLICITUD DE RETIRO paso 3 de 4] </b>

Saldo: <b> {round(data[6], 3)} USD  </b>
Saldo de referencia: <b> {data[7]} USD </b>

Monto mínimo de retiro: <b> 50 USD </b>

❗Ingrese el monto del retiro y el saldo del que desea retirar dinero.
    """
    return msg
async def checkingWithdrawRequest():
    msg = """
<b> [COMPROBANDO LA SOLICITUD CREADA] </b>

Estamos revisando su solicitud para crear una aplicación...
    """
    return msg
async def withdrawStage4(vendor):
    msg = f"""
<b> [CREANDO UNA SOLICITUD DE RETIRO paso 4 de 4] </b>

Queda muy poco 🫣

⏳ Introduce el número de cuenta <b> {data['txt']['USDTTRC'] if vendor == 'usdt_trc' else data['txt']['USDTERC'] if vendor == 'usdt_erc' else data['txt']['BTC'] if vendor == 'btc' else data['txt']['ETH'] if vendor == 'eth' else f"Vendor: {vendor}"} </b> a la que debemos enviarte el dinero que has ganado.

    """
    return msg
async def withdrawPreFinale(ref, sum, vendorstring):
    msg = f"""
<b> ✅ [LA CONFIRMACIÓN] </b>

💼 Método de pago: <b> {data['vendors'][f'{vendorstring.split(".")[0]}']} </b>
💲 Monto de pago: <b>{round(sum, 3)}</b> USD {data['txt']['fromRefBalance'] if ref == 1 else ""}
✍️ Número de cuenta de pago: <code> {vendorstring.split(".")[2]} </code>

ℹ️El pago se realiza una vez por semana de jueves a domingo.


    """
    return msg
async def withdrawRequestCreated(ref, sum, requestNum, vendorstring):
    msg = f"""
<b> [SOLICITUD DE RETIRO CREADA CON ÉXITO] </b>

✅ Aplicación №{requestNum} creada con éxito 👍

Método de pago: <b> {data['vendors'][f'{vendorstring.split(".")[0]}']} </b>
Tipo de billetera de pago: <b>{round(sum, 3)}</b> USD {data['txt']['fromRefBalance'] if ref == 1 else ""}
Número de cuenta de pago: <code> {vendorstring.split(".")[2]} </code>

🔔 Lo recibirás cuando se pague el dinero
    """
    return msg
async def myWithdrawRequests(reqs):
    msg = f"""
[SOLICITUDES DE RETIRO]

{reqs}

    """
    return msg
async def getMyWRRequestInText(reqsRaw):
    msgText = ""
    for i in range(len(reqsRaw)):
        msgText = msgText + f"-----------------" \
                            f"\nID: <b> {reqsRaw[i][1]} </b>\n\n" \
                            f"{data['txt']['walletToWithdraw']}: <b>{reqsRaw[i][3]}</b>\n" \
                            f"{data['txt']['paymentSum']}: <b>{round(float(reqsRaw[i][2]))}</b>\n" \
                            f"{data['txt']['paymentWalletType']}: <b>{data['txt']['walletBalance'] if reqsRaw[i][4] == 'WalletBalanceDraw' else data['txt']['refBalance']}</b>\n" \
                            f"{data['txt']['paymentCurrency']}: <b>{data['vendors'][reqsRaw[i][5]]}</b>\n" \
                            f"{data['txt']['paymentDate']}: <b>{reqsRaw[i][6]}</b>\n" \
                            f"-----------------\n\n"

    return msgText
async def contactsMenu():
    msg = f"""
[CONTACTOS  {data['bot']['username'].upper()}]

Importante. No comparta la contraseña de su cuenta con nadie. 

<b>Sitio web oficial </b>
{data['bot']['website']}

<b>Telegram oficial</b>
{data['bot']['telegram']}

<b>Instagram</b>
{data['bot']['instagram']}

<b>Twitter</b>
{data['bot']['twitter']}
    """
    return msg
async def supportMenu():
    msg = f"""
<b> [[APOYO TÉCNICO]] </b>

Si tiene algún problema o pregunta, siempre puede escribir a nuestro soporte  🦾

Nuestro soporte funciona no solo en Telegram sino también en el chat de nuestro sitio web

<b> Sitio web oficial </b>
{data['bot']['website']}

<b> Operador en Telegram </b>
{data['bot']['operator']}
    """
    return msg
async def replenishMenuStage1(id):
    dbdata = await db.getInfo(id)
    msg = f"""
<b> [RECARGAR LA CUENTA 💸] </b>

Saldo: <b> {round(dbdata[6], 3)} </b>USD

Puedes recargar tu cuenta de varias maneras:
📌 Criptomonedas btc, eth, usdt (trc20 y erc20)
📌 SWIFT Transferencia <i> (en desarrollo) </i> 
📌 VISA / MASTERCARD <i> (en desarrollo)</i>
 
Tenemos varios artículos en el sitio con instrucciones paso a paso para recargar una cuenta.

También puede ponerse en contacto con nuestro soporte técnico para obtener ayuda con la recarga.
    """
    return msg
async def replenishChooseVendor():
    msg = """
<b> [SELECCIONE UN MÉTODO DE DEPÓSITO] </b>

Para comenzar, elija el método con el que desea depositar fondos en su cuenta en nuestra plataforma
    """
    return msg
async def replenishSumInput(id, vendorstring):
    vendor = vendorstring[1]
    dbdata = await db.getInfo(id)
    msg = f"""
<b> [INGRESE LA CANTIDAD DE RECARGA EN USD $] </b>

💲 Saldo actual:<b> {round(dbdata[6], 3)} </b> USD
ℹ️ Cantidad mínima de depósito: <b>{data['prefs']['minReplenishSum']}</b> USD
💼 Método de depósito seleccionado: <b> {data['txt']['USDTTRC'] if vendor == 'usdttrc' else data['txt']['USDTERC'] if vendor == 'usdterc' else data['txt']['BTC'] if vendor == 'btc' else data['txt']['ETH'] if vendor == 'eth' else f"Vendor: {vendor}"} </b>

❗ Tenga en cuenta que la casa de cambio o el banco pueden cobrarle una comisión adicional. Tú pagas la comisión.

<b> ✍️ Introduce el importe que quieres recargar en tu cuenta </b>
    """
    return msg
async def generateReplenishInvoice(id, sum, vendor):
    msg = f"""
<b> [INVOICE CREATION] </b>

ID: <b> {id} </b>
Sum: <b> {sum} </b>
Vendor: <b> {data['txt']['USDTTRC'] if vendor == 'usdttrc' else data['txt']['USDTERC'] if vendor == 'usdterc' else data['txt']['BTC'] if vendor == 'btc' else data['txt']['ETH'] if vendor == 'eth' else f"Vendor: {vendor}"} </b>
    """
    return msg
async def buyAdditionalTasks(id):
    dbdata = await db.getInfo(id)
    msg = f"""
[COMPRAR MISIONES ADICIONALES]

Tareas restantes:  <b>{dbdata[8]}</b>

Aquí puedes comprar tareas adicionales. Para la compra, puede usar dinero de los saldos regulares y de referencia. 

No vendemos asignaciones individualmente, vendemos asignaciones en lotes.
🎟
<b>Pack {data['packs']['pack1'].split("|")[0]} заданий </b> | Precio: {data['packs']['pack1'].split("|")[1]}
<b>Pack {data['packs']['pack2'].split("|")[0]} заданий </b> | Precio: {data['packs']['pack2'].split("|")[1]}
<b>Pack {data['packs']['pack3'].split("|")[0]} заданий </b> | Precio: {data['packs']['pack3'].split("|")[1]}
<b>Pack {data['packs']['pack4'].split("|")[0]} заданий </b> | Precio: {data['packs']['pack4'].split("|")[1]}
<b>Pack {data['packs']['pack5'].split("|")[0]} заданий </b> | Precio: {data['packs']['pack5'].split("|")[1]}
<b>Pack {data['packs']['pack6'].split("|")[0]} заданий </b> | Precio: {data['packs']['pack6'].split("|")[1]}


Elige el paquete que necesitas y págalo del saldo.
    """
    return msg
async def buyPackApprove(id, stateData):
    dbdata = await db.getInfo(id)
    msg = f"""
<b>[COMPRA PAQUETE DE TAREAS]</b>

Quiere comprar un paquete. 
Tipo de paquete: <b>{stateData['taskCount']} tareas </b>
Precio del paquete: <b>{stateData['packPrice']}$</b>

Saldo: <b>{round(dbdata[6], 3)} USD</b>
Saldo de referencia: <b>{dbdata[7]} USD</b>

❗Asegúrate de tener suficiente dinero en tu saldo y confirma la compra
    """
    return msg
async def onTaskBuycheckBalance():
    msg = """
<b> [COMPROBACIÓN DE SALDO] </b>

Consultando tu saldo...


    """
    return msg
async def packBuyApproved(id, stateData):
    dbdata = await db.getInfo(id)
    msg = f"""
<b> [PAQUETE DE COMPRA APROBADO✅] </b>

Paquete comprado. 
Has sido acreditado: <b> {stateData['taskCount']} tareas </b>
Cobrado de su cuenta: <b>{stateData['packPrice']} USD</b>

Saldo: <b>{round(dbdata[6], 3)} USD</b>
Saldo de referencia: <b>{dbdata[7]} USD</b>
Tareas restantes: <b>{dbdata[8]}</b>


    """
    return msg
#----------------------------------------------------------------
@dp.message_handler(commands=['start'], state="*")
async def processNewStartCommand(msg: types.Message):
    if await db.checkifExists(msg.chat.id) == 0: #esli NE zaregan
        if len(msg.text.split(" ")) == 2: # esli est' Ref priglasivhiy
            ref = msg.text.split(" ")[1]
            await db.regUser(msg.chat.id, "inProcess", str(datetime.datetime.now()).split(".")[0], msg.from_user.first_name, ref, msg.from_user.username)
            await msg.bot.send_message(ref, reply_markup=kb.onNewRefNotification(), disable_notification=True, text=f"{data['txt']['newRefNotification']} <code> @{msg.from_user.username if msg.from_user.username is not None else msg.chat.id} </code>")
        else: #rega bez priglosa
            await db.regUser(msg.chat.id, "inProcess", str(datetime.datetime.now()).split(".")[0],
                             msg.from_user.first_name, 0, msg.from_user.username)
        await msg.bot.send_message(msg.chat.id, reply_markup=kb.requestContact(), disable_notification=True,
                               text=await afterStart(msg.from_user.first_name, msg.from_user.last_name))
        await States.awaitingContact.set()
    else: #esli zaregan
        if await db.checkPhone(msg.chat.id) == "inProcess":
            await msg.bot.send_message(msg.chat.id, reply_markup=kb.requestContact(), disable_notification=True,
                                       text=await afterStart(msg.from_user.first_name, msg.from_user.last_name))
            await States.awaitingContact.set()
        else:
            await msg.bot.send_message(msg.chat.id, reply_markup=kb.menuInline(), disable_notification=True,
                                   text=await menumsg(msg.chat.id))
            await States.menu.set()
            await db.logLastActivity(msg.chat.id, str(datetime.datetime.now()).split(".")[0])

@dp.message_handler(content_types=['contact'], state=States.awaitingContact) # Обработка входящего контакта, завершение регистрации
async def makeReg(msg: types.Message):
    await db.updateContact(msg.chat.id, msg.contact.phone_number)
    await msg.bot.send_message(msg.chat.id, reply_markup=ReplyKeyboardRemove(), disable_notification=True, text=f"{data['txt']['SuccefulRegistration']}")
    await msg.bot.send_message(msg.chat.id, reply_markup=kb.menuInline(), disable_notification=True, text=await menumsg(msg.chat.id))
    await States.menu.set()

@dp.message_handler(content_types=['text'], state=States.menu) # обработка непонятного текста и команды /start
@dp.message_handler(commands=['start'], state=States.menu)
async def processStartCommand(msg: types.Message):
    await msg.bot.send_message(msg.chat.id, reply_markup=kb.menuInline(), disable_notification=True, text=await menumsg(msg.chat.id))
    await States.menu.set()

@dp.callback_query_handler(text="open_task_market", state="*") # Открыть биржу заданий
async def taskMarketOpen(call: types.CallbackQuery):
    await call.bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.bot.send_message(call.from_user.id, reply_markup=kb.taskMarketKeyboard(), disable_notification=True, text=await taskMarket())
    await States.onTaskMarket.set()

# ------------ Varianty dlya birzhy zadaniy -----------------
# 1 - Iron | 2 - Bronze | 3 - Silver | 4 - Gold

@dp.callback_query_handler(text=["iron_tasks", "bronze_tasks", "silver_tasks", "gold_tasks"], state=States.onTaskMarket) # Выбор задания по рангу
async def getTasksByRank(call: types.CallbackQuery):
    cid = call.message.chat.id
    if call.data == "iron_tasks":
        await call.bot.delete_message(cid, call.message.message_id)
        await call.bot.send_message(cid, reply_markup=kb.tasksForAllRanks(), disable_notification=True,
                                    text=await ironTasks(call.from_user.id))
        await States.readyToCompleteTask.set()
    elif call.data == "bronze_tasks" and await db.checkRank(cid) >= 2:
        await call.bot.delete_message(cid, call.message.message_id)
        await call.bot.send_message(cid, reply_markup=kb.tasksForAllRanks(), disable_notification=True,
                                    text=await bronzeTasks(call.from_user.id))
        await States.readyToCompleteTask.set()
    elif call.data == "silver_tasks" and await db.checkRank(cid) >= 3:
        await call.bot.delete_message(cid, call.message.message_id)
        await call.bot.send_message(cid, reply_markup=kb.tasksForAllRanks(), disable_notification=True,
                                    text=await bronzeTasks(call.from_user.id))
        await States.readyToCompleteTask.set()
    elif call.data == "gold_tasks" and await db.checkRank(cid) >= 4:
        await call.bot.delete_message(cid, call.message.message_id)
        await call.bot.send_message(cid, reply_markup=kb.tasksForAllRanks(), disable_notification=True,
                                    text=await goldTasks(call.from_user.id))
        await States.readyToCompleteTask.set()
    else:
        await call.bot.delete_message(cid, call.message.message_id)
        await call.bot.send_message(cid, reply_markup=kb.levelIsTooLow(), disable_notification=True,
                                    text=f"Tu nivel es demasiado bajo para misiones de rango <b>{'Silver' if call.data == 'silver_tasks' else 'Bronze' if call.data == 'bronze_tasks' else 'Gold'}</b>\n"
                                         f"{await levelIsTooLow()}")
        await States.readyToCompleteTask.set()

@dp.callback_query_handler(text=["back_to_rank_choosing"], state=States.readyToCompleteTask) # Назад к выбору рангов
async def backToTaskMarket(call: types.CallbackQuery):
    await call.bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.bot.send_message(call.from_user.id, disable_notification=True, reply_markup=kb.taskMarketKeyboard(), text=await taskMarket())
    await States.onTaskMarket.set()

@dp.callback_query_handler(text="backtomenu", state="*") # Назад в главное меню
async def backToMainMenu(call: types.CallbackQuery):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    try:
        await call.bot.send_message(cid, reply_markup=kb.menuInline(), disable_notification=True, text=await menumsg(call.from_user.id))
    except TypeError:
        await call.bot.send_message(cid, disable_notification=True,
                                    text=data['txt']['registartionErrorOccured'])
    await States.menu.set()
    await db.logLastActivity(cid, str(datetime.datetime.now()).split(".")[0])

# ------------- Получить новое задание ---------------

@dp.callback_query_handler(text=["get_new_task"], state=States.readyToCompleteTask)
async def getNewTask(call: types.CallbackQuery):
    cid = call.message.chat.id
    async def getNextTaskFromDb(id):
        taskid = int(await db.getCurrentTaskId(id))
        try:
            return data['linkbank'][f'{taskid+1}'].split('|')
        except KeyError:
            return "taskListEnded"

    task = await getNextTaskFromDb(cid)
    await call.bot.delete_message(cid, call.message.message_id)
    msgToEdit = await call.bot.send_message(chat_id=cid, disable_notification=True, text=data['txt']['newTaskLoading'])
    await asyncio.sleep(0.5)
    await call.bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id, disable_web_page_preview=True, reply_markup=kb.activeTaskWork(task[0]) if task != "taskListEnded" else kb.justMainMenu(),
                                     text=f"{await activeTask(platform=task[2], type=task[1], link=task[0], id=cid, addInfo=task[3]) if task != 'taskListEnded' else data['txt']['noMoreTasksInFile']}")
    await States.readyToCompleteTask.set()

 # "Я выполнил задание"
@dp.callback_query_handler(text=["i_completed_task"], state=States.readyToCompleteTask)
async def iCompletedTaskFunc(call: types.CallbackQuery):
    cid = call.message.chat.id
    dbdata = await db.getInfo(cid)
    async def processCompletedTaskData(id):
        taskid = int(await db.getCurrentTaskId(id))
        return data['linkbank'][f'{taskid}'].split('|')

    if await db.taskCompletedHandler(dbdata[0], dbdata[11], dbdata[12], dbdata[9], dbdata[10], dbdata[8], dbdata[13]) == "Success":
        await call.bot.delete_message(cid, call.message.message_id)
        msgToEdit = await call.bot.send_message(chat_id=cid, disable_notification=True, text=data['txt']['checkingTaskCompletion'])
        await asyncio.sleep(1.5)
        processCompletedTaskDataResult = await processCompletedTaskData(cid)
        await call.bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id, reply_markup=kb.acceptedTask(),
                                         text=await acceptedTask(cid, processCompletedTaskDataResult[1], processCompletedTaskDataResult[2]))
        if await db.completedJobLevelHandler(cid) == "levelup": await call.bot.send_message(cid, reply_markup=kb.close(), disable_notification=True, text=data['txt']['levelup'])  # "Левел или ранк повышен уведомление"
        await States.readyToCompleteTask.set()

    elif await db.taskCompletedHandler(dbdata[0], dbdata[11], dbdata[12], dbdata[9], dbdata[10], dbdata[8], dbdata[13]) == "DailyLimitReached":
        await call.bot.delete_message(cid, call.message.message_id)
        await call.bot.send_message(chat_id=cid, reply_markup=kb.justMainMenu(), disable_notification=True, text=f"{data['txt']['dailyTaskLimitReached']}\n\n"
                                                                                                                 f"<b>{dbdata[10]}/{dbdata[9]}</b>")
    elif await db.taskCompletedHandler(dbdata[0], dbdata[11], dbdata[12], dbdata[9], dbdata[10], dbdata[8], dbdata[13]) == "AvailableJobLimitReached":
        await call.bot.delete_message(cid, call.message.message_id)
        await call.bot.send_message(chat_id=cid, reply_markup=kb.justMainMenu(), disable_notification=True,
                                    text=f"{data['txt']['wholeTaskLimitReached']}\n\n"
                                         f"{data['txt']['availableTasksLeft']} <b>{dbdata[8]}</b>")

# Реферальная программа
@dp.callback_query_handler(text=["ref_program"], state="*")
async def RefferalProgram(call: types.CallbackQuery):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    await call.bot.send_message(cid, reply_markup=kb.referralProgramMenu(), disable_notification=True, text=await refProgram(cid))
    await States.onRefProgram.set()

# Получить список рефов
@dp.callback_query_handler(text=["my_refs_list"], state=States.onRefProgram)
async def getRefsList(call: types.CallbackQuery):
    cid = call.message.chat.id
    reflist = await db.getRefsListFromDb(cid)
    async def unpackRefList(listFromDb):
        msg = """"""
        for i in (range(0, len(listFromDb))):
            msg = msg + f"<b>id{listFromDb[i][0]}</b> @{listFromDb[i][1] if listFromDb[i][1] != 'None' else ''}\n"
        return msg
    lastRefsList = await unpackRefList(reflist)
    await call.bot.delete_message(cid, call.message.message_id)
    msgToEdit = await call.bot.send_message(cid, disable_notification=True, text=data['txt']['refsListLoading'])
    await call.bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id, reply_markup=kb.inRefListMenu(), text=f"{await myRefList(cid) if len(lastRefsList) != 0 else data['txt']['youDontInvitedAnyoneYet']} \n"
                                                                                 f"{lastRefsList if len(lastRefsList) !=0 else ''}")
    await States.onRefProgram.set()

 # Скопировать реферальную ссылку
@dp.callback_query_handler(text=["copy_reflink"], state=States.onRefProgram)
async def showReflinkAlert(call: types.CallbackQuery):
    await call.bot.answer_callback_query(callback_query_id=call.id, text=f"{data['txt']['refLinkAlert']}", show_alert=False)
    await States.onRefProgram.set()

 # Меню вывода
@dp.callback_query_handler(text=["withdraw"], state=[States.menu, States.withdrawStage1])
async def withdrawFirstStage(call: types.CallbackQuery):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    await call.bot.send_message(cid, disable_notification=True, reply_markup=kb.withdrawStart(), text=await startWithdraw(cid))
    await States.withdrawStage1.set()

# Создать заявку на вывод, шаг 1
@dp.callback_query_handler(text=["create_withdraw_request"], state=States.withdrawStage1)
async def createWithdrawRequestStageFirst(call: types.CallbackQuery):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    msgToEdit = await call.bot.send_message(cid, disable_notification=True, text=await checkingWithdrawRequestsCount())
    await asyncio.sleep(1.5)
    if await db.getActiveWithdrawRequests(cid) < int(data['prefs']['maxWithdrawRequests']):
        await call.bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id, reply_markup=kb.payVendors(), text=await withdrawStage2())
        await States.withdrawStage2.set()
    else: await call.bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id, reply_markup=kb.justMainMenu(), text=await maxRequestsWithdrawDenied(cid))

# -------------------- Если выбрали недоступную платежку --------------------------
@dp.callback_query_handler(text=["visa_mc", "swift", "astropay"], state=[States.withdrawStage2])
async def showUnavailablePayVendorAlert(call: types.CallbackQuery):
    await call.bot.answer_callback_query(callback_query_id=call.id, text=f"{data['txt']['payVendorAlert']}", show_alert=True)
    await States.withdrawStage2.set()

@dp.callback_query_handler(text=["REPLvisa_mc", "REPLswift", "REPLastropay"], state=[States.replenishStage2])
async def showUnavailablePayVendorAlert(call: types.CallbackQuery):
    await call.bot.answer_callback_query(callback_query_id=call.id, text=f"{data['txt']['payVendorAlert']}", show_alert=True)
    await States.replenishStage2.set()
# ---------------------------------------------------------------------------------

# Выбор баланса для вывода
@dp.callback_query_handler(text=["usdt_erc", "usdt_trc", "btc", "eth"], state=States.withdrawStage2)
async def witdhdrawThirdStage(call: types.CallbackQuery, state: FSMContext):
    cid = call.message.chat.id
    await state.set_state(call.data)
    await call.bot.delete_message(cid, call.message.message_id)
    await call.bot.send_message(cid, reply_markup=kb.chooseWithdrawBalance(), disable_notification=True, text=await withdrawStage3(cid))

# Проверка минимальной суммы вывода с выбранного баланса, ждем ввод кошелька юзером
@dp.callback_query_handler(text=["wallet_bal_withdraw", "ref_bal_withdraw"], state=[States.withdrawStage3, "usdt_trc", "usdt_erc", "btc", "eth"])
async def withdrawFourthStage(call: types.CallbackQuery, state: FSMContext):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    msgToEdit = await call.bot.send_message(cid, disable_notification=True, text=await checkingWithdrawRequest())
    if call.data == "wallet_bal_withdraw":
        if await db.checkWalletBalanceWithdrawPossibility(cid):
            await asyncio.sleep(1.5)
            method = await state.get_state()
            await call.bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id,
                                             text=await withdrawStage4(method))
            await state.set_state(f"{method}.approved")
        else:
            await call.bot.edit_message_text(chat_id=cid, reply_markup=kb.justMainMenu(), message_id=msgToEdit.message_id,
                                             text=data['txt']['walBalLessThenMinimalWithdraw'])
    elif call.data == "ref_bal_withdraw":
        if await db.checkRefBalanceWithdrawPossibility(cid):
            await asyncio.sleep(1.5)
            method = await state.get_state()
            await call.bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id,
                                             text=await withdrawStage4(method))
            await state.set_state(f"{method}.approvedRef")
        else:
            await call.bot.edit_message_text(chat_id=cid, reply_markup=kb.justMainMenu(), message_id=msgToEdit.message_id,
                                             text=data['txt']['refBalLessThenMinimalWithdraw'])

#Предпоследний шаг, ждем кошелька от юзера
@dp.message_handler(content_types=['text'], state=["usdt_trc.approved", "usdt_erc.approved", "btc.approved", "eth.approved",
                                                   "usdt_trc.approvedRef", "usdt_erc.approvedRef", "btc.approvedRef", "eth.approvedRef"])
async def withdrawDetailsInputStage(msg: types.Message, state: FSMContext):
    cid = msg.chat.id
    method = await state.get_state()
    await state.set_state(f"{method}.{msg.text}")
    methodAndVendor = await state.get_state()
    methodAndVendor = await tech.antixss(methodAndVendor)
    if methodAndVendor.split(".")[1] == "approved":
        await msg.bot.delete_message(cid, msg.message_id)
        await msg.bot.send_message(cid, reply_markup=kb.approveWithdrawRequestCreation(), disable_notification=True,
                                               text=await withdrawPreFinale(ref=0, sum=await db.getBalance(cid, 0),
                                                                            vendorstring=methodAndVendor))
        await state.set_state(f"{methodAndVendor}")
    elif methodAndVendor.split(".")[1] == "approvedRef":
        await msg.bot.send_message(cid, reply_markup=kb.approveWithdrawRequestCreation(), disable_notification=True,
                                               text=await withdrawPreFinale(ref=1, sum=await db.getBalance(cid, 1),
                                                                            vendorstring=methodAndVendor))
        await state.set_state(f"{methodAndVendor}")

#Финалочка, создаем заявку
@dp.callback_query_handler(text=["approve_withdraw"], state="*")
async def withdrawFinalStage(call: types.CallbackQuery, state: FSMContext):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    checkstate = await state.get_state() # btc.approved.0xdhbd743
    if checkstate.split('.')[0] in data['vendors']:
        num = await db.getLastRequestNum() + 1
        wallet = checkstate.split('.')[2]
        type = "RefBalanceDraw" if checkstate.split('.')[1] == "approvedRef" else "WalletBalanceDraw"
        sum = await db.getBalance(cid, 1 if type == "RefBalanceDraw" else 0)
        coin = checkstate.split('.')[0]
        date = str(datetime.datetime.now()).split(".")[0]
        if await db.addWithdrawRequest(cid, num, sum, wallet, type, coin, date) != "invalidWallet":
            await tech.adminWithdrawNotification(cid, num, sum, wallet, type, coin, date)
            await call.bot.send_message(cid, reply_markup=kb.justMainMenu(), disable_notification=True,
                                        text=await withdrawRequestCreated(ref=1 if type == "RefBalanceDraw" else 0,
                                                                          requestNum=num, vendorstring=checkstate, sum=sum))
        else:
            await call.bot.send_message(cid, reply_markup=kb.justMainMenu(), disable_notification=True,
                                        text=data['txt']['invalidWalletRequest'])
    else:
        await call.bot.send_message(cid, reply_markup=kb.justMainMenu(), disable_notification=True,
                                    text=data['txt']['createWithdrawRequestEmergencyQuit'])
        await States.menu.set()

#Получаем свои заявки на выводvv

#Список заявок на вывод
@dp.callback_query_handler(text=["my_withdraw_requests"], state=States.withdrawStage1)
async def getMyWithdrawRequests(call: types.CallbackQuery, state: FSMContext):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    reqsRaw = await db.getMyWithdrawRequests(cid)
    try:
        await call.bot.send_message(cid, reply_markup=await kb.deleteMyWithdrawRequests(reqsRaw), disable_notification=True, text=await getMyWRRequestInText(reqsRaw))
    except aiogram.utils.exceptions.MessageTextIsEmpty:
        await call.bot.send_message(cid, reply_markup=kb.justMainMenu(), disable_notification=True,
                                    text=data['txt']['noRequestsLeft'])
    await States.lookingWithdrawRequests.set()

#Удаление заявок на вывод
@dp.callback_query_handler(state=States.lookingWithdrawRequests)
async def deleteWitdrawRequest(call: types.CallbackQuery, state: FSMContext):
    cid = call.message.chat.id
    if "deleterequest" in call.data.split('_'):
        await call.bot.answer_callback_query(callback_query_id=call.id,
                                             text=f"{data['txt']['withdrawRequestDeletedAlert']}",
                                             show_alert=True)
        if await db.deleteWithdrawRequest(cid, call.data.split('_')[1]):
            await call.bot.delete_message(cid, call.message.message_id)
            reqsRaw = await db.getMyWithdrawRequests(cid)
            try:
                await call.bot.send_message(cid, reply_markup=await kb.deleteMyWithdrawRequests(reqsRaw), disable_notification=True,
                                        text=await getMyWRRequestInText(reqsRaw))
            except aiogram.utils.exceptions.MessageTextIsEmpty:
                await call.bot.send_message(cid, reply_markup=kb.justMainMenu(), disable_notification=True,
                                            text=data['txt']['noRequestsLeft'])
        else:
            pass

    else:
        pass

#Закрыть сообщение о повышении уровня
@dp.callback_query_handler(text=["close"], state="*")
async def closeMsg(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = call.message.chat.id
        await call.bot.delete_message(cid, call.message.message_id)
    except: pass

#Обновить данные
@dp.callback_query_handler(text=["update_data"], state="*")
async def updateDataMenu(call: types.CallbackQuery):
    cid = call.message.chat.id
    try:
        await call.bot.delete_message(cid, call.message.message_id)
    except: pass
    try:
        await call.bot.send_message(cid, reply_markup=kb.menuInline(), disable_notification=True,
                                    text=await menumsg(cid))
    except TypeError:
        await call.bot.send_message(cid, disable_notification=True,
                                    text=data['txt']['registartionErrorOccured'])
    await States.menu.set()

#Контакты
@dp.callback_query_handler(text=["contacts"], state=States.menu)
async def contacts(call: types.CallbackQuery):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    await call.bot.send_message(cid, reply_markup=kb.contacts(), disable_notification=True, disable_web_page_preview=True,
                                text=await contactsMenu())

 #Поддержка
@dp.callback_query_handler(text=["support"], state="*")
async def support(call: types.CallbackQuery):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    await call.bot.send_message(cid, reply_markup=kb.support(), disable_notification=True, disable_web_page_preview=True,
                                text=await supportMenu())

#Пополнение шаг 1
@dp.callback_query_handler(text=['replenish'], state="*")
async def replenishMenuFirstStage(call: types.CallbackQuery):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    await call.bot.send_message(cid, reply_markup=kb.replenishFirst(), disable_notification=True, disable_web_page_preview=True,
                                text=await replenishMenuStage1(cid))
    await States.replenishStage1.set()

@dp.callback_query_handler(text=['goto_replenish'], state=States.replenishStage1)
async def replenishSecondStage(call: types.CallbackQuery):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    await bot.send_message(cid, disable_notification=True, reply_markup=kb.replPayVendors(),
                                text=await replenishChooseVendor())
    await States.replenishStage2.set()

@dp.callback_query_handler(text=['REPLusdterc', 'REPLusdttrc', 'REPLbtc', 'REPLeth'], state=States.replenishStage2)
async def replenishVendorChoose(call: types.CallbackQuery, state: FSMContext):
    cid = call.message.chat.id
    vendorStr = call.data.split("REPL")
    await call.bot.delete_message(cid, call.message.message_id)
    await bot.send_message(cid, disable_notification=True, text=await replenishSumInput(cid, vendorStr))
    await States.replenishSumInputAwaiting.set()
    await state.update_data(vendor=vendorStr[1])

@dp.message_handler(content_types=['text'], state=[States.replenishSumInputAwaiting])
async def replenishSecondStage(msg: types.Message, state: FSMContext):
    vendor = await state.get_data()
    vendor = vendor['vendor']
    if msg.text.isdigit():
        if int(msg.text) >= int(data['prefs']['minReplenishSum']):
            paySum = int(msg.text)
            await msg.bot.send_message(msg.chat.id, disable_notification=True,
                                       reply_markup=await kb.webappReplenish(id=paySum*913, amountUSD=paySum,
                                        amountCurrency=f"{await tech.convertUSDToCurrency(coin=vendor, amount=paySum, ratesLink=data['bot']['ratesLink'])}",
                                        tgid=msg.chat.id, paylink=data['bot']['btcpaylink'] if vendor=='btc' else data['bot']['ethpaylink'] if vendor=='eth' else data['bot']['usdttrcpaylink'] if vendor == 'usdttrc' else data['bot']['usdtercpaylink']),
                                        text=await generateReplenishInvoice(msg.chat.id, paySum, vendor))
            await tech.adminReplenishNotify(id=msg.chat.id, sum=paySum,
                                            vendor=f"{data['txt']['USDTTRC'] if vendor == 'usdttrc' else data['txt']['USDTERC'] if vendor == 'usdterc' else data['txt']['BTC'] if vendor == 'btc' else data['txt']['ETH'] if vendor == 'eth' else f'Vendor: {vendor}'}",
                                            dt=str(datetime.datetime.now()).split(".")[0])
        else:
            await msg.bot.send_message(msg.chat.id, reply_markup=kb.justMainMenu(), disable_notification=True, text=f"{data['txt']['lowerThanMinReplenishSum']} <b> {data['prefs']['minReplenishSum']}$ </b>")
            await States.replenishSumInputAwaiting.set()

@dp.callback_query_handler(text=['buy_more_tasks', 'choose_another_pack'], state=[States.menu, States.packTaskChosen])
async def buyNewTasksStepFirst(call: types.CallbackQuery):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    await bot.send_message(cid, reply_markup=kb.buyAddTasks(), disable_notification=True, text=await buyAdditionalTasks(cid))
    await States.onAddTaskMarket.set()

@dp.callback_query_handler(text=['pack1', 'pack2', 'pack3', 'pack4', 'pack5', 'pack6'], state=States.onAddTaskMarket)
async def buyNewTasks(call: types.CallbackQuery, state: FSMContext):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    taskCount, packPrice = data['packs'][f'{call.data}'].split('|')
    await state.update_data(taskCount=taskCount, packPrice=packPrice)
    stateData = await state.get_data()
    await call.bot.send_message(cid, reply_markup=kb.buyAddTasksStageSecond(),disable_notification=True, text=await buyPackApprove(cid, stateData))
    await States.packTaskChosen.set()

@dp.callback_query_handler(text=['buypack_walbal', 'buypack_refbal'], state=States.packTaskChosen)
async def buyPack(call: types.CallbackQuery, state: FSMContext):
    cid = call.message.chat.id
    await call.bot.delete_message(cid, call.message.message_id)
    stateData = await state.get_data()
    taskCount, packPrice = stateData['taskCount'], stateData['packPrice']
    msgToEdit = await call.bot.send_message(cid, disable_notification=True, text=await onTaskBuycheckBalance())
    await asyncio.sleep(1.5)
    if call.data == 'buypack_refbal':
        if await db.buyMoreTasks(cid, price=packPrice, boughtJobsCount=taskCount, refbuy=1):
            await bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id, reply_markup=kb.justMainMenu(), text=await packBuyApproved(cid, stateData))
        else:
            await bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id,reply_markup=kb.packBuyDenied(), text=data['txt']['packBuyRefBalDenied'])
    else:
        if await db.buyMoreTasks(cid, price=packPrice, boughtJobsCount=taskCount, refbuy=0):
            await bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id, reply_markup=kb.justMainMenu(),
                                        text=await packBuyApproved(cid, stateData))
        else:
            await bot.edit_message_text(chat_id=cid, message_id=msgToEdit.message_id, reply_markup=kb.packBuyDenied(),
                                        text=data['txt']['packBuyWalBalDenied'])


if __name__ == '__main__':
    executor.start_polling(dp)