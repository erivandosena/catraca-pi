package br.edu.unilab.catraca.controller;

import java.awt.Color;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.net.UnknownHostException;
import java.sql.Connection;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;

import javax.swing.JFrame;

import br.edu.unilab.catraca.controller.recurso.CartaoRecurso;
import br.edu.unilab.catraca.controller.recurso.CatracaRecurso;
import br.edu.unilab.catraca.controller.recurso.CatracaUnidadeRecurso;
import br.edu.unilab.catraca.controller.recurso.RegistroRecurso;
import br.edu.unilab.catraca.controller.recurso.TipoRecurso;
import br.edu.unilab.catraca.controller.recurso.TurnoRecurso;
import br.edu.unilab.catraca.controller.recurso.TurnoUnidadeRecurso;
import br.edu.unilab.catraca.controller.recurso.UnidadeRecurso;
import br.edu.unilab.catraca.controller.recurso.UsuarioRecurso;
import br.edu.unilab.catraca.controller.recurso.VinculoRecurso;
import br.edu.unilab.catraca.dao.CatracaDAO;
import br.edu.unilab.catraca.dao.CatracaVirtualDAO;
import br.edu.unilab.catraca.dao.TipoDAO;
import br.edu.unilab.catraca.dao.UsuarioDAO;
import br.edu.unilab.catraca.dao.VinculoDAO;
import br.edu.unilab.catraca.view.CatracaVirtualView;
import br.edu.unilab.catraca.view.FrameSplash;
import br.edu.unilab.catraca.view.LoginView;
import br.edu.unilab.unicafe.model.Catraca;
import br.edu.unilab.unicafe.model.Tipo;
import br.edu.unilab.unicafe.model.Turno;
import br.edu.unilab.unicafe.model.Unidade;
import br.edu.unilab.unicafe.model.Usuario;
import br.edu.unilab.unicafe.model.Vinculo;

public class CatracaVirtualController {
	
	private LoginView frameLogin;
	private CatracaVirtualView frameCatracaVirtual;
	private Catraca catracaVirtual;
	private CatracaDAO dao;
	private ArrayList<Turno>turnos;
	private Turno turnoAtual;
	private boolean turnoAtivo;
	private Unidade unidade;
	private FrameSplash splash;
	private Usuario operador;
	
	
	public CatracaVirtualController(){
		turnoAtivo = false;
	}
	
