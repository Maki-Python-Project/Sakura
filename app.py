import json
import logging
import sqlite3

from api import API
from collections import defaultdict
from database.database import (
    create_table, insert_record, update_all_record,
    delete_record, find_all, get_user_by_id, update_one_record
)
from middleware import Middleware


app = API()


def custom_exception_handler(request, response, exception_cls):
    response.text = "Oops! Something went wrong."


app.add_exception_handler(custom_exception_handler)


def create_dict(res, dbCursor):
    rowDict = {}
    rowDict_0 = {}
    dict_data = defaultdict(list)
    for row in res:
        rowDict = dict(zip([c[0] for c in dbCursor.description], row))
        for key in set(list(rowDict.keys())+list(rowDict_0.keys())):
            if key in rowDict:
                dict_data[key].append(rowDict[key])
            if key in rowDict_0:
                dict_data[key].append(rowDict_0[key])
        rowDict_0 = {}
    return dict_data


def find_users(response, dict_data):
    conn = sqlite3.connect('C:\\Maki\\Python code\\Courses\\sakura\\database\\user_records.db')
    dbCursor = conn.cursor()
    if len(dict_data) == 1:
        column = list(dict_data.keys())[0]
        column_val = dict_data[column]
        dbCursor.execute(f"SELECT * FROM User WHERE {column}='{column_val}'")
        res = dbCursor.fetchall()
    else:
        sql_req = "SELECT * FROM User WHERE {column}='{column_val}'"
        for _ in range(len(dict_data)-1):
            sql_req += " AND {column}='{column_val}'"
        for key, val in dict_data.items():
            dbCursor.execute(
                sql_req.format(column=key, column_val=val)
            )
            res = dbCursor.fetchall()
    response.content_type = 'application/json'
    response.status_code = 200
    response.text = json.dumps(res)


@app.route("/users")
def show_users(request, response):
    if request.method == 'GET':
        if request.GET == {}:
            data = create_dict(find_all().fetchall(), find_all())
            response.json = data
            response.content_type = 'application/json'
            response.status_code = 200
            return response
        else:
            find_users(response, dict(request.GET))

    if request.method == 'POST':
        response.json = dict(request.POST)
        id, last_name, first_name, phone, sex = list(dict(request.POST).values())
        create_table()
        insert_record(id, last_name, first_name, phone, sex)
        response.content_type = 'application/json'
        response.status_code = 201
        return response


@app.route("/users/{id}")
def show_user(request, response, id):
    if request.method == 'GET':
        response.json = create_dict(
            get_user_by_id(id).fetchall(),
            get_user_by_id(id)
        )
        response.content_type = 'application/json'
        response.status_code = 200
        return response

    if request.method == 'PUT':
        response.json = dict(request.POST)
        id, last_name, first_name, phone, sex = list(dict(request.POST).values())
        update_all_record(id, last_name, first_name, phone, sex)
        response.content_type = 'application/json'
        response.status_code = 200
        return response

    if request.method == 'PATCH':
        response.json = dict(request.POST)
        column = list(dict(request.POST).keys())[0]
        column_val = dict(request.POST)[column]
        update_one_record(id, column, column_val)
        response.content_type = 'application/json'
        response.status_code = 200
        return response

    if request.method == 'DELETE':
        delete_record(id)
        response.status_code = 204
        return response


class SimpleCustomMiddleware(Middleware):
    def process_request(self, request):
        if request.path == '/secured':
            logging.warning('I\'m here {request.url}')
        print("Processing request", request.url)

    def process_response(self, request, response):
        print("Processing response", request.url)


app.add_middleware(SimpleCustomMiddleware)
