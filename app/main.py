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
        self.URL_GET = self.URI + 'log_imoveis/'
        self.URL_POST_LOG_EMPRESA = self.URI + 'log_imoveis/'
        
    def get_dia(self,dias):
        da = datetime.datetime.now() - datetime.timedelta(days=int(dias))
        y = int(da.strftime('%Y'))
        m = int(da.strftime('%m'))
        d = int(da.strftime('%d'))
        return datetime.datetime(y,m,d,0,0).isoformat()
        
    def get_data(self, chave, valor, data):
        add = {}
        add['data'] = data
        add['id_empresa'] = chave
        add['total_acessos'] = valor['total_empresa']
        del(valor['total_empresa'])
        for ke,va in valor.items():
            add[ke] = {}
            add[ke]['total'] = va['total']
            add[ke]['imoveis'] = va['imoveis']
        return add
        
    
    def roda_dia(self, dias):
        data = self.get_dia(dias)
        g = {'dias':dias}
        itens = requests.get(self.URL_GET,params=g)
        if itens.status_code == 200:
            i = itens.json()
            for k,v in i.items():
                post = json.dumps(self.get_data(k,v,data))
                print(post)
                res = requests.post(self.URL_POST_LOG_EMPRESA,json=post)
                print(res.status_code)
                exit()
        #print(i)
        self.fim = time.time()
        print(self.fim-self.inicio)
        
        
    def main(self):
        dias = 1
        self.roda_dia(dias)
    
if __name__ == '__main__':
    Estatisticas().main()