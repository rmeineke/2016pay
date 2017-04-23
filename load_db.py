#!/usr/bin/python3


import sqlite3
import logging
import sys
import csv
from re import sub


def main():
    # set up for logging
    LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL,
              }
    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        level = LEVELS.get(level_name, logging.NOTSET)
        logging.basicConfig(level=level)

    logger = logging.getLogger()
    logger.debug('Entering main')

    # ######################## CHANGE
    db_name = '2016.pay.db'
    create_db(logger, db_name)

    # ######################## CHANGE
    csv_fn = '2016.pay.csv'
    load_file(logger, csv_fn, db_name)


def create_db(logger, db):
    logger.debug('Entering create_db')

    db = sqlite3.connect('{}'.format(db))
    cur = db.cursor()

    logger.debug('DROP TABLE IF EXISTS paydata')
    cur.execute('DROP TABLE IF EXISTS paydata')

    logger.debug('CREATE TABLE IF NOT EXISTS')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS paydata
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            dept TEXT,
            title TEXT,
            ttl_cash FLOAT,
            base_pay FLOAT,
            ot FLOAT,
            sick_vac_payout FLOAT,
            other_cash FLOAT,
            city_paid_defined_contrib FLOAT,
            medical_dental_vision FLOAT,
            city_paid_ret_contrib FLOAT,
            disability_life_medicare FLOAT,
            misc_costs FLOAT
        )
        ''')

    db.commit()
    cur.close()
    db.close()


def load_file(logger, fn, db):
    logger.debug('Entering load_file')

    db = sqlite3.connect('{}'.format(db))
    cur = db.cursor()
    with open(fn, 'r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            if ',' in row['name']:
                # inject a space for better formatting
                name = row['name'].replace(',', ', ')
            else:
                # if there is no comma .. need to normalize the data
                # seem to be a smattering of names that were not
                # in LN,FN format ... fix those and run again
                print('{} <<<<<<<<<<<<<<< '.format(row['name']))
                name = row['name']

            dept = row['dept']
            title = row['title']
            ttl_cash = convert_to_float(logger, row['ttl_cash'])
            base_pay = convert_to_float(logger, row['base_pay'])
            ot = convert_to_float(logger, row['ot'])
            sick_vac_payout = convert_to_float(logger, row['sick_vac_payout'])
            other_cash = convert_to_float(logger, row['other_cash'])
            city_paid_defined_contrib = convert_to_float(logger, row['city_paid_defined_contrib'])
            medical_dental_vision = convert_to_float(logger, row['medical_dental_vision'])
            city_paid_ret_contrib = convert_to_float(logger, row['city_paid_ret_contrib'])
            disability_life_medicare = convert_to_float(logger, row['disability_life_medicare'])
            misc_costs = convert_to_float(logger, row['misc_costs'])

            cur.execute('INSERT INTO paydata (name, dept, title, ttl_cash, base_pay, ot, \
                            sick_vac_payout, other_cash, city_paid_defined_contrib, \
                            medical_dental_vision, city_paid_ret_contrib, \
                            disability_life_medicare, misc_costs) \
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (name, dept, title,
                         ttl_cash,
                         base_pay,
                         ot,
                         sick_vac_payout,
                         other_cash,
                         city_paid_defined_contrib,
                         medical_dental_vision,
                         city_paid_ret_contrib,
                         disability_life_medicare,
                         misc_costs
                         ))

    db.commit()
    cur.close()
    db.close()


def convert_to_float(logger, v):
    logger.debug('Entering convert_to_float')
    if v:
        return float(sub(r'[^\d.]', '', v))
    else:
        return 0.0


if __name__ == '__main__':
    main()


'''
"Name",
"Department",
"Job Title (as of 12/31/15)",
"Total Cash Compensation",
"Base Pay",
"Overtime",
"Sick and Vacation Payouts",
"Other Cash Compensation",
"Defined Contribution Plan Contributions - City Paid",
"Medical Dental Vision",
"Retirement Contributions - City Paid*",
"Long Term Disability, Life, Medicare",
"Misc Employment Related Costs"



"Meineke,Robert S",
"Fire",
"PSRD",
"102,429.18",
"83,792.80",
"11,179.27",
"",
"7,457.11",
"",
"18,626.76",
"59,738.57",
"1,425.21",
"51.00"

"Guerra,Daniel P",
"Police",
"Police Officer",
"315,390.77",
"106,194.40",
"189,835.56",
"",
"19,360.81",
"",
"15,884.76",
"98,048.25",
"4,490.14",
""

'''
'''
robertm@Sys76:~/programming/2015pay$ ./load_db.py
x Ru Weerakoon <<<<<<<<<<<<<<<
Richard Keit <<<<<<<<<<<<<<<
Abe Andrade <<<<<<<<<<<<<<<
Sandy Shayesteh <<<<<<<<<<<<<<<
Holly Le <<<<<<<<<<<<<<<
Bob Staedler <<<<<<<<<<<<<<<
x Jayme Dickson <<<<<<<<<<<<<<<
'''