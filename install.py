#!/usr/bin/env python3
"""Instala skills portables en Codex y Claude, sin sobrescribir otras skills."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
QUESTIONS = {
    "code_host": "Código: GitHub, GitLab, local u otro",
    "knowledge": "Conocimiento: Notion, Obsidian, Docs, archivos u otro",
    "structured_data": "Datos: SQLite, Postgres, hoja u otro",
    "files": "Archivos: iCloud, Drive, Dropbox, OneDrive, local u otro",
    "communications": "Comunicaciones: correo o mensajería preferidos",
    "automation": "Automatización: herramienta preferida o manual",
}
OPTIONAL_CLIS = ("git", "gh", "sqlite3", "composio", "obsidian", "runpodctl")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest() -> dict[str, str]:
    record = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    declared = record["skills"]
    actual = {p.name: sha(p / "SKILL.md") for p in (HERE / "skills").iterdir()
              if p.is_dir() and (p / "SKILL.md").is_file()}
    if declared != actual:
        raise ValueError("El paquete no coincide con su manifiesto; instalación detenida.")
    catalog = HERE / "skills" / "portable-tools" / "references" / "tool-catalog.md"
    if sha(catalog) != record["tool_catalog_sha256"]:
        raise ValueError("El catálogo de herramientas no coincide con el manifiesto.")
    return declared


def destinations(args) -> dict[str, Path]:
    codex = args.codex_root or Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills"
    claude = args.claude_root or Path.home() / ".claude" / "skills"
    result = {"Codex": Path(codex).expanduser(), "Claude": Path(claude).expanduser()}
    if result["Codex"].resolve() == result["Claude"].resolve():
        raise ValueError("Las rutas de Codex y Claude deben ser diferentes.")
    return result


def check(expected: dict[str, str], targets: dict[str, Path]) -> int:
    failures = 0
    for label, root in targets.items():
        same = missing = different = 0
        for name, digest in expected.items():
            path = root / name / "SKILL.md"
            if not path.exists():
                missing += 1
            elif sha(path) == digest:
                same += 1
            else:
                different += 1
        failures += missing + different
        print(f"{label}: {same} idénticas, {missing} ausentes, {different} distintas en {root}")
    left = targets["Codex"] / "portable-tools" / "references" / "profile.json"
    right = targets["Claude"] / "portable-tools" / "references" / "profile.json"
    catalog_sha = sha(HERE / "skills" / "portable-tools" / "references" / "tool-catalog.md")
    for label, root in targets.items():
        catalog = root / "portable-tools" / "references" / "tool-catalog.md"
        correct = catalog.is_file() and sha(catalog) == catalog_sha
        print(f"Catálogo {label}: {'idéntico' if correct else 'AUSENTE O DISTINTO'}")
        failures += not correct
    if left.exists() and right.exists():
        equal = sha(left) == sha(right)
        print("Perfil en ambas: " + ("idéntico" if equal else "distinto"))
        failures += not equal
    else:
        print("Perfil en ambas: NO VERIFICADO")
        failures += 1
    print("Descubrimiento y uso por cada aplicación: NO VERIFICADOS hasta probarlos allí.")
    return 0 if failures == 0 else 2


def install(expected: dict[str, str], targets: dict[str, Path], repair: bool = False) -> int:
    print("Instalación propuesta en las dos ubicaciones:")
    for label, root in targets.items():
        print(f"  {label}: {root}; CLI detectada: {'sí' if shutil.which(label.lower()) else 'no'}")
    print("Herramientas opcionales detectadas: " + ", ".join(
        f"{name}={'sí' if shutil.which(name) else 'no'}" for name in OPTIONAL_CLIS))
    collisions = [str(root / name) for root in targets.values() for name, digest in expected.items()
                  if (root / name).exists() and
                  (not (root / name / "SKILL.md").is_file() or sha(root / name / "SKILL.md") != digest)]
    source_catalog = HERE / "skills" / "portable-tools" / "references" / "tool-catalog.md"
    for root in targets.values():
        catalog = root / "portable-tools" / "references" / "tool-catalog.md"
        if catalog.exists() and sha(catalog) != sha(source_catalog):
            collisions.append(str(catalog))
    if collisions and not repair:
        print("Hay versiones distintas; no se sobrescriben sin --repair: " + ", ".join(collisions))
        return 2
    if collisions:
        print("--repair actualizará sólo el SKILL.md de estas rutas desde el paquete verificado:")
        for item in collisions:
            print("  " + item)
    print("Preferencias opcionales. Enter = sin decidir. No escribas secretos.")
    answers = {}
    for key, question in QUESTIONS.items():
        value = input(question + ": ").strip()
        if any(marker in value.lower() for marker in ("password=", "token=", "api_key=", "apikey=")):
            raise ValueError("El perfil no acepta credenciales.")
        answers[key] = value or None
    reply = input("¿Permites instalar estas skills en Codex y Claude? [s/N]: ").strip().lower()
    if reply not in {"s", "si", "sí", "y", "yes"}:
        print("Cancelado sin cambios.")
        return 1
    existing_profiles = [root / "portable-tools" / "references" / "profile.json"
                         for root in targets.values()]
    existing_profiles = [p for p in existing_profiles if p.is_file()]
    if len(existing_profiles) == 2 and sha(existing_profiles[0]) != sha(existing_profiles[1]):
        print("Los perfiles ya difieren; resuelve esa preferencia antes de actualizar.")
        return 2
    profile_source = existing_profiles[0] if existing_profiles else HERE / "skills" / "portable-tools" / "references" / "profile.json"
    profile = json.loads(profile_source.read_text(encoding="utf-8"))
    profile["preferences"].update({key: value for key, value in answers.items() if value})
    profile["status"] = "configurado" if any(profile["preferences"].values()) else "sin_decidir"
    rendered = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    for root in targets.values():
        root.mkdir(parents=True, exist_ok=True)
        for name, digest in expected.items():
            source = HERE / "skills" / name
            target = root / name
            if not target.exists():
                shutil.copytree(source, target)
            elif (target / "SKILL.md").is_file() and sha(target / "SKILL.md") != digest:
                shutil.copy2(source / "SKILL.md", target / "SKILL.md")
            elif not (target / "SKILL.md").exists():
                shutil.copy2(source / "SKILL.md", target / "SKILL.md")
            if name == "portable-tools":
                (target / "references").mkdir(parents=True, exist_ok=True)
                catalog = target / "references" / "tool-catalog.md"
                if not catalog.exists() or sha(catalog) != sha(source_catalog):
                    shutil.copy2(source_catalog, catalog)
        (root / "portable-tools" / "references" / "profile.json").write_text(rendered, encoding="utf-8")
    return check(expected, targets)


def main() -> int:
    parser = argparse.ArgumentParser(description="Instala skills portables en Codex y Claude.")
    parser.add_argument("--codex-root", type=Path)
    parser.add_argument("--claude-root", type=Path)
    parser.add_argument("--check", action="store_true", help="Sólo comprueba copias existentes.")
    parser.add_argument("--repair", action="store_true", help="Con permiso, actualiza sólo SKILL.md del paquete.")
    args = parser.parse_args()
    expected = manifest()
    targets = destinations(args)
    return check(expected, targets) if args.check else install(expected, targets, args.repair)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, EOFError, KeyboardInterrupt) as exc:
        print(f"Instalación detenida: {exc}", file=sys.stderr)
        raise SystemExit(2)
