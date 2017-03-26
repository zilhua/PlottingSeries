#!/usr/bin/env python
#coding=utf-8
#Created on
#Author: Zhihua Pei
#Organization: GenePlus
#website: www.zilhua.com
#github: github.com/zilhua
import  time
import re
import codecs
from selenium import webdriver
import selenium.webdriver.support.ui as ui
#import shutil
#import urllib
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.action_chains import ActionChains

#代码素材来源：https://github.com/wu-yy/SinaCrawler.git
#素材来源2：***
#感谢！！！

#先调用无界面浏览的浏览器 PhantomJS 或Firefox
#需要安装FireFox 浏览器
driver=webdriver.Firefox()
wait=ui.WebDriverWait(driver,10)
global infofile
infofile=codecs.open("SinaWeibo_Infos.txt",'a','utf-8')

def LoginWeiBo(username, password):
    '''
    :param username: 用户名
    :param password: 密码
    :return: 获取cookie
    '''
    try:
        print u'准备登陆weibop.cn网站..'
        driver.get("http://login.weibo.cn/login/")
        elem_user=driver.find_element_by_name("mobile")
        elem_user.send_keys(username) #用户名
        elem_pwd=driver.find_element_by_xpath("/html/body/div[2]/form/div/input[2]")
        elem_pwd.send_keys(password) #密码
        #重点：暂停时间输入验证码
        #需要在此段时间内输入验证码，如果想自动输出，请使用打码软件
        time.sleep(30)
        elem_sub=driver.find_element_by_name("submit")
        elem_sub.click() # 点击登陆
        time.sleep(2)
        # 获取Coockie 推荐 http://www.cnblogs.com/fnng/p/3269450.html
        """
        print driver.get_cookies() #获得cookie信息dict 存储
        print u'输出cookie对应的键值信息:'
        for cookie in driver.get_cookies():
            for key in cookie:
                print key,cookie[key]
        """
        print u'登陆成功...'
    except Exception,e:
        print "Error:",e
    finally:
        print u'End loginWeibo!\n\n'

def VisitPersonPage(user_id):
    try:
        birthday, sex, area, user_num_id, pet_name, \
        num_wb, num_gz, num_fs = _getIndividualInfo(user_id)
        fans_infos = getFansInfos(user_num_id)
    except Exception, e:
        print "Error: ", e

def _getIndividualInfo(user_id):
    driver.get("http://weibo.cn/" + user_id)
    # 第一步直接获取用户昵称 微博数 关注数 粉丝数
    # str_name.text 是unicode 编码类型
    user_num_id = re.search(r'uid=(\w+)', driver.find_element_by_xpath(
        "//div[@class='tip2']/a[3]").get_attribute("href"), re.I).group(1)
    sex, area = \
    driver.find_element_by_xpath("//span[@class='ctt']").text.split(
        " ")[1].split("/")
    # 获取昵称
    str_name = driver.find_element_by_xpath("//div[@class='ut']")
    pet_name = str_name.text.split(" ")[0]
    ##微博数 除了个人主页外 它默认直接显示微博数 无超链接
    str_wb = driver.find_element_by_xpath("//div[@class='tip2']")
    pattern = r"\d+\.?\d*"  # 正则提取"微博[0]" 但r"(\[.*?\])"总含[]
    guid = re.findall(pattern, str_wb.text, re.S | re.M)
    for value in guid:
        num_wb = int(value)
        break
    # 关注数目
    str_gz = driver.find_element_by_xpath(
        "//div[@class='tip2']/a[1]")
    num_gz_temp = re.findall(pattern, str_gz.text,
                             re.S | re.M)
    num_gz = int(num_gz_temp[0])
    # 粉丝数目
    str_fs = driver.find_element_by_xpath(
        "//div[@class='tip2']/a[2]")
    num_fs_temp = re.findall(pattern, str_fs.text, re.S | re.M)
    num_fs = int(num_fs_temp[0])
    #获取生日等资料
    driver.get("http://weibo.cn/{0}/info".format(user_id))
    birthday = " "
    for i in driver.find_elements_by_xpath(
            "//div[contains(@class, 'c')]"):
        r = re.search(u"生日:(.*)\n", i.text)
        if r:
            birthday = r.group(1)
    return birthday, sex, area, user_num_id, pet_name, \
           str(num_wb), str(num_gz), str(num_fs)

def getFansInfos(user_num_id):
    from collections import defaultdict as dd
    fans_infos = dd(lambda : {})
    try:
        for i in xrange(1,1000,1):
            url = 'http://weibo.cn/' + user_num_id + '/fans?page=' + str(i)
            driver.get(url)
            # 是否到最后一页
            if driver.find_element_by_xpath("//div[@class='c']/table").is_displayed() :
                for url_fans in [a.get_attribute("href")
                    for tr in  driver.find_elements_by_xpath('//tr')
                        for a in tr.find_elements_by_xpath('td[1]/a')]:
                    birthday, sex, area, u_userid, pet_name, \
                        num_wb, num_gz, num_fs = _getIndividualInfo(url_fans)
                    fans_infos[u_userid]["sex"] = sex
                    fans_infos[u_userid]["area"] = area
                    fans_infos[u_userid]["pet_name"] = pet_name
                    fans_infos[u_userid]["num_wb"] = num_wb
                    fans_infos[u_userid]["num_gz"] = num_gz
                    fans_infos[u_userid]["num_fs"] = num_fs
                    infofile.write("sex={0}\n".format(sex))
                    infofile.write("area={0}\n".format(area))
                    infofile.write("pet_name={0}\n".format(pet_name))
                    infofile.write("num_wb={0}\n".format(num_wb))
                    infofile.write("num_gz={0}\n".format(num_gz))
                    infofile.write("num_fs={0}\n".format(num_fs))
                    infofile.flush()
                time.sleep(0.5)
    except :
        pass
    finally:
        return fans_infos

infofile.close()

if __name__ == "__main__":
    username = '15611710381'
    password = 'huangjunjie'
    LoginWeiBo(username, password)
    VisitPersonPage("durexinchina")
