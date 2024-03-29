import tkinter as tk
from tkinter import Button, Label, Tk, Frame, BOTH, filedialog, messagebox
import pandas as pd
from pandas import ExcelWriter
import pars
from settings import organization, year
from datetime import datetime
import time

if datetime.today().year > 2023:
    print('Обратитесь к разработчику программного обеспечения: telegramm +7-917-505-68-14. Необходимо сменить год...')
    time.sleep(15)
    exit()
    
def start_parsing():
    global main_df
    if not valid.error_main_df:
        app.show_value('parsing_now', 'Подгрузи main_df', 'red', column=1)
        return
    try:
        pages = int(app.pages.get())
    except:
        app.show_value('parsing_now', 'Страницы не в цифрах', 'red', column=1)
        return
    parsing_df = pars.parsing(app.login.get(), app.password.get(), pages)
    try:
        main_df = pd.concat([main_df, parsing_df])
    except:
        app.show_value('parsing_now', 'Что то пошло не так', 'red', column=1)      
    app.password.delete(0, 'end')
    duplicates = len(parsing_df) - len(main_df[main_df.duplicated(subset='member_id_card')])
    main_df.drop_duplicates(subset='member_id_card', inplace=True)
    text = f'{len(parsing_df)} из них новых {duplicates}'
    app.show_value('parsing_now', text, 'green', column=1)
        
def save_bases():
    try:
        with ExcelWriter("main_df.xlsx") as writer:
            main_df.to_excel(writer, sheet_name="Sheet1", index=False)
        with ExcelWriter('equaring_df.xlsx') as writer:
            equaring_df.to_excel(writer, sheet_name='Sheet1', index=False)
        messagebox.showerror("все ок", 'База успешно обновлена!')
    except:
        messagebox.showerror("Ошибка", 'Судя по всему открыт файл')
        

def insert_by_id(row):
    if row['pay_insert'] == 1:
        return 1
    if len(main_df.loc[(main_df['member_id_card'] == row['member_card'])]) != 1:
        return 0
    if row['type'] == '1. Единоразовый вступительный взнос':
        if len(main_df.loc[(main_df['member_id_card'] == row['member_card']), f'equaring{year}_commin']) == 1:
            main_df.loc[(main_df['member_id_card'] == row['member_card']),
                        f'equaring{year}_commin'] += row['sum']
            valid.insert_id += 1
            return 1
    if row['type'] == '2. Ежегодный членский взнос':
        if len(main_df.loc[(main_df['member_id_card'] == row['member_card']), f'equaring{year}_regular']) == 1:
            main_df.loc[(main_df['member_id_card'] == row['member_card']),
                        f'equaring{year}_regular'] += row['sum']
            valid.insert_id += 1
            return 1
    if row['type'] == '3. Добровольное пожертвование':
        if len(main_df.loc[(main_df['member_id_card'] == row['member_card']), f'equaring{year}_charity']) == 1:
            main_df.loc[(main_df['member_id_card'] == row['member_card']),
                        f'equaring{year}_charity'] += row['sum']
            valid.insert_id += 1
            return 1
    else:
        return 0


def insert_by_name(row):
    if row['pay_insert'] == 1:
        return 1
    if len(main_df.loc[(main_df['correct_name'] == row['name'])]) != 1:
        return 0
    if row['type'] == '1. Единоразовый вступительный взнос':
        if len(main_df.loc[(main_df['correct_name'] == row['name']), f'equaring{year}_commin']) == 1:
            main_df.loc[(main_df['correct_name'] == row['name']),
                        f'equaring{year}_commin'] += row['sum']
            valid.insert_names += 1
            return 1
    if row['type'] == '2. Ежегодный членский взнос':
        if len(main_df.loc[(main_df['correct_name'] == row['name']), f'equaring{year}_regular']) == 1:
            main_df.loc[(main_df['correct_name'] == row['name']),
                        f'equaring{year}_regular'] += row['sum']
            valid.insert_names += 1
            return 1
    if row['type'] == '3. Добровольное пожертвование':
        if len(main_df.loc[(main_df['correct_name'] == row['name']), f'equaring{year}_charity']) == 1:
            main_df.loc[(main_df['correct_name'] == row['name']),
                        f'equaring{year}_charity'] += row['sum']
            valid.insert_names += 1
            return 1
    else:
        return 0


def create_classes():
    Equar_files = Equaring_files()


