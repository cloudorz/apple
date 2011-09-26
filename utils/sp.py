# coding: utf-8

import tornado

__all__ = ['sms_send', 'ret_code2desc']

errors = {
        -1: u"没有该用户账户",
        -2: u"密钥不正确（不是用户密码）",
        -3: u"短信数量不足",
        -11: u"该用户被禁用",
        -14: u"短信内容出现非法字符",
        -41: u"手机号码为空",
        -42: u"短信内容为空",
        }

def handler_sms_reqeust(response):
    if response.error:
        print "Oops! error to request the sms service."
    else:
        ret_code = int(response.body)
        print ret_code2desc(ret_code)
        tornado.ioloop.IOLoop.instance().stop()

def sms_send(phone, msg, msg_type):

    assert isinstance(msg_type, int) and isinstance(msg, dict), "apply function with wrong arguments type"

    # sms content
    msg_content = get_sms_template(msg_type) % msg

    # sms api uri
    uri = u"http://utf8.sms.webchinese.cn/?Uid=cloud&Key=q12wer43ui8765tyop09&smsMob=%(phone)s&smsText=%(msg)s"
    uri = uri % {'phone': phone, 'msg': urllib2.quote(msg_content.encode('utf-8'))}

    http_client = httpclient.AsyncHTTPClient()
    http_client.fetch(uri, handle_request)

    tornado.ioloop.IOLoop.instance().start()

def get_sms_template(msg_type):
    res = u""
    if msg_type == 1:
        res = u"乐帮注册验证码:%(code)s。乐帮感谢你的注册！"
    elif msg_type == 2:
        res = u"%(name)s，你好！重置后的密码:%(password)s。乐帮提醒你尽快修改！"
    return res

def ret_code2desc(ret_code):
    if ret_code < 0:
        return errors[ret_code]
    else:
        return u"成功发送%d条" % ret_code
