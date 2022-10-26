import gspread
from bot_req import *


def gs_update():
    gc = gspread.service_account(filename='testbot-365118-7a5c7350796d.json')
    sh = gc.open("Клинни")
    worksheet = sh.get_worksheet(0)

    cleaners_inf = cleaners()

    worksheet.update_cell(2, 1, check_list())
    worksheet.update_cell(2, 2, cleaners_inf[0])
    worksheet.update_cell(2, 3, cleaners_inf[1])
    how_work_inf = '\n'.join(how_work())
    worksheet.update_cell(2, 4, how_work_inf)
    general_information_inf = general_information()
    worksheet.update_cell(2, 5, general_information_inf[0] + '__!\n' + '\n'.join(general_information_inf[1]))

    worksheet = sh.get_worksheet(1)
    count = 1
    for name, v in cleaners_inf[2].items():
        v = v.split('\n')
        worksheet.update_cell(count, 1, name)
        worksheet.update_cell(count, 2, v[0])
        worksheet.update_cell(count, 3, v[1])
        worksheet.update_cell(count, 4, v[2])
        count += 1

    worksheet = sh.get_worksheet(2)
    additional_services_inf = additional_services()
    for i in range(2, len(additional_services_inf) + 2):
        if len(additional_services_inf[i - 2].split('+')) == 2:
            worksheet.update_cell(i, 1, additional_services_inf[i - 2].split('+')[1])
            worksheet.update_cell(i, 2, additional_services_inf[i - 2].split('+')[0])
        else:
            worksheet.update_cell(i, 1, additional_services_inf[i - 2])


