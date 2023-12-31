#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json

from requests.exceptions import Timeout
from requests.exceptions import HTTPError
from requests.exceptions import TooManyRedirects
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError

from catraca.logs import Logs
from catraca.util import Util
from catraca.visao.interface.aviso import Aviso
from catraca.modelo.dados.servidor_restful import ServidorRestful
from catraca.modelo.dao.catraca_dao import CatracaDAO
from catraca.modelo.entidades.catraca import Catraca


__author__ = "Erivando Sena" 
__copyright__ = "Copyright 2015, © 09/02/2015" 
__email__ = "erivandoramos@bol.com.br" 
__status__ = "Prototype"


class CatracaJson(ServidorRestful):
    
    log = Logs()
    aviso = Aviso()
    catraca_dao = CatracaDAO()
    contador_acesso_servidor = 0
    util = Util()
    
    def __init__(self):
        super(CatracaJson, self).__init__()
        ServidorRestful.__init__(self)
        
    def catraca_get(self, limpa_tabela=False):
        servidor = self.obter_servidor()
        try:
            if servidor:
                url = str(self.URL) + "catraca/jcatraca"
                print url
                r = servidor.get(url)
                if r.text != '':
                    dados  = json.loads(r.text)
                    LISTA_JSON = dados["catracas"]
                    if LISTA_JSON != []:
                        if limpa_tabela:
                            return self.mantem_tabela_local(None, True)
                        catraca_local = None
                        for item in LISTA_JSON:
                            obj = self.dict_obj(item)
                            if obj:
                                self.mantem_tabela_local(obj)
                                if obj.interface == 'eth0' or obj.interface == 'wlan0':
                                    if (self.util.obtem_nome_rpi().upper() == obj.nome.upper()):
                                        
                                        #print "catraca fisica local"
                                        catraca_local = obj
                                        ip_local = self.util.obtem_ip_por_interface(obj.interface.lower())
                                        mac_local = self.util.obtem_MAC_por_interface(obj.interface.lower())
                                        
                                        if ip_local != "127.0.0.1":
                                            
                                            if obj.ip != ip_local:
                                                 catraca_local.ip = ip_local
                                                 self.objeto_json(catraca_local, "PUT")
                                                 return self.catraca_get()

                                            if obj.interface.lower() == "eth0":
                                                if mac_local != obj.maclan:
                                                    catraca_local.maclan = mac_local
                                                    self.objeto_json(catraca_local, "PUT")
                                                    return self.catraca_get()
                                                       
                                            if obj.interface.lower() == "wlan0":
                                                if mac_local != obj.macwlan:
                                                    catraca_local.macwlan = mac_local
                                                    self.objeto_json(catraca_local, "PUT")
                                                    return self.catraca_get()
                                                
                                        if obj.nome.lower() != self.util.obtem_nome_rpi().lower():
                                            print "REINICIAR SISTEMA...."
                                            self.util.altera_hostname( self.util.obtem_string_normalizada( obj.nome.lower() ) )
                                            self.util.reinicia_raspberrypi()
                                            return self.aviso.exibir_reinicia_catraca()
                        if catraca_local is None:
                            print "catraca local ausente no remoto"
                            self.aviso.exibir_catraca_nao_cadastrada()
                            self.cadastra_catraca_remoto()
                            return self.catraca_get()
                        else:
                            return catraca_local
                    else:
                        return None
        except Timeout:
            self.log.logger.error("Timeout", exc_info=True)
            return None
        except HTTPError:
            self.log.logger.error("HTTPError", exc_info=True)
            return None
        except TooManyRedirects:
            self.log.logger.error("TooManyRedirects", exc_info=True)
            return None
        except RequestException:
            self.log.logger.error("RequestException", exc_info=True)
            return None
        except ConnectionError:
            self.log.logger.error("ConnectionError", exc_info=True)
            return None
        except Exception:
            self.log.logger.error("Exception", exc_info=True)
            return None
        
    def mantem_tabela_local(self, obj, mantem_tabela=False):
        #se o obj existir
        if obj:
            # busca o objeto no banco local
            objeto = self.catraca_dao.busca(obj.id)
            #se mantem_tabela for false
            if not mantem_tabela:
                #se o objeto existir
                if objeto:
                    #print "CATRACA EXISTE"
                    # se o objeto for diferente de obj
                    if not objeto.__eq__(obj):
                        #atualiza o objeto
                        return self.atualiza_exclui(obj, mantem_tabela)
                    # se o objeto for igual ao obj
                    else:
                        #nao faz nada
                        #print "[CATRACA]Acao de atualizacao nao necessaria!"
                        return None
                #se o objeto nao existir
                else:
                    print "CATRACA NAO EXISTE"
                     #insere novo obj
                    return self.insere(obj)
            #se mantem_tabela for True
            else:
                #se o objeto existir
                if objeto:
                    #exclui o objeto
                    return self.atualiza_exclui(obj, mantem_tabela)
        #se o obj nao existir
        else:
            #se mantem_tabela for true
            if mantem_tabela:
                #limpa todos os registros da tabela
                return self.atualiza_exclui(obj, mantem_tabela)
            #se mantem_tabela for false
            else:
                #nao faz nada
                print "Nemhuma acao realizada!"
                return None
            
    def atualiza_exclui(self, obj, boleano):
        if self.catraca_dao.atualiza_exclui(obj, boleano):
            print self.catraca_dao.aviso
            if not boleano:
                return obj
            else:
                return None
        
    def insere(self, obj):
        if self.catraca_dao.insere(obj):
            print self.catraca_dao.aviso
            return obj
        
    def dict_obj(self, formato_json):
        catraca = Catraca()
        if isinstance(formato_json, list):
            formato_json = [self.dict_obj(x) for x in formato_json]
        if not isinstance(formato_json, dict):
            return formato_json
        for item in formato_json:
            
            if item == "catr_id":
                catraca.id = self.dict_obj(formato_json[item])
            if item == "catr_ip":
                catraca.ip = self.dict_obj(formato_json[item])
            if item == "catr_tempo_giro":
                catraca.tempo = self.dict_obj(formato_json[item])
            if item == "catr_operacao":
                catraca.operacao = self.dict_obj(formato_json[item])
            if item == "catr_nome":
                catraca.nome = self.dict_obj(formato_json[item]) if self.dict_obj(formato_json[item]) is None else self.dict_obj(formato_json[item]).encode('utf-8')
            if item == "catr_mac_lan":
                catraca.maclan = self.dict_obj(formato_json[item]) if self.dict_obj(formato_json[item]) is None else self.dict_obj(formato_json[item]).encode('utf-8')
            if item == "catr_mac_wlan":
                catraca.macwlan = self.dict_obj(formato_json[item]) if self.dict_obj(formato_json[item]) is None else self.dict_obj(formato_json[item]).encode('utf-8')
            if item == "catr_interface_rede":
                catraca.interface = self.dict_obj(formato_json[item]) if self.dict_obj(formato_json[item]) is None else self.dict_obj(formato_json[item]).encode('utf-8')
            if item == "catr_financeiro":
                catraca.financeiro = self.dict_obj(formato_json[item])
        return catraca
    
    def lista_json(self, lista):
        if lista:
            for item in lista:
                catraca = {
                    "catr_ip":str(item[1]),
                    "catr_tempo_giro":item[2],
                    "catr_operacao":item[3],
                    "catr_nome":str(item[4]),
                    "catr_mac_lan":str(item[5]),
                    "catr_mac_wlan":str(item[6]),
                    "catr_interface_rede":str(item[7]),
                    "catr_financeiro":str(item[8])
                }
                return self.catraca_post(catraca)
                
    def objeto_json(self, obj, operacao="POST"):
        if obj:
            catraca = {
                "catr_ip":str(obj.ip),
                "catr_tempo_giro":obj.tempo,
                "catr_operacao":obj.operacao,
                "catr_nome":str(obj.nome),
                "catr_mac_lan":str(obj.maclan),
                "catr_mac_wlan":str(obj.macwlan),
                "catr_interface_rede":str(obj.interface),
                "catr_financeiro":str(obj.financeiro)
            }
            if operacao == "POST":
                return self.catraca_post(catraca)
            if operacao == "PUT":
                return self.catraca_put(catraca, obj.id)
                
    def catraca_post(self, formato_json):
        servidor = self.obter_servidor()
        try:
            if servidor:
                url = str(self.URL) + "catraca/insere"
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
        
    def catraca_put(self, formato_json, id):
        servidor = self.obter_servidor()
        try:
            if servidor:
                url = str(self.URL) + "catraca/atualiza/"+ str(id)
                r = servidor.put(url, data=json.dumps(formato_json))
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
        
    def cadastra_catraca_remoto(self):
        interface_padrao = "eth0"
        catraca = Catraca()
        catraca.ip = self.util.obtem_ip_por_interface(interface_padrao)
        catraca.tempo = 20
        catraca.operacao = 1
        catraca.nome = self.util.obtem_nome_rpi().upper()
        catraca.maclan = self.util.obtem_MAC_por_interface('eth0')
        catraca.macwlan = self.util.obtem_MAC_por_interface('wlan0')
        catraca.interface = interface_padrao
        catraca.financeiro = False
        return self.objeto_json(catraca)
        