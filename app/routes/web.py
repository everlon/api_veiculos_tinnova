# /Users/everlonpassos/Downloads/tinnova/app/routes/web.py
from typing import Optional
from fastapi import APIRouter, Request, Form, Query, Path, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import os
import pathlib

from app.services.veiculo import MARCAS_VALIDAS

# Caminho base do projeto (um nível acima de 'app')
# tinnova/app/routes/web.py -> tinnova/
BASE_PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

web_router = APIRouter()

web = Jinja2Templates(directory=os.path.join('web'))
templates = Jinja2Templates(directory=os.path.join(BASE_PROJECT_DIR, 'web', 'templates'))

# Adicionar um filtro 'truncate' ao ambiente Jinja2, se não estiver disponível por padrão
# templates.env.filters['truncate'] = lambda s, length=255, killwords=False, end='...': s[:length] if len(s) > length else s

# URL base da sua API de Veículos Tinnova (FastAPI)
# Ajuste a porta se sua API FastAPI rodar em uma porta diferente de 8000
BASE_API_URL = os.environ.get("TINNOVA_API_URL", "http://localhost:8000/api/v1")

# --- Funções Auxiliares para interagir com a API ---
def get_api_data(endpoint, params=None):
    try:
        url = f"{BASE_API_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Levanta HTTPError para respostas 4xx/5xx
        return response.json(), None
    except requests.exceptions.HTTPError as e:
        # Tenta extrair uma mensagem de erro mais útil do corpo da resposta JSON, se disponível
        error_message = f"Erro HTTP da API: {e.response.status_code}"
        try:
            error_detail = e.response.json().get("detail", e.response.text)
            error_message += f" - {error_detail}"
        except ValueError: # Se o corpo do erro não for JSON
            error_message += f" - {e.response.text}"
        return None, error_message
    except requests.exceptions.RequestException as e:
        return None, f"Erro de conexão com a API: {e}"
    except ValueError: # Erro ao decodificar JSON
        return None, "Resposta inválida da API (não é JSON)."

def post_api_data(endpoint, data=None):
    try:
        url = f"{BASE_API_URL}{endpoint}"
        response = requests.post(url, json=data)
        # Não levantar erro aqui imediatamente, pois queremos inspecionar o status_code e o corpo
        return response, None
    except requests.exceptions.RequestException as e:
        return None, f"Erro de conexão com a API: {e}"

def put_api_data(endpoint, data=None):
    try:
        url = f"{BASE_API_URL}{endpoint}"
        response = requests.put(url, json=data)
        return response, None
    except requests.exceptions.RequestException as e:
        return None, f"Erro de conexão com a API: {e}"

def delete_api_data(endpoint):
    try:
        url = f"{BASE_API_URL}{endpoint}"
        response = requests.delete(url)
        return response, None
    except requests.exceptions.RequestException as e:
        return None, f"Erro de conexão com a API: {e}"


# O prefixo /ui será adicionado pelo FastAPI ao montar o app Flask

@web_router.get('/')
async def index(request: Request):
    return web.TemplateResponse('index.html', {"request": request})

@web_router.get('/fragment/veiculos-lista', response_class=HTMLResponse)
async def fragment_veiculos_lista(
    request: Request,
    marca: str = Query(None),
    ano_str: Optional[str] = Query(None, alias="ano"),
    cor: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10)
):
    ano_int: Optional[int] = None
    if ano_str and ano_str.strip():
        try:
            ano_int = int(ano_str)
        except ValueError:
            pass

    params = {
        'marca': marca,
        'ano': ano_int,
        'cor': cor,
        'skip': skip,
        'limit': limit
    }
    params = {k: v for k, v in params.items() if v is not None}
    veiculos_data, error = get_api_data("/veiculos/", params=params)

    if error:
        return HTMLResponse(content=f"<div class='error'>Erro ao carregar veículos: {error}</div>", status_code=500)
    try:
        response = templates.TemplateResponse(
            '_lista_veiculos.html',
            {"request": request, "veiculos": veiculos_data if veiculos_data else []}
        )
        return response
    except Exception as e_template:
        # Logar o traceback completo aqui seria ideal
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"<div class='error'>Erro interno ao renderizar a lista.</div>", status_code=500)


@web_router.get('/fragment/veiculo-form-criar', response_class=HTMLResponse)
async def fragment_veiculo_form_criar(request: Request):
    return templates.TemplateResponse(
        '_form_veiculo.html',
        {"request": request, "veiculo": {}, "marcas_validas": MARCAS_VALIDAS}
    )

