import xmltodict
from datetime import datetime
import chardet

def extrair_dados_nfe(xml_bytes):
    try:
        if isinstance(xml_bytes, str):
            xml_content = xml_bytes
        else:
            detected = chardet.detect(xml_bytes)
            encoding = detected['encoding'] or 'utf-8'
            
            try:
                xml_content = xml_bytes.decode(encoding)
            except (UnicodeDecodeError, AttributeError):
                for enc in ['utf-8', 'iso-8859-1', 'latin-1', 'cp1252']:
                    try:
                        xml_content = xml_bytes.decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Não foi possível decodificar o arquivo XML")
        
        doc = xmltodict.parse(xml_content)
        
        nfe = doc.get('nfeProc', {}).get('NFe', doc.get('NFe', {}))
        
        if not nfe:
            raise ValueError("Estrutura de NFe não encontrada no XML")
        
        inf_nfe = nfe.get('infNFe', {})
        
        ide = inf_nfe.get('ide', {})
        emit = inf_nfe.get('emit', {})
        dest = inf_nfe.get('dest', {})
        det = inf_nfe.get('det', [])
        total = inf_nfe.get('total', {}).get('ICMSTot', {})
        
        if not isinstance(det, list):
            det = [det]
        
        numero_nota = ide.get('nNF', '')
        
        data_emissao_raw = ide.get('dhEmi', ide.get('dEmi', ''))
        if 'T' in data_emissao_raw:
            data_emissao = datetime.fromisoformat(data_emissao_raw.replace('Z', '+00:00')).strftime('%Y-%m-%d')
        else:
            data_emissao = data_emissao_raw[:10] if len(data_emissao_raw) >= 10 else data_emissao_raw
        
        cnpj_emitente = emit.get('CNPJ', emit.get('CPF', ''))
        cnpj_destinatario = dest.get('CNPJ', dest.get('CPF', ''))
        
        valor_total = float(total.get('vNF', 0))
        
        produtos = []
        for item in det:
            prod = item.get('prod', {})
            nome_produto = prod.get('xProd', 'Produto não especificado')
            quantidade = float(prod.get('qCom', 0))
            unidade = prod.get('uCom', 'UN')
            
            peso = quantidade
            if unidade.upper() in ['KG', 'KILO', 'QUILOGRAMA']:
                peso = quantidade
            elif unidade.upper() in ['G', 'GRAMA', 'GRAMAS']:
                peso = quantidade / 1000
            elif unidade.upper() in ['T', 'TON', 'TONELADA']:
                peso = quantidade * 1000
            
            produtos.append({
                'nome': nome_produto,
                'quantidade': quantidade,
                'unidade': unidade,
                'peso_kg': peso
            })
        
        peso_total = sum(p['peso_kg'] for p in produtos)
        
        produto_principal = produtos[0]['nome'] if produtos else 'Produto não especificado'
        if len(produtos) > 1:
            produto_principal += f' (+{len(produtos)-1} itens)'
        
        return {
            'numero_nota': str(numero_nota),
            'data_emissao': data_emissao,
            'produto': produto_principal,
            'peso': peso_total,
            'valor': valor_total,
            'cnpj_emitente': cnpj_emitente,
            'cnpj_destinatario': cnpj_destinatario,
            'produtos': produtos
        }
    
    except Exception as e:
        raise ValueError(f"Erro ao processar XML: {str(e)}")
