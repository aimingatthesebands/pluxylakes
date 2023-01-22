from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import configparser
data = configparser.ConfigParser()
data.read("setting.ini", encoding='utf-8')

def requestContact():
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	keyboard.add(KeyboardButton(text=f'{data["txt"]["NumberButton"]}', request_contact=True))
	return keyboard

def menuInline():
	keyboard = InlineKeyboardMarkup(row_width=4)
	updateData = InlineKeyboardButton(text=f"{data['txt']['updateData']}",callback_data="update_data")
	keyboard.row(updateData)
	buyAddTasks = InlineKeyboardButton(text=f"{data['txt']['buyAdditionalTasks']}",callback_data="buy_more_tasks")
	keyboard.row(buyAddTasks)
	taskMarket = InlineKeyboardButton(text=f"{data['txt']['taskMarketLabel']}",callback_data="open_task_market")
	keyboard.row(taskMarket)
	balancetopup = InlineKeyboardMarkup(text=f"{data['txt']['balanceTopUp']}",callback_data="replenish")
	withdrawfunds = InlineKeyboardMarkup(text=f"{data['txt']['withdrawFunds']}",callback_data="withdraw")
	keyboard.row(balancetopup, withdrawfunds)
	ref = InlineKeyboardMarkup(text=f"{data['txt']['refProgram']}", callback_data="ref_program")
	conts = InlineKeyboardMarkup(text=f"{data['txt']['contacts']}", callback_data="contacts")
	keyboard.row(ref, conts)
	return keyboard

def taskMarketKeyboard():
	keyboard = InlineKeyboardMarkup()
	iron = InlineKeyboardButton(text=f"{data['txt']['ironTasks']}",callback_data="iron_tasks")
	bronze = InlineKeyboardButton(text=f"{data['txt']['bronzeTasks']}", callback_data="bronze_tasks")
	keyboard.row(iron, bronze)
	silver = InlineKeyboardButton(text=f"{data['txt']['silverTasks']}", callback_data="silver_tasks")
	gold = InlineKeyboardButton(text=f"{data['txt']['goldTasks']}", callback_data="gold_tasks")
	keyboard.row(silver, gold)
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.row(mainmenu)
	return keyboard

def tasksForAllRanks():
	keyboard = InlineKeyboardMarkup(row_width=1)
	getNewTask = InlineKeyboardButton(text=f"{data['txt']['getNewTask']}", callback_data="get_new_task")
	backToRankChoosing = InlineKeyboardButton(text=f"{data['txt']['backToRankChoosing']}", callback_data="back_to_rank_choosing")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(getNewTask, backToRankChoosing, mainmenu)
	return keyboard

def activeTaskWork(link):
	keyboard = InlineKeyboardMarkup(row_width=1)
	openTaskLink = InlineKeyboardButton(text=f"{data['txt']['openTaskLink']}", url=link)
	iCompletedTask = InlineKeyboardButton(text=f"{data['txt']['iCompletedTask']}", callback_data="i_completed_task")
	getNewTask = InlineKeyboardButton(text=f"{data['txt']['getNewTask']}", callback_data="get_new_task")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(openTaskLink, iCompletedTask, getNewTask, mainmenu)
	return keyboard

def acceptedTask():
	keyboard = InlineKeyboardMarkup(row_width=1)
	getNewTask = InlineKeyboardButton(text=f"{data['txt']['getNewTask']}", callback_data="get_new_task")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(getNewTask, mainmenu)
	return keyboard

def justMainMenu():
	keyboard = InlineKeyboardMarkup(row_width=1)
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(mainmenu)
	return keyboard

def levelIsTooLow():
	keyboard = InlineKeyboardMarkup(row_width=1)
	backToRankChoosing = InlineKeyboardButton(text=f"{data['txt']['backToRankChoosing']}", callback_data="back_to_rank_choosing")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(backToRankChoosing, mainmenu)
	return keyboard

def referralProgramMenu():
	keyboard = InlineKeyboardMarkup(row_width=1)
	myInvitations = InlineKeyboardButton(text=f"{data['txt']['myInvitations']}", callback_data="my_refs_list")
	copyRefLink = InlineKeyboardButton(text=f"{data['txt']['copyRefLink']}", callback_data="copy_reflink")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(myInvitations, copyRefLink, mainmenu)
	return keyboard

def onNewRefNotification():
	keyboard = InlineKeyboardMarkup()
	ref = InlineKeyboardMarkup(text=f"{data['txt']['refProgram']}", callback_data="ref_program")
	keyboard.add(ref)
	return keyboard

def inRefListMenu():
	keyboard = InlineKeyboardMarkup(row_width=1)
	ref = InlineKeyboardMarkup(text=f"{data['txt']['refProgram']}", callback_data="ref_program")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(ref, mainmenu)
	return keyboard

