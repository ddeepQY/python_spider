import pandas as pd
from pymongo import MongoClient
import re

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['jd_database']  # 替换为你的数据库名
collection = db['jd_collection']  # 替换为你的集合名

# 从 MongoDB 中读取数据
data = pd.DataFrame(list(collection.find()))

# 数据清洗与处理
data['goods_price'] = data['goods_price'].str.replace('￥', '').astype(float)
data['goods_comments'] = data['goods_comments'].apply(lambda x: int(re.search(r'\d+', x).group()))
data['goods_rating'] = data['goods_rating'].str.replace('%', '').astype(float)

# 输出好评度最高的前10件商品信息
top10_highest_rating = data.sort_values(by='goods_rating', ascending=False).head(10)
top10_highest_rating['rank'] = range(1, len(top10_highest_rating) + 1)
top10_highest_rating = top10_highest_rating.rename(columns={
    'rank': '排名',
    'goods_title': '商品名称',
    'goods_price': '商品价格',
    'goods_link': '商品链接',
    'goods_rating': '商品评分'
})
print("好评度最高的前10件商品信息:")
print(top10_highest_rating[['排名','商品名称', '商品价格', '商品链接', '商品评分']])

# 输出价格最低的前10件商品信息
top10_lowest_price = data.sort_values(by='goods_price').head(10)
top10_lowest_price['rank'] = range(1, len(top10_highest_rating) + 1)
top10_lowest_price = top10_lowest_price.rename(columns={
    'rank': '排名',
    'goods_title': '商品名称',
    'goods_price': '商品价格',
    'goods_link': '商品链接',
    'goods_rating': '商品评分'
})
print("\n价格最低的前10件商品信息:")
print(top10_lowest_price[['排名','商品名称', '商品价格', '商品链接','商品评分']])

# 输出评价总数最多的前10件商品信息
top10_most_comments = data.sort_values(by='goods_comments', ascending=False).head(10)
top10_most_comments['rank'] = range(1, len(top10_highest_rating) + 1)
top10_most_comments = top10_most_comments.rename(columns={
    'rank': '排名',
    'goods_title': '商品名称',
    'goods_price': '商品价格',
    'goods_link': '商品链接',
    'goods_comments': '商品评论'
})
print("\n评价总数最多的前10件商品信息:")
print(top10_most_comments[['排名','商品名称', '商品价格', '商品链接', '商品评论']])

# 输出差评最少的前10件商品信息
# 假设差评度=100-好评度
data['bad_rating'] = 100 - data['goods_rating']
top10_least_bad_rating = data.sort_values(by='bad_rating').head(10)
top10_least_bad_rating['rank'] = range(1, len(top10_highest_rating) + 1)
top10_least_bad_rating = top10_least_bad_rating.rename(columns={
    'rank': '排名',
    'goods_title': '商品名称',
    'goods_price': '商品价格',
    'goods_link': '商品链接',
    'bad_rating': '商品差评率'
})
print("\n差评最少的前10件商品信息:")
print(top10_least_bad_rating[['排名','商品名称', '商品价格', '商品链接', '商品差评率']])

# 输出最热门商品即重复名称最多的商品信息
most_common_title = data['goods_title'].mode()[0]
most_popular_item = data[data['goods_title'] == most_common_title].iloc[0]
most_popular_item_df = most_popular_item.to_frame().T
most_popular_item = most_popular_item.astype(str)
most_popular_item_df = most_popular_item_df.rename(columns={
    'goods_title': '商品名称',
    'goods_price': '商品价格',
    'goods_link': '商品链接',
})

print("\n最热门商品即重复名称最多的商品信息:")
print(most_popular_item_df[['商品名称', '商品价格', '商品链接']])

# 定义一个函数，将 URL 转换为超链接格式
def make_hyperlink(url):
    return f'<a href="{url}">{url}</a>'

# 应用函数到 '商品链接' 列
top10_highest_rating['商品链接'] = top10_highest_rating['商品链接'].apply(make_hyperlink)
top10_lowest_price['商品链接'] = top10_lowest_price['商品链接'].apply(make_hyperlink)
top10_most_comments['商品链接'] = top10_most_comments['商品链接'].apply(make_hyperlink)
top10_least_bad_rating['商品链接'] = top10_least_bad_rating['商品链接'].apply(make_hyperlink)
most_popular_item_df['商品链接'] = most_popular_item_df['商品链接'].apply(make_hyperlink)

# 将结果输出到文件，带标红信息
with open('output.html', 'w', encoding='utf-8') as f:
    f.write('<html>')
    f.write('<head>')
    f.write('<meta charset="utf-8">')
    f.write('</head>')
    f.write("<body>")
    f.write("<h2>好评度最高的前10件商品信息:</h2>")
    f.write(top10_highest_rating.to_html(index=False, columns=['排名','商品名称', '商品价格', '商品链接', '商品评分'], escape=False, justify='center'))

    f.write("<h2>价格最低的前10件商品信息:</h2>")
    f.write(top10_lowest_price.to_html(index=False, columns=['排名','商品名称', '商品价格', '商品链接', '商品评分'], escape=False, justify='center'))

    f.write("<h2>评价总数最多的前10件商品信息:</h2>")
    f.write(top10_most_comments.to_html(index=False, columns=['排名','商品名称', '商品价格', '商品链接', '商品评论'], escape=False, justify='center'))

    f.write("<h2>差评最少的前10件商品信息:</h2>")
    f.write(top10_least_bad_rating.to_html(index=False, columns=['排名','商品名称', '商品价格', '商品链接', '商品差评率'], escape=False, justify='center'))

    f.write("<h2>最热门商品即重复名称最多的商品信息:</h2>")
    f.write(most_popular_item_df.to_html(index=False, columns=['商品名称', '商品价格', '商品链接'], escape=False, justify='center'))
    f.write("</body>")
    f.write("</html>")