#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import sys
import cgi
import cgitb


# global variables
speriod=(15*60)-1
dbname='/var/www/templog.db'

# print the HTTP header
def printHTTPheader():
    print "Content-type: text/html\n\n"


# 打印HTML头部分
# 参数是图表的页面标题和表格
def printHTMLHead(title):
    print "<head>"
    print "    <title>"
    print title
    print "    </title>"
    print "<script src=\"https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.js\"></script>"

    print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />"
    print "</head>"


# 从数据库中获取数据
# 如果成功，从数据库中返回记录列表
def get_data(interval):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if interval == None:
        curs.execute("SELECT * FROM temps")
    else:
        curs.execute("SELECT * FROM temps WHERE timestamp>datetime('now','localtime','-%s hours')" % interval)
#        curs.execute("SELECT * FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hours') AND timestamp<=datetime('2013-09-19 21:31:02')" % interval)

    rows=curs.fetchall()
    conn.close()
    return rows


# 将数据库中的行转换为javascript表格
def create_table(rows):
    times=""
    for row in rows[:-1]:
        rowstr="'{0}', ".format(str(row[0]))
        times+=rowstr

    row=rows[-1]
    rowstr="'{0}'".format(str(row[0]))
    times+=rowstr

    return times

def create_table2(rows):
    datas=""
    for row in rows[:-1]:
        rowstr="'{0}', ".format(str(row[1]))
        datas+=rowstr
    row=rows[-1]
    rowstr="'{0}'".format(str(row[1]))
    datas+=rowstr
    return datas


# 打印javascript以生成图表
# 传递从数据库信息生成的表
def print_graph_script(table,table2):
    # 载入谷歌图标的代码片段
    chart_code="""
    <script>
      var ctx = document.getElementById('myChart');
      var myChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [%s],
          datasets: [{
            label: "pokebox",
            data: [%s],
          }]
        },
        options: {}
      });
    </script>"""

    print chart_code % (table,table2)


# 打印包含图形的div
def show_graph():
    print "<h2>温度图表</h2>"
    print "<div style=\"width: 650px\"><canvas id=\"myChart\" width=\"600\" height=\"400\"></canvas></div>"

# 连接到数据库并显示一些统计数据
# 参数是小时数
def show_stats(option):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if option is None:
        option = str(24)

    curs.execute("SELECT timestamp,max(temp) FROM temps WHERE timestamp>datetime('now','localtime','-%s hour') AND timestamp<=datetime('now','localtime')" % option)
#    curs.execute("SELECT timestamp,max(temp) FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hour') AND timestamp<=datetime('2013-09-19 21:31:02')" % option)
    rowmax=curs.fetchone()
    rowstrmax="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmax[0]),str(rowmax[1]))

    curs.execute("SELECT timestamp,min(temp) FROM temps WHERE timestamp>datetime('now','localtime','-%s hour') AND timestamp<=datetime('now','localtime')" % option)
#    curs.execute("SELECT timestamp,min(temp) FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hour') AND timestamp<=datetime('2013-09-19 21:31:02')" % option)
    rowmin=curs.fetchone()
    rowstrmin="{0}&nbsp&nbsp&nbsp{1}C".format(str(rowmin[0]),str(rowmin[1]))

    curs.execute("SELECT avg(temp) FROM temps WHERE timestamp>datetime('now','localtime','-%s hour') AND timestamp<=datetime('now','localtime')" % option)
#    curs.execute("SELECT avg(temp) FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hour') AND timestamp<=datetime('2013-09-19 21:31:02')" % option)
    rowavg=curs.fetchone()

    print "<hr>"

    print "<h2>最低温度&nbsp</h2>"
    print rowstrmin
    print "<h2>最高温度</h2>"
    print rowstrmax
    print "<h2>平均温度</h2>"
    print "%.3f" % rowavg+"C"

    print "<hr>"

    print "<h2>In the last hour:</h2>"
    print "<table>"
    print "<tr><td><strong>Date/Time</strong></td><td><strong>Temperature</strong></td></tr>"

    rows=curs.execute("SELECT * FROM temps WHERE timestamp>datetime('now','localtime','-1 hour') AND timestamp<=datetime('now','localtime')")
#    rows=curs.execute("SELECT * FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-1 hour') AND timestamp<=datetime('2013-09-19 21:31:02')")
    for row in rows:
        rowstr="<tr><td>{0}&emsp;&emsp;</td><td>{1}C</td></tr>".format(str(row[0]),str(row[1]))
        print rowstr
    print "</table>"
    print "<hr>"
    conn.close()


def print_time_selector(option):

    print """<form action="/cgi-bin/webgui.py" method="POST">
        显示温度记录
        <select name="timeinterval">"""

    if option is not None:
        if option == "6":
            print "<option value=\"6\" selected=\"selected\">最近6小时</option>"
        else:
            print "<option value=\"6\">最近6小时</option>"

        if option == "12":
            print "<option value=\"12\" selected=\"selected\">最近12小时</option>"
        else:
            print "<option value=\"12\">最近12小时</option>"

        if option == "24":
            print "<option value=\"24\" selected=\"selected\">最近一天</option>"
        else:
            print "<option value=\"24\">最近一天</option>"
    else:
        print """<option value="6">最近6小时</option>
            <option value="12">最近12小时</option>
            <option value="24" selected="selected">最近一天</option>"""

    print """        </select>
        <input type="submit" value="显示">
    </form>"""


# 检查该选项是否有效
# 而不是SQL注入
def validate_input(option_str):
    # 检查选项字符串是否代表数字
    if option_str.isalnum():
        # 检查该选项是否在特定范围内
        if int(option_str) > 0 and int(option_str) <= 24:
            return option_str
        else:
            return None
    else: 
        return None


# 返回传递给脚本的选项
def get_option():
    form=cgi.FieldStorage()
    if "timeinterval" in form:
        option = form["timeinterval"].value
        return validate_input (option)
    else:
        return None


# 主函数
def main():
    cgitb.enable()
    # 获取可能已传递给此脚本的选项
    option=get_option()

    if option is None:
        option = str(24)

    # 从数据库中获取数据
    records=get_data(option)

    # 打印HTTP头
    printHTTPheader()

    if len(records) != 0:
        # 将数据转换为表格
        table=create_table(records)
        table2=create_table2(records)
    else:
        print "No data found"
        return

    # 开始打印页面
    print "<html>"
    # 打印表格头部，以及用于图表的JavaScript
    printHTMLHead("树莓派温度记录")

    # print the page body
    print "<body>"
    print "<h1>树莓派温度记录</h1>"
    print "<hr>"
    print_time_selector(option)
    show_graph()
    print_graph_script(table,table2)
    show_stats(option)
    print "</body>"
    print "</html>"

    sys.stdout.flush()

if __name__=="__main__":
    main()