def withdrawStart():
	keyboard = InlineKeyboardMarkup(row_width=1)
	myWithdrawRequests = InlineKeyboardButton(text=f"{data['txt']['myWithdrawRequests']}", callback_data="my_withdraw_requests")
	createWithdrawRequest = InlineKeyboardButton(text=f"{data['txt']['createWithdrawRequest']}", callback_data="create_withdraw_request")
	support = InlineKeyboardButton(text=f"{data['txt']['support']}", callback_data="support")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(myWithdrawRequests, createWithdrawRequest, support, mainmenu)
	return keyboard

def payVendors():
	keyboard = InlineKeyboardMarkup(row_width=1)
	usdterc = InlineKeyboardButton(text=f"{data['txt']['USDTERC']}", callback_data="usdt_erc")
	usdttrc = InlineKeyboardButton(text=f"{data['txt']['USDTTRC']}", callback_data="usdt_trc")
	btc = InlineKeyboardButton(text=f"{data['txt']['BTC']}", callback_data="btc")
	eth = InlineKeyboardButton(text=f"{data['txt']['ETH']}", callback_data="eth")
	keyboard.row(usdterc, usdttrc)
	keyboard.row(btc, eth)
	visamc = InlineKeyboardButton(text=f"{data['txt']['VISAMC']}", callback_data="visa_mc")
	swift = InlineKeyboardButton(text=f"{data['txt']['SWIFT']}", callback_data="swift")
	astropay = InlineKeyboardButton(text=f"{data['txt']['ASTROPAY']}", callback_data="astropay")
	support = InlineKeyboardButton(text=f"{data['txt']['support']}", callback_data="support")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(visamc, swift, astropay, support, mainmenu)
	return keyboard

def chooseWithdrawBalance():
	keyboard = InlineKeyboardMarkup(row_width=1)
	withdrawFromWalletBalance = InlineKeyboardButton(text=f"{data['txt']['walletBalance']}", callback_data="wallet_bal_withdraw")
	withdrawFromRefBalance = InlineKeyboardButton(text=f"{data['txt']['refBalance']}", callback_data="ref_bal_withdraw")
	support = InlineKeyboardButton(text=f"{data['txt']['support']}", callback_data="support")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(withdrawFromWalletBalance, withdrawFromRefBalance, support, mainmenu)
	return keyboard

# (approve, support, mainmenu)
def approveWithdrawRequestCreation():
	keyboard = InlineKeyboardMarkup(row_width=1)
	approve = InlineKeyboardButton(text=f"{data['txt']['approveWithdrawRequestCreation']}", callback_data="approve_withdraw")
	support = InlineKeyboardButton(text=f"{data['txt']['support']}", callback_data="support")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(approve, support, mainmenu)
	return keyboard

async def deleteMyWithdrawRequests(dboutput):
	keyboard = InlineKeyboardMarkup(row_width=1)
	for i in range(len(dboutput)):
		keyboard.add(InlineKeyboardButton(text=f"{data['txt']['deleteWithdrawRequest']}{dboutput[i][1]}", callback_data=f"deleterequest_{dboutput[i][1]}"))
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(mainmenu)
	return keyboard

def close():
	keyboard = InlineKeyboardMarkup(row_width=1)
	close = InlineKeyboardButton(text=f"{data['txt']['closeButton']}", callback_data="close")
	keyboard.add(close)
	return keyboard

def contacts():
	keyboard = InlineKeyboardMarkup(row_width=1)
	support = InlineKeyboardButton(text=f"{data['txt']['support']}", callback_data="support")
	website = InlineKeyboardButton(text=data['txt']['webSite'], url=data['bot']['website'])
	tg = InlineKeyboardButton(text=data['txt']['telegram'], url=data['bot']['telegram'])
	ig = InlineKeyboardButton(text=data['txt']['instagram'], url=data['bot']['instagram'])
	twitter = InlineKeyboardButton(text=data['txt']['twitter'], url=data['bot']['twitter'])
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(support, website, tg, ig, twitter, mainmenu)
	return keyboard

def support():
	keyboard = InlineKeyboardMarkup(row_width=1)
	tgsupport = InlineKeyboardButton(text=data['txt']['tgSupport'], url=data['bot']['operatorUrl'])
	website = InlineKeyboardButton(text=data['txt']['webSite'], url=data['bot']['website'])
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(tgsupport, website, mainmenu)
	return keyboard