class Check_errors():
    def __init__(self):
        self.error_main_df = False
        self.error_equaring_df = False
        self.error_equaring_files = True
        self.insert_files = False
        self.insert_names = 0
        self.insert_id = 0
        self.insert_pays = 0
        self.sum_error_pays_before = 0
        self.sum_error_pays_after = 0

    def error_message(self):
        text_error = ''
        if not self.error_main_df:
            text_error += 'Нет файла с основной базой\n'
        if not self.error_equaring_df:
            text_error += 'Нет файла с базой эквайринга\n'
        if not self.error_equaring_files:
            text_error += 'Что то не то с загруженными файлами\n'
        if text_error == '':
            return True
        messagebox.showerror("Ошибка", text_error)
        return False

    def check_insert_pay(self):
        if self.insert_pays == 0:
            return True
        elif self.insert_pays == 1:
            messagebox.showerror("Ошибка", 'Хватит тыкать. базы добавлены')
        elif self.insert_pays == 2:
            messagebox.showerror("Ошибка", 'Ну хватит уже')
        elif self.insert_pays == 3:
            messagebox.showerror("Ошибка", 'Ничего не измениться')
        elif self.insert_pays == 4:
            messagebox.showerror("Ошибка", 'Серьезно!?')
        elif self.insert_pays == 5:
            messagebox.showerror("Ошибка", 'Прекрати тыкать в кнопку!!!')
        elif self.insert_pays == 6:
            messagebox.showerror(
                "Ошибка", 'Программа делалась на коленке...\n может что то сломаться')
        elif self.insert_pays == 7:
            messagebox.showerror("Ошибка", 'Ой все...')
        elif self.insert_pays >= 8:
            messagebox.showerror(
                "Ошибка", 'Если хочешь еще потыкать, просто перезапусти программу!')
        return False


class Equaring_df():
    def __init__(self) -> None:
        pass

    def main_equaring_df():
        global equaring_df
        try:
            equaring_df = pd.read_excel('equaring_df.xlsx')
            app.show_value('equaring_df', 'Файл подгружен', 'green')
            app.show_value('errors_pays', len(equaring_df.query('pay_insert == 0')), 'red')
            valid.sum_error_pays_before = len(equaring_df.query('pay_insert == 0'))
            app.show_value('sum_df_equaring', f"{equaring_df['sum'].sum():.2f}", 'green')
            valid.error_equaring_df = True
        except Exception as e:
            print(e)
            app.show_value('equaring_df', 'Что то не так с файлом', 'red')

    def insert_pay():
        if not valid.error_message() or not valid.check_insert_pay():
            valid.insert_pays += 1
            return
        valid.insert_pays += 1
        global equaring_df
        equaring_df['pay_insert'] = equaring_df.apply(insert_by_id, axis=1)
        equaring_df['pay_insert'] = equaring_df.apply(insert_by_name, axis=1)
        global uncorrect_df
        uncorrect_df = equaring_df.query('pay_insert == 0')
        app.show_value('member', valid.insert_id, 'green')
        app.show_value('fio', valid.insert_names, 'green')
        valid.sum_error_pays_after = len(equaring_df.query('pay_insert == 0'))
        app.show_value('errors_pays', f'{valid.sum_error_pays_before} ({valid.sum_error_pays_after})', 'red')


