#!/usr/bin/env python
# -*- coding: latin-1 -*-


from contextlib import closing
from catraca.logs import Logs
from catraca.logs import Logs
from catraca.util import Util
from catraca.modelo.dados.conexao import ConexaoFactory
from catraca.modelo.dados.conexaogenerica import ConexaoGenerica
from catraca.modelo.entidades.cartao_valido import CartaoValido
from catraca.modelo.dao.tipo_dao import TipoDAO
from catraca.modelo.dao.vinculo_dao import VinculoDAO


__author__ = "Erivando Sena"
__copyright__ = "Copyright 2015, Unilab"
__email__ = "erivandoramos@unilab.edu.br"
__status__ = "Prototype" # Prototype | Development | Production


class CartaoValidoDAO(ConexaoGenerica):
    
    log = Logs()

    def __init__(self):
        super(CartaoValidoDAO, self).__init__()
        ConexaoGenerica.__init__(self)
        
    def busca_cartao_valido(self, numero, data=None):
        obj = CartaoValido()
        if data is None:
            data = Util().obtem_datahora_postgresql()
        sql = "SELECT cartao.cart_id, cartao.cart_numero, cartao.cart_creditos, "\
            "tipo.tipo_valor, vinculo.vinc_refeicoes, tipo.tipo_id, vinculo.vinc_id, "\
            "vinculo.vinc_descricao, SUBSTR(TRIM(usuario.usua_nome), 0, 16) || '.' as usua_nome "\
            "FROM cartao "\
            "INNER JOIN tipo ON cartao.tipo_id = tipo.tipo_id "\
            "INNER JOIN vinculo ON vinculo.cart_id = cartao.cart_id "\
            "INNER JOIN usuario ON usuario.usua_id = vinculo.usua_id "\
            "WHERE ('"+str(data)+"' BETWEEN vinculo.vinc_inicio AND vinculo.vinc_fim) AND "\
            "(cartao.cart_numero = '"+str(numero)+"')"
        print "=" * 100
        print sql 
        print "=" * 100
        try:
            with closing(self.abre_conexao().cursor()) as cursor:
                cursor.execute(sql)
                dados = cursor.fetchone()
                if dados:
                    obj.id = dados[0]
                    obj.numero = dados[1]
                    obj.creditos = dados[2]
                    obj.valor = dados[3]
                    obj.refeicoes = dados[4]
                    obj.tipo = self.busca_por_tipo(obj)
                    obj.vinculo = self.busca_por_vinculo(obj)
                    obj.descricao = dados[7]
                    obj.nome = dados[8]
                    return obj
                else:
                    return None
        except Exception as excecao:
            self.aviso = str(excecao)
            self.log.logger.error('[cartao] Erro ao realizar SELECT.', exc_info=True)
        finally:
            pass
        
    def busca_por_tipo(self, obj):
        return TipoDAO().busca(obj.id)
    
    def busca_por_vinculo(self, obj):
        return VinculoDAO().busca(obj.id)
    