def replenishFirst():
	keyboard = InlineKeyboardMarkup(row_width=1)
	gotorepl = InlineKeyboardButton(text=f"{data['txt']['goToReplenish']}", callback_data="goto_replenish")
	openmanual = InlineKeyboardButton(text=f"{data['txt']['openReplenishManual']}", callback_data="replenish_manual")
	support = InlineKeyboardButton(text=f"{data['txt']['support']}", callback_data="support")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(gotorepl, openmanual, support, mainmenu)
	return keyboard

def replPayVendors():
	keyboard = InlineKeyboardMarkup(row_width=1)
	usdterc = InlineKeyboardButton(text=f"{data['txt']['USDTERC']}", callback_data="REPLusdterc")
	usdttrc = InlineKeyboardButton(text=f"{data['txt']['USDTTRC']}", callback_data="REPLusdttrc")
	btc = InlineKeyboardButton(text=f"{data['txt']['BTC']}", callback_data="REPLbtc")
	eth = InlineKeyboardButton(text=f"{data['txt']['ETH']}", callback_data="REPLeth")
	keyboard.row(usdterc, usdttrc)
	keyboard.row(btc, eth)
	visamc = InlineKeyboardButton(text=f"{data['txt']['VISAMC']}", callback_data="REPLvisa_mc")
	swift = InlineKeyboardButton(text=f"{data['txt']['SWIFT']}", callback_data="REPLswift")
	astropay = InlineKeyboardButton(text=f"{data['txt']['ASTROPAY']}", callback_data="REPLastropay")
	support = InlineKeyboardButton(text=f"{data['txt']['support']}", callback_data="support")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(visamc, swift, astropay, support, mainmenu)
	return keyboard

def buyAddTasks():
	keyboard = InlineKeyboardMarkup(row_width=1)
	pack1 = InlineKeyboardButton(text=f"🎟{data['packs']['pack1']}$", callback_data="pack1")
	pack2 = InlineKeyboardButton(text=f"🎟{data['packs']['pack2']}$", callback_data="pack2")
	keyboard.row(pack1, pack2)
	pack3 = InlineKeyboardButton(text=f"🎟{data['packs']['pack3']}$", callback_data="pack3")
	pack4 = InlineKeyboardButton(text=f"🎟{data['packs']['pack4']}$", callback_data="pack4")
	keyboard.row(pack3, pack4)
	pack5 = InlineKeyboardButton(text=f"🎟{data['packs']['pack5']}$", callback_data="pack5")
	pack6 = InlineKeyboardButton(text=f"🎟{data['packs']['pack6']}$", callback_data="pack6")
	keyboard.row(pack5, pack6)
	keyboard.row(InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu"))
	return keyboard

def buyAddTasksStageSecond():
	keyboard = InlineKeyboardMarkup(row_width=1)
	buyWithWalBal = InlineKeyboardButton(text=f"{data['txt']['buyWithWalletBalance']}", callback_data="buypack_walbal")
	buyWithRefBal = InlineKeyboardButton(text=f"{data['txt']['buyWithRefBalance']}", callback_data="buypack_refbal")
	chooseAnotherPack = InlineKeyboardButton(text=f"{data['txt']['chooseAnotherPack']}", callback_data="choose_another_pack")
	keyboard.add(buyWithWalBal, buyWithRefBal, chooseAnotherPack)
	keyboard.row(InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu"))
	return keyboard

def packBuyDenied():
	keyboard = InlineKeyboardMarkup(row_width=1)
	balancetopup = InlineKeyboardMarkup(text=f"{data['txt']['balanceTopUp']}", callback_data="replenish")
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	keyboard.add(balancetopup, mainmenu)
	return keyboard

async def webappReplenish(id, amountUSD, amountCurrency, tgid, paylink):
	keyboard = InlineKeyboardMarkup(row_width=1)
	openWebApp = InlineKeyboardButton(text=data['txt']['openReplenishWebApp'], web_app=WebAppInfo(url=paylink.format(id, amountCurrency, amountUSD, tgid)))
	mainmenu = InlineKeyboardButton(text=f"{data['txt']['backtomenu']}", callback_data="backtomenu")
	support = InlineKeyboardButton(text=f"{data['txt']['support']}", callback_data="support")
	keyboard.add(openWebApp, support, mainmenu)
	return keyboard

def adminTakeRequest():
	keyboard = InlineKeyboardMarkup(row_width=1)
	takerequestControl = InlineKeyboardMarkup(text=f"Взять заявку под свое управление", callback_data="admin_take_request")
	keyboard.add(takerequestControl)
	return keyboard

def adminGetAllWithdrawRequests():
	keyboard = InlineKeyboardMarkup(row_width=1)
	getALlRequests = InlineKeyboardMarkup(text=f"Открыть список всех заявок", callback_data="admin_open_reqslist")
	keyboard.add(getALlRequests)
	return keyboard
