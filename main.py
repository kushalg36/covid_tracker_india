from bs4 import BeautifulSoup as bs4
import requests
from tabulate import tabulate
import json
import logging
from slack import slack

PATH  = 'C:/Users/kusha/OneDrive/Desktop/project/corona_tracker/'

logging.basicConfig(format='%(asctime)s %(message)s',filename=PATH + 'program_logs.log',level=logging.DEBUG,filemode='a')
def func(row):
    return [x.get_text().replace('\n','') for x in row]

def save(data):
    with open('C:/Users/kusha/OneDrive/Desktop/project/corona_tracker/data.json','w') as f:
        json.dump(data,f)

def load():
    with open('C:/Users/kusha/OneDrive/Desktop/project/corona_tracker/data.json','r') as f:
        res = json.load(f)
    return res

header = ['State/UT','Indian','Foreign','Cured','Death']



if __name__ == '__main__':
    try:
        response = requests.get('https://www.mohfw.gov.in/',timeout=5).text

        soup = bs4(response,'lxml')

        table_content = soup.find_all('table', class_='table table-striped table-dark')

        mentioned_table = table_content[-1]
        mentioned_rows = mentioned_table.find_all('tr')
        mentioned_rows = mentioned_rows[1:-1]

        data = []

        state_shorts = {'Andaman and Nicobar Islands':'Andaman','Andhra Pradesh':'Andhra','Himachal Pradesh':'HP','Jammu and Kashmir':'J & K','Madhya Pradesh':'MP','Tamil Nadu':'TN','Uttar Pradesh':'UP','Chhattisgarh':'CG','Maharashtra':'MH'}

        for row in mentioned_rows:
            rows = func(row.find_all('td'))
            if(rows[1] in state_shorts):
                rows[1] = state_shorts[rows[1]]
            if(len(rows) == 5):
                rows[0] = 'Total'
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

        event_info = ''
        for event in info:
            logging.warning(event)
            event_info += '\n - ' + event.replace("'","")

        logging.warning(f'{flag_change} -------- outside condition')
        text = f'Corona Virus update in India till now:\n{event_info}\n ```{table}```'
        if flag_change:
            logging.warning(f'{flag_change} -------- inside condition')
            slack()(text)

    except Exception as e:
        logging.exception('script got failed.')
        slack()(f'Exception occured: [{e}]')


