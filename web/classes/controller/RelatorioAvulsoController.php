<?php
/**
 * @author Jefferson Uchoa Ponte
 * @version 1.0
 * @copyright UNILAB - Universidade da Integracao Internacional da Lusofonia Afro-Brasileira.
 * @package Controle
 */

class RelatorioAvulsoProprio{
	private $dao;
	public function start(){
		echo '
		Fiscaliza&ccedil;&atilde;o
		<form action="" method="get">
			
			<input type="date" name="data" />
			<input type="submit"/>
		</form>';
		if(isset($_GET['data']))
			$this->mostrarFiscal($_GET['data']);
	}
	public function mostrarFiscal($data){
		$time = strtotime($data);
		echo 'Dados do dia '.date("d/m/Y", $time);
		$this->dao = new DAO();
		
		$hora1 = date('Y-m-d', $time).' 08:00:00';
		$hora2 = date('Y-m-d', $time).' 15:00:00';
		
		$registroAlmoco = $this->geraNumeroDeRegistros($hora1, $hora2);
		$transacaoAlmoco = $this->geraNumeroDeTransacoes($hora1, $hora2);
		$dinheiroAlmoco = $this->geraValoresEmCaixa($hora1, $hora2);
		$avulsosAlmoco = $this->geraNumeroDeRegistrosAvulsos($hora1, $hora2);


				
		$hora1 = date('Y-m-d', $time).' 15:00:00';
		$hora2 = date('Y-m-d', $time).' 22:00:00';
		
		$registroJantar = $this->geraNumeroDeRegistros($hora1, $hora2);
		$transacaoJantar = $this->geraNumeroDeTransacoes($hora1, $hora2);
		$dinheiroJantar = $this->geraValoresEmCaixa($hora1, $hora2);
		$avulsosJantar = $this->geraNumeroDeRegistrosAvulsos($hora1, $hora2);


		


		echo '<table border="1">
			<tr><th>Almoco</th></tr>
				<tr><td>Catraca Virtual: '.$registroAlmoco.'</td></tr>		

				<tr><td>Catraca Avulsos: '.$avulsosAlmoco.'</td></tr>		

				<tr><td>Transacoes Guiche: '.$transacaoAlmoco .'</td></tr>
				<tr><td>Transacoes Guiche: '.$dinheiroAlmoco .'</td></tr>		
			</table>';
		
		echo '<table border="1">
			<tr><th>Jantar</th></tr>
				<tr><td>Catraca Virtual: '.$registroJantar.'</td></tr>		
				<tr><td>Catraca Avulsos: '.$avulsosJantar.'</td></tr>		


				<tr><td>Transacoes Guiche: '.$transacaoJantar .'</td></tr>		
				<tr><td>Transacoes Guiche: '.$dinheiroJantar .'</td></tr>
			</table>';


	}
	
	public function geraNumeroDeRegistros($data1, $data2){
		$result = $this->dao->getConexao()->query("SELECT * From registro
		WHERE regi_data BETWEEN '$data1' AND '$data2';
			");
		$i = 0;
		foreach($result as $linha){
			$i++;
		}
		return $i;
	}
	public function geraNumeroDeRegistrosAvulsos($data1, $data2){
		$result = $this->dao->getConexao()->query("SELECT * From registro
		INNER JOIN vinculo ON vinculo.vinc_id = registro.vinc_id
		WHERE regi_data BETWEEN '$data1' AND '$data2';
			");
		$i = 0;
		foreach($result as $linha){
			if($linha['vinc_avulso'])
				$i++;
		}
		return $i;
	}

	public function geraNumeroDeTransacoes($data1, $data2){
		$result = $this->dao->getConexao()->query("SELECT * From transacao
		WHERE tran_data BETWEEN '$data1' AND '$data2';
			");
		$i = 0;
		foreach($result as $linha){
			$i++;
		}
		return $i;	
	}
	public function geraValoresEmCaixa($data1, $data2){
		$result = $this->dao->getConexao()->query("SELECT * From transacao
		WHERE tran_data BETWEEN '$data1' AND '$data2';
			");
		$i = 0.0;
		foreach($result as $linha){
			$i += $linha['tran_valor'];
		}
		return $i;	
	}

	
	



}

?>
