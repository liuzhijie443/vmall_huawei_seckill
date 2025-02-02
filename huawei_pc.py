import html
import math
import time
import urllib3
import requests
from loguru import logger
from DrissionPage import WebPage, ChromiumOptions
from datetime import datetime, timedelta

urllib3.disable_warnings()


class WaitUntilBuy:
    def __init__(self, buy_timestamp, offset=50):
        try:
            server_timestamp, local_timestamp, ms_diff = WaitUntilBuy.local_hw_time_diff()
            if not isinstance(buy_timestamp, datetime):
                buy_timestamp = datetime.fromtimestamp(buy_timestamp / 1000)
            logger.success(f'执行时间：{buy_timestamp}，还需等待{str((buy_timestamp - datetime.now()).total_seconds())[:-4]}秒')
            ms_diff = ms_diff + offset
            while True:
                current_time = datetime.now() + timedelta(milliseconds=ms_diff * -1)  # 使用校正后的时间
                if current_time >= buy_timestamp:
                    break
                time.sleep(0.01)  # 防止过度占用CPU

        except Exception as e:
            print(e)
            logger.error("时间校验失败！")

    @staticmethod
    def server_time():
        url = "https://buy.vmall.com/queryRushbuyInfo.json?sbomCodes=2601010519508"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            return data['currentTime']
        else:
            logger.error("华为服务器获取时间失败！")

    @staticmethod
    def local_hw_time_diff():
        start_timestamp = WaitUntilBuy.local_time()
        server_timestamp = WaitUntilBuy.server_time()
        end_timestamp = WaitUntilBuy.local_time()
        # 使用平均时间来获取更准确的本地时间戳
        local_timestamp = round((start_timestamp + end_timestamp) / 2)
        ms_diff = WaitUntilBuy.milliseconds_diff(local_timestamp, server_timestamp)
        logger.info("当前华为服务器时间为：[{}]", WaitUntilBuy.timestamp2time(server_timestamp))
        logger.info("当前本地时间为：【{}】", WaitUntilBuy.timestamp2time(local_timestamp))
        compareRes = "晚于" if ms_diff >= 0 else "早于"
        logger.info("结束获取华为服务器时间及本地时间，结果：本地时间【{}】华为服务器时间【{}】毫秒", compareRes,
                    abs(ms_diff))
        return server_timestamp, local_timestamp, ms_diff

    @staticmethod
    def milliseconds_diff(_local_timestamp, hw_server_timestamp):
        _ms_diff = _local_timestamp - hw_server_timestamp
        return _ms_diff

    @staticmethod
    def timestamp2time(timestamp):
        fromDatetime = datetime.fromtimestamp(timestamp / 1000)
        return fromDatetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    @staticmethod
    def local_time():
        _local_timestamp = math.floor(time.time() * 1000)
        return _local_timestamp


def order_js():
    js = '''
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
},1000)
'''
    return js


def queue_js(sbomCodes, ActivityId):
    js = f'buyUrl = "https://m.vmall.com/order/rush/confirm?types=0&count=1&enableAutoCoupon=true&state=0&skuCodeAndQtys={sbomCodes}:1&mainSkuCodes=&giftSkuCodes=&skuCode={sbomCodes}&rushBuyActivityId={ActivityId}&rushBuyActivityType=0&rushBuyFlag=1&num=1"\n'
    js = js + '''
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

queryQualification1 = function () {
    ec.wait.queryRusult = ec.http.ajaxRequest({
        url: "/queryQualification.json",
        data: {
            activityID: ec.wait.activityId,
            sbomCode: ec.wait.sbomCode,
            portal: ec.wait.portal,
            rushTimestamp: ec.wait.rushTimestamp,
            t: new Date().getTime(),
        },
        success: function (data) {
            if (data && data.success) {
                console.log("停止queryq")
                clearInterval(queryq)
            }
        },
    });
};

joinQueue1();

queryq = setInterval(function () {
    console.log("queryq")
    if (ec.wait.queryRusult) {
        ec.wait.queryRusult.abort();
    }
    queryQualification1();
}, 200);
    '''
    return js


def hw_time_js():
    js = '''
        ec.http.ajaxRequest({
        url: "/queryRushbuyInfo.json",
        data: {
            "sbomCodes":"2601010519526"
        },
        success: function (data) {
            ec.wait.rushTimestamp = data.currentTime
            console.log(ec.wait.rushTimestamp)
        },
        });
    '''
    return js


