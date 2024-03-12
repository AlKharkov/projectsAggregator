import csv
import os

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

TIME_TO_WAIT = 1.5
NUMBER_OF_POSSIBLE_GAPS = 16


def text_by_xpath(xpath):
    global driver
    try:
        return WebDriverWait(driver, TIME_TO_WAIT).until(
            ec.presence_of_element_located((By.XPATH, xpath))).text.replace('\n', ' ')
    except TimeoutException:
        return ''


def list_by_xpath(xpath, f=lambda x: x.text):
    global driver
    try:
        return (list(
            map(f, WebDriverWait(driver, TIME_TO_WAIT).until(ec.presence_of_all_elements_located((By.XPATH, xpath))))))
    except TimeoutException:
        return list()


if __name__ == '__main__':
    driver = webdriver.Chrome()

    if not os.path.isdir('output'):
        os.mkdir('output')

    index_page = 1
    current_gaps = 0

    with open('output/cards.csv', 'w', encoding='UTF-8', newline='') as csvfile:
        fieldnames = ['Название проекта', 'Статус', 'Тэги', 'Описание', 'Проблема/потребность', 'Цель', 'Задачи',
                      'Контур употребления', 'Материалы проекта', 'Команда проекта']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        writer.writeheader()

        while current_gaps <= NUMBER_OF_POSSIBLE_GAPS:
            driver.get(f'https://projects.mmf.nsu.ru/project/{index_page}')
            try:
                WebDriverWait(driver, TIME_TO_WAIT).until(
                    ec.presence_of_element_located((By.XPATH, '//*[@id="page-wrap"]/div[1]/div[1]/h1')))
                current_gaps = 0
                name = text_by_xpath('//*[@id="page-wrap"]/div[1]/div[1]/h1')
                status = text_by_xpath('//*[@id="page-wrap"]/div[1]/div[1]/div/div[2]/div')
                tags = list_by_xpath('//*[@id="page-wrap"]/div[1]/div[2]/div/div[2]')  # unnecessary
                description = text_by_xpath('//*[@id="page-wrap"]/div[1]/div[3]/div[1]/div[1]')
                problem = text_by_xpath('//*[@id="page-wrap"]/div[1]/div[3]/div[1]/div[2]/div[2]')
                goal = text_by_xpath('//*[@id="page-wrap"]/div[1]/div[3]/div[1]/div[3]/div[2]')  # unnecessary
                tasks = list_by_xpath('//*[@id="page-wrap"]/div[1]/div[3]/div[1]/div[4]/div[2]/ol/li')
                target_audience = text_by_xpath('//*[@id="page-wrap"]/div[1]/div[3]/div[1]/div[5]/div[2]')
                materials = list_by_xpath('//*[@id="page-wrap"]/div[1]/div[3]/div[1]/div[6]/div[2]/div/a',
                                          lambda x: x.get_attribute('href'))  # unnecessary
                number_of_members = text_by_xpath('//*[@id="page-wrap"]/div[1]/div[3]/div[2]/div[1]/div[1]/div')
                members = list_by_xpath(
                    '//*[@id="page-wrap"]/div[1]/div[3]/div[2]/div[1]/div[2]/div/div[1]/div[2]/div[1]')  # unnecessary
                recruitment = text_by_xpath('//*[@id="page-wrap"]/div[1]/div[3]/div[2]/div[2]')

                row = {fieldnames[i]: x for i, x in zip(range(10),
                                                        [name, status, ', '.join(tags), description, problem, goal,
                                                         ' '.join(tasks), target_audience, ', '.join(materials),
                                                         number_of_members, ', '.join(members), recruitment])}
                writer.writerow(row)
                with open(f'output/{index_page}.txt', 'w', encoding='UTF-8') as out_file:
                    for e in row.items():
                        out_file.write(f'{e[0]}: {e[1]}\n')
            except TimeoutException:
                current_gaps += 1
            index_page += 1
        driver.quit()
