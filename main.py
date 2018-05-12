from tool import sendemail
import json
from flask import render_template,Flask,redirect,url_for,request

app = Flask('welcome-portal')
app.secret_key = 'shiyanlou'

email_list = ["programvip@sina.com",]

@app.route('/',methods=["GET","POST"])
def home():
    return render_template("index.html")

@app.route('/submit',methods=["GET","POST"])
def post():
    user_name = request.form.get("user_name")
    user_email = request.form.get("user_email")
    user_title = request.form.get("user_title")
    user_content = request.form.get("user_content")
    data = {}
    data["name"] = user_name
    data["title"] = user_title
    data["email"] = user_email
    data["content"] = user_content
    json_str = json.dumps(data)
    sendemail._to = sendemail._to + ','.join(email_list)
    sendemail.send(json_str)
    return render_template("index.html",addition_script="submit")



if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=8080)

