#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
from catraca.logs import Logs
from catraca.visao.restful.servidor_restful import ServidorRestful
from catraca.modelo.dao.isencao_dao import IsencaoDAO
from catraca.modelo.entidades.isencao import Isencao


__author__ = "Erivando Sena" 
__copyright__ = "(C) Copyright 2015, Unilab" 
__email__ = "erivandoramos@unilab.edu.br" 
__status__ = "Prototype" # Prototype | Development | Production 


class IsencaoJson(ServidorRestful):
    
    log = Logs()
    isencao_dao = IsencaoDAO()
    
    def __init__(self, ):
        super(IsencaoJson, self).__init__()
        ServidorRestful.__init__(self)
        
    def isencao_get(self):
        url = self.obter_servidor() + "isencao/jisencao"
        header = {'Content-type': 'application/json'}
        r = requests.get(url, auth=(self.isencao, self.senha), headers=header)
        print "status HTTP: " + str(r.status_code)
        dados  = json.loads(r.text)
        
        for item in dados["isencaos"]:
            obj = self.dict_obj(item)
            if obj.id:
                lista = self.isencao_dao.busca(obj.id)
                if lista is None:
                    print "nao existe - insert " + str(obj.nome)
                    self.isencao_dao.insere(obj)
                    print self.isencao_dao.aviso
                else:
                    print "existe - update " + str(obj.nome)
                    self.isencao_dao.atualiza_exclui(obj, False)
                    print self.isencao_dao.aviso
        
    def dict_obj(self, formato_json):
        isencao = Isencao()
        if isinstance(formato_json, list):
            formato_json = [self.dict_obj(x) for x in formato_json]
        if not isinstance(formato_json, dict):
            return formato_json
        for item in formato_json:
            
            if item == "isen_id":
                isencao.id = self.dict_obj(formato_json[item])
            if item == "isen_inicio":
                isencao.inicio = self.dict_obj(formato_json[item])
            if item == "isen_fim":
                isencao.fim = self.dict_obj(formato_json[item])
            if item == "cart_id":
                isencao.cartao = self.dict_obj(formato_json[item])
                
        return isencao
    