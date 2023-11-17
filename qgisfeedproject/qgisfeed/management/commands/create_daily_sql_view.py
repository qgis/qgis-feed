# coding=utf-8
import os
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """Create sql views from aggregate table
    """

    def load_data_from_sql(self, filename):
        file_path = os.path.join(os.path.dirname(__file__), 'sql/', filename)
        sql_statement = open(file_path).read()
        with connection.cursor() as c:
            c.execute(sql_statement)

    def handle(self, *args, **options):
        self.load_data_from_sql('sql_view_daily.sql')