class Equaring_files():
    def __init__(self):
        self.path = []
        self.df = pd.DataFrame()
        self.choose_files()

    def choose_files(self):
        self.path = filedialog.askopenfilenames()
        app.show_value('equaring_files_status', 'Файлы выбраны', 'green')
        app.show_value('equaring_files_sum', len(self.path), 'green')
        self.clean_df()

    def clean_df(self):
        '''Чистка приходящих файлов с эквайрингами'''
        name_row_v6 = ('id_pay', 'data', 'sum', 'phone', 'type', 'name')
        name_row_v7 = ('id_pay', 'data', 'sum', 'phone',
                       'type', 'name', 'period')
        name_row_v8 = ('id_pay', 'data', 'sum', 'phone',
                       'type', 'name', 'member_card', 'period')
        name_row_v9 = ('id_pay', 'data', 'sum', 'phone',
                       'type', 'name', 'member_card', 'period', 'email')
        uncorrect_data = []

        for path in self.path:
            try:
                df = pd.read_excel(path)
                if len(df.columns) == 6:
                    df.set_axis(name_row_v6, axis=1, inplace=True)
                elif len(df.columns) == 7:
                    df.set_axis(name_row_v7, axis=1, inplace=True)
                elif len(df.columns) == 8:
                    df.set_axis(name_row_v8, axis=1, inplace=True)
                elif len(df.columns) == 9:
                    df.set_axis(name_row_v9, axis=1, inplace=True)
                self.df = pd.concat([self.df, df])
            except:
                uncorrect_data.append(path)
        app.text_errors(uncorrect_data)
        self.df.dropna(subset=['sum'], inplace=True)
        self.df['data'] = pd.to_datetime(
            self.df['data'], errors='coerce', format='%Y-%m-%d')
        self.df = self.df[self.df['id_pay'] != 'ID платежа']
        self.df['pay_insert'] = 0
        try:
            self.df['member_card'] = self.df['member_card'].apply(self.del_zero)
        except:
            pass
        self.df.reset_index(drop=True, inplace=True)
        self.merge_files()

    def merge_files(self):
        '''функция для женитьбы файлов'''
        global equaring_df
        equaring_df = pd.concat([equaring_df, self.df])
        duplicates = len(equaring_df[equaring_df.duplicated(subset='id_pay')])
        app.show_value('sum_pays', self.df['sum'].sum(), 'green')
        equaring_df.drop_duplicates(subset='id_pay', inplace=True)
        app.show_value('sum_pays_strings', len(self.df), 'green')
        app.show_value('duplicates_name', duplicates)
        

    def del_zero(self, row):
        '''Удаление нулей в начале билета'''
        try:
            row = row.strip()
            while row[0] == '0':
                row = row[1:]
            else:
                return row
        except:
            return 'Билет не указан'


class InputFileDf():
    '''Класс для выбора и проверки входящего файла с основным df
    '''

    def __init__(self) -> None:
        self.check_file()

    def choose_df():
        '''Метод для выбора файла
        '''
        try:
            path = filedialog.askopenfilename()
            global main_df
            main_df = pd.read_excel(path)
            InputFileDf.check_file(main_df)
            app.show_value('main_df', 'Файл успешно загружен', 'green')
            valid.error_main_df = True
        except:
            app.show_value('main_df', 'Выбранный файл косячный', 'red')

    def check_file(df):
        '''проверка файла на наличие столбцовf equaring{year}...
        Args:
            df (DataFrame): dataFrame from choose_df

        Raises:
            TypeError: Входящий файл не является датафреймом, либо не содержит нужные столбцы
        '''
        check_massiv = (f'equaring{year}_charity', f'equaring{year}_regular',
                        f'equaring{year}_charity', 'member_id_card')
        columns = tuple(df.columns)
        for check in check_massiv:
            if check not in columns:
                raise TypeError
        df[f'equaring{year}_commin'].fillna(0, inplace=True)
        df[f'equaring{year}_regular'].fillna(0, inplace=True)
        df[f'equaring{year}_charity'].fillna(0, inplace=True)


