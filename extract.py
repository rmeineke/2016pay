#! /usr/bin/python3

import logging
import sys
import sqlite3
import datetime


def main():
    ############################
    # change to current db name
    database = '2016.pay.db'

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
    logger.debug(datetime.date.today().isoformat())

    db = sqlite3.connect(database)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    print_html_headers()
    # header
    # match title
    # match any other relevant fields
    # what color should the table headers be
    params = [
        {'table_title': 'PD Comm Manager', 'title': "'Division Manager'", 'other_fields': 'name = "McDonald, Joey L"',
         'table_color': 'blue'},
        {'table_title': 'PD Asst Comm Manager', 'title': "'Assist Communications Manager'", 'other_fields': '1',
         'table_color': 'blue'},
        {'table_title': 'Fire Supervising PSDs', 'title': "'Supervg Pub Safety Disp'", 'other_fields': 'dept = "Fire"',
         'table_color': 'red'},
        {'table_title': 'PD Supervising PSDs', 'title': "'Supervg Pub Safety Disp'", 'other_fields': 'dept = "Police"',
         'table_color': 'blue'},
        {'table_title': 'All Supervising PSDs', 'title': "'Supervg Pub Safety Disp'", 'other_fields': '1',
         'table_color': 'grey'},

        {'table_title': 'Fire Seniors', 'title': "'Senr Pub Safe Dispatch'", 'other_fields': 'dept = "Fire"',
         'table_color': 'red'},
        {'table_title': 'PD Seniors', 'title': "'Senr Pub Safe Dispatch'", 'other_fields': 'dept = "Police"',
         'table_color': 'blue'},
        {'table_title': 'All Seniors', 'title': "'Senr Pub Safe Dispatch'", 'other_fields': '1',
         'table_color': 'grey'},
        {'table_title': 'Fire PSRDs', 'title': "'Public Safety Radio Disp FT'", 'other_fields': 'dept = "Fire"',
         'table_color': 'red'},
        {'table_title': 'PD PSRDs', 'title': "'Public Safety Radio Disp FT'", 'other_fields': 'dept = "Police"',
         'table_color': 'blue'},
        {'table_title': 'All (Full Time) PSRDs', 'title': "'Public Safety Radio Disp FT'", 'other_fields': '1',
         'table_color': 'grey'},
        {'table_title': 'Part Time PSRDs', 'title': "'Public Safety Radio Disp PT'", 'other_fields': '1',
         'table_color': 'blue'},
        {'table_title': 'PSRD Trainees', 'title': "'Public Sfty Radio Disp Trainee'", 'other_fields': '1',
         'table_color': 'grey'},
        {'table_title': 'PSCSs', 'title': "'Public Safety Com Spec FT'", 'other_fields': '1',
         'table_color': 'blue'},
        {'table_title': 'Part Time PSCSs', 'title': "'Public Safety Com Spec PT'", 'other_fields': '1',
         'table_color': 'blue'}
    ]
    # params = [('PD Comm Mgr', 'title = "Comm. Mgr"', 'name = "Mc Donald,Joey L"', 'blue'),
    #           ('Fire Seniors', 'title = "Sr. PSD"', 'dept = "Fire"', 'red')]
    for p in params:
        print('<table>')
        select_str = construct_select_str(logger, p)
        # call the select_from ...
        # pass in
        #       logger
        #       cur
        #       select_str
        #       title
        #       color of the header
        #     select_from(logger, cur, select_str, 'PD Comm Mgr', )

        select_from(logger, cur, select_str, p['table_title'], p['table_color'])
        print('</table>')

    sql_str = '''
        select *
        FROM paydata
        WHERE title = "'Supervg Pub Safety Disp'"
        AND dept = 'Fire';
        '''
    cols_to_display = ['name', 'ttl_cash', 'base_pay', 'ot', 'other_cash', 'sick_vac_payout']
    title_str = 'Fire Supervisors'
    color = 'red'
    generic_select(logger, cur, sql_str, cols_to_display, title_str, color)

    spec_str = '''
    select name, dept, title, ttl_cash, base_pay, ot, other_cash, sick_vac_payout
    FROM paydata where sick_vac_payout > 99999.99 order by sick_vac_payout DESC;
    '''
    special_select_from(logger, cur, spec_str, 'Sick/Vacation Payouts >= $100,000', 'grey')

    spec_str = '''
        select name, dept, title, ttl_cash, base_pay, ot, other_cash, sick_vac_payout
        FROM paydata where ot > 99999.99 order by sick_vac_payout DESC;
        '''
    select_ot_from(logger, cur, spec_str, 'Overtime >= $100,000', 'grey')

    spec_str = '''
            select name, title, ttl_cash, base_pay, ot, other_cash, sick_vac_payout
            FROM paydata where dept = 'Fire';
            '''
    select_fire_from(logger, cur, spec_str, 'All Fire', 'red')

    spec_str = '''
               select name, title, ttl_cash, base_pay, ot, other_cash, sick_vac_payout
               FROM paydata where dept = 'Police';
               '''
    select_fire_from(logger, cur, spec_str, 'All Police', 'blue')

    # save, then close the cursor and db
    db.commit()
    cur.close()
    db.close()

    print_html_footers()


