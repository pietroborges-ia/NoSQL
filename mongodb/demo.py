from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# 1. Conexão com o MongoDB no Docker (porta 27018)
cliente_mongo = MongoClient("mongodb://127.0.0.1:27018/?directConnection=true")
db = cliente_mongo["loja_demo"]

def configurar_banco_e_regras():
    # Limpa coleções anteriores para resetar a demonstração
    db.pedidos.drop()
    db.produtos.drop()
    db.clientes.drop()

    # Validação estrutural com $jsonSchema para a coleção clientes
    validador_clientes = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["nome", "email", "endereco"],
            "properties": {
                "nome": {"bsonType": "string"},
                "email": {"bsonType": "string"},
                "endereco": {
                    "bsonType": "object",
                    "required": ["cidade", "uf"],
                    "properties": {
                        "cidade": {"bsonType": "string"},
                        "uf": {"bsonType": "string"}
                    }
                }
            }
        }
    }
    db.create_collection("clientes", validator=validador_clientes)
    db.clientes.create_index("email", unique=True)
    db.pedidos.create_index("cliente_id")

def remover_cliente(email):
    """Bloqueia exclusão de clientes com pedidos associados (integridade referencial)."""
    cliente = db.clientes.find_one({"email": email})
    if not cliente:
        return False
    total_pedidos = db.pedidos.count_documents({"cliente_id": cliente["_id"]})
    if total_pedidos > 0:
        raise ValueError(f"Exclusão bloqueada: cliente possui {total_pedidos} pedido(s) associado(s).")
    db.clientes.delete_one({"_id": cliente["_id"]})
    return True

def popular_banco():
    # Inserção dos 5 clientes
    id_ana = db.clientes.insert_one({
        "nome": "Ana Souza", "email": "ana@exemplo.com",
        "telefones": ["62 99999-0001"],
        "endereco": {"cidade": "Goiânia", "uf": "GO"}, "criado_em": datetime.now()
    }).inserted_id

    id_bruno = db.clientes.insert_one({
        "nome": "Bruno Lima", "email": "bruno@exemplo.com",
        "telefones": ["62 98888-0002"],
        "endereco": {"cidade": "Goiânia", "uf": "GO"}, "criado_em": datetime.now()
    }).inserted_id

    id_carla = db.clientes.insert_one({
        "nome": "Carla Mendes", "email": "carla@exemplo.com",
        "endereco": {"cidade": "Brasília", "uf": "DF"}, "criado_em": datetime.now()
    }).inserted_id

    id_diego = db.clientes.insert_one({
        "nome": "Diego Rocha", "email": "diego@exemplo.com",
        "endereco": {"cidade": "Anápolis", "uf": "GO"}, "criado_em": datetime.now()
    }).inserted_id

    id_eduardo = db.clientes.insert_one({
        "nome": "Eduardo Pires", "email": "eduardo@exemplo.com",
        "endereco": {"cidade": "Rio de Janeiro", "uf": "RJ"}, "criado_em": datetime.now()
    }).inserted_id

    # Inserção dos 5 produtos com esquema flexível e atributos variados
    db.produtos.insert_many([
        {
            "sku": "LIV-001", "nome": "Livro NoSQL Essencial", "preco_centavos": 8990, "estoque": 15,
            "atributos": {"autor": "Martin Fowler", "paginas": 216, "editora": "Novatec"}
        },
        {
            "sku": "ELE-001", "nome": "Teclado Mecânico RGB", "preco_centavos": 35000, "estoque": 10,
            "atributos": {"switch": "Gateron Brown", "conexao": "USB-C", "garantia_meses": 12}
        },
        {
            "sku": "CAM-001", "nome": "Camiseta Dev NoSQL", "preco_centavos": 5990, "estoque": 20,
            "atributos": {"tamanhos": ["M", "G"], "cor": "Preta", "material": "100% Algodão"}
        },
        {
            "sku": "LIV-002", "nome": "Sistemas de Banco de Dados", "preco_centavos": 14990, "estoque": 8,
            "atributos": {"autor": "Elmasri & Navathe", "paginas": 800, "editora": "Pearson"}
        },
        {
            "sku": "ELE-002", "nome": "Mouse Gamer Sem Fio", "preco_centavos": 18900, "estoque": 12,
            "atributos": {"dpi": 16000, "conexao": "Wireless", "garantia_meses": 24}
        }
    ])

    # Inserção dos 7 pedidos em estados variados
    db.pedidos.insert_many([
        # Pedidos da Ana (2 pedidos)
        {
            "cliente_id": id_ana, "status": "pago",
            "itens": [{"sku": "LIV-001", "nome": "Livro NoSQL Essencial", "quantidade": 1, "preco_unitario_centavos": 8990}],
            "total_centavos": 8990, "criado_em": datetime.now()
        },
        {
            "cliente_id": id_ana, "status": "pago",
            "itens": [{"sku": "ELE-001", "nome": "Teclado Mecânico RGB", "quantidade": 1, "preco_unitario_centavos": 35000}],
            "total_centavos": 35000, "criado_em": datetime.now()
        },
        # Pedidos dos demais clientes
        {
            "cliente_id": id_bruno, "status": "pago",
            "itens": [{"sku": "LIV-002", "nome": "Sistemas de Banco de Dados", "quantidade": 1, "preco_unitario_centavos": 14990}],
            "total_centavos": 14990, "criado_em": datetime.now()
        },
        {
            "cliente_id": id_bruno, "status": "enviado",
            "itens": [{"sku": "CAM-001", "nome": "Camiseta Dev NoSQL", "quantidade": 1, "preco_unitario_centavos": 5990}],
            "total_centavos": 5990, "criado_em": datetime.now()
        },
        {
            "cliente_id": id_carla, "status": "pago",
            "itens": [{"sku": "ELE-002", "nome": "Mouse Gamer Sem Fio", "quantidade": 1, "preco_unitario_centavos": 18900}],
            "total_centavos": 18900, "criado_em": datetime.now()
        },
        {
            "cliente_id": id_diego, "status": "entregue",
            "itens": [{"sku": "CAM-001", "nome": "Camiseta Dev NoSQL", "quantidade": 2, "preco_unitario_centavos": 5990}],
            "total_centavos": 11980, "criado_em": datetime.now()
        },
        {
            "cliente_id": id_eduardo, "status": "cancelado",
            "itens": [{"sku": "ELE-001", "nome": "Teclado Mecânico RGB", "quantidade": 1, "preco_unitario_centavos": 35000}],
            "total_centavos": 35000, "criado_em": datetime.now()
        }
    ])

