import sqlite3
import configparser
data = configparser.ConfigParser()
data.read("setting.ini", encoding='utf-8')
dbFile = data['bot']['databaseFile']

async def regUser(id, phone, regtime, fn, refid, username):
    db = sqlite3.connect(dbFile)
    cursor = db.cursor()
    try:
        cursor.execute(f"INSERT INTO users (id, phone, rank, exp, level, regtime, walletBalance, refBalance, jobAvailableTotal, jobDailyLimit, jobsCompletedToday, expForJob, completedJobPayout, completedJobBonus, firstName, completedJobs, ref, lastActivity, username, curLevelXp)"
                               f" VALUES ('{id}', '{phone}', {1}, {0}, {1} ,'{regtime}', {0}, {0}, {60}, {20}, {0}, {1}, '{0.3}', {0.01}, '{fn}', {0}, {refid}, '{0}', '{username}', {0})")
        db.commit()
        return True
    except sqlite3.IntegrityError:
        db.commit()
        return False


async def getInfo(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    row = cursor.fetchone()
    return row

async def getRefsCount(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT id FROM users WHERE ref = {id}")
    row = cursor.fetchall()
    return len(row)

async def checkifExists(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT id FROM users WHERE id = {id}")
    row = cursor.fetchall()
    return len(row)

async def checkRank(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT rank FROM users WHERE id = {id}")
    row = cursor.fetchone()
    return row[0]

async def taskCompletedHandler(id, expForJob, completedJobPayout, jobDailyLimit, jobCompletedToday, jobAvailableTotal, completedJobBonus):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    if jobCompletedToday != jobDailyLimit:
        if jobAvailableTotal != 0:
            cursor.execute(f"UPDATE users SET walletBalance = walletBalance + {round(float(completedJobPayout), 3)} WHERE id = {id}")
            db.commit()
            cursor.execute(f"UPDATE users SET walletBalance = walletBalance + {round(float(completedJobBonus), 3)} WHERE id = {id}")
            db.commit()
            cursor.execute(f"UPDATE users SET exp = exp + {expForJob} WHERE id = {id}")
            db.commit()
            cursor.execute(f"UPDATE users SET jobAvailableTotal = jobAvailableTotal - 1 WHERE id = {id}")
            db.commit()
            cursor.execute(f"UPDATE users SET jobsCompletedToday = jobsCompletedToday + 1 WHERE id = {id}")
            db.commit()
            cursor.execute(f"UPDATE users SET completedJobs = completedJobs + 1 WHERE id = {id}")
            db.commit()
            cursor.execute(f"UPDATE users SET curLevelXp = curLevelXp + {expForJob} WHERE id = {id}")
            db.commit()
            return "Success"
        else: return "AvailableJobLimitReached"
    else: return "DailyLimitReached"

async def getCurrentTaskId(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT completedJobs FROM users WHERE id = {id}")
    row = cursor.fetchone()
    return row[0]

async def addRef(masterid, refid):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE users SET ref = {masterid} WHERE id = {refid}")
    db.commit()

async def updateContact(id, phone):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE users SET phone = {phone} WHERE id = {id}")
    db.commit()

async def checkPhone(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT phone FROM users WHERE id = {id}")
    row = cursor.fetchone()
    return row[0]

async def getRefsListFromDb(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT id,username FROM users WHERE ref = {id} LIMIT 10")
    row = cursor.fetchall()
    return row

async def getActiveWithdrawRequests(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT fromid FROM withdrawReqs WHERE fromid = {id}")
    row = cursor.fetchall()
    return len(row)

async def checkWalletBalanceWithdrawPossibility(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT walletBalance FROM users WHERE id = {id}")
    row = cursor.fetchone()
    if int(row[0]) >= int(data['prefs']['minWithdrawSum']):
        return True
    else: return False

async def checkRefBalanceWithdrawPossibility(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT refBalance FROM users WHERE id = {id}")
    row = cursor.fetchone()
    if int(row[0]) >= int(data['prefs']['minWithdrawSum']):
        return True
    else:
        return False

async def getBalance(id, isRefBalance):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    if isRefBalance == 0:
        cursor.execute(f"SELECT walletBalance FROM users WHERE id = {id}")
        row = cursor.fetchone()
        return row[0]
    elif isRefBalance == 1:
        cursor.execute(f"SELECT refBalance FROM users WHERE id = {id}")
        row = cursor.fetchone()
        return row[0]
    else:
        return False

async def addWithdrawRequest(fromid, num, sum, wallet, type, coin, date):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    try:
        cursor.execute(
            f"INSERT INTO withdrawReqs (fromid, reqNum, sum, wallet, type, coin, date, isPayed)"
            f" VALUES ('{fromid}', {num}, {round(sum,3)}, '{wallet}', '{type}', '{coin}', '{date}', 0)")
        db.commit()
    except sqlite3.OperationalError:
        return "invalidWallet"
    if type == "RefBalanceDraw":
        cursor.execute(f"UPDATE users SET refBalance = refBalance - {sum} WHERE id = {fromid}")
        db.commit()
    else:
        cursor.execute(f"UPDATE users SET walletBalance = walletBalance - {sum} WHERE id = {fromid}")
        db.commit()

async def getLastRequestNum():
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT MAX(reqNum) FROM withdrawReqs")
    row = cursor.fetchone()
    return row[0]

async def getMyWithdrawRequests(fromid):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM withdrawReqs WHERE fromid = {fromid} ORDER BY date DESC")
    row = cursor.fetchall()
    return row

async def deleteWithdrawRequest(id, reqNum):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    async def security():
        cursor.execute(f"SELECT fromid FROM withdrawReqs WHERE reqNum = {reqNum}")
        row = int(cursor.fetchone()[0])
        if id == row: return True
        else: return False
    if await security():
        try:
            cursor.execute(f"SELECT sum FROM withdrawReqs WHERE reqNum = {reqNum}")
            row = cursor.fetchone()[0]
            cursor.execute(f"UPDATE users SET walletBalance = walletBalance + {row} WHERE id = {id}")
            db.commit()
            cursor.execute(f"DELETE FROM withdrawReqs WHERE reqNum = {reqNum}")
            db.commit()
            return True
        except:
            db.commit()
            return False
    else: return False

async def completedJobLevelHandler(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT completedJobs FROM users WHERE id = {id}")
    row = cursor.fetchone()[0]
    try:
        chapter = data['lvlsys'][f'{row}']
        level, complJobBonus, jobdailylimit, rank, expPerTask, completedJobPayout = chapter.split("|")
        cursor.execute(f"UPDATE users SET level = {level} WHERE id = {id}")
        db.commit()
        cursor.execute(f"UPDATE users SET completedJobBonus = {complJobBonus} WHERE id = {id}")
        db.commit()
        cursor.execute(f"UPDATE users SET jobDailyLimit = {jobdailylimit} WHERE id = {id}")
        db.commit()
        cursor.execute(f"UPDATE users SET rank = {rank} WHERE id = {id}")
        db.commit()
        cursor.execute(f"UPDATE users SET expForJob = {expPerTask} WHERE id = {id}")
        db.commit()
        cursor.execute(f"UPDATE users SET completedJobPayout = {completedJobPayout} WHERE id = {id}")
        db.commit()
        cursor.execute(f"UPDATE users SET curLevelXp = 0 WHERE id = {id}")
        db.commit()
        return "levelup"
    except KeyError:
        pass


def Test(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT completedJobPayout FROM users WHERE id = {id}")
    row = cursor.fetchone()
    return f"{row[0]} | {row} | {row[0][0]}"

async def buyMoreTasks(id, price, boughtJobsCount, refbuy):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    if refbuy == 1:
        cursor.execute(f"SELECT refBalance FROM users WHERE id = {id}")
        row = int(cursor.fetchone()[0])
        if row >= int(price):
            cursor.execute(
                f"UPDATE users SET refBalance = refBalance - {price} WHERE id = {id}")
            db.commit()
            cursor.execute(
                f"UPDATE users SET jobAvailableTotal = jobAvailableTotal + {boughtJobsCount} WHERE id = {id}")
            db.commit()
            return True
        else:
            return False
    else:
        cursor.execute(f"SELECT walletBalance FROM users WHERE id = {id}")
        row = int(cursor.fetchone()[0])
        if row >= int(price):
            cursor.execute(
                f"UPDATE users SET walletBalance = walletBalance - {price} WHERE id = {id}")
            db.commit()
            cursor.execute(
                f"UPDATE users SET jobAvailableTotal = jobAvailableTotal + {boughtJobsCount} WHERE id = {id}")
            db.commit()
            return True
        else:
            return False

async def logLastActivity(id, dt):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE users SET lastactivity = '{dt}' WHERE id = {id}")
    db.commit()

#______________ ADMIN FUNCTIONS ___________________

async def replAdminFunc(id, sum):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    try:
        cursor.execute(f"UPDATE users SET walletBalance = walletBalance + {sum} WHERE id = {id}")
        db.commit()
        return True
    except:
        return False


async def checkifAdminExists(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT id FROM adminfunc WHERE id = {id}")
    row = cursor.fetchall()
    if len(row) == 1:
        return True
    else:
        return False

async def checkIfAdminLogged(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT logged FROM adminfunc WHERE id = {id}")
    row = cursor.fetchone()[0]
    if row == 1:
        return True
    else:
        return False

async def regAdminStageOne(id, logged, status, regtime, name, username):
    # name = first_name + last_name if not None else " "
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    try:
        cursor.execute(
            f"INSERT INTO adminfunc (id, logged, status, regtime, name, username)"
            f" VALUES ('{id}', {logged}, '{status}', '{regtime}', '{name}', '{username}' )")
        db.commit()
        return True
    except sqlite3.IntegrityError:
        db.commit()
        return False

async def logAdmin(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE adminfunc SET logged = 1 WHERE id = {id}")
    db.commit()

async def getUserByUsername(unstring): # raw
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    try:
        if "@" in unstring:
            unstringClr = unstring.replace("@", "")
            cursor.execute(f"SELECT id FROM users WHERE username = '{unstringClr}'")
            row = cursor.fetchone()[0]
            return row
        else:
            cursor.execute(f"SELECT id FROM users WHERE username = '{unstring}'")
            row = cursor.fetchone()[0]
            return row
    except TypeError:
        return False

async def getAllAdmins():
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute("SELECT id FROM adminfunc")
    row = cursor.fetchall()
    return row

async def getUsernameByID(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT username FROM users WHERE id = {id}")
    try:
        row = cursor.fetchone()[0]
        if row!="None": return row
        else: return "noUsername"
    except TypeError: return "noUsername"

def resetDayLimit():
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE users SET jobsCompletedToday = 0")
    db.commit()

async def getMasterRefID(id):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT ref FROM users WHERE id = {id}")
    row = cursor.fetchone()[0]
    if int(row) == 0:
        return False
    else:
        return row

async def refMasterIncomeEnroll(masterid, sum):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE users SET refBalance = refBalance + {sum} WHERE id = {masterid}")
    db.commit()

async def getAllWithdrawRequests():
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM withdrawReqs ORDER BY date DESC")
    row = cursor.fetchall()
    return row

async def getLast10WithdrawRequests():
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM withdrawReqs ORDER BY date DESC LIMIT 10")
    row = cursor.fetchall()
    return row

async def getWithdrawRequestByNumber(reqNum):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM withdrawReqs WHERE reqNum = {reqNum}")
    try:
        row = cursor.fetchall()[0]
        return row
    except IndexError: return False

async def markWRasPayed(reqNum):
    db = sqlite3.connect('proj.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE withdrawReqs SET isPayed = 1 WHERE reqNum = {reqNum}")
    db.commit()