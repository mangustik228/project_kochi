import pandas as pd
from pandas import ExcelWriter
import requests
import fake_useragent
from bs4 import BeautifulSoup
from time import sleep
import re
from tqdm import tqdm
from settings import admin_url, member_url, main_url

def clean_id(row):
    pattern = r'[0-9]+-*[0-9]*'
    if ''.join(re.findall(pattern, row)) == '':
        return 'Безбилетник'
    return ''.join(re.findall(pattern, row))


def parsing(login, password, sum_pages):
    session = requests.Session()
    user = fake_useragent.UserAgent().random
    data = {
    'name' : login,
    'pass' : password,
    'form_id' : 'user_login',
    'op' : 'Войти'
    }
    header =  {
    'user-agent' : user
    }
    url = admin_url  # url с адресом где авторизовываемся
    response = session.post(url, data=data, headers=header).text # Создаем сессию и передаем user-agent url
    urls_with_members = parsing_urls(sum_pages, session)
    df = parsing_members(urls_with_members, session)
    df.drop(columns=['lastname', 'first_name', 'middle_name', 'country', 'member_id_card_status', 'member_region', 'adress'], inplace=True)
    df['member_id_card'] =df['member_id_card'].apply(clean_id)
    return df
    
    
def parsing_urls(sum_pages, session):
    '''Функци для парсинга urls с карточками'''    
    urls_with_members = []
    for now_url in range(sum_pages):
        if now_url == 0:
            page = member_url
        else:
            page = f'{member_url}?page={now_url}'
        page_responce = session.get(page)  # Переходим поочередно на страницы из нашего массива 
        soup = BeautifulSoup(page_responce.text, 'lxml') # Получаем суп из нашей страницы
        hrefs = soup.findAll('td', class_='views-field views-field-title')
        for href in hrefs:
            href = href.find('a').get('href')
            href = main_url + href
            urls_with_members.append(href)
        sleep(1)
    return(urls_with_members)

def parsing_members(urls_with_members, session):
    df = pd.DataFrame(columns=['page', 'correct_name', 'lastname', 'first_name', 
                               'middle_name', 'country', 'birthday', 'work_place', 
                               'type_employment', 'member_region', 'member_status', 
                               'member_id_card', 'member_id_card_status', 'member_data', 
                               'member_year', 'adress', 'phone_one', 'email'])
    for page in tqdm(urls_with_members):
        try:
            df = pd.concat([df, pars_person_info(page, session)])
        except:
            break
        sleep(0.8)
    df = df.reset_index(drop=True)
    return df


def clean_df(df):
    pass        
    
def pars_person_info(page, session):
    '''pars one page of person information
    if No information in cell: change too None

    Args:
        soup (soup): page with person information

    Returns:
        df: df to concat with main df
    '''
    page_responce = session.get(page) 
    soup = BeautifulSoup(page_responce.text, 'lxml')
    data_members = []
    try:
        fullname = soup.find('h1', class_='page__title title').text
    except:
        fullname = None
    try:
        lastname = soup.find('div', class_='field field-name-field-lastname field-type-text field-label-hidden').find('div').find('div').text
    except:
        lastname = None
    try:
        first_name = soup.find('div', class_='field field-name-field-firstname field-type-text field-label-hidden').find('div').find('div').text
    except:
        first_name = None
    try:
        middle_name = soup.find('div', class_='field field-name-field-middlename field-type-text field-label-hidden').find('div').find('div').text
    except:
        middle_name = None
    try:
        country = soup.find('div', class_='field field-name-field-citizenship field-type-list-text field-label-hidden').find('div').find('div').text
    except:
        country = None
    try:
        birthday = soup.find('div', class_='field field-name-field-birthday field-type-datetime field-label-hidden').find('div').find('div').text
    except:
        birthday = None
    try:
        work_place = soup.find('div', class_='field field-name-field-work-place field-type-text field-label-hidden').find('div').find('div').text
    except:
        work_place = None
    try:
        type_employment = soup.find('div', class_='field field-name-field-work-sphere field-type-text field-label-hidden').find('div').find('div').text
    except:
        type_employment = None
    try:
        member_region = soup.find('div', class_='field field-name-field-region field-type-list-integer field-label-hidden').find('div').find('div').text
    except:
        member_region = None
    try:
        member_status = soup.find('div', class_='field field-name-field-mem-status field-type-list-integer field-label-hidden').find('div').find('div').text
    except:
        member_status = None
    try:
        member_id_card = soup.find('div', class_='field field-name-field-mem-card field-type-field-token-value field-label-hidden').find('div').find('div').text
    except:
        member_id_card = None
    try:
        member_id_card_status = soup.find('div', class_='field field-name-field-mem-card-status field-type-list-integer field-label-hidden').find('div').find('div').text
    except:
        member_id_card_status = None
    try:
        member_data = soup.find('div', class_='field field-name-field-mem-date field-type-datetime field-label-hidden').find('div').find('div').text
    except:
        member_data = None
    try:
        member_year = soup.find('div', class_='field field-name-field-reg-year field-type-number-integer field-label-hidden').find('div').find('div').text
    except:
        member_year = None
    try:
        adress = soup.find('div', class_='field field-name-field-addr field-type-text field-label-hidden').find('div').find('div').text
    except:
        adress = None
    try:
        mphone = soup.find('div', class_='field field-name-field-mphone field-type-number-decimal field-label-hidden').find('div').find('div').text
    except:
        mphone = None
    try:
        email = soup.find('div', class_='field field-name-field-email field-type-email field-label-hidden').find('div').find('div').text
    except:
        email = None
    try:
        type_employment = soup.find('div', class_='field field-name-field-work-sphere field-type-text field-label-hidden').find('div').find('div').text
    except:
        type_employment = None

    data_members.append([page, fullname, lastname, first_name, 
                         middle_name, country, birthday, work_place, 
                         type_employment, member_region, member_status, 
                         member_id_card, member_id_card_status, member_data, 
                         member_year, adress, mphone, email])
    name_columns = ['page', 'correct_name', 'lastname', 'first_name', 
                               'middle_name', 'country', 'birthday', 'work_place', 
                               'type_employment', 'member_region', 'member_status', 
                               'member_id_card', 'member_id_card_status', 'member_data', 
                               'member_year', 'adress', 'phone_one', 'email']   
    df = pd.DataFrame(data_members, columns=name_columns)
    # Есть лишние столбцы, по идеи надо бы удалить, но мне лень, и возможно что то переиграется, поэтому оставлю как есть
    return df

if __name__ == '__main__':
    parsing(1)