	public void iniciar(){
		this.splash = new FrameSplash();
		splash.setVisible(true);
		
		this.catracaVirtual = new Catraca();
		this.dao = new CatracaDAO();
		
		
		this.frameLogin = new LoginView();
		this.frameLogin.getLabelMensagem().setText("Aguarde a Sincronização dos Dados");
		this.frameLogin.setExtendedState(JFrame.MAXIMIZED_BOTH);
		try {
			
			this.catracaVirtual.maquinaLocal();
			
		} catch (UnknownHostException e) {
			System.out.println("Impossivel determinar nome da maquina. ");
			e.printStackTrace();
			return;
		}
		
		this.sincronizacaoBasica();
		
		splash.setVisible(false);
		this.frameLogin.setVisible(true);
		
		this.verificarNomeDaCatraca();
		this.verificarUnidadeDaCatraca();
		this.verificarTurnosDaCatraca();
		this.adicionarEventosDeLogin();
		
	}
	public void adicionarEventosDeLogin(){
		getFrameLogin().getSenha().addKeyListener(new KeyAdapter() {
			@Override
			public void keyPressed(KeyEvent e) {
				if(e.getKeyCode() == KeyEvent.VK_ENTER){
					tentarLogar();
				}
			}
		});
		
		getFrameLogin().getBtnEntrar().addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				tentarLogar();
			}
		});
		
		
	}
	
	public void adicionarEventosCartao(){
		getFrameCatracaVirtual().getNumeroCartao().addKeyListener(new KeyAdapter() {
			@Override
			public void keyPressed(KeyEvent e) {
				if(e.getKeyCode() == KeyEvent.VK_ENTER){
					String numero = getFrameCatracaVirtual().getNumeroCartao().getText();
					getFrameCatracaVirtual().getNumeroCartao().setText("");
					
					if(turnoAtivo){
						passarCartao(numero);
					}else{
						erroForaDoTurno();
					}
					
				}
			}
		});
				
	}
	
	
	
	public void passarCartao(final String numero){
		Thread passando = new Thread(new Runnable() {
			
			@Override
			public void run() {
				getFrameCatracaVirtual().getNumeroCartao().setEnabled(false);
				System.out.println(numero);
				CatracaVirtualDAO catracaVirtualDAO= new CatracaVirtualDAO();
				Vinculo vinculo = new Vinculo();
				vinculo.getCartao().setNumero(numero);
				if(catracaVirtualDAO.verificaVinculo(vinculo)){

					getFrameCatracaVirtual().getNomeUsuario().setText(vinculo.getResponsavel().getNome());
					getFrameCatracaVirtual().getTipoUsuario().setText(vinculo.getCartao().getTipo().getNome());
					getFrameCatracaVirtual().getValorCobrado().setText(""+vinculo.getCartao().getTipo().getValorCobrado());
					getFrameCatracaVirtual().getPanel_3().setVisible(true);	
				}else{
					getFrameCatracaVirtual().getLblErro().setText("Sem Vinculo Valido");
					getFrameCatracaVirtual().getPanelErro().setVisible(true);
				}
				
				try {
					Thread.sleep(3000);
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				
				getFrameCatracaVirtual().getPanel_3().setVisible(false);
				getFrameCatracaVirtual().getPanelErro().setVisible(false);
				getFrameCatracaVirtual().getNumeroCartao().setEnabled(true);
				getFrameCatracaVirtual().getNumeroCartao().grabFocus();
				
			}
		});
		passando.start();
	}
	public void erroForaDoTurno(){
		Thread mostrar = new Thread(new Runnable() {
			
			@Override
			public void run() {
				getFrameCatracaVirtual().getLblErro().setText("Fora do horário de atendimento. ");
				getFrameCatracaVirtual().getPanelErro().setVisible(true);
				try {
					Thread.sleep(3000);
				} catch (InterruptedException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				getFrameCatracaVirtual().getPanelErro().setVisible(false);
			}
		});
		mostrar.start();
	}
	
	public void tentarLogar(){
		@SuppressWarnings("deprecation")
		String senha = UsuarioDAO.getMD5(getFrameLogin().getSenha().getText());
		this.operador = new Usuario();
		this.operador.setLogin(getFrameLogin().getLogin().getText().toLowerCase().trim());
		this.operador.setSenha(senha);
		UsuarioDAO usuarioDao = new UsuarioDAO(this.dao.getConexao());
		this.getFrameLogin().getLogin().setText("");
		this.getFrameLogin().getSenha().setText("");
		
		
		
		if(usuarioDao.autentica(this.operador))
		{
			this.iniciarCatracaVirtual();
		}
		else
		{
			this.getFrameLogin().getLabelMensagem().setText("Errou login ou senha");
		}
		
	}
	
	public void verificandoTurnoAtual(){
		Thread verificando = new Thread(new Runnable() {
			
			@Override
			public void run() {
				while(true){

					try {
						Thread.sleep(1000);
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
					
					Date horaAtual = new Date();
					SimpleDateFormat dataNoFrame = new SimpleDateFormat("dd/MM/yyyy HH:mm:ss");
					getFrameCatracaVirtual().getLabelDataHora().setText(dataNoFrame.format(horaAtual));
					
					
					if(turnoAtivo){
						
						Turno turno = turnoAtual;
						String horaInicial = turno.getHoraInicial();
						String horaFinal = turno.getHoraFinal();
						
						Date dateHoraInicial = null;
						Date dateHoraFinal = null;
						SimpleDateFormat format = new SimpleDateFormat("HH:mm:ss");
						format.setLenient(false);
						try {
							dateHoraFinal = format.parse(horaFinal);
							dateHoraInicial = format.parse(horaInicial);
						} catch (ParseException e) {
							// TODO Auto-generated catch block
							e.printStackTrace();
						}
						Calendar calendarAtual = Calendar.getInstance();
						
						calendarAtual.setTime(horaAtual);
						int hourAtual = calendarAtual.get(Calendar.HOUR_OF_DAY);
						int minuteAtual = calendarAtual.get(Calendar.MINUTE);
						
						
						Calendar calendarInicioTurno = Calendar.getInstance();
						calendarInicioTurno.setTime(dateHoraInicial);
						int hourInicioTurno = calendarInicioTurno.get(Calendar.HOUR_OF_DAY);
						int minuteInicioTurno = calendarInicioTurno.get(Calendar.MINUTE);
						
						
						Calendar calendarFimTurno = Calendar.getInstance();
						calendarFimTurno.setTime(dateHoraFinal);
						int hourFimTurno = calendarFimTurno.get(Calendar.HOUR_OF_DAY);
						int minuteFimTurno = calendarFimTurno.get(Calendar.MINUTE);
						
						
						if(hourAtual >= hourInicioTurno && hourAtual <= hourFimTurno){
							if(hourAtual == hourInicioTurno && minuteAtual >= minuteInicioTurno){
								continue;
								
							}
							else if(hourAtual > hourInicioTurno && hourAtual < hourFimTurno){
								continue;
								
							}else if(hourAtual >= hourInicioTurno && hourAtual == hourFimTurno && minuteAtual <= minuteFimTurno){
								continue;
							}else{
								getFrameCatracaVirtual().getLabelTurno().setText("Turno "+turno.getDescricao()+"  finalizado. ");
								turnoAtivo = false;
							}
						}else{
							getFrameCatracaVirtual().getLabelTurno().setText("Turno "+turno.getDescricao()+"  finalizado. ");
							turnoAtivo = false;
							
						}
						
						continue;
					}
					for(Turno turno : turnos){
						String horaInicial = turno.getHoraInicial();
						String horaFinal = turno.getHoraFinal();
						
						Date dateHoraInicial = null;
						Date dateHoraFinal = null;
						SimpleDateFormat format = new SimpleDateFormat("HH:mm:ss");
						format.setLenient(false);
						try {
							dateHoraFinal = format.parse(horaFinal);
							dateHoraInicial = format.parse(horaInicial);
						} catch (ParseException e) {
							// TODO Auto-generated catch block
							e.printStackTrace();
						}
						Calendar calendarAtual = Calendar.getInstance();
						
						calendarAtual.setTime(horaAtual);
						int hourAtual = calendarAtual.get(Calendar.HOUR_OF_DAY);
						int minuteAtual = calendarAtual.get(Calendar.MINUTE);
						
						
						Calendar calendarInicioTurno = Calendar.getInstance();
						calendarInicioTurno.setTime(dateHoraInicial);
						int hourInicioTurno = calendarInicioTurno.get(Calendar.HOUR_OF_DAY);
						int minuteInicioTurno = calendarInicioTurno.get(Calendar.MINUTE);
						
						
						Calendar calendarFimTurno = Calendar.getInstance();
						calendarFimTurno.setTime(dateHoraFinal);
						int hourFimTurno = calendarFimTurno.get(Calendar.HOUR_OF_DAY);
						int minuteFimTurno = calendarFimTurno.get(Calendar.MINUTE);
						
						
						if(hourAtual >= hourInicioTurno && hourAtual <= hourFimTurno){
							if(hourAtual == hourInicioTurno && minuteAtual >= minuteInicioTurno){
								getFrameCatracaVirtual().getLabelTurno().setText("Turno "+turno.getDescricao()+" iniciado");
								turnoAtual = turno;
								turnoAtivo = true;
								continue;
								
							}
							else if(hourAtual > hourInicioTurno && hourAtual < hourFimTurno){
								getFrameCatracaVirtual().getLabelTurno().setText("Turno "+turno.getDescricao()+" iniciado");
								turnoAtual = turno;
								turnoAtivo = true;
								continue;
								
							}else if(hourAtual >= hourInicioTurno && hourAtual == hourFimTurno && minuteAtual <= minuteFimTurno){
								getFrameCatracaVirtual().getLabelTurno().setText("Turno "+turno.getDescricao()+" iniciado");
								turnoAtual = turno;
								turnoAtivo = true;
								continue;
							}
						}
													
						
						
						
						
					}
					
				}
				
			}
		});
		verificando.start();
		
	}
	public void iniciarCatracaVirtual(){
		TipoDAO tipoDao = new TipoDAO(this.dao.getConexao());
		ArrayList<Tipo> listaTipos = tipoDao.lista();
		int tamanho = listaTipos.size();
		String colunas[] = new String[tamanho+3];
		colunas[0] = "Catraca Virtual";
		String dados[][] = new String[1][tamanho+3];
		int i = 1;
		for (Tipo tipo : listaTipos) {
			colunas[i] = tipo.getNome();
			dados[0][i] = "0";
			i++;
		}	
		dados[0][i] = "0";
		dados[0][i+1] = "0";
		colunas[i] = "Isento";
		colunas[i+1] = "Total";

		
		
		this.frameCatracaVirtual = new CatracaVirtualView(colunas, dados);
		this.frameCatracaVirtual.getNumeroCartao().setFocusable(true);
		
		this.frameCatracaVirtual.setFinanceiroAtivo(this.catracaVirtual.isFinanceiroAtivo());
		
		this.frameCatracaVirtual.getDados()[0][0] = this.catracaVirtual.getNome();
		this.frameCatracaVirtual.getTabela().updateUI();
		
		this.frameCatracaVirtual.getNomeUsuario().setText("");
		this.frameCatracaVirtual.getTipoUsuario().setText("");
		this.frameCatracaVirtual.getRefeicoesRestantes().setText("");
		this.frameCatracaVirtual.getValorCobrado().setText("");
		
		this.frameCatracaVirtual.getTabela().updateUI();

		
		this.getFrameLogin().setVisible(false);
		
		this.getFrameCatracaVirtual().setVisible(true);
		getFrameCatracaVirtual().getLabelTurno().setText(" Turno Inativo ");
		getFrameCatracaVirtual().getNumeroCartao().grabFocus();
		getFrameCatracaVirtual().getPanel_3().setVisible(false);
		getFrameCatracaVirtual().getPanelErro().setVisible(false);
		this.adicionarEventosCartao();
		this.verificandoTurnoAtual();
		
	}
	
	public void sincronizacaoBasica(){
		
//		UnidadeRecurso unidadeRecurso = new UnidadeRecurso();
//		unidadeRecurso.sincronizar(this.dao.getConexao());
//		
//		CatracaRecurso catracaRecurso = new CatracaRecurso();
//		catracaRecurso.sincronizar(this.dao.getConexao());
//		
//		TipoRecurso tipoRecurso = new TipoRecurso();
//		tipoRecurso.sincronizar(this.dao.getConexao());
//				
//		TurnoRecurso turnoRecurso = new TurnoRecurso();
//		turnoRecurso.sincronizar(this.dao.getConexao());
//		
//		TurnoUnidadeRecurso turnoUnidade = new TurnoUnidadeRecurso();
//		turnoUnidade.sincronizar(this.dao.getConexao());
//
//		CartaoRecurso cartaoRecurso = new CartaoRecurso();
//		cartaoRecurso.sincronizar(this.dao.getConexao());
//		
//		UsuarioRecurso usuarioRecurso = new UsuarioRecurso();
//		usuarioRecurso.sincronizar();
//		
//		VinculoRecurso vinculoRecurso = new VinculoRecurso();
//		vinculoRecurso.sincronizar(this.dao.getConexao());
//		
//		CatracaUnidadeRecurso catracaUnidadeRecurso = new CatracaUnidadeRecurso();
//		catracaUnidadeRecurso.sincronizar(this.dao.getConexao());
//		
//		RegistroRecurso registroRecurso = new RegistroRecurso();
//		registroRecurso.sincronizar(this.dao.getConexao());
		
	}
	public void verificarNomeDaCatraca(){
		boolean passou = false;
		do{
			if(this.dao.retornaCatracaPorNome(this.catracaVirtual) == null){
				this.frameLogin.getLabelMensagem().setText("Cadastre a catraca virtual");
				try {
					Thread.sleep(2000);
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				
				CatracaRecurso catracaRecurso = new CatracaRecurso();
				catracaRecurso.sincronizar(this.dao.getConexao());
			}else{
				passou = true;
				this.frameLogin.getLabelMensagem().setText("Catraca Virtual: "+catracaVirtual.getNome());
				
			}	
		}while(!passou);
	}
	public void verificarUnidadeDaCatraca(){
		boolean passou = false;
		do{
			this.unidade = this.dao.unidadeDaCatraca(this.catracaVirtual);
			if(this.unidade == null){
				this.frameLogin.getLabelMensagem().setText("Cadastre a catraca em alguma unidade academica");
				try {
					Thread.sleep(2000);
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}

				UnidadeRecurso unidadeRecurso = new UnidadeRecurso();
				unidadeRecurso.sincronizar(this.dao.getConexao());
				CatracaUnidadeRecurso recurso = new CatracaUnidadeRecurso();
				recurso.sincronizar(this.dao.getConexao());
			}else{
				this.frameLogin.getLabelMensagem().setText("Unidade: "+unidade.getNome());
				passou = true;
			}
		}while(!passou);
	}
	public void verificarTurnosDaCatraca(){
		boolean passou = false;
		do{
			this.turnos = this.dao.turnosDaUnidade(this.unidade);
			if(this.turnos == null || this.turnos.size() == 0){
				this.frameLogin.getLabelMensagem().setText("Adicione turnos na Unidade Academica");
				try {
					Thread.sleep(2000);
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				TurnoUnidadeRecurso recurso = new TurnoUnidadeRecurso();
				recurso.sincronizar(this.dao.getConexao());
			}else{
				this.frameLogin.getLabelMensagem().setText("");
				passou = true;
			}
			
		}while(!passou);
	}
	
	
	public LoginView getFrameLogin() {
		return frameLogin;
	}
	public CatracaVirtualView getFrameCatracaVirtual() {
		return frameCatracaVirtual;
	}
	
	
}
