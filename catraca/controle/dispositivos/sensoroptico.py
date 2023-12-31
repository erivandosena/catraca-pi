#!/usr/bin/env python
# -*- coding: utf-8 -*-


from time import sleep
import subprocess
import threading
from multiprocessing import Process
from threading import Thread
from catraca.logs import Logs
from catraca.util import Util
from catraca.visao.interface.aviso import Aviso
from catraca.controle.raspberrypi.pinos import PinoControle
from catraca.controle.dispositivos.solenoide import Solenoide
from catraca.controle.dispositivos.pictograma import Pictograma
from numbers import Number
# from _ast import While
# from __builtin__ import True


__author__ = "Erivando Sena" 
__copyright__ = "Copyright 2015, © 09/02/2015" 
__email__ = "erivandoramos@bol.com.br" 
__status__ = "Prototype"


class SensorOptico(object):

    log = Logs()
    util = Util()
    aviso = Aviso()
    rpi = PinoControle()
    sensor_1 = rpi.ler(6)['gpio']
    sensor_2 = rpi.ler(13)['gpio']
    solenoide = Solenoide()
    pictograma = Pictograma()
    tempo_decorrido = 0
    tempo_decorrente = 0
    finaliza_giro = False
    status_alerta = False
    tempo = 0

    def __init__(self):
        super(SensorOptico, self).__init__()

    def ler_sensor(self, sensor):
        if sensor == 1:
            return self.rpi.estado(self.sensor_1)
        elif sensor == 2:
            return self.rpi.estado(self.sensor_2)
        
    def registra_giro(self, tempo, catraca):
        giro = self.obtem_codigo_sensores()
        contragiro = self.obtem_codigo_sensores()
        try:
            while self.tempo < tempo:
                self.tempo +=1
                print str(self.tempo) + " de " + str(tempo)
                #OPCAO 1 ou 2
                if catraca.operacao == 1 or catraca.operacao == 2:
                    
                    if self.obtem_codigo_sensores() != "00":
                        print "===================> " + str(self.obtem_codigo_sensores())
                        giro = self.obtem_codigo_sensores()
                        while self.obtem_codigo_sensores() == "01":
                            print "===================> " + str(self.obtem_codigo_sensores())
                            giro = self.obtem_codigo_sensores()
                        else:
                            while self.obtem_codigo_sensores() == "11":
                                print "===================> " + str(self.obtem_codigo_sensores())
                                if giro == "01":
                                    giro += self.obtem_codigo_sensores()
                            else:
                                while self.obtem_codigo_sensores() == "10":
                                    print "===================> " + str(self.obtem_codigo_sensores())
                                    if giro == "0111":
                                        giro += self.obtem_codigo_sensores()
                                    elif giro == "11":
                                        giro = "011110"
                                else:
                                    print "===================> " + str(self.obtem_codigo_sensores())
                                    if giro == "011110" or giro == "011100" and giro != "00":
                                        print giro
                                        return True
                                    else:
                                        print "saindo sem giro confirmado"
                #OPCAO 3 ou 4
                if catraca.operacao == 3 or catraca.operacao == 4:
                    if self.obtem_codigo_sensores() != "00":
                        print "===================> " + str(self.obtem_codigo_sensores())
                        giro = self.obtem_codigo_sensores()
                        while self.obtem_codigo_sensores() == "10":
                            print "===================> " + str(self.obtem_codigo_sensores())
                            giro = self.obtem_codigo_sensores()
                        else:
                            while self.obtem_codigo_sensores() == "11":
                                print "===================> " + str(self.obtem_codigo_sensores())
                                if giro == "10":
                                    giro += self.obtem_codigo_sensores()
                            else:
                                while self.obtem_codigo_sensores() == "01":
                                    print "===================> " + str(self.obtem_codigo_sensores())
                                    if giro == "1011":
                                        giro += self.obtem_codigo_sensores()
                                    elif giro == "11":
                                        giro = "101101"
                                else:
                                    print "===================> " + str(self.obtem_codigo_sensores())
                                    if giro == "101101" or giro == "101100" and giro != "00":
                                        print giro
                                        return True
                                    else:
                                        print "saindo sem giro confirmado"
                sleep(1)
            else:
                return False
        except SystemExit, KeyboardInterrupt:
            raise
        except Exception:
            self.log.logger.error('Erro lendo sensores opticos.', exc_info=True)
        finally:
            self.tempo = 0
            
    def obtem_codigo_sensores(self):
        return str(self.ler_sensor(1)) + '' + str(self.ler_sensor(2))
    
    def detecta_giro_completo(self, codigo_sensores):
        retorno = True
        if codigo_sensores != "10" or codigo_sensores != "01":
            if codigo_sensores != "11":
                if codigo_sensores == "00":
                    retorno = False
            return retorno
    
    def obtem_direcao_giro(self):
        opcoes = {
                   '10' : 'horario',
                   '01' : 'antihorario',
                   '11' : 'incompleto',
                   '00' : 'repouso',
        }
        return opcoes.get(self.obtem_codigo_sensores(), None)
    
    def obtem_giro_iniciado(self, modo_operacao):
        opcoes = {
                   'horario' : 1,
                   'antihorario' : 2,
        }
        return opcoes.get(modo_operacao, None)
   
    def cronometro_tempo(self, tempo_decorrido, tempo, milissegundos):
        self.tempo_decorrente += milissegundos
        if tempo_decorrido > tempo/1000:
            self.finaliza_giro = False
            return self.finaliza_giro
        else:
            return True
        
    def bloqueia_acesso(self, catraca):
        if catraca.operacao == 1:
            #self.solenoide.ativa_solenoide(1,0)
            self.pictograma.seta_esquerda(0)
            self.pictograma.xis(0)
        elif catraca.operacao == 2:
            #self.solenoide.ativa_solenoide(2,0)
            self.pictograma.seta_direita(0)
            self.pictograma.xis(0)
        self.aviso.exibir_acesso_bloqueado()
        self.aviso.exibir_aguarda_cartao()
        