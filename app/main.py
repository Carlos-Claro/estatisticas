# -*- coding: utf-8 -*-
import requests
import datetime
import time
import os
import sys
import json

class Estatisticas(object):
    
    def __init__(self):
        if 'localhost' in sys.argv:
            self.localhost = True
            self.URI = 'http://localhost:5000/'
        else:
            self.localhost = False
            self.URI = 'http://imoveis.powempresas.com/'
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
        itens = requests.get(self.URL_GET,params=g)
        if itens.status_code == 200:
            i = itens.json()
            for k,v in i.items():
                post = json.dumps(self.get_data(k,v,data))
                print(post)
                res = requests.post(self.URL_POST_LOG_EMPRESA,json=post)
                del post
                del res
        
    def roda_imovel_dia(self, dias):
        data = self.get_dia(dias)
        g = {'dias':dias}
        itens = requests.get(self.URL_GET_IMOVEIS,params=g)
        if itens.status_code == 200:
            imoveis = itens.json()
            for chave,valor in imoveis.items():
                print(valor)
                ga = {'dias':dias,'id_imovel':chave}
                i = requests.get(self.URL_GET_IMOVEIS_B,params=ga)
                tipos = i.json()
                imovel = tipos
                imovel['id_imovel'] = int(chave)
                imovel['data'] = self.get_dia(dias)
                imovel['total_acessos'] = valor
                print(imovel)
                res = requests.post(self.URL_POST_LOG_IMOVEL,json=json.dumps(imovel))
                del imovel
                #exit()
                #for k,v in i.items():
                #    post = json.dumps(self.get_data_imovel(k,v,data))
                #    print(post)
    
    def imovel(self):
        get_data = requests.get(self.URL_GET_IMOVEIS_MIN)
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
        
    def empresa(self):
        get_data = requests.get(self.URL_GET_DATA_MAX)
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
        print(self.fim-self.inicio)
    
if __name__ == '__main__':
    Estatisticas()
