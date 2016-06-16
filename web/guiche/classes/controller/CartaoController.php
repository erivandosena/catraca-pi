<?php


class CartaoController{
	private $view;
	public static function main($nivelDeAcesso){
		
		switch ($nivelDeAcesso){
			case Sessao::NIVEL_SUPER:
				$controller = new CartaoController();
				$controller->telaCartao();
				break;
			default:
				UsuarioController::main ( $nivelDeAcesso );
				break;
		}
	}
	
	
	public function telaCartao(){
		$this->view = new CartaoView();
		echo '<div class = "simpleTabs">
		        <ul class = "simpleTabsNavigation">
				
					<li><a href="#">Identifica&ccedil;&atilde;o</a></li>
					<li><a href="#">Cadastro</a></li>
					
		        </ul>
		        <div class = "simpleTabsContent">';
		
		$this->telaIdentificacao();
		echo '	</div>
						
						
				<div class = "simpleTabsContent">';
		$this->telaCadastro();
		echo '	</div>		
						
		    </div>';
		
		
		
	}
	public function telaIdentificacao(){
		
		$this->view->formBuscaCartao();
		
		if(isset($_GET['numero_cartao'])){
			$cartao = new Cartao();
			$cartao->setNumero($_GET['numero_cartao']);
			$numeroCartao = $cartao->getNumero();
			$dataTimeAtual = date ( "Y-m-d G:i:s" );
			$sqlVerificaNumero = "SELECT * FROM usuario 
				INNER JOIN vinculo
				ON vinculo.usua_id = usuario.usua_id
				LEFT JOIN cartao ON cartao.cart_id = vinculo.cart_id
				LEFT JOIN tipo ON cartao.tipo_id = tipo.tipo_id
				WHERE cartao.cart_numero = '$numeroCartao'
					";
			$dao = new DAO();
			$result = $dao->getConexao()->query($sqlVerificaNumero);
			$idCartao = 0;
			$usuario = new Usuario();
			$tipo = new Tipo();
			$vinculoDao = new VinculoDAO($dao->getConexao());
			$vinculo = new Vinculo();
			foreach($result as $linha){
				$idDoVinculo = $linha['vinc_id'];
				$tipo->setNome($linha['tipo_nome']);
				$usuario->setNome($linha['usua_nome']);
				$usuario->setIdBaseExterna($linha['id_base_externa']);
				$idCartao = $linha['cart_id'];
				$vinculo->setAvulso($linha['vinc_avulso']);
				$avulso = $linha['vinc_avulso'];
				if($avulso){
					$usuario->setNome("Avulso");
				}
				break;
				
			}
			if($idCartao){
				
				$vinculo->setId($idDoVinculo);
				$cartao->setId($idCartao);
				$vinculoDao->vinculoPorId($vinculo);
				
				echo '<div class="borda"><h1>'.ucwords(strtolower(htmlentities($usuario->getNome()))).'. Tipo: '.$tipo->getNome();
				
				echo '</h1>';
				if(!$vinculo->isActive()){
					echo '<p>O vinculo não está ativo </p><br>
							<a href="?pagina=cartao&numero_cartao='.$_GET['numero_cartao'].'&cartao_renovar=1" class="botao">Renovar</a> ';
				
					if(isset($_GET['cartao_renovar'])){
						if(isset($_POST['certeza'])){
							$usuarioDao = new UsuarioDAO(null, DAO::TIPO_PG_SIGAAA);
							
							
							$usuarioDao->retornaPorIdBaseExterna($usuario);
							
							if($vinculoDao->usuarioJaTemVinculo($usuario))
							{
								$this->view->mostraSucesso("Esse usuário já possui vínculo válido.");
								echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $usuario->getIdBaseExterna() . '">';
								return;
							}
							if($vinculo->isAvulso()){
						
								$this->view->mostraSucesso("Não existe renovação de vínculos avulsos!");
								echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $usuario->getIdBaseExterna() . '">';
								return;
							}
							
							
							
							if(!$this->verificaSeAtivo($usuario)){
								$this->view->mostraSucesso("Esse usuário possui um problema quanto ao status!");
								echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $usuario->getIdBaseExterna() . '">';
								return;
						
							}
								
							$daqui3Meses = date ( 'Y-m-d', strtotime ( "+60 days" ) ) . 'T' . date ( 'G:00:01' );
							$vinculo->setFinalValidade($daqui3Meses);
								
							if($vinculoDao->atualizaValidade($vinculo)){
								$this->view->mostraSucesso("Vínculo Atualizado com Sucesso!  ");
							}else{
								$this->view->mostraSucesso("Erro ao tentar renovar vínculo.  ");
							}
							echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $usuario->getIdBaseExterna() . '">';
							return;
						}
						
						$this->view->formConfirmacaoRenovarVinculo();
					}
				}
				echo '
						
						
						</div>';
			}else
			{

				echo '<div class="borda"><h1>Cartão Não possui Vínculo Válido.</h1></div>';
				
			}
			
			
			
		}
		
		
	}
	public function telaCadastro(){
		$this->view->formBuscaUsuarios();
		
		if (isset ( $_GET ['selecionado'] )) {
			$idDoSelecionado = $_GET['selecionado'];
			$usuarioDao = new UsuarioDAO(null, DAO::TIPO_PG_SIGAAA);
			$usuario = new Usuario();
			$usuario->setIdBaseExterna($idDoSelecionado);
			
			$usuarioDao->retornaPorIdBaseExterna($usuario);
			
			
			$this->view->mostraSelecionado($usuario);
			$vinculoDao = new VinculoDAO();
				
			
			
			if(isset($_GET['vinculo_cancelar'])){
				$vinculo = new Vinculo();
				$vinculo->setId($_GET['vinculo_cancelar']);
				
				if(isset($_POST['certeza'])){
					if($vinculoDao->invalidarVinculo($vinculo)){
						$this->view->mostraSucesso("Vínculo Invalidado.  ");
					}else{
						$this->view->mostraSucesso("Erro ao tentar invalidar vínculo.  ");
					}
					echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $usuario->getIdBaseExterna() . '">';
					return;
				}
				
				
				$this->view->formConfirmacaoEliminarVinculo($vinculo);
				return;
			}
			
			if(isset($_GET['vinculo_renovar'])){
				$vinculo = new Vinculo();
				$vinculo->setId($_GET['vinculo_renovar']);
				$vinculoDao->vinculoPorId($vinculo);
				
				$daqui3Meses = date ( 'Y-m-d', strtotime ( "+60 days" ) ) . 'T' . date ( 'G:00:01' );
				$vinculo->setFinalValidade($daqui3Meses);
				
				
				if(isset($_POST['certeza'])){
					if($vinculoDao->usuarioJaTemVinculo($usuario))
					{
						$this->view->mostraSucesso("Esse usuário já possui vínculo válido.");
						echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $usuario->getIdBaseExterna() . '">';
						return;
					}
					if($vinculo->isAvulso()){
						
						$this->view->mostraSucesso("Não existe renovação de vínculos avulsos!");
						echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $usuario->getIdBaseExterna() . '">';
						return;
					}
					
					if(!$this->verificaSeAtivo($usuario)){
						$this->view->mostraSucesso("Esse usuário possui um problema quanto ao status!");
						echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $usuario->getIdBaseExterna() . '">';
						return;
						
					}
					
					
					
					if($vinculoDao->atualizaValidade($vinculo)){
						$this->view->mostraSucesso("Vínculo Atualizado com Sucesso!  ");
					}else{
						$this->view->mostraSucesso("Erro ao tentar renovar vínculo.  ");
					}
					echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $usuario->getIdBaseExterna() . '">';
					return;
				}
			
			
				$this->view->formConfirmacaoRenovarVinculo();
				return;
			}
			
			
			
			
			
			$vinculos = $vinculoDao->retornaVinculosValidosDeUsuario($usuario);
			
			$podeComer = $this->verificaSeAtivo($usuario);
			
			if(!sizeof($vinculos) && $podeComer){
				if (!isset ( $_GET ['cartao'] )){
					echo '<a class="botao" href="?pagina=cartao&selecionado=' . $idDoSelecionado . '&cartao=add">Adicionar</a>';
				}else{
					$tipoDao = new TipoDAO($vinculoDao->getConexao());
					$listaDeTipos = $tipoDao->retornaLista();
					foreach ($listaDeTipos as $chave => $tipo){
						if(strtolower (trim( $tipo->getNome())) == 'aluno'){
							if(strtolower (trim($usuario->getTipodeUsuario())) == 'aluno' && strtolower (trim($usuario->getStatusDiscente())) == 'ativo'){
								continue;
							}
							unset($listaDeTipos[$chave]);
							continue;
						}
						if(strtolower (trim( $tipo->getNome())) == 'servidor tae'){
							if(strtolower (trim($usuario->getStatusServidor())) == 'ativo' && strpos(strtolower (trim($usuario->getCategoria())), 'administrativo')){
								continue;
							}
							unset($listaDeTipos[$chave]);
							continue;
						}
						if(strtolower (trim( $tipo->getNome())) == 'servidor docente'){
							if(strtolower (trim($usuario->getStatusServidor())) == 'ativo' && strtolower (trim($usuario->getCategoria())) == 'docente'){
								continue;
							}
							unset($listaDeTipos[$chave]);
							continue;
						}
						if(strtolower (trim( $tipo->getNome())) == 'terceirizado'){
							if(strtolower (trim($usuario->getTipodeUsuario())) == 'terceirizado'){
								continue;
							}
							unset($listaDeTipos[$chave]);
							continue;
						}
						unset($listaDeTipos[$chave]);
							
					}
					if(isset($_GET['salvar'])){
						foreach($listaDeTipos as $tipo){
							if($tipo->getId() == $_GET['id_tipo'])
								$esseTipo = $tipo;	
						}
						$vinculo = new Vinculo();
						$daqui3Meses = date ( 'Y-m-d', strtotime ( "+60 days" ) ) . 'T' . date ( 'G:00:01' );
						$vinculo->setFinalValidade($daqui3Meses);
						$vinculo->getCartao()->getTipo()->setId($tipo->getId());
						$vinculo->getCartao()->setNumero($_GET['numero_cartao2']);
						$vinculo->getResponsavel()->setIdBaseExterna(intval($usuario->getIdBaseExterna()));
						$vinculo->setInicioValidade(date ( "Y-m-d G:i:s" ));
						if($vinculoDao->usuarioJaTemVinculo($vinculo->getResponsavel())){
								echo '<div class="borda">';
								echo '<p>Esse usuário já possui cartão. Inative o cartão atual para adicionar um novo.</p><br>';
								//echo '<a href="?pagina=cartao&cartaoselecionado=' .$vinculo->getCartao()->getId().'">Clique aqui para ver</a>';
								echo '</div>';
								return;
	
						}
						if($vinculoDao->cartaoTemVinculo($vinculo->getCartao())){
							echo '<div class="borda">';
							echo '<p>O numero do cartão digitado já possui vinculo, utilize outro cartão.</p><br>';
							echo '</div>';
							echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $vinculo->getResponsavel()->getIdBaseExterna() . '&cartao=add">';
							return;
						}
						
						if(isset($_POST['enviar_vinculo'])){
							
							if($vinculoDao->usuarioJaTemVinculo($vinculo->getResponsavel())){
								echo '<div class="borda">';
								echo '<p>Esse usuário já possui cartão. Invalide o cartão atual para adicionar um novo.</p><br>';
								//echo '<a href="?pagina=cartao&cartaoselecionado=' .$vinculo->getCartao()->getId().'">Clique aqui para ver</a>';
								echo '</div>';
								return;
						
							}
							if($vinculoDao->cartaoTemVinculo($vinculo->getCartao())){
								echo '<div class="borda">';
								echo '<p>O numero do cartão digitado já possui vinculo, utilize outro cartão.</p><br>';
								echo '</div>';
								return;
							}
							if($vinculoDao->adicionaVinculo ($vinculo)){
								$this->view->mostraSucesso("Vinculo Adicionado Com Sucesso. ");
							}else{
								$this->view->mostraSucesso("Erro na tentativa de Adicionar Vínculo. ");
							}
							echo '<meta http-equiv="refresh" content="4; url=.\?pagina=cartao&selecionado=' . $vinculo->getResponsavel()->getIdBaseExterna() . '">';
							return;
						}
						
						$this->view->formConfirmacaoEnvioVinculo($usuario, $_GET['numero_cartao2'], $tipo);
					}else{
						$this->view->mostraFormAdicionarVinculo($listaDeTipos, $idDoSelecionado);
					}
					
				
				}
			}
			
			foreach($vinculos as $vinculoComIsencao)
				$vinculoDao->isencaoValidaDoVinculo($vinculoComIsencao);
			$podeRenovar = true;
			if(sizeof($vinculos)){
				$podeRenovar = false;
			}
			$vinculosVencidos = $vinculoDao->retornaVinculosVencidos($usuario);
			$vinculosALiberar = $vinculoDao->retornaVinculosFuturos($usuario);
			
			
			if(sizeof($vinculos)){
				echo '<h2>Vinculos ativos</h2>';
				$this->view->mostraVinculos($vinculos);
			}
			if(sizeof($vinculosVencidos)){

				echo '<h2>Vinculos Vencidos</h2>';
				$this->view->mostraVinculos($vinculosVencidos, $podeRenovar);
			}
			if(sizeof($vinculosALiberar)){
				echo '<h2>Vinculos A Liberar</h2>';
				$this->view->mostraVinculos($vinculosALiberar, false);					
			}
			
		}
		

		if (isset ( $_GET ['nome'] )) {
				
			$usuarioDao = new UsuarioDAO(null, DAO::TIPO_PG_SIGAAA);
			$listaDeUsuarios = $usuarioDao->pesquisaNoSigaa( $_GET ['nome']);
			$this->view->mostraResultadoBuscaDeUsuarios($listaDeUsuarios);
			$usuarioDao->fechaConexao();
		}
		
		
	}
	public function verificaSeAtivo(Usuario $usuario){
		if(strtolower (trim($usuario->getStatusServidor())) == 'ativo'){
			
			return true;
		}
		if(strtolower (trim($usuario->getStatusDiscente())) == 'ativo'){
			return true;	
		}
		
		if(strtolower (trim($usuario->getTipodeUsuario())) == 'terceirizado'){
			return true;
		}

		return false;
	}
	
	
	
	
}



?>