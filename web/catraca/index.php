<?php
ini_set ( 'display_errors', 1 );
ini_set ( 'display_startup_erros', 1 );
error_reporting ( E_ALL );
function __autoload($classe) {
	if (file_exists ( 'classes/dao/' . $classe . '.php' ))
		include_once 'classes/dao/' . $classe . '.php';
	if (file_exists ( 'classes/model/' . $classe . '.php' ))
		include_once 'classes/model/' . $classe . '.php';
	if (file_exists ( 'classes/controller/' . $classe . '.php' ))
		include_once 'classes/controller/' . $classe . '.php';
	if (file_exists ( 'classes/util/' . $classe . '.php' ))
		include_once 'classes/util/' . $classe . '.php';
	if (file_exists ( 'classes/view/' . $classe . '.php' ))
		include_once 'classes/view/' . $classe . '.php';
}

$sessao = new Sessao ();

if (isset ( $_GET ["sair"] )) {
	
	$sessao->mataSessao ();
	header ( "Location:./index.php" );
}

?>
<!DOCTYPE html>
<html lang="pt-BR" xml:lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Catraca</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<!-- meta tag para responsividade em Windows e Linux -->
<link rel="stylesheet"
	href="http://spa.dsi.unilab.edu.br/spa/css/spa.css" />
<link rel="stylesheet" href="css/style.css" />

</head>
<body>
	<div class="pagina fundo-cinza1">
		<div id="barra-governo">
			<div class="resolucao">
				<div class="a-esquerda">
					<a href="http://brasil.gov.br/" target="_blank"><span id="bandeira"></span><span>BRASIL</span></a>
					<a href="http://acessoainformacao.unilab.edu.br/" target="_blank">Acesso
						à informação</a>
				</div>
				<div class="a-direita">
					<a href="#"><i class="icone-menu"></i></a>
				</div>
				<ul>
					<li><a href="http://brasil.gov.br/barra#participe" target="_blank">Participe</a></li>
					<li><a href="http://www.servicos.gov.br/" target="_blank">Serviços</a></li>
					<li><a href="http://www.planalto.gov.br/legislacao" target="_blank">Legislação</a></li>
					<li><a href="http://brasil.gov.br/barra#orgaos-atuacao-canais"
						target="_blank">Canais</a></li>
				</ul>
			</div>
		</div>
<?php



if ($sessao->getNivelAcesso () == Sessao::NIVEL_SUPER) {
	UsuarioController::main ( $sessao->getNivelAcesso() );
	echo 'Teste da view:<br>';
	$dao = new DAO ( null, DAO::TIPO_PG_LOCAL);
	$novoNivel = Sessao::NIVEL_SUPER;
	
// 	$result = $dao->getConexao ()->exec( "UPDATE usuario set usua_nivel = $novoNivel WHERE usua_login = 'erivando'" );
// 	echo $result;
	$result = $dao->getConexao ()->query ( "SELECT * FROM usuario" );
	
	foreach ( $result as $linha ) {
		print_r($linha);
	}
	
} else {
	
	UsuarioController::main($sessao->getNivelAcesso());
	
	//Primeiro relat�rio. 
	//Precisamos saber o n�mero de fichas de cada tipo. 
	

}


?>

</div>
</body>
</html>