def print_html_headers():
    print("""
<!DOCTYPE html>
<html>
<head>
<title> 2016 </title>
<link rel="stylesheet" type="text/css" href="paydata.css">
</head>
<body>
""")


def print_html_footers():
    print("""
</body>
</html>
""")


def select_from(logger, cur, str, title_str, color):
    logger.debug('Entering select_from')
    logger.debug('title_str: {}'.format(title_str))
    logger.debug(color)
    print('<tr class="{0}"><th colspan="7">{1}</th></tr>'.format(color, title_str))
    print('<tr class="hdr"><td>&nbsp;</td>')
    print('<td class="name">Name</td>')
    print('<td>Total Cash</td>')
    print('<td>Base Pay</td>')
    print('<td>Overtime</td>')
    print('<td>Other Cash</td>')
    print('<td>S/V Payouts</td></tr>')

    logger.debug(str)
    cur.execute(str)
    rows = cur.fetchall()
    psrd_count = 0
    for r in rows:
        psrd_count += 1
        print('<tr>')
        print('<td>{}</td>'.format(psrd_count))
        print('<td class="name">{}</td>'.format((r['name']).replace(',', ', ')))
        print('<td>{:,.2f}</td>'.format(r['ttl_cash']))
        print('<td>{:,.2f}</td>'.format(r['base_pay']))
        print('<td>{:,.2f}</td>'.format(r['ot']))
        print('<td>{:,.2f}</td>'.format(r['other_cash']))
        print('<td>{:,.2f}</td>'.format(r['sick_vac_payout']))

        print('</tr>')
        # print()


def construct_select_str(logger, p):
    logger.debug('Entering construct_select_str')
    sql_str = """SELECT name, ttl_cash, base_pay, ot, other_cash, sick_vac_payout
              FROM paydata
              WHERE title = {0}
              AND sick_vac_payout=0
              AND {1}
              UNION ALL
              SELECT name, ttl_cash, base_pay, ot, other_cash, sick_vac_payout
              FROM paydata
              WHERE title = {0}
              AND sick_vac_payout>0
              AND {1}""".format(p['title'], p['other_fields'])
    return sql_str


def special_select_from(logger, cur, str, title_str, color):
    logger.debug('Entering special_select_from')
    logger.debug('title_str: {}'.format(title_str))
    logger.debug(color)
    print('<table>')
    print('<tr class="{0}"><th colspan="9">{1}</th></tr>'.format(color, title_str))
    print('<tr class="hdr"><td>&nbsp;</td>')
    print('<td class="name">Name</td>')
    print('<td class="name">Department</td>')
    print('<td class="name">Title</td>')
    print('<td>Total Cash</td>')
    print('<td>Base Pay</td>')
    print('<td>Overtime</td>')
    print('<td>Other Cash</td>')
    print('<td class="bold">S/V Payouts</td></tr>')

    logger.debug(str)
    cur.execute(str)
    rows = cur.fetchall()
    psrd_count = 0
    for r in rows:
        psrd_count += 1
        print('<tr>')
        print('<td>{}</td>'.format(psrd_count))
        print('<td class="name">{}</td>'.format(r['name']))
        print('<td class="name">{}</td>'.format(r['dept']))

        print('<td class="name">{}</td>'.format(r['title']))

        print('<td>{:,.2f}</td>'.format(r['ttl_cash']))
        print('<td>{:,.2f}</td>'.format(r['base_pay']))
        print('<td>{:,.2f}</td>'.format(r['ot']))
        print('<td>{:,.2f}</td>'.format(r['other_cash']))
        print('<td class="bold">{:,.2f}</td>'.format(r['sick_vac_payout']))

        print('</tr>')
        # print()
    print('</table>')


