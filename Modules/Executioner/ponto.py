import datetime
import os
import time

import requests, pickle
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import easygui
from dotenv import load_dotenv

def bater_ponto(login,senha, console):
    if login is None or senha is None:
       return False




    ua = UserAgent(os='windows')
    userAgent = ua.chrome
    print(userAgent)


    options = Options()
    options.add_argument('--headless')
    #options.add_experimental_option("detach", True)
    options.add_argument(f'user-agent={userAgent}')

    driver = webdriver.Chrome(options=options)
    driver.get("https://sigrh.uffs.edu.br/")
    driver.maximize_window()
    try:
        username = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, "login")))
        password = driver.find_element(By.ID, "senha")
        username.send_keys(login)
        password.send_keys(senha)
        WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, "logar"))).click()
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Frequência')]"))).click()
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Ponto Eletrônico')]"))).click()
        WebDriverWait(driver, 4).until(EC.presence_of_element_located(
            (By.XPATH, "//td[contains(text(), 'Registro de horário de trabalho')]"))).click()
        try:
            # WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, "idFormDadosEntradaSaida:idBtnRegistrarEntrada"))).click()
            console.log(f"Registered at work at {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        except TimeoutException:
            # WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, "idFormDadosEntradaSaida:idBtnRegistrarSaida"))).click()
            console.log(f"Failed registry at work at {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        return True
    except TimeoutException:
        print("Took to much time to find element.")
    except Exception as e:
        easygui.textbox(str(e), "Erro detectado:")
