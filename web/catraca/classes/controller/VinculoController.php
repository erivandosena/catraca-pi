<?php


class VinculoController{
	
	public static function main($tela){
		switch ($tela){
			case Sessao::NIVEL_SUPER:
				$controller = new VinculoController();
				$controller->telaVinculo();
				/*
				 * Queremos 
				 * um formulario de pesquisa. 
				 * Ao digitar um nome, vamos buscar. 
				 * Temos uma lista que tras SIAP, Matricula, Nome, documentos. 
				 * Vamos fazer o teste. 
				 * 
				 */
				
				break;
			case Sessao::NIVEL_DESLOGADO:
				break;
			default:
				break;
		}
		
		
	
	
	}
	public function telaVinculo(){
		
		echo '								
									<form method="post" action="" class="formulario em-linha" >
										<div class="borda">
										<label for="opcoes-1">
											<object class="rotulo texto-preto">Buscar por: </object>
											<select name="opcoes-1" id="opcoes-1" class="texto-preto">
												<option value="1">Nome</option>
												<option value="2">CPF</option>
												<option value="3">RG</option>
												<option value="3">Matrícula</option>							            										            
												<option value="3">Vinculo</option>
												<option value="3">SIAPE</option>
											</select>
											<input class="texto-preto" type="text" name="nome" id="campo-texto-2" /><br>
											<input type="submit" />											    
										</label>
									</form>';
		
		
		
		if(isset($_POST['nome'])){
			$pesquisa = preg_replace('/[^[:alnum:]]/', '',$_POST['nome']);
			$pesquisa = strtoupper($pesquisa);
			$sql = "SELECT * FROM vw_usuarios_catraca WHERE nome LIKE '%$pesquisa%'";
			$dao = new DAO(null, DAO::TIPO_PG_SIGAAA);
			$result = $dao->getConexao()->query($sql);
			echo '
											<div class="doze linhas">
												<br><h2 class="texto-preto">Resultado da busca:</h2><br><br>
											</div>
											<table class="tabela borda-vertical zebrada texto-preto">
												<thead>
											        <tr>
											            <th>Nome</th>
											            <th>CPF</th>
											            <th>Passaporte</th>
											            <th>Matrícula</th>
														<th>SIAPE</th>
											            <th>Selecionar</th>
											        </tr>
											    </thead>
												<tbody>';
												foreach($result as $linha){
													echo '<tr>';
													echo '<td>'.$linha['nome'].'</a></td>';
													echo '<td>'.$linha['cpf_cnpj'].'</td>';
													echo '<td>'.$linha['passaporte'].'</td>';
													echo '<td>'.$linha['matricula_disc'].'</td>';
													echo '<td>'.$linha['siape'].'</td>';
													echo '<td class="centralizado">
											            	<a href="?selecionado='.$linha['id_usuario'].'"><span class="icone-checkmark texto-verde2 botao" title="Selecionar"></span></a>
											            </td>';
													echo '</tr>';
												}
			echo '<br><br><br>
											    </tbody>
											</table>
										</div>';
				

		}
		if(isset($_GET['selecionado'])){
			
			if(is_int(intval($_GET['selecionado'])) && intval($_GET['selecionado']))
			{
				$dao = new DAO(null, DAO::TIPO_PG_SIGAAA);
				$id = intval($_GET['selecionado']);
				$sql = "SELECT * FROM vw_usuarios_catraca WHERE id_usuario = $id";
				$result = $dao->getConexao()->query($sql);
				foreach($result as $row){
					echo '<div class="borda">
									        Nome: '.$row['nome'].' 
									     <br>Login: '.$row['login'].'
									     <br> CPF: '.$row['cpf_cnpj'].'
									     <br> Identidade: '.$row['identidade'].'
									     <br> Passaporte: '.$row['passaporte'].'
									     <br>SIAPE: '.$row['siape'].'
									     <br>Status Servidor: '.$row['status_servidor'].'
									     <br>Status Discente: '.$row['status_discente'].'
									     <br>Matricula Discente: '.$row['matricula_disc'].'
									     <br>Tipo de Usuario: '.$row['tipo_usuario'].'
									     <br>Categoria: '.$row['categoria'].'
									    
						</div>';
					
					break;
					
				}
				$dao->fechaConexao();
				$dao= new DAO(null, DAO::TIPO_PG_LOCAL);
				//Agora vamos pegar os vinculos ativos desse usuario. 
				$sql = "SELECT * FROM vinculo INNER JOIN usuario ON vinculo.usua_id = usuario.usua_id 
						WHERE usuario.usua_id = $id";
				$result = $dao->getConexao()->query($sql);
				foreach ($result as $row){
					print_r($row);
					
				}
				if(isset($_GET['cartao']) && isset($_GET['selecionado']))
				{
					$daqui3Meses = date('Y-m-d',strtotime("+60 days")).'T'.date('h:00:01', strtotime("+60 days"));
					
					echo '<form method="post" action="" class="formulario texto-preto" >
										<div class="borda">										
									    <label for="campo-texto-1">
									        Cartão: <input type="text" name="numero_cartao" id="cartao" />
									    </label>
									    <label for="campo-texto-1">
									        Validade: <input type="datetime-local" name="data_validade" value="'.$daqui3Meses.'" />
									    </label>
									     <label for="tipo">Tipo</label>
									       <select id="tipo" name="tipo">';
					$pesquisaTipos = $dao->getConexao()->query("SELECT * FROM tipo");
					foreach($pesquisaTipos as $linhaTipos){
						echo '<option value="'.$linhaTipos['tipo_id'].'">'.$linhaTipos['tipo_nome'].'</option>';
					}
					
					echo '
									        			
									        </select>
									    
									    <fieldset>
									        <legend>Cartão Avulso:</legend>
									        <label for="checkbox-1.1">
									            <input type="checkbox" name="checkbox-1" id="checkbox-1.1" value="1" /> Sim
									        </label>									        
									    </fieldset><br>
										<label for="campo-texto-1">
									        Quantidade de refeições: <input type="text" name="quantidade_refeicoes" id="periodo" />
									    </label><br>
										<input type="hidden" name="id_base_externa"  value="'.$_GET['selecionado'].'"/>
									   	<input type="submit"  name="salvar" value="Salvar"/>
									</form>';
				}
				else{
					echo '<a href="?selecionado='.$_GET['selecionado'].'&cartao=add">Adicionar</a>';
				}
				if(isset($_POST['salvar'])){
					
					//Todos os cadastros inicialmente ser�o n�o avulsos. 
					$validade = $_POST['data_validade'];
					$numeroCartao = $_POST['numero_cartao'];
					$usuarioBaseExterna = $_POST['id_base_externa'];
					$tipoCartao = $_POST['tipo'];
					$vinculoDao = new  VinculoDAO($dao->getConexao());
					$vinculoDao->adicionaVinculo($usuarioBaseExterna, $numeroCartao, $validade, $tipoCartao);
					//No final eu redireciono para a pagina de selecao do usuario. 
					echo '<meta http-equiv="refresh" content="10; url=.\?selecionado='.$_POST['id_base_externa'].'">';
				}
				
				
			}
		}
	}

}


?>