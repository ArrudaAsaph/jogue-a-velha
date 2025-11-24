# 📄 Análise do WSDL - Serviço SOAP Jogo da Velha

## 🔍 Informações do Serviço

- **URL do WSDL:** http://localhost:8001/?wsdl
- **Namespace:** http://jogovelha.com/soap
- **Serviço:** JogoDaVelhaService
- **Protocolo:** SOAP 1.1
- **Estilo:** Document/Literal

---

## 📋 Estrutura Completa do WSDL

### 1. Definições (definitions)

```xml
<wsdl:definitions
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:wsdlsoap11="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:tns="http://jogovelha.com/soap"
    targetNamespace="http://jogovelha.com/soap"
    name="Application">
```

**Explicação:**
- Define todos os namespaces XML utilizados
- `targetNamespace` identifica uniquely este WSDL
- `name` é o nome da aplicação

---

### 2. Types (Tipos de Dados)

```xml
<wsdl:types>
    <xs:schema targetNamespace="http://jogovelha.com/soap"
               elementFormDefault="qualified">

        <!-- Tipo de entrada da operação -->
        <xs:complexType name="criarSala">
            <xs:sequence>
                <xs:element name="porta"
                           type="xs:string"
                           minOccurs="0"
                           nillable="true"/>
            </xs:sequence>
        </xs:complexType>

        <!-- Tipo de saída da operação -->
        <xs:complexType name="criarSalaResponse">
            <xs:sequence>
                <xs:element name="criarSalaResult"
                           type="xs:string"
                           minOccurs="0"
                           nillable="true"/>
            </xs:sequence>
        </xs:complexType>

        <!-- Elementos que referenciam os tipos -->
        <xs:element name="criarSala" type="tns:criarSala"/>
        <xs:element name="criarSalaResponse" type="tns:criarSalaResponse"/>
    </xs:schema>
</wsdl:types>
```

**Principais Tags:**
- **`xs:complexType`** - Define estrutura de dados complexa
- **`xs:sequence`** - Elementos devem aparecer na ordem especificada
- **`xs:element`** - Define um elemento com nome e tipo
- **`minOccurs="0"`** - Elemento opcional
- **`nillable="true"`** - Pode ser null
- **`type="xs:string"`** - Tipo primitivo string do XML Schema

**Explicação dos Tipos:**

1. **criarSala** (Input):
   - Contém um campo `porta` do tipo string
   - Porta é opcional e pode ser null

2. **criarSalaResponse** (Output):
   - Contém um campo `criarSalaResult` do tipo string
   - Retorna o ID da sala criada

---

### 3. Messages (Mensagens)

```xml
<!-- Mensagem de entrada -->
<wsdl:message name="criarSala">
    <wsdl:part name="criarSala" element="tns:criarSala"/>
</wsdl:message>

<!-- Mensagem de saída -->
<wsdl:message name="criarSalaResponse">
    <wsdl:part name="criarSalaResponse" element="tns:criarSalaResponse"/>
</wsdl:message>
```

**Principais Tags:**
- **`wsdl:message`** - Define uma mensagem abstrata
- **`wsdl:part`** - Parte da mensagem (payload)
- **`element`** - Referencia um elemento definido em types

**Explicação:**
- Messages são abstrações das mensagens trocadas
- Cada operação tem uma mensagem de entrada e outra de saída
- `part` conecta a mensagem aos tipos definidos

---

### 4. PortType (Interface do Serviço)

```xml
<wsdl:portType name="Application">
    <wsdl:operation name="criarSala" parameterOrder="criarSala">
        <wsdl:input name="criarSala" message="tns:criarSala"/>
        <wsdl:output name="criarSalaResponse" message="tns:criarSalaResponse"/>
    </wsdl:operation>
</wsdl:portType>
```

**Principais Tags:**
- **`wsdl:portType`** - Interface abstrata do serviço
- **`wsdl:operation`** - Uma operação disponível
- **`wsdl:input`** - Mensagem de entrada da operação
- **`wsdl:output`** - Mensagem de saída da operação
- **`parameterOrder`** - Ordem dos parâmetros

**Explicação:**
- PortType é como uma "interface" em OOP
- Define QUE operações existem, mas não COMO acessá-las
- Especifica entrada e saída de cada operação

---

### 5. Binding (Protocolo Concreto)

```xml
<wsdl:binding name="Application" type="tns:Application">
    <wsdlsoap11:binding
        style="document"
        transport="http://schemas.xmlsoap.org/soap/http"/>

    <wsdl:operation name="criarSala">
        <wsdlsoap11:operation
            soapAction="criarSala"
            style="document"/>

        <wsdl:input name="criarSala">
            <wsdlsoap11:body use="literal"/>
        </wsdl:input>

        <wsdl:output name="criarSalaResponse">
            <wsdlsoap11:body use="literal"/>
        </wsdl:output>
    </wsdl:operation>
</wsdl:binding>
```

**Principais Tags:**
- **`wsdl:binding`** - Vincula portType a um protocolo concreto
- **`wsdlsoap11:binding`** - Especifica SOAP 1.1
- **`style="document"`** - Estilo document (vs RPC)
- **`transport`** - Usa HTTP como transporte
- **`soapAction`** - Header SOAPAction da requisição
- **`use="literal"`** - Payload segue exatamente o schema (vs encoded)

**Explicação:**
- Binding define COMO acessar as operações
- **Document/Literal** significa:
  - Os dados são validados contra o XML Schema
  - Não usa codificação SOAP proprietária
  - Mais interoperável

---

### 6. Service (Endpoint Concreto)

