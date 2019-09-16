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
        self.URL_POST_LOG_EMPRESA = self.URI + 'log_empresa/'
        self.URL_GET_IMOVEIS = self.URI + 'log_imoveis/'
        self.URL_POST_LOG_IMOVEL = self.URI + 'log_imovel/'
        
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
        self.fim = time.time()
        print(self.fim-self.inicio)
        
    def roda_imovel_dia(self, dias):
        data = self.get_dia(dias)
        g = {'dias':dias}
        itens = requests.get(self.URL_GET_IMOVEIS,params=g)
        if itens.status_code == 200:
            i = itens.json()
            print(i)
            for k,v in i.items():
                post = json.dumps(self.get_data_imovel(k,v,data))
                print(post)
                #res = requests.post(self.URL_POST_LOG_EMPRESA,json=post)
        self.fim = time.time()
        print(self.fim-self.inicio)
        
        
    def main(self):
        
        self.roda_imovel_dia(90)
        #for x in range(365,181,-1):
        #    print(x)
    
if __name__ == '__main__':
    Estatisticas().main()