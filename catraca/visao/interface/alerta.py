#!/usr/bin/env python
# -*- coding: latin-1 -*-


import threading
from multiprocessing import Process
from time import sleep
from catraca.logs import Logs
from catraca.util import Util
from catraca.visao.interface.aviso import Aviso
from catraca.controle.dispositivos.solenoide import Solenoide
from catraca.controle.dispositivos.sensoroptico import SensorOptico
from catraca.controle.dispositivos.leitorcartao import LeitorCartao
from catraca.visao.interface.mensagem import Mensagem
from catraca.controle.restful.relogio import Relogio
from catraca.controle.restful.recursos_restful import RecursosRestful
from catraca.controle.dispositivos.pictograma import Pictograma


__author__ = "Erivando Sena" 
__copyright__ = "Copyright 2015, Unilab" 
__email__ = "erivandoramos@unilab.edu.br"
__status__ = "Prototype" # Prototype | Development | Production 


class Alerta(threading.Thread):
    
    log = Logs()
    util = Util()
    aviso = Aviso()
    solenoide = Solenoide()
    sensor_optico = SensorOptico()
    pictograma = Pictograma()
    status_alerta = False

    def __init__(self, intervalo=0.1):
        super(Alerta, self).__init__()
        threading.Thread.__init__(self)
        self.intervalo = intervalo
        self.name = 'Thread Alerta(Sonoro).'
        
    def run(self):
        print "%s Rodando... " % self.name
        mensagens = Mensagem()
        while True:
            catraca = Relogio.catraca
            while catraca is None:
                catraca = Relogio.catraca
                print "tentando obter catraca no alerta"
            # libera giro antihorario-livre quando nao houver leitura de cartao em andamento
            if not LeitorCartao.uso_do_cartao:
                
