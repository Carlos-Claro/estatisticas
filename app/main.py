# -*- coding: utf-8 -*-
import requests
import datetime
import time
import os
import sys
import json
from requests.auth import HTTPBasicAuth

class Estatisticas(object):

    def __init__(self):
        if 'localhost' in sys.argv:
            self.localhost = True
            self.URI = 'http://localhost:5000/'
        else:
            self.localhost = False
            self.URI = 'http://imoveis.powempresas.com/'
        with open('/var/www/json/keys.json') as json_file:
            data = json.load(json_file)
        self.user = data['basic']['user']
        self.passwd = data['basic']['passwd']
        self.auth = HTTPBasicAuth(self.user,self.passwd)
        self.inicio = time.time()
        self.URL_GET = self.URI + 'log_empresas/'
        self.URL_GET_DATA_MIN = self.URI + 'log_empresa_min_data/'
        self.URL_GET_DATA_MAX = self.URI + 'log_empresa_max_data/'
        self.URL_POST_LOG_EMPRESA = self.URI + 'log_empresa/'
        self.URL_GET_IMOVEIS = self.URI + 'log_imoveis/'
        self.URL_GET_IMOVEIS_MIN = self.URI + 'log_imovel_min_data/'
        self.URL_GET_IMOVEIS_MAX = self.URI + 'log_imovel_max_data/'
        self.URL_GET_IMOVEIS_B = self.URI + 'log_imoveis_b/'
        self.URL_POST_LOG_IMOVEL = self.URI + 'log_imovel/'
        self.ARQUIVO_LOG = '/var/log/sistema/estatisticas.log'
        self.FORMATO_LOG_UNITARIO = '{data} - status_code {status_code} - empresa {idEmpresa} - total {total} - dataLog {dataLog} - funcao: {acao} - tempo: {tempo} '
        self.FORMATO_LOG_TOTAL = '{data} - status_code: {status_code} - funcao: {acao} - tempo: {tempo} '
        if 'imovel' in sys.argv:
            self.imovel()
        else:
            self.empresa()

    def get_dia(self,dias):
        da = datetime.datetime.now() - datetime.timedelta(days=int(dias))
        retorno = []
        retorno.append(da.strftime('%Y'))
        retorno.append(da.strftime('%m'))
        retorno.append(da.strftime('%d'))
        y = int(da.strftime('%Y'))
        m = int(da.strftime('%m'))
        d = int(da.strftime('%d'))
        return retorno
        #return datetime.datetime(y,m,d,0,0)


    def get_data(self, chave, valor, data):
        add = {}
        add['data'] = data
        add['id_empresa'] = int(chave)
        add['total_acessos'] = valor['total_empresa']
        del(valor['total_empresa'])
        for ke,va in valor.items():
            add[ke] = {}
            add[ke]['total'] = va['total']
            add[ke]['imoveis'] = va['imoveis']
        return add

    def get_data_imovel(self, chave, valor, data):
        add = {}
        add['data'] = data
        add['id_imovel'] = int(chave)
        add['total_acessos'] = valor['total_imovel']
        del(valor['total_imovel'])
        return add


    def roda_empresa_dia(self, dias):
        data = self.get_dia(dias)
        g = {'dias':dias}
        itens = requests.get(self.URL_GET,params=g, auth=self.auth)
        if itens.status_code == 200:
            i = itens.json()
            for k,v in i.items():
                inicio = time.time()
                data_log_empresa = {
                    'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'acao': 'adiciona_empresa',
                    'total': v['total_empresa'],
                    'idEmpresa': k,
                    'dataLog': data
                }
                post = json.dumps(self.get_data(k,v,data))
                print(post)
                res = requests.post(self.URL_POST_LOG_EMPRESA,json=post, auth=self.auth)
                fim = time.time()
                data_log_empresa['tempo'] = fim - inicio
                data_log_empresa['status_code'] = res.status_code
                linha = self.FORMATO_LOG_UNITARIO.format(**data_log_empresa)
                with open(self.ARQUIVO_LOG, 'a') as arq:
                    arq.write(linha)
                    arq.write('\r\n')
                del post
                del res

    def roda_imovel_dia(self, dias):
        data = self.get_dia(dias)
        g = {'dias':dias}
        itens = requests.get(self.URL_GET_IMOVEIS,params=g, auth=self.auth)
        if itens.status_code == 200:
            imoveis = itens.json()
            for chave,valor in imoveis.items():
                print(valor)
                ga = {'dias':dias,'id_imovel':chave}
                i = requests.get(self.URL_GET_IMOVEIS_B,params=ga, auth=self.auth)
                tipos = i.json()
                imovel = tipos
                imovel['id_imovel'] = int(chave)
                imovel['data'] = self.get_dia(dias)
                imovel['total_acessos'] = valor
                print(imovel)
                res = requests.post(self.URL_POST_LOG_IMOVEL,json=json.dumps(imovel), auth=self.auth)
                del imovel
                #exit()
                #for k,v in i.items():
                #    post = json.dumps(self.get_data_imovel(k,v,data))
                #    print(post)

    def imovel_anterior(self):
        get_data = requests.get(self.URL_GET_IMOVEIS_MIN, auth=self.auth)
        if get_data.status_code == 200:
            data_min = get_data.json()
            date_time_str = data_min['itens'][0]['data']
            date_time_obj = datetime.datetime.strptime(str(date_time_str), "%Y-%m-%dT%H:%M:%SZ")
            data_menos = date_time_obj - datetime.timedelta(days=1)
            date_now = datetime.datetime.now()
            dias = data_menos.date() - date_now.date()
            d = str(abs(dias)).split(' ')
            di = int(d[0])
            for x in range(di,di+5,1):
                print(x)
                self.roda_imovel_dia(x)
        self.fim = time.time()
        print(self.fim-self.inicio)

    def imovel(self):
        get_data = requests.get(self.URL_GET_IMOVEIS_MAX, auth=self.auth)
        if get_data.status_code == 200:
            data_min = get_data.json()
            date_time_str = data_min['itens'][0]['data']
            date_time_obj = datetime.datetime.strptime(str(date_time_str), "%Y-%m-%dT%H:%M:%SZ")
            data_menos = date_time_obj + datetime.timedelta(days=1)
            date_now = datetime.datetime.now()
            print(data_menos.strftime('%Y-%m-%d'))
            print(date_now.strftime('%Y-%m-%d'))
            dias = data_menos.date() - date_now.date()
            d = str(abs(dias)).split(' ')
            di = int(d[0])
            for x in range(di,1,-1):
                print(x)
                self.roda_imovel_dia(x)
        self.fim = time.time()
        print(self.fim-self.inicio)

    def empresa(self):
        get_data = requests.get(self.URL_GET_DATA_MAX, auth=self.auth)
        data_log = {
            'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'acao': 'log_empresa_dia',
            'status_code': get_data.status_code
        }
        if get_data.status_code == 200:
            data_max = get_data.json()
            date_time_str = data_max['itens'][0]['data']
            print(date_time_str)
            date_time_obj = datetime.datetime.strptime(str(date_time_str), "%Y-%m-%dT%H:%M:%SZ")
            date_now = datetime.datetime.now()
            data_mais = date_time_obj + datetime.timedelta(days=1)
            print(data_mais.strftime('%Y-%m-%d'))
            print(date_now.strftime('%Y-%m-%d'))
            dias = data_mais.date() - date_now.date()
            d = str(abs(dias)).split(' ')
            print(d)
            for x in range(int(d[0]),1,-1):
                print(x)
                self.roda_empresa_dia(x)
        self.fim = time.time()
        data_log['tempo'] = self.fim-self.inicio
        linha = self.FORMATO_LOG_TOTAL.format(**data_log)
        with open(self.ARQUIVO_LOG, 'a') as arq:
            arq.write(linha)
            arq.write('\r\n')
    
if __name__ == '__main__':
    Estatisticas()
