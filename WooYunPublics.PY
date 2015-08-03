#!/usr/bin/env python
# encoding: utf-8
import sys, os, requests, socket, re, time, json
from pyquery import PyQuery


socket.setdefaulttimeout(10)    # 10s超时

GET_URL = 'http://www.wooyun.org/bugs/new_public/page/'
USER_AGENT = 'DoDo'


def get_attrvalue(node, attrname):
    return node.getAttribute(attrname) if node else ''

def get_nodevalue(node, index = 0):
    if (len(node.childNodes) < (index + 1)): return ''
    return node.childNodes[index].nodeValue if node else ''

def get_xmlnode(node, name):
    return node.getElementsByTagName(name) if node else []

def GetResult(html):
    # 解析XML
    # Time, Title, Author, Comment, Start, Money, Credit, Url,
    result = []
    doc = PyQuery(html)
    for row in doc('tbody tr'):
        items = row.findall('*')
        # 提交日期
        dtime = items[0].text
        # 漏洞名称/漏洞URL/漏洞等级/漏洞奖金
        dtitle = items[1].find('a').text
        durl = items[1].find('a').attrib['href']
        expands = items[1].find_class('credit')
        # 等级和奖金
        dcredit = 0
        dmoney = 0
        for expand in expands:
            src = expand.attrib['src'].lower()
            if (src.find('credit.')>0): dcredit = 1
            elif (src.find('m1.')>0): dmoney = 1
            elif (src.find('m2.')>0): dmoney = 2
            elif (src.find('m3.')>0): dmoney = 3
        # 漏洞评论/漏洞关注
        commentandstart = items[2].find('a').text.split('/')
        dcomment = int(commentandstart[0])
        dstart = int(commentandstart[1])
        # 漏洞作者
        dauthor = items[3].find('a').attrib['title']

        result.append({'time':dtime, 'title':dtitle, 'url':durl, 'author':dauthor, 'comment':dcomment,
                       'start':dstart, 'credit':dcredit, 'money':dmoney
                      })
        
    return result
        
            
            
    
def GetData(page):
    # 发送消息
    url = '{0}{1}'.format(GET_URL, page)
    cookies = { }
    headers = {
               'User-Agent': USER_AGENT
              }
    r = requests.get(url, headers=headers)
    return r.text.strip()

def GetPublicList(fpage, tpage=None):
    # 获取最新公开列表
    result = []
    if tpage == None: tpage=fpage+1
    for page in range(fpage, tpage):
        # 读取网页
        print u'当前页: %d' % page
        for r in range(4):
            # 重试4次
            html = GetData(page)
            if (html.startswith('<!DOCTYPE')==False):
                html = ''
                print u'{0}失败页面: {1}'.format(time.strftime('%m/%d %H:%M:%S'), page)
                continue
            else: break
        if (html == ''): break

        # 解析数据
        data = GetResult(html)
        if (len(data)==0): break
        else: result.extend(data)
    return result


if __name__=='__main__':
    # 程序入口
    # 读取所有公开列表
    result = GetPublicList(1, 1504)
    jsondata = json.dumps(result)
    f = open('wooyun.json', 'w')
    f.write(jsondata)
    f.close()

    #
    f = open('wooyun.json', 'r')
    jsondata = f.read()
    f.close()

    result = json.loads(jsondata)

    maxcomment = 0
    maxurl = ''
    for item in result:
        if (maxcomment < item['comment']):
            maxcomment = item['comment']
            maxurl = item['url']
        if (item['comment']>50):
            print item['url'], item['comment'], item['credit'], item['money'], item['title']

    
    print 'Finish.'


        
    
    
    
    
