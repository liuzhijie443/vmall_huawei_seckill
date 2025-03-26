import datetime
import json
import math
import time
import re

import requests
from mitmproxy.script import concurrent
from mitmproxy.tools.main import mitmdump
from mitmproxy.http import HTTPFlow


# mitm插件类
class HWSHOP:
    def __init__(self):
        self.startTime = 1767196800000
        self.js_url = "/rushbuy2/1.25.1.300/js/queue.js"

    @concurrent
    def response(self, flow: HTTPFlow):
        # 提前进入抢购页面并解锁购买按钮
        if "/queryRushbuyInfo.json" in flow.request.url:
            print("进入商品抢购页，并提前解锁购买按钮")
            try:
                body = json.loads(flow.response.text)
                for item in body.get("skuRushBuyInfoList", []):
                    # 开始时间提前
                    startTime = item['startTime']
                    self.startTime = startTime - 100
                    # 将开始时间提前1440分钟（24小时）
                    startTime = datetime.datetime.fromtimestamp(startTime / 1000) - datetime.timedelta(minutes=1440)
                    startTime = math.floor(startTime.timestamp() * 1000)
                    item['startTime'] = startTime
                    # 写入请求体
                    flow.response.text = json.dumps(body)
            except Exception as e:
                print(f"处理/queryRushbuyInfo.json时出错: {e}")

        # 修改排队界面的js代码
        if "/queue.html" in flow.request.url:
            print("进入排队页，等待抢购开始。")
            timestamp = int(time.time() * 1000)
            body = flow.response.text
            self.js_url = re.findall(r"/rushbuy2/.+/js/queue.js", body)[0]
            body = body.replace(self.js_url, f"/rushbuy2/1.25.1.300/js/{timestamp}.js")
            if self.startTime == 1767196800000:
                body = body.replace("取消排队", "时间错误，请返回商品界面重新进入")
            # 写入请求体
            flow.response.text = body

        # 修改抢购界面的js代码
        if "/rushbuy2/" in flow.request.url:
            matches = re.findall(r"\d{13}.js", flow.request.url)
            if matches:
                print("抢购等待界面")
                js_res = requests.get("https://res.vmallres.com" + self.js_url)
                _js_text = js_res.text.replace("活动暂未开始，感谢您的参与。", "抢购中，请勿进行其他操作，保持此界面等待。").replace("ec.wait.init();", "//ec.wait.init();")
                _js = '''
    document.querySelector("body").classList.remove("hide");
    document.querySelector(".t-small").innerText = "等待自动运行，保持亮屏，请勿刷新或进行其他操作，保持此界面等待。"
    
    ec.wait.initQueryTimer = function () {
        if (ec.wait.queryTime && ec.wait.queryTime != "999") {
            if (ec.wait.queryTimer) {
                window.clearInterval(ec.wait.queryTimer);
            }
            ec.wait.queryTimer = setInterval(function () {
                if (ec.wait.queryRusult) {
                    ec.wait.queryRusult.abort();
                }
                ec.wait.queryQualification();
            }, 200);
        }
    }
    
    joinQueue1 = function () {
        const params = {
            activityID: ec.wait.activityId,
            sbomCode: ec.wait.sbomCode,
            num: ec.wait.num,
            portal: ec.wait.portal,
        }
        ec.http.ajaxRequest({
            url: "/joinQueue.json",
            data: params,
            success: function (data) {
                let rp = '999';
                let code = '';
                if (data && data.success && data.data && data.data.rp) {
                    rp = data.data.rp;
                } else if (data && !data.success) {
                    code = data.code;
                } else {
                    code = '880001';
                }
                let length = rp.split("T").length;
                ec.wait.queryTime = rp.split("T")[0];
                ec.wait.rushTimestamp = length > 1 ? rp.split("T")[1] : '';
                setTimeout(function () {
                    if (!ec.wait.rushTimestamp){
                        joinQueue1();
                    }
                }, 200);
            },
        });
    };
    
    var send = setInterval(()=>{
    '''
                _js2 = f"t = {self.startTime}" + '''
                    if(Date.now() > t){
                        clearInterval(send)
                        ec.wait.init();
                        joinQueue1()
                    }
                },100)
                '''
                flow.response.status_code = 200
                flow.response.headers["Content-Type"] = "text/plain; charset=utf-8"
                flow.response.text = _js_text + _js + _js2

        # 订单页自动下单
        if "/order/rush/confirm" in flow.request.url:
            _js = '''
console.log("测试内容")
try{
    document.querySelector(".system-empty-title").textContent = "脚本加载成功"
}catch{}
buy_order = function() {
    if(!$("#agreeListMsg").is(":checked")){
        var agreeListMsg = document.querySelector("#agreeListMsg")
        if (agreeListMsg !== null && typeof(agreeListMsg) === 'object') {
            $("#agreeListMsg").trigger("click");
        }
    }
    
    if ($("#ecWap-box-0")) {
        $("#ecWap-box-0").remove();
    }
    if ($("#ecWap-box-bg-0")) {
        $("#ecWap-box-bg-0").remove();
    }

    var sHwjf=document.getElementsByClassName('global-switch-btn point-btn active')[0];//积分处理
    if (sHwjf !== null && typeof(sHwjf) === 'object') {
        sHwjf.click();
    }

    var sMsg=document.getElementsByClassName('ecWap-box-title')[0];
    if (sMsg !== null && typeof(sMsg) === 'object') {
        if (sMsg.innerText=="短信认证"){
            clearInterval(t4);
        }
    }

    var goSub = document.querySelector('a.button-gradual-1.js-order-submit')
    if (goSub !== null && typeof(goSub) === 'object') {
        goSub.click();
    }else{
        goSub = document.querySelector("#confirmSubmit");
        if (goSub !== null && typeof(goSub) === 'object') {
            goSub.click();
        }
    }
}

setInterval(()=>{
    buy_order()
},300)
})();
buy_order()
            '''
            body = flow.response.text
            body = body.replace(" })();", _js)
            # 写入请求体
            flow.response.text = body


# addons插件列表
addons = [
    HWSHOP()
]

# 启动
if __name__ == '__main__':
    print("启动运行mitmproxy，手机设置代理 ip:18888，访问http://mitm.it进行安装证书。")
    command = ['--quiet', '--listen-host', '0.0.0.0', '-p', '18888', '--set', 'block_global=false', '-s', __file__,
               '--ssl-insecure']
    mitmdump(command)
