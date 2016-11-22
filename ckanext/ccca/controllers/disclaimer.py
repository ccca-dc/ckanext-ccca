# encoding: utf-8
import ckan.lib.base as base


class DisclaimerController(base.BaseController):

    def disclaimer(self):
        return base.render('home/disclaimer.html')
