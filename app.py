from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from database import (
    init_db, inserir_nota_entrada, listar_notas_entrada, inserir_nota_saida, obter_estatisticas,
    inserir_container, listar_containers, obter_container, obter_container_por_numero,
    registrar_desova, registrar_saida, obter_historico_container, obter_estatisticas_containers
)
from xml_parser import extrair_dados_nfe

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'xml_file' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['xml_file']
        
        if file.filename == '' or file.filename is None:
            return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'}), 400
        
        if not file.filename.lower().endswith('.xml'):
            return jsonify({'success': False, 'message': 'Apenas arquivos XML são permitidos'}), 400
        
        try:
            xml_bytes = file.read()
            
            dados = extrair_dados_nfe(xml_bytes)
            
            inserir_nota_entrada(
                dados['numero_nota'],
                dados['data_emissao'],
                dados['produto'],
                dados['peso'],
                dados['valor'],
                dados['cnpj_emitente'],
                dados['cnpj_destinatario']
            )
            
            return jsonify({
                'success': True, 
                'message': f'Nota fiscal {dados["numero_nota"]} carregada com sucesso!',
                'dados': dados
            })
        
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    return render_template('upload.html')

@app.route('/acompanhamento')
def acompanhamento():
    notas = listar_notas_entrada()
    return render_template('acompanhamento.html', notas=notas)

@app.route('/api/notas')
def api_notas():
    notas = listar_notas_entrada()
    return jsonify([dict(nota) for nota in notas])

@app.route('/saida', methods=['GET', 'POST'])
def saida():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            numero_cte = data.get('numero_cte')
            notas_selecionadas = data.get('notas', [])
            data_saida = data.get('data_saida')
            
            if not numero_cte or not notas_selecionadas or not data_saida:
                return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
            
            for nota in notas_selecionadas:
                inserir_nota_saida(
                    numero_cte,
                    nota['numero_nota'],
                    nota['peso_saida'],
                    nota['valor_frete'],
                    data_saida
                )
            
            return jsonify({
                'success': True, 
                'message': f'Saída registrada com sucesso! CTe: {numero_cte}'
            })
        
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    
    notas = listar_notas_entrada()
    return render_template('saida.html', notas=notas)

@app.route('/dashboard')
def dashboard():
    stats_notas = obter_estatisticas()
    stats_containers = obter_estatisticas_containers()
    return render_template('dashboard.html', stats_notas=stats_notas, stats_containers=stats_containers)

@app.route('/api/estatisticas')
def api_estatisticas():
    stats = obter_estatisticas()
    return jsonify(stats)

@app.route('/containers')
def containers():
    containers_list = listar_containers()
    return render_template('containers.html', containers=containers_list)

@app.route('/containers/novo', methods=['GET', 'POST'])
def container_novo():
    if request.method == 'POST':
        try:
            numero_container = request.form.get('numero_container')
            tipo = request.form.get('tipo')
            armador = request.form.get('armador')
            observacao = request.form.get('observacao', '')
            
            if not numero_container or not tipo or not armador:
                return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
            
            container_existente = obter_container_por_numero(numero_container)
            if container_existente:
                return jsonify({'success': False, 'message': f'Container {numero_container} já está cadastrado'}), 400
            
            container_id = inserir_container(numero_container, tipo, armador, observacao)
            
            return jsonify({
                'success': True,
                'message': f'Container {numero_container} registrado com sucesso!',
                'container_id': container_id
            })
        
        except Exception as e:
            error_msg = str(e)
            if 'UNIQUE constraint' in error_msg or 'unique' in error_msg.lower():
                return jsonify({'success': False, 'message': f'Container {numero_container} já está cadastrado no sistema'}), 400
            return jsonify({'success': False, 'message': f'Erro ao registrar container: {error_msg}'}), 400
    
    return render_template('container_novo.html')

@app.route('/containers/<int:container_id>')
def container_detalhe(container_id):
    container = obter_container(container_id)
    if not container:
        return redirect(url_for('containers'))
    
    historico = obter_historico_container(container_id)
    return render_template('container_detalhe.html', container=container, historico=historico)

@app.route('/containers/<int:container_id>/desova', methods=['POST'])
def container_desova(container_id):
    try:
        observacao = request.form.get('observacao', '')
        
        container = obter_container(container_id)
        if not container:
            return jsonify({'success': False, 'message': 'Container não encontrado'}), 404
        
        if container['status'] == 'patio_vazio':
            return jsonify({'success': False, 'message': 'Container já foi desovado'}), 400
        
        if container['status'] == 'liberado_saida':
            return jsonify({'success': False, 'message': 'Container já saiu'}), 400
        
        registrar_desova(container_id, observacao)
        
        return jsonify({
            'success': True,
            'message': f'Desova do container {container["numero_container"]} registrada com sucesso!'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/containers/<int:container_id>/saida', methods=['POST'])
def container_saida(container_id):
    try:
        observacao = request.form.get('observacao', '')
        
        container = obter_container(container_id)
        if not container:
            return jsonify({'success': False, 'message': 'Container não encontrado'}), 404
        
        if container['status'] == 'liberado_saida':
            return jsonify({'success': False, 'message': 'Container já foi liberado para saída'}), 400
        
        registrar_saida(container_id, observacao)
        
        return jsonify({
            'success': True,
            'message': f'Saída do container {container["numero_container"]} registrada com sucesso!'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/containers')
def api_containers():
    containers_list = listar_containers()
    return jsonify([dict(c) for c in containers_list])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
