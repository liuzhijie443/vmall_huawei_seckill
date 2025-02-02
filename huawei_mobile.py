import datetime
import json
import math
import time
from mitmproxy.script import concurrent
from mitmproxy.tools.main import mitmdump
from mitmproxy.http import HTTPFlow


# mitm插件类
class HWSHOP:
    def __init__(self):
        self.startTime = 1767196800000

    @concurrent
    def response(self, flow: HTTPFlow):
        # 提前进入抢购页面
        if "/queryRushbuyInfo.json" in flow.request.url:
            body = flow.response.text
            body = json.loads(body)
            for item in body['skuRushBuyInfoList']:
                # 开始时间提前
                startTime = item['startTime']
                self.startTime = startTime - 100
                # startTime = time.time() * 1000
                startTime = datetime.datetime.fromtimestamp(startTime / 1000) - datetime.timedelta(minutes=1440)
                startTime = math.floor(startTime.timestamp() * 1000)
                item['startTime'] = startTime
                # 写入请求体
                flow.response.text = json.dumps(body)

        # 修改排队界面的js代码
        if "/queue.html" in flow.request.url:
            timestamp = int(time.time() * 1000)
            body = flow.response.text
            body = body.replace("/rushbuy2/1.24.11.300/js/queue.js", f"/rushbuy2/1.24.11.300/js/{timestamp}.js")
            if self.startTime == 1767196800000:
                body = body.replace("取消排队","请返回商品界面重新进入")
            # 写入请求体
            flow.response.text = body

        # 修改抢购界面的js代码
        if "/rushbuy2/1.24.11.300/js/" in flow.request.url:
            _js = '''
var vmallAndroid = vmallAndroid || {};
var vmallJSBridge = vmallJSBridge || {};
window.ec = {};
ec.http = {};
ec.utils = {};
ec.wait = {};
ec.imgUrl = {
    wait: "",
    busy: "",
    tips: "",
    error: "",
};
ec.wait.tipMsg = {
    880001: "抱歉，没有抢到 ！",
    880002: "抱歉，您没有抢到 ！",
    880003: "抱歉，仅限预约用户购买 ！",
    880004: "抢购活动未开始，看看其他商品吧。",
    880005: "本次发售商品数量有限，您已超过购买上限，将机会留给其他人吧。",
    880006: "活动已结束",
    880007: "抱歉，不符合购买条件 ！",
    880008: "抱歉，已售完，下次再来 ！",
    880009: "抱歉，您不符合购买条件 ！",
    880010: "登记排队，有货时通知您 ！",
    880011: "抱歉，没有抢到 ！",
    880012: "本次发售商品数量有限，您已超过购买上限，将机会留给其他人吧。",
    880013: "抱歉，库存不足 ！",
    880017: "抱歉，您不符合购买条件",
    880018: "本次发售商品数量有限，您已超过购买上限，请勿重复购买，将机会留给其他人吧 ！"
};
ec.wait.images = ["wait1", "wait4", "wait3", "wait5", "wait6"];
ec.wait.queryRusult = null;
ec.wait.queryTimer = null;
ec.wait.progressTimer = null;
ec.wait.backgroundImgTimer = null;
ec.wait.swiperTimer = null;
ec.wait.showFixImg = false;
ec.wait.swiperImgList = [];
ec.wait.firstImgLoad = false;
ec.utils.getQueryStr = function (str) {
    let strs = window.location.search.match(
        new RegExp("[?&]" + str + "=([^&]+)", "i")
    );
    if (strs == null || strs.length < 1) {
        return "";
    }
    return strs[1];
};

ec.http.ajaxRequest = function (options) {
    options = options || {};
    options.method = (options.method || "get").toUpperCase();
    options.dataType = options.dataType || "json";
    options.contentType =
        options.contentType || "application/json;charset=UTF-8";
    options.headers = options.headers || {};
    options.data = options.data || null;
    options.async = options.async || true;
    //请求的数据
    let params = [];
    let timeoutTimer = null;
    if (options.data && typeof options.data === "object") {
        for (let key in options.data) {
            params.push(key + "=" + options.data[key]);
        }
        params = params.join("&");
    }
    let xhr;
    //考虑兼容性
    if (window.XMLHttpRequest) {
        xhr = new XMLHttpRequest();
    } else if (window.ActiveObject) {
        //兼容IE6以下版本
        xhr = new ActiveXobject("Microsoft.XMLHTTP");
    }
    xhr.withCredentials = true;
    if (options.method === "GET") {
        xhr.open("GET", options.url + "?" + params, options.async);
        xhr.send(null);
    } else if (options.method == "POST") {
        xhr.open("POST", options.url, options.async);
        xhr.setRequestHeader("x-requested-with", "XMLHttpRequest");
        xhr.setRequestHeader("cache-control", "no-cache");
        xhr.setRequestHeader("Content-type", options.contentType);

        for (let key in options.headers) {
            xhr.setRequestHeader(key, options.headers[key]); //设置请求头
        }

        if (options.contentType.toLowerCase().indexOf("json") > 0) {
            if (typeof options.data === "object") {
                try {
                    options.data = JSON.stringify(options.data);
                } catch (e) {}
            }
            xhr.send(options.data);
        } else {
            xhr.send(params);
        }
    }

    xhr.onreadystatechange = function () {
        let status = xhr.status;
        let isSuccess = (status >= 200 && status < 300) || status === 304;
        if (xhr.readyState == 4) {
            if (isSuccess) {
                if (options.dataType === "json") {
                    try {
                        let res = JSON.parse(xhr.responseText);
                        options.success &&
                        options.success(res, status, xhr.responseXML);
                    } catch (error) {}
                } else {
                    options.success &&
                    options.success(xhr.responseText, status, xhr.responseXML);
                }
            } else {
                options.error && options.error(status);
            }
        }
    };
    return xhr;
};

// 获取页面URL上的参数
ec.wait.getParams = function () {
    ec.wait.rushBuyFlag = ec.utils.getQueryStr("rushBuyFlag");
    if (ec.wait.rushBuyFlag != 1) { // RN新版本标志位
        let rp = ec.utils.getQueryStr("r") || '999';
        let length = rp.split("T").length;
        ec.wait.queryTime = rp.split("T")[0];
        ec.wait.rushTimestamp = length > 1 ? rp.split("T")[1] : '';
    }
    ec.wait.portal = ec.utils.getQueryStr("portal") || 1;
    ec.wait.orderUrl = ec.utils.getQueryStr("fUrl");
    ec.wait.activityId = ec.utils.getQueryStr("activityID");
    ec.wait.sbomCode = ec.utils.getQueryStr("sbom");
    ec.wait.num = ec.utils.getQueryStr("num");
    ec.wait.hasCarousel = ec.utils.getQueryStr("hasCarousel") || true;
    ec.wait.addressId = ec.utils.getQueryStr("addressId") || null;
};

// cookie工具
ec.utils.cookie = {
    // 获取Cookie
    get: function (item) {
        var f = null;
        if (document.cookie && document.cookie != "") {
            var cookies = document.cookie.split(";");
            for (var idx = 0; idx < cookies.length; idx++) {
                var cookie = (cookies[idx] || "").replace(
                    /^(\s|\u00A0)+|(\s|\u00A0)+$/g,
                    ""
                );
                if (cookie.substring(0, item.length + 1) == item + "=") {
                    var e = function (j) {
                        j = j.replace(/\+/g, " ");
                        var h = '()<>@,;:\\"/[]?={}';
                        for (var g = 0; g < h.length; g++) {
                            if (j.indexOf(h.charAt(g)) != -1) {
                                if (j.startWith('"')) {
                                    j = j.substring(1);
                                }
                                if (j.endWith('"')) {
                                    j = j.substring(0, j.length - 1);
                                }
                                break;
                            }
                        }
                        return decodeURIComponent(j);
                    };

                    f = e(cookie.substring(item.length + 1));
                    break;
                }
            }
        }
        return f;
    },
    // 设置Cookie
    set: function (item, val, c) {
        c = c || {};
        if (val === null) {
            val = "";
            c.expires = -1;
        }
        var expires = "";
        if (
            c.expires &&
            (typeof c.expires == "number" || c.expires.toUTCString)
        ) {
            var now;
            if (typeof c.expires == "number") {
                now = new Date();
                now.setTime(now.getTime() + c.expires * 24 * 60 * 60 * 1000);
            } else {
                now = c.expires;
            }
            expires = "; expires=" + now.toUTCString();
        }
        var path = "; path=" + (c.path || "/");
        var domain = c.domain ? "; domain=" + c.domain : "";
        var secure = c.secure ? "; secure=" : "";
        document.cookie = [
            item,
            "=",
            encodeURIComponent(val),
            expires,
            path,
            domain,
            secure,
        ].join("");
    },
    // 删除Cookie
    remove: function (item) {
        this.set(item, null);
    },
};

// 启动
ec.wait.init = function () {
    ec.wait.getParams();
    if (ec.wait.portal == 1) {
        document.querySelector("body").classList.add("ecWeb-queue");
        document.querySelector(".t-small").classList.add("t-small-big");
    } else {
        document.querySelector("body").classList.add("ecWap-queue");
    }
    document.querySelector("body").classList.remove("hide");
    // hasCarousel传参为false则不调用，否则都要调用
    // url传参取值会变成字符串，所以用字符串false判断
    if (ec.wait.hasCarousel !== 'false') {
        ec.wait.getAdsImg();
    } else {
        // 展示默认的排队图片
        ec.wait.showDefaultQueueImg();
    }

    ec.wait.initProgressTimer();
    if (ec.wait.rushBuyFlag == 1) {
        ec.wait.joinQueue();
    } else {
        if (ec.wait.needStop()) {
            ec.wait.stop();
        } else {
            ec.wait.initQueryTimer();
        }
    }
};

ec.wait.joinQueue = function () {
    const params = {
        activityID: ec.wait.activityId,
        sbomCode: ec.wait.sbomCode,
        num: ec.wait.num,
        portal: ec.wait.portal,
    }
    if (ec.wait.addressId) {
        params.addressId = ec.wait.addressId
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
            if (ec.wait.needStop()) {
                ec.wait.stop(code);
            } else {
                ec.wait.initQueryTimer();
            }
        },
        error: function () {
            ec.wait.queryTime = '999';
            ec.wait.stop();
        }
    });
};

ec.wait.queryQualification = function () {
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
            ec.wait.queryCallback(data);
        },
    });
};

ec.wait.queryPromotionInfo = function () {
    ec.http.ajaxRequest({
        url: "/queryPromotionInfo.json",
        data: {
            activityID: ec.wait.activityId,
            sbomCode: ec.wait.sbomCode,
            portal: ec.wait.portal,
            t: new Date().getTime(),
        },
        success: function (data) {
            document.querySelector(".t-big").classList.remove("hide");
            if (ec.wait.portal == 1) {
                document.querySelector(".t-small").classList.remove("t-small-big");
            }
            if (data && data.data && data.data.easyBuyEnterUrl) {
                ec.wait.clearTimer();
                ec.wait.redirectUrl = data.data.easyBuyEnterUrl;
                if (data.data.easyBuyEnterText) {
                    document.querySelector(".t-small").textContent = data.data.easyBuyEnterText;
                }
                document.querySelector(".btn-cancel").textContent = "优享购";
                document.querySelector(".btn-cancel").setAttribute("onclick", "ec.wait.redirect()");
            }
        },
    });
};

// 启动进度条定时器
ec.wait.initProgressTimer = function () {
    ec.wait.countDownTime = parseInt(new Date().getTime() / 1000) + 30;
    ec.wait.newTime = parseInt(new Date().getTime() / 1000);
    ec.wait.endTime = ec.wait.countDownTime - ec.wait.newTime;

    if (ec.wait.progressTimer) {
        window.clearInterval(ec.wait.progressTimer);
    }
    ec.wait.progressTimer = setInterval(function () {
        if (ec.wait.endTime <= 0) {
            ec.wait.clearTimer();
            ec.wait.renderGoHome();
            document.querySelector(".btn-ok").classList.remove("hide");
            document.querySelector(".queue-btn").classList.add("double-btn");
            if (ec.wait.portal == 1) {
                document.querySelectorAll(".q-btn")[1].classList.remove("btn-ok");
                document.querySelectorAll(".q-btn")[1].classList.add("btn-cancel");
                document.querySelectorAll(".q-btn")[0].classList.remove("btn-cancel");
                document.querySelectorAll(".q-btn")[0].classList.add("btn-ok");
            }
            document.querySelector(".queue-progress").classList.add("hide");
            document.querySelector(".t-small").textContent = "当前排队人数过多，是否继续排队等待？";
        } else {
            document.querySelector(".progress-red").style.width =
                ((30 - ec.wait.endTime) / 30) * 100 + "%";
            ec.wait.endTime--;
        }
    }, 1000);
};

// 启动查询接口定时器
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
        }, ec.wait.queryTime);
    }
}

ec.wait.continueWait = function () {
    if (ec.wait.portal == 1) {
        document.querySelectorAll(".q-btn")[0].classList.remove("btn-ok");
        document.querySelectorAll(".q-btn")[0].classList.add("btn-cancel");
        document.querySelectorAll(".q-btn")[1].classList.remove("btn-cancel");
        document.querySelectorAll(".q-btn")[1].classList.add("btn-ok");
    }
    document.querySelector(".btn-ok").classList.add("hide");
    document.querySelector(".queue-btn").classList.remove("double-btn");
    document.querySelector(".queue-progress").classList.remove("hide");
    document.querySelector(".progress-red").style.width = "0%";
    document.querySelector(".t-small").textContent = "排队中…";
    document.querySelector(".btn-cancel").textContent = "取消排队";
    document.querySelector(".btn-cancel").setAttribute("onclick", "ec.wait.cancelWait()");

    // 继续排队，定时器重新启动
    if (ec.wait.showFixImg) {
        ec.wait.showDefaultQueueImg();
    }
    ec.wait.initProgressTimer();
    ec.wait.initQueryTimer();
};

ec.wait.queryCallback = function (data) {
    ec.wait.activityType = data.data ? data.data.activityType : 0;
    if (ec.wait.activityType == 2) {
        ec.wait.tipMsg[880006] = "秒杀活动已结束";
        ec.wait.tipMsg[880008] =
            ec.wait.tipMsg[880010] =
                "秒杀火爆<br/>该秒杀商品已售罄";
    }
    if (data && data.success) {
        ec.wait.clearTimer();
        if (ec.wait.portal == 1) {
            ec.wait.cancelWait();
            parent.location.href = decodeURI(
                decodeURIComponent(ec.wait.orderUrl)
            );
        } else {
            window.location.href = decodeURI(
                decodeURIComponent(ec.wait.orderUrl)
            );
        }
    } else if (data && data.code) {
        document.querySelector(".queue-progress").classList.add("hide");
        ec.wait.clearTimer();
        if (ec.wait.showFixImg) {
            ec.wait.renderImg(data.code);
        }
        if (ec.wait.tipMsg[data.code]) {
            document.querySelector(".t-small").innerHTML = ec.wait.tipMsg[data.code];
        } else {
            document.querySelector(".t-small").textContent = "抱歉，没有抢到 ！";
        }
        if (data.data && data.data.guideUrl && data.data.guideText && data.code != "880010" && data.code != "880012") {
            ec.wait.redirectUrl = data.data.guideUrl;
            document.querySelector(".btn-cancel").textContent = data.data.guideText;
            document.querySelector(".btn-cancel").setAttribute("onclick", "ec.wait.redirect()");
            if (data.data.guideText.length > 4) {
                document.querySelector(".q-btn").classList.add("btn-adaptive");
            }
        } else {
            ec.wait.renderGoHome(data.code);
            if (data.code == "880010") {
                ec.wait.queryPromotionInfo();
            }
            if (data.code == "880012" && data.data.availableNum && data.data.availableNum > 0) {
                document.querySelector(".t-small").textContent = "您已超过购买上限，本场活动最多还能买 " + data.data.availableNum + " 件";
            }
        }
    }
};

ec.wait.clearTimer = function () {
    if (ec.wait.queryTimer) {
        window.clearInterval(ec.wait.queryTimer);
        ec.wait.queryTimer = null;
    }
    if (ec.wait.progressTimer) {
        window.clearInterval(ec.wait.progressTimer);
        ec.wait.progressTimer = null;
    }
    if (ec.wait.backgroundImgTimer) {
        window.clearInterval(ec.wait.backgroundImgTimer);
        ec.wait.backgroundImgTimer = null;
    }
};

ec.wait.goHome = function () {
    switch (Number(ec.wait.portal)) {
        case 1:
            parent.location.href = "https://www.vmall.com/";
            break;
        case 2:
            window.location.href = "https://m.vmall.com/";
            break;
        case 3:
        case 10:
            window.location.href = "https://mw.vmall.com/";
            break;
        default:
            break;
    }
};

/**
 * 跳转分享的链接
 */
ec.wait.redirect = function () {
    if (ec.wait.portal == 1) {
        parent.location.href = ec.wait.redirectUrl;
    } else {
        window.location.href = ec.wait.redirectUrl;
    }
};

/**
 * 是否需要停止排队
 */
ec.wait.needStop = function () {
    let flag = false;
    if (ec.wait.queryTime == "999" || !ec.wait.orderUrl || !ec.wait.activityId || !ec.wait.sbomCode) {
        flag = true;
    }
    return flag;
};

/**
 * 停止排队
 */
ec.wait.stop = function(code) {
    ec.wait.clearTimer();

    let textContent = "抱歉，没有抢到 ！";
    if (code) {
        textContent = ec.wait.tipMsg[code] || textContent;
    }
    document.querySelector(".t-small").textContent = textContent;
    document.querySelector(".queue-progress").classList.add("hide");
    if (ec.wait.showFixImg) {
        ec.wait.renderImg(code);
    }
    ec.wait.renderGoHome();
}

/**
 * 取消等待
 */
ec.wait.cancelWait = function () {
    ec.wait.clearTimer();
    if (ec.wait.portal == 1) {
        window.parent.postMessage({ cancel: true }, "*");
    } else if (ec.wait.portal == 2) {
        window.history.go(-1);
    } else {
        if (ec.wait.portal == 10) {
            if (
                window.webkit &&
                window.webkit.messageHandlers &&
                window.webkit.messageHandlers.vmalliOS &&
                window.webkit.messageHandlers.vmalliOS.postMessage
            ) {
                var data = {
                    method: "onReturn",
                    parameters: [],
                };
                window.webkit.messageHandlers.vmalliOS.postMessage(data);
            } else {
                ec.wait.goHome();
            }
        } else if (ec.wait.portal == 90 && vmallJSBridge && vmallJSBridge.onReturn) {
            vmallJSBridge.onReturn();
        } else {
            if (vmallAndroid && vmallAndroid.onReturn) {
                vmallAndroid.onReturn();
            } else {
                ec.wait.goHome();
            }
        }
    }
};

ec.wait.renderGoHome = function () {
    if (ec.wait.activityType == 2) {
        document.querySelector(".btn-cancel").textContent = "返回";
    } else {
        document.querySelector(".btn-cancel").textContent = "返回";
    }
    document.querySelector(".btn-cancel").setAttribute("onclick", "ec.wait.cancelWait()");
};

ec.wait.renderImg = function (code) {
    let imgName;
    switch (Number(code)) {
        case 880001:
        case 880002:
        case 880008:
        case 880010:
        case 880011:
        case 880013:
            imgName = ec.wait.images[4];
            break;
        case 880003:
        case 880007:
        case 880009:
        case 880017:
            imgName = ec.wait.images[1];
            break;
        case 880004:
        case 880006:
            imgName = ec.wait.images[3];
            break;
        case 880005:
        case 880012:
        case 880018:
            imgName = ec.wait.images[2];
            break;
        default:
            imgName = ec.wait.images[2];
            break;
    }
    // 轮播图隐藏
    let imgs = document.getElementsByTagName("img");
    for (let i = 0; i < imgs.length; i++) {
        imgs[i].style.display = "none";
    }
    // 排队等待图片隐藏
    let queuePic = document.getElementById("wait1");
    queuePic.style.display = 'none';

    if (document.getElementById(imgName)) {
        document.getElementById(imgName).style.display = "block";
    } else {
        let imgDivNode = ec.wait.buildImgNode(imgName);
        if (imgName == "wait3") {
            imgDivNode.style.backgroundSize = '2000% 100%';
            if (ec.wait.backgroundImgTimer) {
                window.clearInterval(ec.wait.backgroundImgTimer);
            }
            ec.wait.backgroundImgTimer = setInterval(ec.wait.backgroundImgChange(imgDivNode, false), 200);
        } else {
            imgDivNode.style.backgroundSize = '100% 100%';
        }
    }
};

ec.wait.initSwiper = function (index, flag) {
    let content = document.getElementsByClassName("content")[0];
    let wrapper = document.getElementsByClassName("wrapper")[0];
    let imgWidth = wrapper.children[0].clientWidth;
    let imgsLen = ec.wait.swiperImgList.length;
    let wrapIndex = 0;

    function animate(el, target) {
        let dotIndex = -target / imgWidth;
        let dotParent = document.querySelector(".swiper-dots");
        let dotLen = dotParent.children.length;
        if (dotLen > 0) {
            for (let i = 0; i < dotLen; i++) {
                dotParent.children[i].classList.remove("active");
            }
            if (dotIndex == 1) {
                dotParent.children[1].classList.add("active");
            } else {
                if (dotLen == 2) {
                    dotParent.children[0].classList.add("active");
                } else {
                    if (dotIndex == 2) {
                        dotParent.children[2].classList.add("active");
                    } else {
                        dotParent.children[0].classList.add("active");
                    }
                }
            }
        }
        clearInterval(el.timer);
        el.timer = setInterval(function () {
            let move = 8;
            let present = wrapper.offsetLeft;
            move = present > target ? -move : move;
            present += move;
            if (Math.abs(present - target) > Math.abs(move)) {
                wrapper.style.left = present + "px";
            } else {
                clearInterval(el.timer);
                el.timer = null;
                wrapper.style.left = target + "px";
            }
        }, 16);
    }

    if (flag == "error") {
        imgsLen;
        if (index == imgsLen) {
            if (wrapper.children.length == 2) {
                document.querySelector("#swiperDots").remove();
                if (!ec.wait.firstImgLoad) {
                    document.querySelector(".wrapper").classList.add("hide");
                    document.querySelector("#wait1").classList.remove("hide");
                    document
                        .querySelector(".queue-pic")
                        .classList.remove("swipe-pic");
                    ec.wait.showFixImg = true;
                }
            } else {
                wrapIndex = index - 1;
                animate(wrapper, -wrapIndex * imgWidth);
                ec.wait.swiperTimer = setInterval(function () {
                    if (wrapIndex === wrapper.children.length - 1) {
                        wrapIndex = 0;
                        wrapper.style.left = 0 + "px";
                    }
                    wrapIndex++;
                    animate(wrapper, -wrapIndex * imgWidth);
                }, 5000);
            }
        } else {
            ec.wait.creatImg(ec.wait.swiperImgList, index);
        }
    } else {
        setTimeout(function () {
            ec.wait.creatImg(ec.wait.swiperImgList, index + 1);
        }, 5000);
        wrapIndex = index;
        if (index != imgsLen - 1) {
            animate(wrapper, -index * imgWidth);
        } else {
            if (wrapper.children.length == imgsLen + 1) {
                animate(wrapper, -index * imgWidth);
            } else {
                animate(wrapper, -(index - 1) * imgWidth);
                wrapIndex--;
            }
        }
        if (index == imgsLen - 1) {
            ec.wait.swiperTimer = setInterval(function () {
                if (wrapIndex === wrapper.children.length - 1) {
                    wrapIndex = 0;
                    wrapper.style.left = 0 + "px";
                }
                wrapIndex++;
                animate(wrapper, -wrapIndex * imgWidth);
            }, 5000);
        }
    }
};

ec.wait.getAdsImg = function () {
    ec.http.ajaxRequest({
        url: "/getCarouselInfo.json",
        data: {
            activityId: ec.wait.activityId,
        },
        success: function (data) {
            if (data && data.carouselList && data.carouselList.length > 0) {
                ec.wait.swiperImgList = data.carouselList;
                document.querySelector(".queue-pic").classList.add("swipe-pic");
                document.querySelector(".wrapper").classList.remove("hide");
                let imgs = document.querySelectorAll(".swiper1");
                for (let i = 0; i < imgs.length; i++) {
                    imgs[i].src = data.carouselList[0];
                }
            } else {
                // 展示默认的排队图片
                ec.wait.showDefaultQueueImg();
            }
        },
        error: function () {
            // 展示默认的排队图片
            ec.wait.showDefaultQueueImg();
        },
    });
};

ec.wait.creatImg = function (imgList, index, flag) {
    if (!imgList[index]) {
        if (!ec.wait.firstImgLoad) {
            document.querySelector(".wrapper").classList.add("hide");
            document.querySelector("#wait1").classList.remove("hide");
            document.querySelector(".queue-pic").classList.remove("swipe-pic");
            ec.wait.showFixImg = true;
        }
        return;
    }
    let li = document.createElement("li");
    let img = new Image();
    img.addEventListener(
        "load",
        function () {
            if (!ec.wait.firstImgLoad) {
                ec.wait.firstImgLoad = true;
                let children = document.querySelector(".wrapper").children;
                img.className = "swiper1";
                for (let i = 0; i < children.length; i++) {
                    children[i].appendChild(img.cloneNode(true));
                }
                let imgLen = ec.wait.swiperImgList.length;
                if (imgLen - index > 1) {
                    let dotLen = imgLen - index;
                    let dotParent = document.querySelector(".swiper-dots");
                    for (let i = 0; i < dotLen; i++) {
                        let dotSpan = document.createElement("span");
                        dotParent.appendChild(dotSpan);
                    }
                    let firstDot = dotParent.children[0];
                    firstDot.classList.add("active");
                    dotParent.parentElement.classList.remove("hide");
                }
                setTimeout(function () {
                    ec.wait.creatImg(ec.wait.swiperImgList, 2);
                }, 5000);
            } else {
                li.appendChild(img);
                let oldNode = document.querySelectorAll(".swiper1")[1];
                oldNode.parentElement.parentElement.insertBefore(
                    li,
                    oldNode.parentElement
                );
                ec.wait.initSwiper(index, flag);
            }
        },
        false
    );
    img.addEventListener(
        "error",
        function () {
            if (index > imgList.length - 1) {
                if (!ec.wait.firstImgLoad) {
                    document.querySelector(".wrapper").classList.add("hide");
                    document.querySelector("#wait1").classList.remove("hide");
                    document
                        .querySelector(".queue-pic")
                        .classList.remove("swipe-pic");
                    ec.wait.showFixImg = true;
                }
                return;
            } else {
                if (
                    document.querySelector(".swiper-dots") &&
                    document.querySelector(".swiper-dots").children.length > 0
                ) {
                    document
                        .querySelector(".swiper-dots")
                        .children[
                    document.querySelector(".swiper-dots").children.length - 1
                        ].remove();
                }
                ec.wait.initSwiper(index + 1, "error");
            }
        },
        false
    );
    img.src = imgList[index];
};

/**
 * 加载轮播图第一张图片失败
 */
ec.wait.loadFirstImgError = function () {
    document.querySelectorAll(".swiper1").forEach(function (item, i) {
        item.remove();
    });
    if (ec.wait.swiperImgList.length == 1) {
        document.querySelector(".wrapper").classList.add("hide");
        document.querySelector("#wait1").classList.remove("hide");
        document.querySelector(".queue-pic").classList.remove("swipe-pic");
        ec.wait.showFixImg = true;
    } else {
        ec.wait.creatImg(ec.wait.swiperImgList, 1);
    }
};

/**
 * 加载轮播图第一张图片
 */
ec.wait.loadFirstImg = function () {
    ec.wait.firstImgLoad = true;
    if (ec.wait.swiperImgList.length > 1) {
        let dotsLen = ec.wait.swiperImgList.length;
        let dotParent = document.querySelector(".swiper-dots");
        for (let i = 0; i < dotsLen; i++) {
            let dotSpan = document.createElement("span");
            dotParent.appendChild(dotSpan);
        }
        let firstDot = dotParent.children[0];
        firstDot.classList.add("active");
        dotParent.parentElement.classList.remove("hide");
        setTimeout(function () {
            ec.wait.creatImg(ec.wait.swiperImgList, 1);
        }, 5000);
    }
};

/**
 * 展示默认图片
 */
ec.wait.showDefaultQueueImg = function () {
    ec.wait.showFixImg = true;
    if (ec.wait.backgroundImgTimer) {
        window.clearInterval(ec.wait.backgroundImgTimer);
    }
    if (ec.wait.queryTime == "999") {
        let imgDivNode = ec.wait.buildImgNode("wait3");
        imgDivNode.style.backgroundSize = '2000% 100%';
        ec.wait.backgroundImgTimer = setInterval(ec.wait.backgroundImgChange(imgDivNode, false), 200);
    } else {
        let obj = document.querySelector("#wait1");
        obj.classList.remove("hide");
        document.querySelector(".queue-pic").classList.remove("swipe-pic");
        ec.wait.backgroundImgTimer = setInterval(ec.wait.backgroundImgChange(obj, true), 200);
    }
}

ec.wait.buildImgNode = function (imgName) {
    let imgDivNode = document.createElement("div");
    imgDivNode.setAttribute("id", imgName);
    imgDivNode.style.height = "100%";
    imgDivNode.style.width = "100%";
    imgDivNode.style.backgroundPosition = "0 0";
    let imageUrl = "https://res.vmallres.com/rushbuy2/1.24.11.300/images/" + imgName + ".png";
    imgDivNode.style.backgroundImage = "url(" + imageUrl + ")";
    document.querySelector(".queue-pic").appendChild(imgDivNode);
    return imgDivNode;
};

/**
 * 背景图变化
 *
 * @param obj 图片节点
 * @param repeatFlag 重复标志（移动到最后一帧后重新从第一帧继续变化）
 */
ec.wait.backgroundImgChange = function(obj, repeatFlag) {
    return function () {
        obj.style.backgroundSize = "2000% 100%";
        let backgroundPositionX = ec.wait.styleExtract(obj, "backgroundPositionX");
        if(backgroundPositionX == '0px') {
            backgroundPositionX = '0%'
        }
        let nextPositionX = Number(backgroundPositionX.substring(1,backgroundPositionX.length - 1)) + 100;
        if (nextPositionX >= 2000) {
            if (repeatFlag) {
                obj.style.backgroundPositionX = "0%";
            } else {
                window.clearInterval(ec.wait.backgroundImgTimer);
                ec.wait.backgroundImgTimer = null;
            }
        } else {
            obj.style.backgroundPositionX = "-" + nextPositionX + "%";
        }
    }
}

/**
 * 获取样式
 *
 * @param obj 节点
 * @param name 属性名
 */
ec.wait.styleExtract = function (obj, name) {
    if (window.getComputedStyle){
        //适配Chrome、火狐、IE9以上版本浏览器
        return getComputedStyle(obj, null)[name];
    } else {
        //适配IE8浏览器
        return obj.currentStyle[name];
    }
};
// ec.wait.init();


document.querySelector("body").classList.remove("hide");
document.querySelector(".t-small").innerText = "等待自动运行，请勿操作"

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
            },10)
            '''
            # 写入请求体
            flow.response.status_code = 200
            flow.response.headers["Content-Type"] = "text/plain; charset=utf-8"
            flow.response.text = _js + _js2

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
    print("启动运行。")
    command = ['--quiet', '--listen-host', '0.0.0.0', '-p', '18888', '--set', 'block_global=false', '-s', __file__, '--ssl-insecure']
    mitmdump(command)
``