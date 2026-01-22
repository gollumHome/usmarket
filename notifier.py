import requests
import json
import time


class WechatNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_text(self, title, content):
        """
        发送纯文本消息
        """
        if not self.webhook_url:
            print(f"未配置 Webhook，消息 [{title}] 仅打印：\n{content}")
            return

        full_text = f"【{title}】\n\n{content}"

        payload = {
            "msgtype": "text",  # 类型改为 text
            "text": {
                "content": full_text  # key 也必须改为 text
                # "mentioned_list": ["@all"]  # 如果需要，可以取消注释来 @ 所有人
            }
        }

        try:
            for _ in range(3):
                res = requests.post(self.webhook_url, json=payload, timeout=10)
                result = res.json()

                # 企业微信接口 errcode 为 0 代表真正成功
                if res.status_code == 200 and result.get("errcode") == 0:
                    print(f"✅ {title} 文本推送成功")
                    return
                else:
                    print(f"⚠️ {title} 推送异常: {result.get('errmsg')}")

                time.sleep(2)
        except Exception as e:
            print(f"❌ 通讯异常: {e}")

    # 为了兼容你之前的调用，可以保留一个别名
    def send_markdown(self, title, content):
        self.send_text(title, content)