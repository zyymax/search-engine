# -*- coding:utf-8 -*-
import tornado.web
from base import BaseHandler
from util.common import home_feed_number,accounts_show_number,account_feed_number,permit_read_status,common_account,search_accounts_number,search_essays_number
import urllib

class MoreHandler(BaseHandler):
    def get(self, page, kind):
        template_values = {}
        startindex = self.get_argument("lastindex", None)
        startindex = int(startindex)
        lastindex = startindex + home_feed_number
        if page == 'home':
            if kind == 'recent':
                account_essay = self.db.query("select a.wid,a.wname,e.essay,e.title,e.link,e.publish_time,e.digest,a.score from account a inner join essay e on a.account = e.account and a.status = %s and e.status = %s order by e.publish_time desc limit %s, %s", permit_read_status, permit_read_status, startindex, home_feed_number)
            elif kind == 'old':
                account_essay = self.db.query("select a.wid,a.wname,e.essay,e.title,e.link,e.publish_time,e.digest,a.score from account a inner join essay e on a.account = e.account and a.status = %s and e.status = %s order by e.publish_time asc limit %s, %s", permit_read_status, permit_read_status, startindex, home_feed_number)
            elif kind == 'hot':
                account_essay = self.db.query("select a.wid,a.wname,e.essay,e.title,e.link,e.publish_time,e.digest,a.score from account a inner join essay e on a.account = e.account and a.status = %s and e.status = %s order by e.view_count desc limit %s, %s", permit_read_status, permit_read_status, startindex, home_feed_number)
            elif kind == 'select':
                account_essay = self.db.query("select a.wid,a.wname,e.essay,e.title,e.link,e.publish_time,e.digest,a.score from account a inner join essay e on a.account = e.account and a.status = %s and e.status = %s and a.score > %s and itemidx = 1 order by e.publish_time desc limit %s, %s", permit_read_status, permit_read_status, common_account, (startindex/(home_feed_number * 2)) * (home_feed_number * 2), home_feed_number * 2)
            total = self.db.get("SELECT count(*) as total FROM essay WHERE status = %s", permit_read_status)
            total_count = total['total']
            template_values['lastindex'] = lastindex
            is_even = 1 if lastindex % (home_feed_number * 2) == 0 else 0
            template_values['account_essay'] = sorted(account_essay, key=lambda ae: ae['score'], reverse=True)[is_even * home_feed_number : home_feed_number * (1 + is_even)]
            template_values['hasnext'] = 1 if total_count > lastindex else 0
            self.render("modules/home_feed.html", template_values=template_values)