@web_router.get('/fragment/veiculos-estatisticas', response_class=HTMLResponse)
async def fragment_veiculos_estatisticas(request: Request):
    stats_data, error = get_api_data("/veiculos/estatisticas/geral")
    if error:
        return HTMLResponse(content=f"<div class='error'>Erro ao carregar estatísticas: {error}</div>", status_code=500)
    return templates.TemplateResponse(
        '_estatisticas.html',
        {"request": request, "stats": stats_data if stats_data else {}}
    )

@web_router.get('/fragment/veiculo-detalhes/{veiculo_id}', response_class=HTMLResponse)
async def fragment_veiculo_detalhes(request: Request, veiculo_id: int = Path(...)):
    veiculo_data, error = get_api_data(f"/veiculos/{veiculo_id}")
    if error:
        status_code = 500
        if "404" in error or (hasattr(error, 'response') and error.response.status_code == 404):
            status_code = 404
        return HTMLResponse(
            content=f"<div class='error'>Erro ao carregar detalhes do veículo {veiculo_id}: {error}</div>",
            status_code=status_code
        )
    return templates.TemplateResponse('_detalhes_veiculo.html', {"request": request, "veiculo": veiculo_data})

@web_router.get('/fragment/veiculo-form-editar/{veiculo_id}', response_class=HTMLResponse)
async def fragment_veiculo_form_editar(request: Request, veiculo_id: int = Path(...)):
    veiculo_data, error = get_api_data(f"/veiculos/{veiculo_id}")
    if error:
        status_code = 500
        if "404" in error or (hasattr(error, 'response') and error.response.status_code == 404):
            status_code = 404
        return HTMLResponse(
            content=f"<div class='error'>Erro ao carregar veículo para edição: {error}</div>",
            status_code=status_code
        )
    return templates.TemplateResponse(
        '_form_veiculo_editar.html',
        {"request": request, "veiculo": veiculo_data, "marcas_validas": MARCAS_VALIDAS}
    )

@web_router.post('/action/veiculo-criar', response_class=HTMLResponse)
async def action_veiculo_criar(
    request: Request,
    veiculo: str = Form(...),
    marca: str = Form(...),
    ano: int = Form(...),
    descricao: str = Form(None),
    vendido: bool = Form(False) # FastAPI converte "true" para True, ausência para False se o tipo for bool
):
    form_data_dict = {
        "veiculo": veiculo,
        "marca": marca,
        "ano": ano,
        "descricao": descricao,
        "vendido": vendido
    }
    # A conversão de 'ano' para int já é feita pelo FastAPI com o type hint
    # A conversão de 'vendido' para bool também

    api_response, error_conn = post_api_data("/veiculos/", data=form_data_dict)

    if error_conn: # Erro de conexão com a API
        return templates.TemplateResponse(
            '_form_veiculo.html',
            {"request": request, "veiculo": form_data_dict, "form_error": f"Erro de comunicação com API: {error_conn}", "marcas_validas": MARCAS_VALIDAS},
            status_code=500
        )

    if api_response.status_code == 201:
        success_message = "<div id='form-messages' class='success' style='color: green; padding: 10px; border: 1px solid green; margin-bottom: 10px;'>Veículo criado com sucesso!</div>"
        return HTMLResponse(content=success_message, headers={'HX-Trigger': 'reloadVeiculosListEvent'})

    else: # Erro da API (validação, etc.)
        error_details = "Erro desconhecido ao criar veículo."
        print(error_details)
        try:
            error_data = api_response.json()
            if 'detail' in error_data:
                if isinstance(error_data['detail'], list): # FastAPI validation errors
                     error_details = "; ".join([f"{e.get('loc', ['campo'])[-1]}: {e.get('msg', '')}" for e in error_data['detail']])
                else:
                    error_details = str(error_data['detail'])
            elif 'errors' in error_data and isinstance(error_data['errors'], list): # Outro formato de erro
                 error_details = "; ".join([f"{e.get('loc', ['campo'])[-1]}: {e.get('msg', '')}" for e in error_data['errors']])
        except ValueError: # Se a resposta de erro não for JSON
            error_details = api_response.text or f"Erro {api_response.status_code} da API."

        response = templates.TemplateResponse(
            '_form_veiculo.html',
            {"request": request, "veiculo": form_data_dict, "form_error": error_details, "marcas_validas": MARCAS_VALIDAS},
            status_code=api_response.status_code
        )
        response.headers["HX-Reswap"] = "innerHTML" # Instrui HTMX a fazer o swap
        return response

