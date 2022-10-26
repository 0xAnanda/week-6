# Connecting to MySQL
from re import L
import mysql.connector
from mysql.connector import errorcode
from password import MySQLpassword
connection = mysql.connector.connect(
                        user='root',
                        password=MySQLpassword(),
                        port='3306',
                        database='weHelp',
                        host='localhost'
                        )
print("成功連線MySQL")
# cursor = connection.cursor()
#===============================================================================

# 載入Flask 所有相關的工具
from http import client
from sqlite3 import connect
from flask import *
# 建立 Application 物件， 靜態檔案處理設定
app= Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)


# 設定 Session 的密鑰
app.secret_key="ImKey"
#-------------------------------
# 處理路由
@app.route("/")
def index():
    return render_template("index.html")
#------------------------------- 
# 會員頁面
@app.route("/member")
def member():

    if "email" in session:
        name=session['name']
        sql_message= " SELECT member_name, content FROM messages"
        cursor = connection.cursor()
        cursor.execute(sql_message)
        messages= cursor.fetchall()
        cursor.close()
        length=(len(messages))
        return render_template("member.html" , name=name, messages =messages ,length=length)
    else:
        return redirect("/")
        

#-------------------------------
# 錯誤訊息
@app.route("/error") 
def error():
    message=request.args.get("msg", "發生錯誤，請聯繫客服")
    return render_template("error.html", message=message)    
#-------------------------------
# 註冊
@app.route("/signUp", methods=['POST'])
def signUp():
    # 從前端接收資料
    name= request.form["name"]
    email=request.form["email"]
    password= request.form["password"]
    # 根據接受到的資料，和資料庫互動
    sql_email="SELECT email FROM members WHERE email = '"+ email +"'"
    cursor = connection.cursor()
    cursor.execute(sql_email)
    data= cursor.fetchone()
    # 檢查是否有相同email的文件資料
    if not data == None:
        # print("{}帳號已存在".format(sql_email))
        return redirect("/error?msg=信箱已經被註冊")
    cursor.close()

    # 把資料放進資料庫，完成註冊
    sql_insert= "INSERT INTO members(name, email, password) VALUES('"+name+"', '"+email+"', '"+password+"') "
    cursor = connection.cursor()
    cursor.execute(sql_insert)
    connection.commit()
    print("{}已註冊成功".format(name))
    cursor.close()
    return redirect("/")
#------------------------------
# 登入
@app.route("/signin", methods=['POST'])
def signin():
    # 從前端取得使用者輸入
    email= request.form["email"]
    password= request.form["password"]
       
    # 和資料庫做互動
    # 先確定有沒有帳號
    sql_email= "SELECT email FROM members WHERE email =  '"+ email +"' "
    cursor= connection.cursor()
    cursor.execute(sql_email)
    confirmEmail= cursor.fetchone()
    if confirmEmail == None:
        return redirect("/error?msg=帳號不存在")
    cursor.close()

    # 搜尋帳號密碼是否in DB
    account= "SELECT name, email , password FROM members WHERE  email = '"+ email +"' AND password= '"+ password +"' "
    cursor = connection.cursor()
    cursor.execute(account)
    result= cursor.fetchone()

    # 找不到相應的資料，登入失敗，導向到錯誤頁面
    if result == None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    # 登入成功， 在Session 紀錄會員資訊，導向到會員頁面
    session['name']= result[0]
    session['email']= result[1]
    session['password']= result[2]
    connection.commit()
    cursor.close()
    return redirect("/member")
#------------------------------  
# 登出
@app.route("/signout")
def signout():
    # 移除 Session 中的會員資訊
    del session['email']
    return redirect("/")
#------------------------------
# 留言回覆
@app.route("/message", methods=['POST'])
def message():
    name= session["name"]
    content= request.form["content"]
    insert_message= " INSERT INTO messages (member_name, content) VALUES('"+ name + "' , '"+ content + "') "
    cursor = connection.cursor()
    cursor.execute(insert_message)
    connection.commit()
    cursor.close()
    return redirect(url_for('member'))
 
#------------------------------ 
#啟動伺服器在Port 3000
if __name__ == '__main__':
    app.run(port=3000 ,debug=True)
#==============================================================================
# 關閉連結
connection.close()


