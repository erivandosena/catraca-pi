#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
from catraca.logs import Logs
from catraca.modelo.dados.servidor_restful import ServidorRestful
from catraca.modelo.dao.giro_dao import GiroDAO
from catraca.modelo.entidades.giro import Giro


__author__ = "Erivando Sena" 
__copyright__ = "(C) Copyright 2015, Unilab" 
__email__ = "erivandoramos@unilab.edu.br" 
__status__ = "Prototype" # Prototype | Development | Production 


class GiroJson(ServidorRestful):
    
    log = Logs()
    giro_dao = GiroDAO()
    
    def __init__(self, ):
        super(GiroJson, self).__init__()
        ServidorRestful.__init__(self)
        
    def giro_get(self):
        servidor = self.obter_servidor()
        try:
            if servidor:
                url = str(servidor) + "giro/jgiro"
                header = {'Content-type': 'application/json'}
                r = requests.get(url, auth=(self.usuario, self.senha), headers=header)
                print "status HTTP:" + str(r.status_code)
                dados  = json.loads(r.text)
                
                if dados["giros"] is not []:
                    for item in dados["giros"]:
                        obj = self.dict_obj(item)
                        if obj.id:
                            lista = self.giro_dao.busca(obj.id)
                            if lista is None:
                                print "nao existe - insert " + str(obj.numero)
                                self.giro_dao.insere(obj)
                                self.giro_dao.commit()
                                print self.giro_dao.aviso
                            else:
                                print "existe - update " + str(obj.numero)
                                self.giro_dao.atualiza_exclui(obj, False)
                                self.giro_dao.commit()
                                print self.giro_dao.aviso
                if dados["giros"] == []:
                    self.giro_dao.atualiza_exclui(None,True)
                    print self.giro_dao.aviso
                    
        except Exception as excecao:
            print excecao
            self.log.logger.error('Erro obtendo json giro.', exc_info=True)
        finally:
            pass
        
    def dict_obj(self, formato_json):
        giro = Giro()
        if isinstance(formato_json, list):
            formato_json = [self.dict_obj(x) for x in formato_json]
        if not isinstance(formato_json, dict):
            return formato_json
        for item in formato_json:
            
            if item == "giro_id":
                giro.id = self.dict_obj(formato_json[item])
            if item == "giro_giros_horario":
                giro.horario = self.dict_obj(formato_json[item])
            if item == "giro_giros_antihorario":
                giro.antihorario = self.dict_obj(formato_json[item])
            if item == "giro_data_giros":
                giro.data = self.dict_obj(formato_json[item])
            if item == "catr_id":
                giro.catraca = self.dict_obj(formato_json[item])
                
        return giro
    