@web_router.put('/action/veiculo-editar/{veiculo_id}', response_class=HTMLResponse)
async def action_veiculo_editar(
    request: Request,
    veiculo_id: int = Path(...),
    veiculo: str = Form(...),
    marca: str = Form(...),
    ano: int = Form(...),
    descricao: str = Form(None),
    vendido: bool = Form(False)
):
    form_data_dict = {
        "veiculo": veiculo,
        "marca": marca,
        "ano": ano,
        "descricao": descricao,
        "vendido": vendido
    }
    print(f"DEBUG: Dados recebidos no formulário de edição para ID {veiculo_id}: {form_data_dict}") 

    api_response, error_conn = put_api_data(f"/veiculos/{veiculo_id}", data=form_data_dict)

    if error_conn:
        form_data_dict['id'] = veiculo_id # Adiciona ID para o template
        return templates.TemplateResponse(
            '_form_veiculo_editar.html',
            {"request": request, "veiculo": form_data_dict, "form_error": f"Erro de comunicação com API: {error_conn}", "marcas_validas": MARCAS_VALIDAS},
            status_code=500
        )

    if api_response.status_code == 200:
        updated_veiculo = api_response.json()
        return templates.TemplateResponse('_detalhes_veiculo.html', {"request": request, "veiculo": updated_veiculo})
    else:
        error_details = f"Erro ao atualizar veículo (ID: {veiculo_id})."
        try:
            error_data = api_response.json()
            if 'detail' in error_data:
                if isinstance(error_data['detail'], list):
                     error_details = "; ".join([f"{e.get('loc', ['campo'])[-1]}: {e.get('msg', '')}" for e in error_data['detail']])
                else:
                    error_details = str(error_data['detail'])
            elif 'errors' in error_data and isinstance(error_data['errors'], list):
                 error_details = "; ".join([f"{e.get('loc', ['campo'])[-1]}: {e.get('msg', '')}" for e in error_data['errors']])
        except ValueError:
            error_details = api_response.text or f"Erro {api_response.status_code} da API."
        print(f"DEBUG: Erro da API ao editar (ID: {veiculo_id}): {error_details}") 


        form_data_dict['id'] = veiculo_id
        current_veiculo_data, _ = get_api_data(f"/veiculos/{veiculo_id}") # Pega os dados atuais para repopular

        resposta_com_erro = None

        if current_veiculo_data:
            # Mescla dados atuais com os do formulário, priorizando os do formulário
            # Isso é útil se a API não retornar os dados submetidos em caso de erro
            merged_veiculo_data = {**current_veiculo_data, **form_data_dict}
            resposta_com_erro = templates.TemplateResponse(
                '_form_veiculo_editar.html',
                {"request": request, "veiculo": merged_veiculo_data, "form_error": error_details, "marcas_validas": MARCAS_VALIDAS},
                status_code=api_response.status_code
            )
            resposta_com_erro.headers["HX-Reswap"] = "innerHTML"
            return resposta_com_erro

        resposta_com_erro = templates.TemplateResponse(
            '_form_veiculo_editar.html',
            {"request": request, "veiculo": form_data_dict, "form_error": error_details, "marcas_validas": MARCAS_VALIDAS},
            status_code=api_response.status_code
        )
        resposta_com_erro.headers["HX-Reswap"] = "innerHTML"
        return resposta_com_erro


@web_router.delete('/action/veiculo-remover/{veiculo_id}', response_class=HTMLResponse)
async def action_veiculo_remover(veiculo_id: int = Path(...)):
    api_response, error_conn = delete_api_data(f"/veiculos/{veiculo_id}")

    if error_conn:
        return HTMLResponse(
            content=f"<div class='error' hx-swap-oob='true' id='error-messages'>Erro de comunicação com API: {error_conn}</div>",
            status_code=500
        )

    if api_response.status_code == 200 or api_response.status_code == 204: # OK ou No Content
        return HTMLResponse(content="", status_code=200)
    elif api_response.status_code == 404:
        return HTMLResponse(content="", status_code=200) # HTMX remove o item da UI
    else:
        error_msg = f"Erro ao remover veículo (ID: {veiculo_id}). Status: {api_response.status_code}"
        try:
            error_data = api_response.json()
            error_msg = error_data.get("detail", error_msg)
        except ValueError:
            error_msg = api_response.text or error_msg
        return HTMLResponse(
            content=f"<div class='error' hx-swap-oob='true' id='error-messages'>{error_msg}</div>",
            status_code=api_response.status_code
        )