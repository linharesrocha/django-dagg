from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
import platform

df_nutri = pd.read_excel('nutricionistas_bh_crn9.org.br.xlsx')

    
if platform.system() == 'Linux':
    webdriver_path = 'chromedriver'
elif platform.system() == 'Windows':
    webdriver_path = 'C:\workspace\django-dagg\mercado\scripts\chromedriver.exe'

service = Service(webdriver_path)
options = Options()
options.add_argument('--user-data-dir=C:\\Users\\FAT-01\\AppData\\Local\\Google\\Chrome\\User Data')
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()
wait=WebDriverWait(driver, 30)


for index, row in df_nutri.iterrows():
    name = str(row['nome'])
    name_contact = name.split(' ')[0]
    name_contact = name_contact.title()
    contact_number = str(row['numero'])
    contact_number = f'55' + contact_number
    
    print(f'{index+1}/{str(len(df_nutri))} - {name_contact} - {contact_number}')

    default_message = f'''
    Olá {name_contact}! Espero que essa mensagem te encontre bem!
    Sou Helena Santos, trabalho na Dagg, empresa dedicada ao bem-estar e qualidade de vida. Ficamos interessados com seu trabalho como profissional de nutrição e gostaríamos de saber se você tem interesse em uma parceria conosco. Temos uma variedade de produtos voltados para a saúde e atividades físicas, e acreditamos que juntos podemos incentivar e ajudar ainda mais pessoas nessa jornada
    Segue um PDF com informações sobre os benefícios para a parceria
    Ficaremos animados em saber sua opinião sobre essa possibilidade. Aguardamos sua resposta! #EquipeDagg
    A fim de proporcionar uma melhor compreensão sobre a nossa marca e os nossos produtos, recomendamos que você visite nosso site: www.dagg.com.br. Além disso, também convidamos você a explorar nossa página no Instagram: @daggsport. :blush
    '''

    # path file
    path_file_to_send = "C:\\Users\\FAT-01\\Downloads\\PROGRAMA_RELACIONAMENTO_NUTRICIONISTAS.pdf"

    link_message = f'https://wa.me/{contact_number}'

    # Whatsapp Web
    driver.get(link_message)

    # Enter web
    wait.until(EC.element_to_be_clickable((By.ID, 'action-button'))).click()

    # Confirm web
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fallback_block"]/div/div/h4[2]/a/span'))).click()

    try:
        # Chat
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '_3Uu1_'))).send_keys(default_message + Keys.ENTER)

        # Clip
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[data-testid="clip"]'))).click()

        # load pdf
        driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/div/ul/li[4]/button/input').send_keys(path_file_to_send)

        # Send pdf
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[data-testid="send"]'))).click()
        sleep(5)
    except:
        pass