# vmall_huawei_seckill
华为商城手机抢购代码，Mate 70系列手机。
# 如果对你有帮助或抢到了麻烦在issues反馈。
# 推荐使用手机抢购。
## 说明
分为电脑抢和手机抢两个脚本，流程是跑通了，但是暂时 __没有抢购过成功一次__ 。
使用前提前设好默认收货地址。

## 1.电脑抢购 huawei_pc.py
安装依赖运行后自动打开网站，手动登录后等待自动运行。
抢购商品在代码最后面编辑。
## 2.手机抢购 huawei_mobile.py
> 需要使用手机进行抢购，下面是使用步骤，不懂可以问。

1.安装依赖后运行脚本。手机同局域网中，在WiFi配置代理为电脑端ip:18888
2.访问`mitm.it`选择相应的系统进行证书的安装。
![image](https://github.com/user-attachments/assets/a00b5525-701a-46a1-b905-e773b11d7768)

3.关闭代理正常访问华为商城网页版（http://m.vmall.com/ ），找到需要抢购的商品页面正常登陆账号，返回WIFI设置代理，商品页面抢购按钮变为`立即购买`
![image](https://github.com/user-attachments/assets/d2085e08-c23d-4597-bd14-f40938da7387)

4.抢购前几分钟点击立即购买进入排队界面，显示如图。
![image](https://github.com/user-attachments/assets/032fa076-2f0d-4ae3-8226-6068a36c5eab)

5. 手机保持此界面并亮屏等待自动运行，下单页会自动提交。
