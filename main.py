from bs4 import BeautifulSoup as bs4
import requests
from tabulate import tabulate
import json
import logging

logging.basicConfig(format='%(asctime)s %(message)s',filename='program_logs.log',level=logging.DEBUG,filemode='a')
def func(row):
    return [x.get_text().replace('\n','') for x in row]

def save(data):
    with open('data.json','w') as f:
        json.dump(data,f)

def load():
    with open('data.json','r') as f:
        res = json.load(f)
    return res

header = ['Name of State / UT','Confirmed cases(Indian National)','Confirmed cases(Foreign National)','Cured','Death']



if __name__ == '__main__':
    try:
        response = requests.get('https://www.mohfw.gov.in/',timeout=5).text

        soup = bs4(response,'lxml')

        table_content = soup.find_all('table', class_='table table-striped table-dark')

        mentioned_table = table_content[-1]
        mentioned_rows = mentioned_table.find_all('tr')
        mentioned_rows = mentioned_rows[1:-1]

        data = []

        for row in mentioned_rows:
            rows = func(row.find_all('td'))
            if(len(rows) == 5):
                data.append(rows)
            else:
                data.append(rows[1:])

        cur_data = {x[0]: {'latest':x[1:]} for x in data}

        flag_change = False
        info = []

        prev_data = load()

        for state in cur_data:
            if state not in prev_data:
                info.append(f'{state} got its first case of corona virus: {cur_data[state]["latest"]}')
                flag_change = True
            else:
                curr = cur_data[state]['latest']
                prev = prev_data[state]['latest']
                if prev != curr:
                    info.append(f'Change in the number of cases for {state}: {prev} -> {curr}')
                    flag_change = True

        if flag_change:
            for state in cur_data:
                prev_data = cur_data
            save(prev_data)

        table = tabulate(data,headers=header,tablefmt='psql')
        print(table)

        event_info = ''
        for event in info:
            logging.warning(event)
            event_info += '\n - ' + event.replace("'","")

        print(event_info)
    except Exception as e:
        logging.exception('script got failed.')