def executar_demonstracao():
    print("=== CONFIGURANDO O BANCO LOJA_DEMO ===")
    configurar_banco_e_regras()
    popular_banco()
    print(f"-> Banco populado com sucesso: {db.clientes.count_documents({})} clientes, {db.produtos.count_documents({})} produtos e {db.pedidos.count_documents({})} pedidos.")

    print("\n=== DEMONSTRAÇÃO PRÁTICA DO CRUD E REGRAS ===")
    
    # 1. READ
    print("\n1. [READ] Consultando clientes em Goiânia por campo aninhado:")
    for c in db.clientes.find({"endereco.cidade": "Goiânia"}):
        print(f"   - {c['nome']} ({c['email']})")

    # 2. CREATE e Validação $jsonSchema
    print("\n2. [CREATE] Testando validação de esquema ($jsonSchema):")
    try:
        db.clientes.insert_one({"nome": "Invalido", "email": "sem_end@aula.com"})
    except Exception:
        print("   -> Sucesso: Cliente sem endereço foi rejeitado pelo $jsonSchema.")

    # 3. UPDATE
    print("\n3. [UPDATE] Atualizando cidade com $set e telefone com $addToSet:")
    db.clientes.update_one({"email": "bruno@exemplo.com"}, {"$set": {"endereco.cidade": "Trindade"}})
    db.clientes.update_one({"email": "bruno@exemplo.com"}, {"$addToSet": {"telefones": "62 98888-0002"}}) # Não duplica
    bruno = db.clientes.find_one({"email": "bruno@exemplo.com"})
    print(f"   -> Bruno atualizado: Cidade = {bruno['endereco']['cidade']} | Telefones = {bruno.get('telefones')}")

    # 4. DELETE e Integridade Referencial
    print("\n4. [DELETE] Testando integridade referencial manual:")
    try:
        remover_cliente("ana@exemplo.com")
    except ValueError as e:
        print(f"   -> Sucesso: {e}")

    # Exclusão bem-sucedida de registro sem pedidos
    temp_id = db.clientes.insert_one({
        "nome": "Temporario", "email": "temp@aula.com",
        "endereco": {"cidade": "Goiânia", "uf": "GO"}
    }).inserted_id
    db.clientes.delete_one({"_id": temp_id})
    print("   -> Registro temporário (sem pedidos) excluído com sucesso.")

    print("\n=== Demonstração finalizada com sucesso! ===")

if __name__ == "__main__":
    executar_demonstracao()