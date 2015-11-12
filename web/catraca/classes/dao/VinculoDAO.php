<?php


class VinculoDAO extends DAO{
	
	/**
	 * Pega-se o Id da base do SIG. Antes vamos verificar se existe na base local. 
	 * Se existe � mais f�cil. Vamos para o Passo adicionar Vinculo.
	 * 
	 * Se n�o existir, pegamos da base do SIG e adicionamos na base local. Indo para o passo de adicionar vinculo. 
	 * 
	 * Adicionar Vinculo
	 *
	 * Vai ser o seguinte, acabamos de adicionar um usuario na base local. Utilizaremos o id inserido. 
	 * Iremos adicionar o vinculo para esse usuario com dados de cartao e vinculo. 
	 * 
	 * 
	 * Mas antes n�o sabemos se o cart�o j� � cadastrado. 
	 *  
	 * 
	 * 
	 * 
	 * @param int $idUsuarioBaseExterna
	 * @param Vinculo $vinculo
	 */
	public function adicionaVinculo($idUsuarioBaseExterna, Vinculo $vinculo){
		
		$idUsuarioBaseExterna = intval($idUsuarioBaseExterna);
		
		
		
	}
	
	
}

?>