from django.shortcuts import render

from data_source.import_from_db import get_users_from_db

def users():
    return get_users_from_db()