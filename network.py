#!/usr/bin/env python3
"""Asistente opcional para crear una red de trabajo pequeña y verificable."""
from __future__ import annotations

import getpass
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

VERSION = "2026-03-11"
API = "https://api.notion.com/v1"


def ask(prompt: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    return input(f"{prompt}{hint}: ").strip() or default


def yes(prompt: str, default: bool = False) -> bool:
    hint = "S/n" if default else "s/N"
    answer = input(f"{prompt} [{hint}]: ").strip().lower()
    return default if not answer else answer in {"s", "si", "sí", "y", "yes"}


def items(prompt: str, maximum: int) -> list[str]:
    raw = ask(prompt)
    result = list(dict.fromkeys(part.strip() for part in raw.split(",") if part.strip()))
    if len(result) > maximum:
        raise ValueError(f"Máximo {maximum} elementos en esta etapa.")
    return result


def page_id(value: str) -> str:
    match = re.search(r"([a-fA-F0-9]{32})(?:[?#]|$)", value.replace("-", ""))
    if not match:
        raise ValueError("Indica una URL de página de Notion o un ID válido.")
    raw = match.group(1).lower()
    return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"


def rich(content: str) -> list[dict]:
    return [{"type": "text", "text": {"content": content[:2000]}}]


def paragraph(content: str) -> dict:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich(content)}}


