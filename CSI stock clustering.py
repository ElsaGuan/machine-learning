
import numpy as np
import MySQLdb as mdb
from sklearn.cluster import KMeans
import pandas as pd

#链接MySQL数据库
db_host = 'localhost'
db_user = 'root'
f = open('/Users/chocolatekuma/Documents/MySQL_pw.txt','r')
db_pass = f.read()
db_name = 'test'
#链接数据库
con = mdb.connect(db_host, db_user, db_pass, db_name,use_unicode = True, charset = 'utf8')

#sql命令
sql = """select symbol_id,price_date,open_price,close_price,volume from daily_price 
where price_date between '2013-01-07' and '2018-08-01';"""

#直接将sql的数据读取成dataframe
#df储存的是沪深300的价格数据
df = pd.read_sql_query(sql, con=con)   

#从table：symbol获取股票的名称和代号
with con: 
    cur = con.cursor()
    cur.execute("SELECT id, ticker, name FROM symbol")
    data = cur.fetchall()
    #将data强行转为list，利于后面取用和修改
    #但是tuple格式更安全
    data = [[d[0], d[1],d[2]] for d in data] 

#创建字典，key为id，value为股票中文名字和代号
#方便之后可视化和聚类的时候直观看到是哪只股票
name = dict(zip([d[0] for d in data],[d[2] for d in data]))
symbol = dict(zip([d[0] for d in data],[d[1] for d in data]))
name1 = dict(zip([d[1] for d in data],[d[2] for d in data]))  

# df['ticker'] = df['symbol_id'].apply(lambda v: symbol[v])
# df['name'] = df['symbol_id'].apply(lambda v: name[v])

#创建两个新的特征，一个是前一天的收盘价格last_close，一个是今天收盘价相对昨天收盘价变化的百分比change
# df['last_close'] = df['close_price'].shift(periods = -1)
# df['change'] = df['close_price'].pct_change(periods = -1)*100

#获取300支股票中在2013年之前已经上市的股票
new_symbol = []
for i in range(1,301):
    if len(df[df['symbol_id']==i]) == 1356:
        new_symbol.append(i)

#制作用于cluster的dataframe，这里仅使用收盘和开盘的变化作为feature
#首先制作open price的dataframe，列为各只股票，索引为日期，内容为open price

#首先定义一个新的dataframe，取第一只股票的open price和日期
open_p = pd.DataFrame(df[df['symbol_id'] == 1][['open_price','price_date']])
#将column名字改为股票的代码
open_p.rename(columns = {'open_price':symbol[1]}, inplace = True)

#循环所有股票，得到open price和日期
for i in new_symbol[1:]:
    
    open_price = pd.DataFrame(df[df['symbol_id'] == i][['open_price','price_date']])
    
    open_price.rename(columns = {'open_price':symbol[i]}, inplace = True)
    
    open_price = open_price.reset_index(drop=True)
    
    open_p = pd.merge(open_p,open_price, how = 'left', on = 'price_date')
    print(i, open_p.head())

open_p.set_index('price_date',inplace = True)

#同样的方式获取close price
close_p = pd.DataFrame(df[df['symbol_id'] == 1][['close_price','price_date']])
close_p.rename(columns = {'close_price':symbol[1]}, inplace = True)

for i in new_symbol[1:]:
    
    close_price = pd.DataFrame(df[df['symbol_id'] == i][['close_price','price_date']])
    
    close_price.rename(columns = {'close_price':symbol[i]}, inplace = True)
    
    close_price = close_price.reset_index(drop=True)
    
    close_p = pd.merge(close_p,close_price, how = 'left', on = 'price_date')
close_p.set_index('price_date',inplace = True)

#得到variation
variation = close_p - open_p

x = df1/df1.std(0)
X = x.values.T
model = KMeans(init='k-means++', n_clusters=50, n_init=10)
model.fit(X)
labels = model.labels_
n_labels = labels.max()
for i in range(n_labels + 1):
    print('Cluster %i: %s' %((i + 1), ', '.join([name2[key] for key in df1.columns[labels == i]])))