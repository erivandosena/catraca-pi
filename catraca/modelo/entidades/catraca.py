#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = "Erivando Sena"
__copyright__ = "(C) Copyright 2015, Unilab"
__email__ = "erivandoramos@unilab.edu.br"
__status__ = "Prototype" # Prototype | Development | Production


class Catraca(object):
    
    def __init__(self):
        self.__catr_id = None
        self.__catr_ip = None
        self.__catr_tempo_giro = None
        self.__catr_operacao = None
        self.__catr_nome = None
    
    @property
    def id(self):
        return self.__catr_id
    
    @id.setter
    def id(self, valor):
        self.__catr_id = valor
    
    @property
    def ip(self):
        return self.__catr_ip
    
    @ip.setter
    def ip(self, valor):
        self.__catr_ip = valor
    
    @property
    def tempo(self):
        return self.__catr_tempo_giro
    
    @tempo.setter
    def tempo(self, valor):
        self.__catr_tempo_giro = valor
    
    @property
    def operacao(self):
        return self.__catr_operacao
    
    @operacao.setter
    def operacao(self, valor):
        self.__catr_operacao = valor
    
    @property
    def nome(self):
        return self.__catr_nome
    
    @nome.setter
    def nome(self, valor):
        self.__catr_nome = valor

        