class Notion:
    def __init__(self, token: str):
        self.token = token

    def call(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(API + path, data=body, method=method, headers={
            "Authorization": "Bearer " + self.token,
            "Notion-Version": VERSION,
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            # Never print the token or full request body.
            raise RuntimeError(f"Notion devolvió HTTP {exc.code} en {method} {path}.") from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"Resultado incierto de {method} {path}; lee el destino antes de reintentar.") from None

    def children(self, parent: str) -> list[dict]:
        result: list[dict] = []
        cursor = None
        while True:
            query = "?page_size=100" + ("&start_cursor=" + urllib.parse.quote(cursor) if cursor else "")
            data = self.call("GET", f"/blocks/{parent}/children{query}")
            result.extend(data.get("results", []))
            if not data.get("has_more"):
                return result
            cursor = data.get("next_cursor")
            if not cursor:
                raise RuntimeError("Paginación incompleta; no se puede descartar un duplicado.")


def schema() -> dict:
    return {
        "Nombre": {"title": {}},
        "Tipo": {"select": {"options": [{"name": n} for n in ("Objetivo", "Tema", "Acción", "Evidencia", "Agente")]}},
        "Estado": {"select": {"options": [{"name": n} for n in ("Borrador", "Activo", "Bloqueado", "Verificado")]}},
        "Owner": {"rich_text": {}},
        "Escritor": {"rich_text": {}},
        "Siguiente acción": {"rich_text": {}},
        "Destino": {"url": {}},
        "Fuente": {"url": {}},
    }


def title_of(block: dict) -> str:
    if block.get("type") != "child_page":
        return ""
    return block.get("child_page", {}).get("title", "")


def create_notion(plan: dict) -> str:
    parent = page_id(ask("URL o ID de una página tuya compartida con la integración de Notion"))
    token = getpass.getpass("Token de la integración de Notion (entrada oculta; no se guarda): ").strip()
    if not token:
        raise ValueError("Falta la conexión a Notion; no se creó nada.")
    client = Notion(token)
    parent_page = client.call("GET", f"/pages/{parent}")
    if parent_page.get("id", "").replace("-", "") != parent.replace("-", ""):
        raise RuntimeError("La página padre no coincide con el ID solicitado.")
    root_title = "Red de trabajo · " + plan["name"]
    existing = [b for b in client.children(parent) if title_of(b) == root_title]
    if existing:
        raise RuntimeError("Ya existe una página con ese nombre bajo el padre. Revísala antes de repetir la instalación.")
    print(f"Crearé 1 página y 1 base de datos bajo la página {parent}.")
    if not yes("¿Autorizas crear esta red en tu Notion?"):
        print("No se creó nada en Notion.")
        return ""
    root = client.call("POST", "/pages", {
        "parent": {"type": "page_id", "page_id": parent},
        "properties": {"title": {"type": "title", "title": rich(root_title)}},
        "children": [
            paragraph("Propósito: " + plan["purpose"]),
            paragraph("Cada objeto tiene un owner y un escritor. Una acción conserva objetivo, destino, evidencia y siguiente paso. No dupliques una entrada antes de buscarla."),
            paragraph("Estado inicial: borrador. El inventario de esta página no demuestra ejecución ni adopción."),
        ],
    })
    root_id = root["id"]
    reread = client.call("GET", f"/pages/{root_id}")
    if reread.get("id") != root_id:
        raise RuntimeError("La página fue creada pero su lectura de vuelta falló. No reintentes a ciegas.")
    if not client.children(root_id):
        raise RuntimeError("No se pudo leer el contenido del índice creado; revisa la página.")
    db = client.call("POST", "/databases", {
        "parent": {"type": "page_id", "page_id": root_id},
        "title": rich("Nodos"),
        "description": rich("Objetivos, temas, acciones, evidencias y agentes sin bases duplicadas."),
        "initial_data_source": {"properties": schema()},
    })
    db_id = db["id"]
    database = client.call("GET", f"/databases/{db_id}")
    if database.get("id") != db_id:
        raise RuntimeError("La base fue creada pero su lectura de vuelta falló.")
    sources = database.get("data_sources") or db.get("data_sources") or []
    if len(sources) != 1 or not sources[0].get("id"):
        raise RuntimeError("No se pudo identificar la fuente de datos única. La página existe; revisa el enlace antes de continuar.")
    source_id = sources[0]["id"]
    source = client.call("GET", f"/data_sources/{source_id}")
    if source.get("id") != source_id or not set(schema()).issubset(source.get("properties", {})):
        raise RuntimeError("El esquema no coincide en la lectura de vuelta; no se cargarán nodos.")
    client.call("PATCH", f"/data_sources/{source_id}", {"properties": {
        "Relacionado con": {"relation": {"data_source_id": source_id, "single_property": {}}}
    }})
    source = client.call("GET", f"/data_sources/{source_id}")
    if source.get("properties", {}).get("Relacionado con", {}).get("type") != "relation":
        raise RuntimeError("La relación entre nodos no quedó instalada; revisa el esquema.")
    goal_ids = []
    for kind, names in (("Objetivo", plan["goals"]), ("Tema", plan["topics"])):
        for index, name in enumerate(names):
            properties = {
                "Nombre": {"title": rich(name)},
                "Tipo": {"select": {"name": kind}},
                "Estado": {"select": {"name": "Borrador"}},
                "Owner": {"rich_text": rich(plan["owner"])},
                "Siguiente acción": {"rich_text": rich("Definir alcance y primer checkpoint")},
            }
            if kind == "Tema" and plan["links"].get(name) is not None:
                properties["Relacionado con"] = {"relation": [{"id": goal_ids[plan["links"][name]]}]}
            node = client.call("POST", "/pages", {
                "parent": {"type": "data_source_id", "data_source_id": source_id},
                "properties": properties,
            })
            verify = client.call("GET", f"/pages/{node['id']}")
            observed = verify.get("properties", {})
            observed_title = "".join(part.get("plain_text", part.get("text", {}).get("content", ""))
                                     for part in observed.get("Nombre", {}).get("title", []))
            observed_type = observed.get("Tipo", {}).get("select", {}).get("name")
            if verify.get("id") != node["id"] or observed_title != name or observed_type != kind:
                raise RuntimeError("Un nodo se creó sin readback; revisa la base antes de reintentar.")
            if kind == "Objetivo":
                goal_ids.append(node["id"])
            elif plan["links"].get(name) is not None:
                related = verify.get("properties", {}).get("Relacionado con", {}).get("relation", [])
                if goal_ids[plan["links"][name]] not in [r.get("id") for r in related]:
                    raise RuntimeError("El enlace de un tema no aparece en el readback; revisa el nodo.")
    print("Red creada y objetos leídos de vuelta:", root.get("url", f"https://www.notion.so/{root_id.replace('-', '')}"))
    return root_id


def create_local(plan: dict) -> str:
    target = Path(ask("Carpeta nueva para la red local", "./mi-red-de-trabajo")).expanduser()
    if target.exists():
        raise ValueError("La carpeta ya existe; elige otra o revísala antes de repetir.")
    if not yes(f"¿Autorizas crear la red en {target}?"):
        return ""
    target.mkdir(parents=True)
    (target / "red.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (target / "README.md").write_text(
        "# " + plan["name"] + "\n\n" + plan["purpose"] + "\n\n"
        "## Objetivos\n" + "".join(f"- {v}\n" for v in plan["goals"]) + "\n"
        "## Temas\n" + "".join(f"- {v}\n" for v in plan["topics"]) + "\n"
        "Un objeto, un owner y un escritor; conserva fuente, destino, evidencia y siguiente acción.\n",
        encoding="utf-8",
    )
    print("Red local creada:", target.resolve())
    return str(target.resolve())


def main() -> int:
    print("Diseñemos tu red de trabajo. Notion es una opción recomendada; puedes elegir archivos locales.")
    name = ask("Nombre corto de tu red", "Mi red")
    purpose = ask("¿Para qué quieres usarla?", "Coordinar mis objetivos y proyectos")
    goals = items("Hasta 3 objetivos actuales, separados por comas", 3)
    topics = items("Hasta 5 temas o proyectos actuales, separados por comas", 5)
    if not goals:
        raise ValueError("Indica al menos un objetivo real; no crearé objetivos ficticios.")
    owner = ask("¿Quién decide sobre estos objetivos?", "Yo")
    links = {}
    if topics:
        print("Relaciona cada tema con un objetivo; Enter lo deja sin vínculo.")
        for topic in topics:
            for number, goal in enumerate(goals, 1):
                print(f"  {number}. {goal}")
            selected = ask(f"Objetivo de «{topic}» (número)")
            if selected:
                if not selected.isdigit() or not 1 <= int(selected) <= len(goals):
                    raise ValueError("Vínculo de tema inválido; no se creó nada.")
                links[topic] = int(selected) - 1
    plan = {"name": name, "purpose": purpose, "goals": goals, "topics": topics, "owner": owner, "links": links}
    print("\nPropuesta de red inicial (sin tareas ni agentes inventados):")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    print("Estructura: un índice y una base de nodos; cada nodo admite tipo, estado, owner, escritor, siguiente acción, fuente y destino.")
    choice = ask("Destino: Notion (recomendado) o local", "Notion").lower()
    if choice == "notion":
        create_notion(plan)
    elif choice in {"local", "archivos", "markdown"}:
        create_local(plan)
    else:
        print("Destino no reconocido; sin cambios.")
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, EOFError, KeyboardInterrupt) as exc:
        print(f"Configuración detenida: {exc}", file=sys.stderr)
        raise SystemExit(2)
