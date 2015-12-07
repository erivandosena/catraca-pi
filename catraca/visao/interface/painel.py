#!/usr/bin/env python
# -*- coding: latin-1 -*-


from catraca.logs import Logs
from catraca.util import Util
from catraca.visao.interface.aviso import Aviso
from catraca.visao.interface.alerta import Alerta
from catraca.controle.dispositivos.leitorcartao import LeitorCartao
from catraca.controle.restful.relogio import Relogio
from catraca.visao.interface.verifica_rede import VerificaRede


__author__ = "Erivando Sena"
__copyright__ = "Copyright 2015, Unilab"
__email__ = "erivandoramos@unilab.edu.br"
__status__ = "Prototype" # Prototype | Development | Production


class Painel(object):
    
    log = Logs()
    util = Util()
    aviso = Aviso() 
    
    def __init__(self):
        super(Painel, self).__init__()
    
    def main(self):
        print '\nIniciando API...\n'
        self.log.logger.info('Iniciando Api...')
        self.aviso.exibir_inicializacao()
        self.aviso.exibir_estatus_catraca(self.util.obtem_ip())
        self.threads()
            
    def threads(self):
        #os.system("echo 'Sistema da Catraca iniciado!' | mail -s 'Raspberry Pi B' erivandoramos@bol.com.br")
        try:
            alerta = Alerta()
            alerta.start()
            relogio = Relogio()
            relogio.start()
            leitor = LeitorCartao()
            leitor.start()
            
#             Relogio().start()
#             #Alerta().start()
#             LeitorCartao().start()
        except KeyboardInterrupt:
                alerta.terminate()
                alerta.join()
                relogio.terminate()
                relogio.join()
                leitor.terminate()
                leitor.join()
        except Exception as excecao:
            print excecao
            self.log.logger.error('Erro executando Painel.', exc_info=True)
        finally:
            pass
        