#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import Queue
import threading
import datetime
from time import sleep
from catraca.util import Util
from catraca.logs import Logs
from catraca.visao.interface.aviso import Aviso
from catraca.modelo.dao.turno_dao import TurnoDAO
from catraca.modelo.dao.catraca_dao import CatracaDAO
from catraca.controle.restful.cliente_restful import ClienteRestful


__author__ = "Erivando Sena" 
__copyright__ = "Copyright 2015, Unilab" 
__email__ = "erivandoramos@unilab.edu.br" 
__status__ = "Prototype" # Prototype | Development | Production 


class Relogio(threading.Thread):
    
    log = Logs()
    util = Util()
    aviso = Aviso()
    turno_dao = TurnoDAO()
    catraca_dao = CatracaDAO()
    
    __periodo_ativo = None
    __turno_ativo = []

    hora_atual = None
    hora_inicio = None
    hora_fim = None
    
    contador = 30
    
    def __init__(self, intervalo=1):
        super(Relogio, self).__init__()
        self.hora_atual = self.util.obtem_hora()
        threading.Thread.__init__(self)
        self.name = 'Thread Relogio'
        self.intervalo = intervalo
        
        self.queue = Queue.Queue()
        self.parent_thread = threading.current_thread() 
        self._stop = threading.Event()
        
        thread = threading.Thread(group=None, target=self.processa, args=())
        thread.daemon = True # Daemonize thread
        #thread.start()
        print "%s. Rodando... " % self.name
        
    def run(self):
        self.processa()
        
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
        
    def processa(self):
        cliente_restful = ClienteRestful()
        cliente_restful.start()
        while True:
            # atualiza variaveis locais
            self.hora_atual = self.util.obtem_hora()
            
            # verifica a disponibilidade de turnos
            self.periodo = None

            # atualiza thread com variaveis
            cliente_restful.hora = self.hora_atual
            cliente_restful.datahora = self.util.obtem_datahora()
            cliente_restful.periodo = self.periodo
            cliente_restful.turno = self.turno
            
            print self.hora_atual
            print self.periodo

            # delay de 1 segundo
            sleep(self.intervalo)
              
    @property
    def periodo(self):
        return self.__periodo_ativo

    @periodo.setter
    def periodo(self, *valor):
        valor = self.obtem_periodo()
        self.__periodo_ativo = valor
        
    @property
    def turno(self):
        return self.__turno_ativo
 
    @turno.setter
    def turno(self, lista):
        self.__turno_ativo = lista
        
    def obtem_catraca(self):
        return self.catraca_dao.busca_por_ip(self.util.obtem_ip())
    
    def obtem_turno(self):
        p1 = datetime.datetime.strptime('05:59:59','%H:%M:%S').time()
        p2 = datetime.datetime.strptime('22:29:59','%H:%M:%S').time()
        self.contador += 1
        if (self.hora_atual > p1) and (self.hora_atual < p2):
            if self.contador >= 30:
                self.turno = self.turno_dao.busca_por_catraca(self.obtem_catraca(), self.hora_atual)
                self.contador = 0
                print "select no BD!"
                if self.turno:
                    self.hora_inicio = datetime.datetime.strptime(str(self.turno[1]),'%H:%M:%S').time()
                    self.hora_fim = datetime.datetime.strptime(str(self.turno[2]),'%H:%M:%S').time()       
                    return self.turno
                else:
                    return None
        else:
            self.turno = None
            return None

    def obtem_periodo(self):
        self.obtem_turno()
        if self.turno:
            if ((self.hora_atual >= self.hora_inicio) and (self.hora_atual <= self.hora_fim)) or ((self.hora_atual >= self.hora_inicio) and (self.hora_atual <= self.hora_fim)):  
                print "turno ativo => "+ str(self.turno)
                return True
            else:
                self.turno = None
                print "turno inativo => "+ str(self.turno)
                return False
        else:
            return False
        