from tool import sendemail
import json
from flask import render_template,Flask,redirect,url_for,request
import redis
import flask
import datetime

app = Flask('welcome-portal')
app.secret_key = 'shiyanlou'

email_list = ["programvip@sina.com",]
r = redis.StrictRedis()

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



# 消息生成器
def event_stream():
    pubsub = r.pubsub()
    # 订阅'chat'频道
    pubsub.subscribe('chat')
    # 开始监听消息，如果有消息产生在返回消息
    for message in pubsub.listen():
        print(message)
        # Server-Send Event 的数据格式以'data:'开始
        yield 'data: %s\n\n' % message['data']


# 登陆函数，首次访问需要登陆
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        # 将用户信息记录到 session 中
        flask.session['user'] = flask.request.form['user']
        return flask.redirect('/')
    return '<form action="" method="post">user: <input name="user">'


# 接收 javascript post 过来的消息
@app.route('/js_post', methods=['POST'])
def post():
    message = flask.request.form['message']
    user = flask.session.get('user', 'anonymous')
    now = datetime.datetime.now().replace(microsecond=0).time()
    # 将消息发布到'chat'频道中
    r.publish('chat', u'[%s] %s: %s' % (now.isoformat(), user, message))
    return flask.Response(status=204)


# 事件流接口
@app.route('/stream')
def stream():
    # 返回的类型是'text/event-stream'，否则浏览器不认为是 SSE 事件流
    return flask.Response(event_stream(),
                          mimetype="text/event-stream")


@app.route('/chat')
def home():
    # 如果用户没有登陆的话，则强制登陆
    if 'user' not in flask.session:
        return flask.redirect('/login')
    return u"""
        <!doctype html>
        <title>chat</title>
        <script src="http://labfile.oss.aliyuncs.com/jquery/2.1.3/jquery.min.js"> </script>
        <style>body { max-width: 500px; margin: auto; padding: 1em; background: black; color: #fff; font: 16px/1.6 menlo, monospace; }</style>
        <p><b>hi, %s!</b></p>
        <p>Message: <input id="in" /></p>
        <pre id="out"></pre>
        <script>
            function sse() {
                // 接入服务器的事件流
                var source = new EventSource('/stream');
                var out = document.getElementById('out');
                source.onmessage = function(e) {
                    out.innerHTML =  e.data + '\\n' + out.innerHTML;
                };
            }
            // POST 消息到服务端
            $('#in').keyup(function(e){
                if (e.keyCode == 13) {
                    $.post('/js_post', {'message': $(this).val()});
                    $(this).val('');
                }
            });
            sse();
        </script>

    """ % flask.session['user']



if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=8080)

