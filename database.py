import sqlite3
from datetime import datetime

DATABASE = 'controle_notas.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas_entrada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_nota TEXT NOT NULL,
            data_emissao TEXT NOT NULL,
            produto TEXT NOT NULL,
            peso REAL NOT NULL,
            valor REAL NOT NULL,
            cnpj_emitente TEXT NOT NULL,
            cnpj_destinatario TEXT NOT NULL,
            data_carregamento TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas_saida (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_cte TEXT NOT NULL,
            numero_nota TEXT NOT NULL,
            peso_saida REAL NOT NULL,
            valor_frete REAL NOT NULL,
            data_saida TEXT NOT NULL,
            FOREIGN KEY (numero_nota) REFERENCES notas_entrada (numero_nota)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS containers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_container TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            armador TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'portaria',
            local_atual TEXT NOT NULL DEFAULT 'portaria',
            data_registro TEXT NOT NULL,
            data_atualizacao TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_movimentacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            container_id INTEGER NOT NULL,
            tipo_movimento TEXT NOT NULL,
            data_movimento TEXT NOT NULL,
            observacao TEXT,
            FOREIGN KEY (container_id) REFERENCES containers (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def inserir_nota_entrada(numero_nota, data_emissao, produto, peso, valor, cnpj_emitente, cnpj_destinatario):
    conn = get_db()
    cursor = conn.cursor()
    data_carregamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO notas_entrada (numero_nota, data_emissao, produto, peso, valor, cnpj_emitente, cnpj_destinatario, data_carregamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (numero_nota, data_emissao, produto, peso, valor, cnpj_emitente, cnpj_destinatario, data_carregamento))
    
    conn.commit()
    conn.close()

def listar_notas_entrada():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            ne.*,
            COALESCE(SUM(ns.peso_saida), 0) as peso_carregado,
            GROUP_CONCAT(DISTINCT ns.numero_cte) as numero_cte
        FROM notas_entrada ne
        LEFT JOIN notas_saida ns ON ne.numero_nota = ns.numero_nota
        GROUP BY ne.id
        ORDER BY ne.data_emissao DESC
    ''')
    
    notas = cursor.fetchall()
    conn.close()
    return notas

def obter_saldo_nota(numero_nota):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            ne.peso,
            COALESCE(SUM(ns.peso_saida), 0) as peso_saida_total
        FROM notas_entrada ne
        LEFT JOIN notas_saida ns ON ne.numero_nota = ns.numero_nota
        WHERE ne.numero_nota = ?
        GROUP BY ne.numero_nota
    ''', (numero_nota,))
    
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        saldo = resultado['peso'] - resultado['peso_saida_total']
        return saldo
    return 0

def inserir_nota_saida(numero_cte, numero_nota, peso_saida, valor_frete, data_saida):
    saldo_disponivel = obter_saldo_nota(numero_nota)
    
    if peso_saida > saldo_disponivel:
        raise ValueError(f"Peso de saída ({peso_saida} kg) excede o saldo disponível ({saldo_disponivel:.2f} kg) para a nota {numero_nota}")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO notas_saida (numero_cte, numero_nota, peso_saida, valor_frete, data_saida)
        VALUES (?, ?, ?, ?, ?)
    ''', (numero_cte, numero_nota, peso_saida, valor_frete, data_saida))
    
    conn.commit()
    conn.close()

def obter_estatisticas():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COALESCE(SUM(peso), 0) as total_peso, COALESCE(SUM(valor), 0) as total_valor FROM notas_entrada')
    entrada = cursor.fetchone()
    
    cursor.execute('SELECT COALESCE(SUM(peso_saida), 0) as total_peso, COALESCE(SUM(valor_frete), 0) as total_frete FROM notas_saida')
    saida = cursor.fetchone()
    
    conn.close()
    
    return {
        'entrada_peso': entrada['total_peso'],
        'entrada_valor': entrada['total_valor'],
        'saida_peso': saida['total_peso'],
        'saida_frete': saida['total_frete'],
        'saldo_peso': entrada['total_peso'] - saida['total_peso']
    }

def inserir_container(numero_container, tipo, armador, observacao=''):
    conn = get_db()
    cursor = conn.cursor()
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO containers (numero_container, tipo, armador, status, local_atual, data_registro, data_atualizacao)
        VALUES (?, ?, ?, 'portaria', 'portaria', ?, ?)
    ''', (numero_container, tipo, armador, agora, agora))
    
    container_id = cursor.lastrowid
    
    cursor.execute('''
        INSERT INTO registro_movimentacao (container_id, tipo_movimento, data_movimento, observacao)
        VALUES (?, 'entrada_portaria', ?, ?)
    ''', (container_id, agora, observacao or f'Container {numero_container} deu entrada na portaria'))
    
    conn.commit()
    conn.close()
    return container_id

def listar_containers():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            c.*,
            (SELECT MAX(rm.data_movimento) 
             FROM registro_movimentacao rm 
             WHERE rm.container_id = c.id) as ultima_movimentacao
        FROM containers c
        ORDER BY c.data_registro DESC
    ''')
    
    containers = cursor.fetchall()
    conn.close()
    return containers

def obter_container(container_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM containers WHERE id = ?', (container_id,))
    container = cursor.fetchone()
    conn.close()
    return container

def obter_container_por_numero(numero_container):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM containers WHERE numero_container = ?', (numero_container,))
    container = cursor.fetchone()
    conn.close()
    return container

def registrar_desova(container_id, observacao=''):
    conn = get_db()
    cursor = conn.cursor()
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        UPDATE containers 
        SET status = 'patio_vazio', local_atual = 'patio_vazio', data_atualizacao = ?
        WHERE id = ?
    ''', (agora, container_id))
    
    cursor.execute('''
        INSERT INTO registro_movimentacao (container_id, tipo_movimento, data_movimento, observacao)
        VALUES (?, 'desova', ?, ?)
    ''', (container_id, agora, observacao or 'Container desovado e movido para pátio vazio'))
    
    conn.commit()
    conn.close()

def registrar_saida(container_id, observacao=''):
    conn = get_db()
    cursor = conn.cursor()
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        UPDATE containers 
        SET status = 'liberado_saida', data_atualizacao = ?
        WHERE id = ?
    ''', (agora, container_id))
    
    cursor.execute('''
        INSERT INTO registro_movimentacao (container_id, tipo_movimento, data_movimento, observacao)
        VALUES (?, 'saida', ?, ?)
    ''', (container_id, agora, observacao or 'Container liberado para saída'))
    
    conn.commit()
    conn.close()

def obter_historico_container(container_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM registro_movimentacao 
        WHERE container_id = ?
        ORDER BY data_movimento DESC
    ''', (container_id,))
    
    movimentacoes = cursor.fetchall()
    conn.close()
    return movimentacoes

def obter_estatisticas_containers():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM containers')
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as count FROM containers WHERE status = 'portaria'")
    portaria = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM containers WHERE status = 'patio_cheio'")
    patio_cheio = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM containers WHERE status = 'desova'")
    desova = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM containers WHERE status = 'patio_vazio'")
    patio_vazio = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM containers WHERE status = 'liberado_saida'")
    liberado = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total': total,
        'portaria': portaria,
        'patio_cheio': patio_cheio,
        'desova': desova,
        'patio_vazio': patio_vazio,
        'liberado_saida': liberado
    }

if __name__ == '__main__':
    init_db()
    print("Banco de dados inicializado com sucesso!")