class BUY:
    def __init__(self, _sku_list, test=False):
        # 浏览器设定
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        co = ChromiumOptions()
        # 使用默认的Chrome浏览器
        # co.use_system_user_path()
        # 使用手机UA
        co.set_user_agent(ua)
        self.page = WebPage(chromium_options=co)
        self.test = test
        time.sleep(3)

        # 检测是否登录
        self.is_login()

        # 循环遍历商品
        for sku in _sku_list:
            sku_info = self.get_sku_info(sku)
            if sku_info:
                self.startTime = sku_info[0]['startTime']
                self.activityId = sku_info[0]['activityId']
                self.sbomCode = sku_info[0]['sbomCode']
                # 下单链接
                self.order_url = f"https://m.vmall.com/order/rush/confirm?types=0&count=1&enableAutoCoupon=true&state=0&skuCodeAndQtys={self.sbomCode}:1&mainSkuCodes=&giftSkuCodes=&skuCode={self.sbomCode}&rushBuyActivityId={self.activityId}&rushBuyActivityType=0&rushBuyFlag=1&num=1"
                # 进入操作
                self.dp_main()
        time.sleep(1)
        self.page.close()

    # 判断是否登录
    def is_login(self):
        login_url = "https://m.vmall.com/order/rush/confirm?types=0&count=1&enableAutoCoupon=true&state=0&skuCodeAndQtys=0:1&mainSkuCodes=&giftSkuCodes=&skuCode=0&rushBuyActivityId=0&rushBuyActivityType=0&rushBuyFlag=1&num=1"
        self.page.get(login_url)
        if not self.page.wait.title_change("友情提示"):
            logger.error("检测到未登录，未登录账号请先登录")
            while True:
                if self.page.url == login_url:
                    logger.success("登录成功")
                    break
                time.sleep(0.1)

    def dp_main(self):
        # 排队链接
        queue_url = f"https://buy.vmall.com/queue.html?activityID={self.activityId}&sbom={self.sbomCode}&portal=2&fUrl={self.order_url}"
        self.page.get(queue_url)
        # 判断是否为测试
        if self.test:
            # 获取服务器时间，用于校正时间
            #  当前时间上添加10秒
            t = datetime.now() + timedelta(seconds=10)
            # 去除毫秒
            t = t.replace(microsecond=0)
            WaitUntilBuy(t)
            self.get_hw_time(t)
            exit(0)
        else:
            # 阻塞，等待抢购时间开始
            WaitUntilBuy(self.startTime)
            # 运行排队
            if self.buy_queue():
                # 排队后下单
                self.buy_order()

    def buy_order(self):
        # 监测等待网站跳转到下单链接
        logger.info("等待网站跳转到下单链接")
        # 监听查询排队状态
        self.page.listen.start('/queryQualification.json')
        _package_num = 0
        _package_code = 0
        for p in self.page.listen.steps():
            _package_num += 1
            try:
                body = p.response.body
                success = body.get("success")
                code = body.get("code")
                if success:
                    # 跳转到下单链接
                    self.page.get(self.order_url)
                    self.page.listen.stop()
                    break
                if code == "880008" or code == "880006":
                    _package_code += 1
            except Exception as e:
                # logger.error(e)
                pass
            if _package_num > 150:  # 超过150个数据包，则放弃抢购该商品
                logger.error("排队失败，货源过少或无货源，停止或抢购下一个商品")
                return
            if _package_code > 5:
                logger.error("已售罄，停止或抢购下一个商品")
                return
        while True:
            if self.page.url == self.order_url:
                break
            time.sleep(0.01)
            # self.page.wait.url_change("https://m.vmall.com/order/rush/confirm?types=0&count=1&enableAutoCoupon=true&state=0&skuCodeAndQtys=")
        logger.success("开始执行下单活动")
        # 监听网络请求
        self.page.listen.start('/order/rush/create.json')
        try:
            # 下单js
            orderjs = order_js()
            self.page.run_js(orderjs)
        except Exception as e:
            logger.error("请提前执行登录的操作")
        # 获取商品名称
        p_name = self.page.ele("@class=p-name")
        if p_name:
            p_name = p_name.text
            logger.warning(f"抢购 {p_name}")
        else:
            logger.error("进入订单页失败")
            return
        # 监听数据包，等待下单完成，等待30个数据包
        for packet in self.page.listen.steps(count=60, timeout=60):
            try:
                body = packet.response.body
                success = body.get("success")
                # 下单成功
                if success:
                    # 因为页面会跳转，所以来不到这里
                    pass
                else:
                    # 下单失败 提示消息
                    msg = body.get("msg")
                    code = body.get("code")
                    if msg and code:
                        msg = html.unescape(body.get("msg"))
                        logger.error(f"{p_name} {msg} code:{code}")
                        if code == "880008" or code == "880006":
                            break
                    else:
                        riskCode = body.get("riskCode")
                        eopRiskCode = body.get("eopRiskCode")
                        if riskCode and eopRiskCode:
                            logger.error(f"{p_name} 下单失败 riskCode:{riskCode} eopRiskCode:{eopRiskCode}")
            except Exception as e:
                if "payment.vmall.com" in self.page.url:
                    logger.critical(f"{p_name} 下单成功！请使用及时付款。")
                    self.page.listen.stop()
                    # 停止循环
                    input('')
                    exit(0)
            # 继续下单
            # self.page.run_js("buy_order()")
            # time.sleep(0.2)

    def buy_queue(self):
        # 运行抢购
        self.page.listen.start('/joinQueue.json')
        try:
            queuejs = queue_js(self.sbomCode, self.activityId)
            self.page.run_js(queuejs)
        except Exception as e:
            self.page.get(self.order_url)
        logger.success("开始执行排队抢购活动")
        # 监听joinQueue
        res = self.page.listen.wait(timeout=3)
        try:
            if res:
                body = res.response.body
                if body.get("code") == "880006":
                    logger.error("抢购活动已结束")
                    self.page.run_js("clearInterval(queryq)")
                    return False
        except Exception as e:
            logger.error("账号异常")
            self.page.close()
            exit(0)
        return True

    # 获取服务器时间
    def get_hw_time(self, local_time):
        # 获取服务器时间
        self.page.run_js(hw_time_js())
        time.sleep(1)
        hw_time = self.page.run_js("return ec.wait.rushTimestamp")
        local_time = int(local_time.timestamp() * 1000)
        diff_t = WaitUntilBuy.milliseconds_diff(local_time, hw_time)
        msg = f"与本地时间相差：{diff_t} 毫秒"
        logger.info("当前华为服务器时间为：{}", WaitUntilBuy.timestamp2time(hw_time))
        if diff_t >= 0:
            logger.error(f"早于服务器时间，请重新设置时间偏移值，{msg}")
        else:
            logger.info(msg)

    @staticmethod
    # 获取商品信息
    def get_sku_info(sku):
        url = f"https://buy.vmall.com/queryRushbuyInfo.json?sbomCodes={sku}"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            return data['skuRushBuyInfoList']
        else:
            logger.error("华为服务器获取信息失败！")


