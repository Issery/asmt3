# -*- coding:utf-8 -*-
from numpy.core import overrides
import pymssql
import pyodbc
from flask import Flask, render_template, flash, request,  redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import query, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import urllib
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField,IntegerField
from wtforms.validators import DataRequired, NumberRange
import pandas as pd
from sqlalchemy import text
import os

import imp
import sys
imp.reload(sys)


app = Flask(__name__)


# 数据库配置: 数据库地址/关闭自动跟踪修改
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://lancer:Lrd19970323@test1-server.database.windows.net/test1database?driver=ODBC+Driver+17+for+SQL+Server&charset=utf8'
# app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'lancer'

db = SQLAlchemy(app)

# process csv
vdf = pd.read_csv('./static/v.csv')
seqdf = pd.read_csv('./static/vindex.csv')

# definition of tables
class Volcano(db.Model):
    # table name
    __tablename__ = 'volcanos'

    # field name
    number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    country = db.Column(db.String(32))
    region = db.Column(db.String(32))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    elev = db.Column(db.Integer)


    #Referece


    def save(self):
        db.session.add(self)
        db.session.commit()

class Vindex(db.Model):
    # 表名
    __tablename__ = 'vindex'

    # 字段
    sequence = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(32), unique=True)

    def save(self):
        db.session.add(self)
        db.session.commit()


class Form(FlaskForm):
    Numberstart = IntegerField(label='start_number')
    Numberend = IntegerField(label='end_number')
    start_eval = IntegerField(label='start_eval')
    end_eval = IntegerField(label='end_eval')

    submit = SubmitField('search')


@app.route('/search', methods=['post'])
def search():
    seach_form = Form(request.form)
    form_dict = request.form.to_dict()
    number_start = form_dict.get("Numberstart")
    number_end = form_dict.get("Numberend")
    start_eval = form_dict.get("start_eval")
    end_eval = form_dict.get("end_eval")
    query = str('{}<number<{}'.format(number_start,number_end))
    res = Volcano.query.filter(text(query))

    return render_template('result.html',res=res,df=vdf)

@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    验证逻辑:
    1. 调用WTF的函数实现验证
    2. 验证通过获取数据
    3. 判断作者是否存在
    4. 如果作者存在, 判断书籍是否存在, 没有重复书籍就添加数据, 如果重复就提示错误
    5. 如果作者不存在, 添加作者和书籍
    6. 验证不通过就提示错误
    '''
    # # 查询所有的作者信息, 让信息传递给模板
    volcano = Volcano.query.all()
    print('-------------------------------------------------')
    # form = peopleForm()
    # form2 = UpForm()
    # print(form.data)
    return render_template('index.html',df=vdf,volcanos=volcano)






if __name__ == '__main__':
    # 删除表
    db.drop_all()
    # 创建表
    db.create_all()
    volcano_list = []
    vdf.fillna('unk', inplace=True)
    print('adding data')
    for idx in range(len(vdf)):
        v_number = int(vdf.iloc[idx]['Number'])
        v_name = vdf.iloc[idx]['Volcano Name']
        v_country = vdf.iloc[idx]['Country']
        v_region = vdf.iloc[idx]['Region']
        v_latitude = float(vdf.iloc[idx]['Latitude'])
        v_longitude = float(vdf.iloc[idx]['Longitude'])
        v_elev = None if vdf.iloc[idx]['Elev']=='unk' else int(vdf.iloc[idx]['Elev'])
        volcano = Volcano(number=v_number,name=v_name,country=v_country,
                        region=v_region,latitude=v_latitude,longitude=v_longitude,
                        elev=v_elev)
        # volcano_list.append(volcano)
        db.session.add(volcano)
        db.session.commit()
    # db.session.add_all(volcano_list)
    # db.session.commit()
    app.run(debug=True)