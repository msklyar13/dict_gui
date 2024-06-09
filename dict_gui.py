import sqlite3
import re
from tkinter import *
from tkinter import ttk 
import locale
locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')

# Створити базу даних (БД) SQLite для двомовного словника
conn = sqlite3.connect('corpus_db.db')
c = conn.cursor()

c.execute('''DROP TABLE IF EXISTS vocab''')

# Зробити мінімум 4 категорії, до яких належатимуть слова
c.execute('''CREATE TABLE IF NOT EXISTS vocab (
    id INTEGER PRIMARY KEY,
    dialect TEXT,
    pol word TEXT,
    ukr word TEXT)
    ''')

# Наповнити БД словами (мінімум 50) та їхніми перекладами
def typeDial(text):
    dialName = re.search(r'([а-яіїґє]+)\.txt', text).group(1)
    return dialName

def dialDict(file): 
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        dictPolUkr = {}
        for pair in text.split('\n'):
            dictPolUkr[pair.split(' - ')[0]] = pair.split(' - ')[1]
        return dictPolUkr

text_lib = ['сілезький.txt',
            'малопольський.txt',
            'мазовецький.txt',
            'великопольський.txt']

wId = 1
for text in text_lib:
    dial = typeDial(text)
    for i in dialDict(text):
        wPol = i
        wUkr = dialDict(text)[i]
        c.execute('''INSERT INTO vocab VALUES (?, ?, ?, ?)''',
                    (wId, dial, wPol, wUkr))
        wId += 1

conn.commit()

# Створити новий графічний (віконний) проєкт мовою Python
window = Tk()
window.title('dict_gui')

# У вікні програми зробити 2 вкладки (Tab): «Словник» і «Про автора»
tabs = ttk.Notebook(window)
tabDict = ttk.Frame(tabs)
tabs.add(tabDict, text='Словник')

tabAuth = ttk.Frame(tabs)
tabs.add(tabAuth, text='Про словник')
tabs.grid()

labelAuth = Button(tabAuth, text = '''Словник польських діалектів.''',
                   font = 'Arial 16 bold')
labelAuth.place(relx=0.5, rely=0.5, anchor=CENTER)
labelAuth.place()

# Додатковий напис-хедер (для краси)))
labelDict = Label(tabDict, text = 'СЛОВНИК ПОЛЬСЬКИХ ДІАЛЕКТИЗМІВ', font = ('Arial 16 bold'), bg='white', fg='red')
labelDict.grid(pady=4)

# У вкладці «Словник» додати: напис (Label); спадний список (ComboBox); таблицю для даних
labelDict = Label(tabDict, text = 'Оберіть, що саме вас цікавить', font = ('Arial 16 bold'), bg='red', fg='white')
labelDict.grid(pady=4)

comboDict = ttk.Combobox(tabDict, textvariable = StringVar()) 
comboDict.grid(pady=4)

col = ['id', 'dial', 'wPol', 'wUkr']
dictDial = ttk.Treeview(tabDict, columns=col, show='headings')
dictDial.heading('id', text='ІНДЕКС У СЛОВНИКУ')
dictDial.heading('dial', text='ДІАЛЕКТ')
dictDial.heading('wPol', text='СЛОВО')
dictDial.heading('wUkr', text='ПЕРЕКЛАД')
dictDial.grid(pady=4)

# Створити в проєкті під’єднання до БД
conn = sqlite3.connect('corpus_db.db')
c = conn.cursor()

# Наповнити спадний список (ComboBox) назвами категорій слів
c.execute("SELECT dialect from vocab")
listDial = list(set(c.fetchall()))
comboDict.configure(values=listDial)

# Створити SQL-запит до БД, який наповнює таблицю всіма словами
# Відсортувати польські слова за абеткою за зростанням
# Переконатися, що при сортуванні дотримано правил, прийнятих у цій мові
def polish_sort_key(item):
    return locale.strxfrm(item[2])

c.execute("SELECT id, dialect, pol, ukr from vocab")
listDict = sorted(c.fetchall(), key=polish_sort_key)
for i in range(len(listDict)):
    dictDial.insert("", END, values=listDict[i])

# Реалізувати в таблиці смуги прокрутки
dictDial.grid(row=3, column=0)
verscrlbar = ttk.Scrollbar(tabDict, orient="vertical", command=dictDial.yview)
verscrlbar.grid(row=3, column=5, sticky='ns')  # Adjust the row and column values as needed
dictDial.configure(yscrollcommand=verscrlbar.set)

# Створити обробник для реакції на зміну обраної користувачем комірки в таблиці
def selectWord(event):
    selectedItem = dictDial.focus()
    itemData = dictDial.item(selectedItem, "values")
    labelDict.config(text=f"{itemData[2]} — {itemData[3]}")
dictDial.bind("<<TreeviewSelect>>", selectWord)

# Створити обробник спадного списку з SQL-запитом:
# після зміни обраного варіанту таблиця очищується, і до неї завантажуються лише слова, що належать до обраної категорії
def load_words_for_dialect(event):
    selectedDial = comboDict.get()
    dictDial.delete(*dictDial.get_children())

    c.execute("SELECT id, dialect, pol, ukr FROM vocab WHERE dialect=?", (selectedDial,))
    listDict = sorted(c.fetchall(), key=polish_sort_key)
    for i in range(len(listDict)):
        dictDial.insert("", END, values=listDict[i])
        
comboDict.bind("<<ComboboxSelected>>", load_words_for_dialect)

window.mainloop()
