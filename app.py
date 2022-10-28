# Connecting to MySQL
import mysql.connector
from password import MySQLpassword

dbconfig= {
    "database": "weHelp",
    "user": "root"
}
connection = mysql.connector.connect(

                        password=MySQLpassword(),
                        pool_name = "mypool",       #
                        pool_size = 3,              #
                        **dbconfig                  #
                        )
print("成功連線MySQL")
#===============================================================================

# 載入Flask 所有相關的工具
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
        sql_message= " SELECT name, content FROM members INNER JOIN messages ON members.id = messages.members_id"
        cursor = connection.cursor(buffered=True)
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
    sql_email="SELECT email FROM members WHERE email = %s "           #'"+ email +"'
    cursor = connection.cursor(buffered=True)
    cursor.execute(sql_email, [email])
    data= cursor.fetchone()
    # 檢查是否有相同email的文件資料
    if not data == None:
        # print("{}帳號已存在".format(sql_email))
        return redirect("/error?msg=信箱已經被註冊")

    # 把資料放進資料庫，完成註冊
    sql_insert= "INSERT INTO members(name, email, password)" " VALUES (%s, %s, %s)"                # ('"+name+"', '"+email+"', '"+password+"') 
    datas= [name, email, password]
    cursor.execute(sql_insert, datas)
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

    # 搜尋帳號密碼是否in DB
    account= "SELECT name, email , password FROM members WHERE  email = %s AND password= %s "           # '"+ email +"' AND password= '"+ password +"' "
    datas= [email, password]
    cursor = connection.cursor(buffered=True)
    cursor.execute(account, datas)
    result= cursor.fetchone()

    if result == None:
        return redirect("/error?msg=帳號不存在 or 帳號、密碼輸入錯誤")

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
    sql_name="SELECT id FROM members WHERE name = %s "
    cursor = connection.cursor(buffered=True)
    cursor.execute(sql_name, [name])
    member_ids= cursor.fetchone()
    member_id = member_ids[0]
    content= request.form["content"]
    insert_message= " INSERT INTO messages (members_id, content) VALUES(%s, %s) "          # ('"+ name + "' , '"+ content + "') "
    datas= [member_id, content]
    cursor.execute(insert_message, datas)
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


