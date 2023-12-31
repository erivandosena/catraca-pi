#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests

from requests.exceptions import Timeout
from requests.exceptions import HTTPError
from requests.exceptions import TooManyRedirects
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError

from catraca.logs import Logs
from catraca.modelo.dados.servidor_restful import ServidorRestful
from catraca.modelo.dao.unidade_dao import UnidadeDAO
from catraca.modelo.entidades.unidade import Unidade


__author__ = "Erivando Sena" 
__copyright__ = "Copyright 2015, © 09/02/2015" 
__email__ = "erivandoramos@bol.com.br" 
__status__ = "Prototype"


class UnidadeJson(ServidorRestful):
    
    log = Logs()
    unidade_dao = UnidadeDAO()
    
    def __init__(self):
        super(UnidadeJson, self).__init__()
        ServidorRestful.__init__(self)
        
    def unidade_get(self, limpa_tabela=False):
        servidor = self.obter_servidor()
        try:
            if servidor:
                url = str(self.URL) + "unidade/junidade"
                r = servidor.get(url)
                print url
                if r.text != '':
                    dados  = json.loads(r.text)
                    LISTA_JSON = dados["unidades"]
                    if LISTA_JSON != []:
                        if limpa_tabela:
                            return self.mantem_tabela_local(None, True)
                        lista = []
                        for item in LISTA_JSON:
                            obj = self.dict_obj(item)
                            if obj:
                                lista.append(obj)
                                self.mantem_tabela_local(obj)
                        return lista
                else:
                    return None
        except Timeout:
            self.log.logger.error("Timeout", exc_info=True)
        except HTTPError:
            self.log.logger.error("HTTPError", exc_info=True)
        except TooManyRedirects:
            self.log.logger.error("TooManyRedirects", exc_info=True)
        except RequestException:
            self.log.logger.error("RequestException", exc_info=True)
        except ConnectionError:
            self.log.logger.error("ConnectionError", exc_info=True)
        except Exception:
            self.log.logger.error("Exception", exc_info=True)
            
    def mantem_tabela_local(self, obj, mantem_tabela=False):
        if obj:
            objeto = self.unidade_dao.busca(obj.id)
            if not mantem_tabela:
                if objeto:
                    if not objeto.__eq__(obj):
                        return self.atualiza_exclui(obj, mantem_tabela)
                    else:
                        #print "[UNIDADE]Acao de atualizacao nao necessaria!"
                        return None
                else:
                    return self.insere(obj)
            else:
                if objeto:
                    return self.atualiza_exclui(obj, mantem_tabela)
        else:
            if mantem_tabela:
                return self.atualiza_exclui(obj, mantem_tabela)
            else:
                print "Nemhuma acao realizada!"
                return None

            
    def atualiza_exclui(self, obj, boleano):
        if self.unidade_dao.atualiza_exclui(obj, boleano):
            print self.unidade_dao.aviso
            if not boleano:
                return obj
            else:
                return None
            
    def insere(self, obj):
        if self.unidade_dao.insere(obj):
            print self.unidade_dao.aviso
            return obj
        
    def dict_obj(self, formato_json):
        unidade = Unidade()
        if isinstance(formato_json, list):
            formato_json = [self.dict_obj(x) for x in formato_json]
        if not isinstance(formato_json, dict):
            return formato_json
        for item in formato_json:
            
            if item == "unid_id":
                unidade.id = self.dict_obj(formato_json[item])
            if item == "unid_nome":
                unidade.nome = self.dict_obj(formato_json[item]) if self.dict_obj(formato_json[item]) is None else self.dict_obj(formato_json[item]).encode('utf-8')
                
        return unidade
    