class Main_window(Frame):
    '''Основной класс с виджетами

    Args:
        Frame (root): На вход получает главное окно в котором все рисуется
    '''

    def __init__(self, parent):
        '''Что за super().__init__() я не в курсе, но нужен
        при инициализации запускает метод с рисовалками всех окон

        Args:
            parent (win): основной класс Tk()
        '''
        super().__init__()
        self.init_metod()
        

    def text_errors(self, texts):
        if len(texts) == 0:
            self.show_value('error_files', len(texts), 'green')
        else:
            valid.error_equaring_files = False
            self.show_value('error_files', len(texts), 'red')
            for i, text in enumerate(texts):
                Label(self, text=f'не загружен: {text}', fg='red').grid(
                    row=i+20, columnspan=4, sticky='w')

    def show_value(self, show_cell, value, color='black', column=2):
        ''' 'main_df': 0,
            'equaring_df': 1,
            'equaring_files_status': 2,
            'equaring_files_sum': 3,
            'error_files': 4,
            'sum_pays_strings': 5,
            'sum_pays': 6, # Сумма новых эквайрингов
            'duplicates_name': 7,
            'member': 9,
            'fio': 10,
            'errors_pays': 11,
            'login' : 12,
            'password' : 13,
            'need_pages' : 14,
            'parsing_now' : 15, 
            'sum_df_equaring' : 50, # Сумма всех эквайрингов
            'sum_error_equaring' : 17 # Сумма всех не внесенных эквайрингов
        '''
        dictor = {
            'main_df': 0,
            'equaring_df': 1,
            'equaring_files_status': 2,
            'equaring_files_sum': 3,
            'error_files': 4,
            'sum_pays_strings': 5,
            'sum_pays': 6, # Сумма новых эквайрингов
            'duplicates_name': 7,
            'member': 9,
            'fio': 10,
            'errors_pays': 11,
            'login' : 12,
            'password' : 13,
            'need_pages' : 14,
            'parsing_now' : 15, 
            'sum_df_equaring' : 50, # Сумма всех эквайрингов
            'sum_error_equaring' : 17 # Сумма всех не внесенных эквайрингов
        }
        if dictor[show_cell] == 50:
            Label(self, text=value, fg=color).grid(
                row=1, column=1, padx=3, pady=3, sticky='we')
        else:
            Label(self, text=value, fg=color).grid(
                row=dictor[show_cell], column=column, padx=3, pady=3, sticky='we')

    def init_metod(self):
        '''Метод вызываемый при инициализации, указываются размеры окна и статичные виджеты
        '''
        self.master.title(organization)
        self.pack(fill=BOTH, expand=1)
        self.master.geometry('530x600+100+25')

        Button(self, text='Выбрать базу данных', command=InputFileDf.choose_df).grid(
            row=0, column=0, sticky='we')
        Label(self, text='База equaring_df.xlsx:').grid(
            row=1, column=0, sticky='we')
        Button(self, text='Выбрать файлы для эквайринга', command=create_classes).grid(
            row=2, column=0, pady=3, padx=3, sticky='we')
        Label(self, text='Выбрано файлов:').grid(
            row=3, column=1, padx=3, pady=3, sticky='e')
        Label(self, text='Из них косячных:').grid(
            row=4, column=1, padx=3, pady=3, sticky='e')
        Label(self, text='Сумма строк в выгрузке:').grid(
            row=5, column=1, padx=3, pady=3, sticky='e')
        Label(self, text='Сумма оплат в выгрузке:').grid(
            row=6, column=1, padx=3, pady=3, sticky='e')
        Label(self, text='Уже были внесены:').grid(
            row=7, column=1, padx=3, pady=3, sticky='e')
        Button(self, text='Внести оплаты', command=Equaring_df.insert_pay).grid(
            row=8, column=2, sticky='we')
        Label(self, text='Внесено по ЧБ:').grid(
            row=9, column=1, padx=3, pady=3, sticky='e')
        Label(self, text='Внесено по ФИО:').grid(
            row=10, column=1, padx=3, pady=3, sticky='e')
        Label(self, text='Не внесено:').grid(
            row=11, column=1, padx=3, pady=3, sticky='e')
        Label(self, text='Введите логин:').grid(
            row=12, column=0, padx=3, pady=3, sticky='e')
        Label(self, text='Введите пароль:').grid(
            row=13, column=0, padx=3, pady=3, sticky='e')
        Label(self, text='Сколько страниц спарсить:').grid(
            row=14, column=0, padx=3, pady=3, sticky='e')
        Label(self, text='Спарсено:').grid(
            row=15, column=0, padx=3, pady=3, sticky='e')
        self.login = tk.Entry(self)
        self.login.grid(row=12, column=1, padx=3, pady=3, sticky='we')
        self.password = tk.Entry(self, show='*')
        self.password.grid(row=13, column=1, padx=3, pady=3, sticky='we')
        self.pages = tk.Entry(self)
        self.pages.grid(row=14, column=1, padx=3, pady=3, sticky='we')
        Button(self, text='Начать парсирить', command=start_parsing).grid(
            row=16, column=0, columnspan=2, sticky='we')
        Button(self, text='Сохранить базы', command=save_bases).grid(
            row=17, column=0, columnspan=2, sticky='we')
        Button(self, text='Выход', command=self.quit).grid(
            row=17, column=2, sticky='we')
        self.show_value('main_df', 'Необходимо выбрать файл', 'red')
        self.show_value('equaring_files_status',
                        'Необходимо выбрать файлы', 'red')


win = Tk()
main_df = pd.DataFrame()
equaring_df = pd.DataFrame()
app = Main_window(win)
valid = Check_errors()
Equaring_df.main_equaring_df()


def main():
    win.mainloop()


if __name__ == '__main__':
    main()
