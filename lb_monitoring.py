#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import oci
import json
import slackweb
import ssl
import time

# slack連携
slack = slackweb.Slack(url="<URL>")
ssl._create_default_https_context = ssl._create_unverified_context

class Lb_info_get:
    def __init__(self):
        # config設定
        config = oci.config.from_file("/home/opc/.oci/config",)
        identity = oci.identity.IdentityClient(config)

        # LB情報取得
        lbc = oci.load_balancer.LoadBalancerClient(config)
        lb_info = lbc.get_backend_health("<lbのocid>", "<バックエンド名>", "<IPアドレス:ポート>").data
        self.lb_info = lb_info

# 定期的に1分毎に監視するため、whileで実行
while True:
    lb_info_get_ins = Lb_info_get()
    lb_info = lb_info_get_ins.lb_info
    # jsonに変換
    lb_info = json.loads(str(lb_info))

    # LBのステータスがOK以外の場合はslackに通知する
    if not lb_info["status"] == "OK":
        attachments = [{"title": "サーバで障害発生", "pretext": lb_info["status"], "text": "コンテナがダウンしています", "color": "danger", "mrkdwn_in": ["text", "pretext"]}]
        slack.notify(attachments=attachments)
    time.sleep(60)