def select_ot_from(logger, cur, str, title_str, color):
    logger.debug('Entering special_select_from')
    logger.debug('title_str: {}'.format(title_str))
    logger.debug(color)
    print('<table>')
    print('<tr class="{0}"><th colspan="9">{1}</th></tr>'.format(color, title_str))
    print('<tr class="hdr"><td>&nbsp;</td>')
    print('<td class="name">Name</td>')
    print('<td class="name">Department</td>')
    print('<td class="name">Title</td>')
    print('<td>Total Cash</td>')
    print('<td>Base Pay</td>')
    print('<td class="bold">Overtime</td>')
    print('<td>Other Cash</td>')
    print('<td>S/V Payouts</td></tr>')

    logger.debug(str)
    cur.execute(str)
    rows = cur.fetchall()
    psrd_count = 0
    for r in rows:
        psrd_count += 1
        print('<tr>')
        print('<td>{}</td>'.format(psrd_count))
        print('<td class="name">{}</td>'.format(r['name']))
        print('<td class="name">{}</td>'.format(r['dept']))

        print('<td class="name">{}</td>'.format(r['title']))

        print('<td>{:,.2f}</td>'.format(r['ttl_cash']))
        print('<td>{:,.2f}</td>'.format(r['base_pay']))
        print('<td class="bold">{:,.2f}</td>'.format(r['ot']))
        print('<td>{:,.2f}</td>'.format(r['other_cash']))
        print('<td>{:,.2f}</td>'.format(r['sick_vac_payout']))

        print('</tr>')
        # print()
    print('</table>')


def generic_select(logger, cur, sql_str, cols_to_display, title_str, color):
    logger.debug('Entering generic_select')
    logger.debug(cur)
    logger.debug(sql_str)
    logger.debug(cols_to_display)
    logger.debug(title_str)
    logger.debug(color)
    logger.debug('Exiting generic_select')


def select_fire_from(logger, cur, str, title_str, color):
    logger.debug('Entering special_select_from')
    logger.debug('title_str: {}'.format(title_str))
    logger.debug(color)
    print('<table>')
    print('<tr class="{0}"><th colspan="9">{1}</th></tr>'.format(color, title_str))
    print('<tr class="hdr"><td>&nbsp;</td>')
    print('<td class="name">Name</td>')
    print('<td class="name">Title</td>')
    print('<td>Total Cash</td>')
    print('<td>Base Pay</td>')
    # print('<td class="bold">Overtime</td>')
    print('<td>Overtime</td>')
    print('<td>Other Cash</td>')
    print('<td>S/V Payouts</td></tr>')

    logger.debug(str)
    cur.execute(str)
    rows = cur.fetchall()
    psrd_count = 0
    for r in rows:
        psrd_count += 1
        print('<tr>')
        print('<td>{}</td>'.format(psrd_count))
        print('<td class="name">{}</td>'.format(r['name']))
        print('<td class="name">{}</td>'.format(r['title']))
        print('<td>{:,.2f}</td>'.format(r['ttl_cash']))
        print('<td>{:,.2f}</td>'.format(r['base_pay']))
        print('<td>{:,.2f}</td>'.format(r['ot']))
        print('<td>{:,.2f}</td>'.format(r['other_cash']))
        print('<td>{:,.2f}</td>'.format(r['sick_vac_payout']))

        print('</tr>')
        # print()
    print('</table>')

if __name__ == '__main__':
    main()