if __name__ == '__main__':
    # 需要抢购的商品列表
    sku_list = [
        # 2601010519527,  # HUAWEI Mate 70 Pro 12GB+512GB 鸿蒙NEXT先锋版 云杉绿
        # 2601010519526,  # HUAWEI Mate 70 Pro 12GB+512GB 鸿蒙NEXT先锋版 雪域白
        # 2601010519525,  # HUAWEI Mate 70 Pro 12GB+512GB 鸿蒙NEXT先锋版 曜石黑
        # 2601010519529,  # HUAWEI Mate 70 Pro 12GB+1TB 鸿蒙NEXT先锋版 曜石黑
        # 2601010519530,  # HUAWEI Mate 70 Pro 12GB+1TB 鸿蒙NEXT先锋版 雪域白
        # 2601010519512,  # HUAWEI Mate 70 Pro 12GB+1TB 风信紫
        # 2601010519511,  # HUAWEI Mate 70 Pro 12GB+1TB 云杉绿
        # 2601010519510,  # HUAWEI Mate 70 Pro 12GB+1TB 雪域白
        # 2601010519509,  # HUAWEI Mate 70 Pro 12GB+1TB 曜石黑
        #
        # 2601010529106,  # HUAWEI Mate 70 RS 非凡大师 16GB+1TB 瑞红 ULTIMATE DESIGN
        # 2601010529105,  # HUAWEI Mate 70 RS 非凡大师 16GB+1TB 皓白 ULTIMATE DESIGN
        # 2601010529104,  # HUAWEI Mate 70 RS 非凡大师 16GB+1TB 玄黑 ULTIMATE DESIGN
        # 2601010529102,  # HUAWEI Mate 70 RS 非凡大师 16GB+512GB 皓白 ULTIMATE DESIGN
        # 2601010529101,  # HUAWEI Mate 70 RS 非凡大师 16GB+512GB 玄黑 ULTIMATE DESIGN
        # 2601010529103,  # HUAWEI Mate 70 RS 非凡大师 16GB+512GB 瑞红 ULTIMATE DESIGN

        2601010506011,  # HUAWEI Mate XT 非凡大师 16GB+1TB 玄黑 ULTIMATE DESIGN
        2601010506009,  # HUAWEI Mate XT 非凡大师 16GB+512GB 玄黑 ULTIMATE DESIGN
        2601010506012,  # HUAWEI Mate XT 非凡大师 16GB+1TB 瑞红 ULTIMATE DESIGN
        2601010506010,  # HUAWEI Mate XT 非凡大师 16GB+512GB 瑞红 ULTIMATE DESIGN

        # 2601010515135,  # HUAWEI Mate 70 Pro+ 16GB+512GB 金丝银锦
        # 2601010515139,  # HUAWEI Mate 70 Pro+ 16GB+1TB 金丝银锦
        # 2601010515133,  # HUAWEI Mate 70 Pro+ 16GB+512GB 墨韵黑
        # 2601010515137,  # HUAWEI Mate 70 Pro+ 16GB+1TB 墨韵黑
        # 2601010515134,  # HUAWEI Mate 70 Pro+ 16GB+512GB 羽衣白
        # 2601010515138,  # HUAWEI Mate 70 Pro+ 16GB+1TB 羽衣白
        # 2601010515136,  # HUAWEI Mate 70 Pro+ 16GB+512GB 飞天青
        # 2601010515140,  # HUAWEI Mate 70 Pro+ 16GB+1TB 飞天青
    ]
    buy = BUY(sku_list)