#                 if catraca.operacao == 1 or catraca.operacao == 2:
# #                     if self.sensor_optico.obtem_codigo_sensores() != "00" or self.sensor_optico.obtem_codigo_sensores() == "00":
# #                         if not self.solenoide.obtem_estado_solenoide(2):
# #                             self.solenoide.ativa_solenoide(2,1)
# #                             print "SOLENOIDE 02 ATIVADO"
# #                     if self.sensor_optico.obtem_codigo_sensores() == "01":
# #                         if not self.solenoide.obtem_estado_solenoide(1):
# #                             self.solenoide.ativa_solenoide(1,1)
# #                             print "SOLENOIDE 01 ATIVADO"

                if catraca.operacao == 1 or catraca.operacao == 2:
                    if self.sensor_optico.obtem_codigo_sensores() != "00":
                        if self.solenoide.obtem_estado_solenoide(2):
                            self.solenoide.ativa_solenoide(2,0)
                        if self.solenoide.obtem_estado_solenoide(1):
                            self.solenoide.ativa_solenoide(1,0)
                            
                if catraca.operacao == 3:
                    if not self.solenoide.obtem_estado_solenoide(2):
                        self.solenoide.ativa_solenoide(2,1)
                    if self.sensor_optico.obtem_codigo_sensores() == "01":
                        self.pictograma.xis(1)
                        self.pictograma.seta_direita(1)
                        self.verifica_giro_inverso(catraca)
                        
                if catraca.operacao == 4:
                    if not self.solenoide.obtem_estado_solenoide(1):
                        self.solenoide.ativa_solenoide(1,1)
                    if self.sensor_optico.obtem_codigo_sensores() == "10":
                        self.pictograma.xis(1)
                        self.pictograma.seta_esquerda(1)
                        self.verifica_giro_inverso(catraca)
                        
                if catraca.operacao == 5:
                    if self.sensor_optico.obtem_codigo_sensores() != "00":
                        if not self.solenoide.obtem_estado_solenoide(2):
                            self.solenoide.ativa_solenoide_individual(2,1)
                        if not self.solenoide.obtem_estado_solenoide(1):
                            self.solenoide.ativa_solenoide_individual(1,1)
                            
                        self.aviso.exibir_acesso_livre()    
                            
                        if self.sensor_optico.obtem_codigo_sensores() == "01":
                            self.pictograma.seta_direita(1)
                            while self.sensor_optico.detecta_giro_completo(self.sensor_optico.obtem_codigo_sensores()):
                                self.verifica_meio_giro()
                            self.pictograma.seta_direita(0)
                        if self.sensor_optico.obtem_codigo_sensores() == "10":
                            self.pictograma.seta_esquerda(1)
                            while self.sensor_optico.detecta_giro_completo(self.sensor_optico.obtem_codigo_sensores()):
                                self.verifica_meio_giro()
                            self.pictograma.seta_esquerda(0)
                            
            if catraca.operacao <= 0 or catraca.operacao >= 6:
                if self.sensor_optico.obtem_codigo_sensores() != "00":
                    if self.solenoide.obtem_estado_solenoide(2):
                        self.solenoide.ativa_solenoide(2,0)
                    if self.solenoide.obtem_estado_solenoide(1):
                        self.solenoide.ativa_solenoide(1,0)
                    self.aviso.exibir_bloqueio_total()
                        
            self.verifica_giro_irregular(catraca)

            if self.status_alerta:
                self.status_alerta = False
                self.aviso.exibir_aguarda_cartao()
                
            # trata exibicao de mensagens padroes quando nao houver turno ativo
            if not Relogio.periodo:
                # durante a leitura de um cartao
                if LeitorCartao.uso_do_cartao:
                    if mensagens.isAlive():
                        mensagens.join()
                else:
                    if not mensagens.isAlive():
                        mensagens = Mensagem()
                        mensagens.start()
                # durante a sincronizacao da catraca com o servidor RESTful
                if RecursosRestful.obtendo_recurso:
                    if mensagens.isAlive():
                        mensagens.join()
                else:
                    if not mensagens.isAlive():
                        mensagens = Mensagem()
                        mensagens.start()
            
            # trata exibicao de mensagens padroes quando nao houver tipo de giro definido ou giros livres opcao = 5
            if catraca.operacao == 5 or catraca.operacao <= 0 or catraca.operacao >= 6:
                # durante a leitura de um cartao
                if LeitorCartao.uso_do_cartao:
                    if mensagens.isAlive():
                        mensagens.join()
                else:
                    if not mensagens.isAlive():
                        mensagens = Mensagem()
                        mensagens.start()
            else:
                if mensagens.isAlive():
                    mensagens.join()
            
            sleep(self.intervalo)
            
    def verifica_giro_inverso(self, catraca):
        try:
            if catraca.operacao == 3 and self.pictograma.obtem_estado_pictograma('esquerda') == 0:
                self.aviso.exibir_acesso_liberado()
                if self.solenoide.obtem_estado_solenoide(2):
                    while self.sensor_optico.detecta_giro_completo(self.sensor_optico.obtem_codigo_sensores()):
                        self.verifica_meio_giro()
                    
            if catraca.operacao == 4 and self.pictograma.obtem_estado_pictograma('direita') == 0:
                self.aviso.exibir_acesso_liberado()
                if self.solenoide.obtem_estado_solenoide(1):
                    while self.sensor_optico.detecta_giro_completo(self.sensor_optico.obtem_codigo_sensores()):
                        self.verifica_meio_giro()
        finally:
            if self.solenoide.obtem_estado_solenoide(2):
                self.pictograma.seta_direita(0)
            if self.solenoide.obtem_estado_solenoide(1):
                self.pictograma.seta_esquerda(0)
                
            self.aviso.exibir_acesso_bloqueado()
            self.pictograma.xis(0)
                    
    def verifica_giro_irregular(self, catraca):
        try:
            if catraca.operacao == 1 or catraca.operacao == 2 or catraca.operacao <= 0 or catraca.operacao >= 6:
                while (self.sensor_optico.obtem_direcao_giro() == 'horario' and self.solenoide.obtem_estado_solenoide(1) == 0) or \
                       (self.sensor_optico.obtem_direcao_giro() == 'antihorario' and  self.solenoide.obtem_estado_solenoide(2) == 0):
                    if (self.sensor_optico.obtem_codigo_sensores() == "01") or (self.sensor_optico.obtem_codigo_sensores() == "10"):
                        if self.util.cronometro == 0:
                            self.status_alerta = True
                        self.util.beep_buzzer_delay(860, 1, 1, 10)
                        if self.util.cronometro/1000 == 10:
                            self.aviso.exibir_uso_incorreto()
                            self.util.cronometro = 0
                    else:
                        break
                     
            if catraca.operacao == 3:
                if self.sensor_optico.obtem_codigo_sensores() == "10":
                    while (self.sensor_optico.obtem_direcao_giro() == 'horario' and self.solenoide.obtem_estado_solenoide(1) == 0):
                        if (self.sensor_optico.obtem_codigo_sensores() == "10"):
                            if self.util.cronometro == 0:
                                self.status_alerta = True
                            self.util.beep_buzzer_delay(860, 1, 1, 10)
                            if self.util.cronometro/1000 == 10:
                                self.aviso.exibir_uso_incorreto()
                                self.util.cronometro = 0
                        else:
                            break
                        
            if catraca.operacao == 4:
                if self.sensor_optico.obtem_codigo_sensores() == "01":
                    while (self.sensor_optico.obtem_direcao_giro() == 'antihorario' and self.solenoide.obtem_estado_solenoide(2) == 0):
                        if (self.sensor_optico.obtem_codigo_sensores() == "01"):
                            if self.util.cronometro == 0:
                                self.status_alerta = True
                            self.util.beep_buzzer_delay(860, 1, 1, 10)
                            if self.util.cronometro/1000 == 10:
                                self.aviso.exibir_uso_incorreto()
                                self.util.cronometro = 0
                        else:
                            break
                                   
            self.verifica_meio_giro()       
        finally:
            pass
        
    def verifica_meio_giro(self):
        ##############################################################
        ## VERIFICA SE A CATRACA SE ENCONTRA EM MEIO GIRO
        ##############################################################
        while self.sensor_optico.obtem_codigo_sensores() == "11":
            if self.util.cronometro == 0:
                self.status_alerta = True
            self.util.beep_buzzer_delay(860, 1, 1, 40)
            if self.util.cronometro/1000 == 40:
                self.aviso.exibir_uso_incorreto()
                self.util.cronometro = 0
        self.util.cronometro = 0
        