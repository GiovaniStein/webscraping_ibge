import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

main_url = 'https://cidades.ibge.gov.br/'

option = Options()
option.headless = True

# O geckodriver.exe deve estar no mesmo diretório deste arquivo para funcionar
# driver = webdriver.Chrome('chromedriver.exe', options=option)
driver = webdriver.Chrome('chromedriver.exe')

# Se instanciar o driver sem passar parametros, é possivel ver o navegador executando os comandos em tempo real
# driver = webdriver.Firefox()

driver.get(main_url)

action = ActionChains(driver)

values = []


def get_links():
    div_main = driver.find_element_by_tag_name("aside")
    # Simular evento de mouse over
    action.move_to_element(div_main).perform()

    button = driver.find_element_by_xpath("//button[. = 'Selecionar local']")

    driver.execute_script("arguments[0].click();", button)

    menu = driver.find_element_by_id("menu__municipio")

    driver.execute_script("arguments[0].click();", menu)

    div = driver.find_element_by_id("segunda-coluna")

    ul = div.find_element_by_tag_name("ul")

    # estados = ul.text.split('\n')

    # estados.remove('Todos')

    # Faltou: Bahia
    estados = ['Ceará']

    for estado in estados:
        action.move_to_element(ul).click().perform()
        path = "//li[contains(., '{0}')]".format(estado)
        ul.find_element_by_xpath(path).click()
        div_municipios = driver.find_elements_by_class_name("conjunto")
        div_capital = driver.find_element_by_xpath("//div[@class='estado']")
        capital = div_capital.find_element_by_tag_name("a").get_attribute("href")
        values.append(capital)
        for element in div_municipios:
            tag_a = element.find_elements_by_tag_name("a")
            for el in tag_a:
                values.append(el.get_attribute("href"))
        print('foi url estado ' + estado)


def get_topo_values(municipio):
    div_topo = driver.find_element_by_class_name("topo")
    topo_values = div_topo.text.split('\n')
    if len(topo_values) != 6:
        municipio['Código do Município'] = ""
        municipio['Gentílico'] = ""
        municipio['Prefeito'] = ""
    else:
        municipio[topo_values[0]] = topo_values[1]
        municipio[topo_values[2]] = topo_values[3]
        municipio[topo_values[4]] = topo_values[5]


def get_table_values(municipio):
    table = driver.find_element_by_class_name("lista")
    tr_list = table.find_elements_by_class_name("lista__cabecalho")
    for tr in tr_list:
        if tr.get_attribute("class").find('recolhido') > 0:
            driver.execute_script("arguments[0].click();", tr)
        tr2 = list(filter(lambda x: (x.text != ''), table.find_elements_by_class_name("lista__indicador")))
        for li in tr2:
            text_name = li.find_element_by_class_name("lista__nome")
            value = li.find_element_by_class_name("lista__valor")
            municipio[text_name.text.strip()] = value.text.strip()



def get_information():
    with open('teste_ibge.csv', mode='w', newline='') as csv_file:
        contains_header = False
        for municipio_url in values:
            uf = municipio_url.split("/")[4].upper() if len(municipio_url.split("/")) > 5 else ''
            mu = municipio_url.split("/")[5] if len(municipio_url.split("/")) == 6 else ''
            municipio = {'UF': uf, 'Municipio': mu}
            driver.get(municipio_url)
            try:
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'topo__celula-esquerda'))
                WebDriverWait(driver, 1).until(element_present)
            except TimeoutException:
                print("Timed out waiting for page to load")
            finally:
                print("Page loaded")

            get_topo_values(municipio)
            get_table_values(municipio)
            if not contains_header:
                fieldnames = municipio.keys()
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                contains_header = True
            writer.writerow(municipio)
            print(municipio)


get_links()
get_information()
driver.quit()
