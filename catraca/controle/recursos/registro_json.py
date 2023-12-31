#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import datetime

from requests.exceptions import Timeout
from requests.exceptions import HTTPError
from requests.exceptions import TooManyRedirects
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError

from catraca.logs import Logs
from catraca.util import Util
from catraca.modelo.dados.servidor_restful import ServidorRestful
from catraca.modelo.dao.registro_dao import RegistroDAO
from catraca.modelo.entidades.registro import Registro
from catraca.modelo.dao.turno_dao import TurnoDAO
from catraca.controle.recursos.turno_json import TurnoJson
from catraca.modelo.dao.catraca_dao import CatracaDAO


__author__ = "Erivando Sena" 
__copyright__ = "Copyright 2015, © 09/02/2015" 
__email__ = "erivandoramos@bol.com.br" 
__status__ = "Prototype"


class RegistroJson(ServidorRestful):
    
    log = Logs()
    util = Util()
    turno_dao = TurnoDAO()
    registro_dao = RegistroDAO()

    hora_inicio = datetime.datetime.strptime('00:00:00','%H:%M:%S').time()
    hora_fim = datetime.datetime.strptime('00:00:00','%H:%M:%S').time()
    
    def __init__(self):
        super(RegistroJson, self).__init__()
        ServidorRestful.__init__(self)
        
    def registro_get(self, limpa_tabela=False):
        servidor = self.obter_servidor()
        try:
            turno = self.obtem_turno_valido()
            if turno:
                data_atual = str(self.util.obtem_datahora().strftime("%Y%m%d"))
                self.hora_inicio = datetime.datetime.strptime(str(turno.inicio),'%H:%M:%S').time().strftime('%H%M%S')
                self.hora_fim = datetime.datetime.strptime(str(turno.fim),'%H:%M:%S').time().strftime('%H%M%S')
                if servidor:
                    url = str(self.URL) + "registro/jregistro/" + str(data_atual+str(self.hora_inicio)) + "/" +str(data_atual+str(self.hora_fim))
                    r = servidor.get(url)
                    if r.text != '':
                        dados  = json.loads(r.text)
                        LISTA_JSON = dados["registros"]
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
            
    def registro_utilizacao_get(self, hora_ini, hora_fim, cartao_id):
        data_atual = str(self.util.obtem_datahora().strftime("%Y%m%d"))
        self.hora_inicio = datetime.datetime.strptime(str(hora_ini),'%H:%M:%S').time().strftime('%H%M%S')
        self.hora_fim = datetime.datetime.strptime(str(hora_fim),'%H:%M:%S').time().strftime('%H%M%S')
        servidor = self.obter_servidor()
        try:
            if servidor:
                url = str(self.URL) + "registro/jregistro/" +str(data_atual+self.hora_inicio) + "/" +str(data_atual+self.hora_fim)+ "/" +str(cartao_id)
                r = servidor.get(url)
                if r.text != '':
                    dados  = json.loads(r.text)
                    LISTA_JSON = dados["quantidade"]
                    if LISTA_JSON != []:
                        for item in LISTA_JSON:
                            obj = self.dict_obj_utilizacao(item)
                            if obj:
                                return int(obj)
                            else:
                                return 0
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
            objeto = self.registro_dao.busca(obj.id)
            if not mantem_tabela:
                if objeto:
                    if not objeto.__eq__(obj):
                        return self.atualiza_exclui(obj, mantem_tabela)
                    else:
                        #print "[REGISTRO]Acao de atualizacao nao necessaria!"
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
        if self.registro_dao.atualiza_exclui(obj, boleano):
            print self.registro_dao.aviso
            if not boleano:
                return obj
            else:
                return None
            
    def insere(self, obj):
        if self.registro_dao.insere(obj):
            print self.registro_dao.aviso
            return obj
        
    def dict_obj(self, formato_json):
        registro = Registro()
        if isinstance(formato_json, list):
            formato_json = [self.dict_obj(x) for x in formato_json]
        if not isinstance(formato_json, dict):
            return formato_json
        for item in formato_json:
            if item == "cart_id":
                registro.cartao = self.dict_obj(formato_json[item])
            if item == "catr_id":
                registro.catraca = self.dict_obj(formato_json[item])
            if item == "regi_valor_custo":
                registro.custo = self.dict_obj(formato_json[item])
            if item == "regi_id":
                registro.id = self.dict_obj(formato_json[item])
            if item == "regi_data":
                registro.data = self.dict_obj(formato_json[item])
            if item == "regi_valor_pago":
                registro.pago = self.dict_obj(formato_json[item])
            if item == "vinc_id":
                registro.vinculo = self.dict_obj(formato_json[item])
        return registro
    
    def dict_obj_utilizacao(self, formato_json):
        utilizado = None
        if isinstance(formato_json, list):
            formato_json = [self.dict_obj_utilizacao(x) for x in formato_json]
        if not isinstance(formato_json, dict):
            return formato_json
        for item in formato_json:
            if item == "total":
                utilizado = self.dict_obj_utilizacao(formato_json[item])
        return utilizado
    
    def lista_json(self, lista):
        if lista:
            for item in lista:
                registro = {
                    "cart_id":item[1],
                    "catr_id":item[2], 
                    "regi_valor_custo":float(item[3]),
                    "regi_data":str(item[4]),
                    "regi_valor_pago":float(item[5]),
                    "vinc_id":item[6]
                }
                return self.registro_post(registro)

    def objeto_json(self, obj):
        if obj:
            registro = {
                "cart_id":obj.cartao,
                "catr_id":obj.catraca, 
                "regi_valor_custo":float(obj.custo),
                "regi_data":str(obj.data),
                "regi_valor_pago":float(obj.pago),
                "vinc_id":obj.vinculo
            }
            return self.registro_post(registro)
            
    def registro_post(self, formato_json):
        servidor = self.obter_servidor()
        try:
            if servidor:
                url = str(self.URL) + "registro/insere"
                r = servidor.post(url, data=json.dumps(formato_json))
                return r.status_code
            else:
                return 0
        except Timeout:
            self.log.logger.error("Timeout", exc_info=True)
            return 0
        except HTTPError:
            self.log.logger.error("HTTPError", exc_info=True)
            return 0
        except TooManyRedirects:
            self.log.logger.error("TooManyRedirects", exc_info=True)
            return 0
        except RequestException:
            self.log.logger.error("RequestException", exc_info=True)
            return 0
        except ConnectionError:
            self.log.logger.error("ConnectionError", exc_info=True)
            return 0
        except Exception:
            self.log.logger.error("Exception", exc_info=True)
            return 0
        
    def obtem_turno_valido(self):
        #remoto
        turno_ativo = TurnoJson().turno_funcionamento_get()
        if turno_ativo is None:
            #local
            turno_ativo = self.turno_dao.obtem_turno( CatracaDAO().busca_por_ip(self.util.obtem_ip_por_interface()), self.util.obtem_hora())
        if turno_ativo:
            return turno_ativo
        else:
            return None

        