```xml
<wsdl:service name="JogoDaVelhaService">
    <wsdl:port name="Application" binding="tns:Application">
        <wsdlsoap11:address location="http://localhost:8001/"/>
    </wsdl:port>
</wsdl:service>
```

**Principais Tags:**
- **`wsdl:service`** - Define um serviço web concreto
- **`wsdl:port`** - Endpoint específico do serviço
- **`binding`** - Referencia o binding a usar
- **`wsdlsoap11:address`** - URL real do endpoint

**Explicação:**
- Service é o endereço físico onde o serviço está
- Pode haver múltiplas ports (HTTP, HTTPS, etc)
- `location` é a URL que o cliente deve usar

---

## 🔄 Fluxo de uma Requisição SOAP

### 1. Cliente monta a requisição baseado no WSDL:

```xml
POST http://localhost:8001/ HTTP/1.1
Content-Type: text/xml
SOAPAction: criarSala

<?xml version="1.0"?>
<soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ser="http://jogovelha.com/soap">
   <soapenv:Header/>
   <soapenv:Body>
      <ser:criarSala>
         <ser:porta>8080</ser:porta>
      </ser:criarSala>
   </soapenv:Body>
</soapenv:Envelope>
```

**Como o WSDL foi usado:**
- `location` do service → URL do POST
- `soapAction` do binding → Header SOAPAction
- `criarSala` type → Estrutura do body
- Namespace `tns` → xmlns:ser

### 2. Servidor processa e responde:

```xml
HTTP/1.1 200 OK
Content-Type: text/xml

<?xml version='1.0' encoding='UTF-8'?>
<soap11env:Envelope
    xmlns:soap11env="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:tns="http://jogovelha.com/soap">
   <soap11env:Body>
      <tns:criarSalaResponse>
         <tns:criarSalaResult>a89a87f8-5dc6-44f7-94a9-19926b5e7253</tns:criarSalaResult>
      </tns:criarSalaResponse>
   </soap11env:Body>
</soap11env:Envelope>
```

**Como o WSDL define a resposta:**
- `criarSalaResponse` type → Estrutura da resposta
- `criarSalaResult` element → Nome do campo de retorno
- `xs:string` → Tipo do valor retornado

---

## 🛠️ Como Clientes Usam o WSDL

### Abordagem 1: Ferramentas Automáticas (SOAP UI, etc)
1. Importa o WSDL
2. Gera interface automaticamente
3. Cria stub/proxy baseado nos tipos
4. Cliente usa métodos como se fossem locais

### Abordagem 2: Manual (nosso Gateway)
```python
# gateway/main.py extrai informações do WSDL manualmente

# Do WSDL sabemos:
# - Namespace: http://jogovelha.com/soap
# - Operação: criarSala
# - Input: porta (string)
# - Output: criarSalaResult (string)

soap_request = f"""<?xml version="1.0"?>
<soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ser="http://jogovelha.com/soap">
   <soapenv:Body>
      <ser:criarSala>
         <ser:porta>{porta}</ser:porta>
      </ser:criarSala>
   </soapenv:Body>
</soapenv:Envelope>"""

resp = requests.post(SOAP_API_URL, data=soap_request,
                    headers={"Content-Type": "text/xml"})

# Parseia resposta baseado na estrutura do WSDL
match = re.search(r"<tns:criarSalaResult>(.*?)</tns:criarSalaResult>", resp.text)
room_id = match.group(1)
```

---

## 📊 Comparação: WSDL vs REST

| Aspecto | WSDL/SOAP | REST |
|---------|-----------|------|
| **Contrato** | WSDL formal e rígido | Informal (OpenAPI opcional) |
| **Descoberta** | Automática via WSDL | Manual ou via docs |
| **Tipos** | Fortemente tipado (XML Schema) | Fracamente tipado (JSON) |
| **Validação** | Automática contra schema | Manual |
| **Ferramentas** | Geração automática de código | Codificação manual |
| **Verbosidade** | Alta (XML) | Baixa (JSON) |
| **Interoperabilidade** | Excelente (padrão W3C) | Boa (padrão de facto) |

---

## ✅ Vantagens do WSDL

1. **Contrato Formal** - Define exatamente o que o serviço oferece
2. **Validação Automática** - Tipos são validados contra schema
3. **Geração de Código** - Ferramentas geram proxies automaticamente
4. **Descoberta** - Cliente descobre operações dinamicamente
5. **Documentação** - WSDL é auto-documentado
6. **Interoperabilidade** - Padrão suportado por todas as plataformas

---

## 🎯 Uso no Projeto

No nosso projeto, o WSDL permite:

1. **Gateway Python** consome SOAP API:
   - Lê WSDL para entender estrutura
   - Monta requisições XML corretas
   - Parseia respostas baseado no schema

2. **Ferramentas de teste** (SOAP UI, Postman):
   - Importam WSDL
   - Geram requisições automaticamente
   - Validam respostas

3. **Documentação**:
   - WSDL serve como documentação formal
   - Descreve tipos, operações e endpoint

---

## 📝 Comandos Úteis

```bash
# Baixar WSDL
curl http://localhost:8001/?wsdl > service.wsdl

# Testar operação
curl -X POST http://localhost:8001 \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ser="http://jogovelha.com/soap">
   <soapenv:Body>
      <ser:criarSala>
         <ser:porta>8080</ser:porta>
      </ser:criarSala>
   </soapenv:Body>
</soapenv:Envelope>'

# Validar WSDL
xmllint --noout --schema wsdl.xsd service.wsdl
```
