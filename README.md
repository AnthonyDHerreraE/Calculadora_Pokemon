# ⚡ PokeCalc Uranium • Calculadora de Tipos Pokémon (Gen VI+)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/PySide6-Qt_6.6%2B-41CD52.svg?logo=qt&logoColor=white)](https://wiki.qt.io/Qt_for_Python)
[![Network](https://img.shields.io/badge/API-PokéAPI_v2-EF5350.svg)](https://pokeapi.co/)
[![Tests](https://img.shields.io/badge/Tests-47%2F47_Passing-success.svg)](#suite-de-pruebas-unitarias)
[![Platform](https://img.shields.io/badge/Platform-Windows_x64-0078D6.svg?logo=windows&logoColor=white)](#distribución-y-despliegue)

Aplicación nativa de escritorio de alto rendimiento para el análisis matemático defensivo y de cobertura ofensiva (STAB) de Pokémon. Construida con **PySide6 (Qt 6)** bajo principios estrictos de **Clean Architecture**, **Domain-Driven Design (DDD)** y desacoplamiento **MVC**.

Integra las mecánicas canónicas de la **Generación VI en adelante** y soporte exhaustivo para el fan-game **Pokémon Uranium** (incorporando el **Tipo Nuclear** con sus 361 cruces matemáticos).

---

## 📸 Interfaz de Usuario y Arquitectura Visual

La ventana principal está optimizada para monitores panorámicos (16:9) dividida en dos paneles con navegación por pestañas:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ⚡ CALCULADORA DE TIPOS POKÉMON • GEN VI+                          [FASE 6 • RELEASE] │
├──────────────────────────────────────────┬─────────────────────────────────────────────┤
│ [🔍 Buscar Pokémon (Ctrl+F)...] [Buscar] │ [🛡️ Análisis Defensivo] [⚔️ Cobertura STAB]   │
│ ---------------------------------------- │ ------------------------------------------- │
│  [Normal]  [Fuego]    [Agua]    [Planta] │ ⚠️ VULNERABILIDAD EXTREMA (x4)             │
│  [Electr]  [Hielo]    [Lucha]   [Veneno] │  • Planta [x2 Agua • x2 Tierra]             │
│  [Tierra]  [Volador]  [Psíquic] [Bicho]  │  • Nuclear [x2 Agua • x2 Tierra]            │
│  [Roca]    [Fantasma] [Dragón]  [Siniest]│ ------------------------------------------- │
│  [Acero]   [Hada]     [☢ NUCLEAR]       │ 🛡️ RESISTENCIAS (x0.5)                      │
│                                          │  • Fuego [x0.5 Agua • x1 Tierra]            │
│ [ Restablecer Selección (Esc) ]          │  • Acero [x1 Agua • x0.5 Tierra]            │
│                                          │ ------------------------------------------- │
│                                          │ ⛔ INMUNIDADES (x0)                          │
│                                          │  • Eléctrico [x2 Agua • x0 Tierra]          │
└──────────────────────────────────────────┴─────────────────────────────────────────────┘
```

---

## ✨ Características Principales

### 1. 🛡️ Análisis Defensivo con Desglose Matemático
- **Cálculo Multiplicativo Preciso**: Cruce simultáneo de debilidades, resistencias e inmunidades para mono-tipos y doble-tipos.
- **Desglose Explicativo en Chips**: En Pokémon de doble tipo, cada `TypeChip` muestra la fórmula matemática exacta en HTML enriquecido con el color oficial de cada tipo:
  $$\text{Ejemplo: Swampert (Agua / Tierra) frente a Eléctrico} \longrightarrow \text{x2 Agua} \bullet \text{x0 Tierra} = \mathbf{x0\text{ (Inmune)}}$$
  $$\text{Ejemplo: Swampert (Agua / Tierra) frente a Planta} \longrightarrow \text{x2 Agua} \bullet \text{x2 Tierra} = \mathbf{x4\text{ (Doble debilidad)}}$$
- **Ocultamiento Inteligente**: Las categorías sin tipos asociados se ocultan automáticamente para mantener una UI limpia y concisa.

### 2. ⚔️ Cobertura Ofensiva STAB con Rastreo de Fuente
- **Pestaña Dedicada (`QTabWidget`)**: Pestaña independiente "⚔️ Cobertura Ofensiva (STAB)" que analiza el mejor daño posible frente a cada uno de los 19 tipos defensores.
- **Lógica de Máximo Daño**:
  $$\text{Daño STAB Máximo}(D) = \max\left(\text{Matriz}[T_1, D],\, \text{Matriz}[T_2, D]\right)$$
- **Resolución de Ambigüedad STAB**: Cada chip ofensivo incluye un subtítulo dinámico indicando el origen del golpe (ej. *vía Tierra*, *vía Agua*, o *vía Agua / Tierra* en caso de empate).

### 3. ☢️ Soporte Oficial para Pokémon Uranium (Tipo Nuclear)
- **Matriz Expandida 19x19 (361 combinaciones)**:
  - **Ataque Nuclear**: Causa daño crítico (**x2.0**) a todos los tipos del juego, excepto a **Acero (x0.5)** y **Nuclear (x0.5)**.
  - **Defensa Nuclear**: Es vulnerable (**x2.0**) frente a todos los tipos del juego, resistiendo únicamente ataques de tipo **Nuclear (x0.5)**.
- **Identidad Visual Neón**: Botones y chips radioactivos con código `#39FF14`.

### 4. ⚡ Buscador Híbrido Offline (0 ms) & PokéAPI v2
- **Capa Local-First (0 ms)**: Consulta en memoria mediante [`custom_pokedex.json`](file:///c:/Users/AnthonyHerrera/OneDrive/Documentos/Calculadora_Pokemon/src/data/custom_pokedex.json) con ~189 Fakemon y formas atómicas de Pokémon Uranium (*Nucleon, Urayne, Baariette, Corsoreef-Nuclear*, etc.).
- **Capa Remota Asíncrona (`QThread`)**: Fallback a PokéAPI v2 oficial ejecutado en un hilo secundario sin congelar la interfaz gráfica (*UI Thread*).
- **Caché en Memoria**: Evita peticiones de red redundantes.

### 5. 🎯 UX Nativa de Escritorio: Hotkeys & Typeahead
- **Autocompletado Reactivo (`QCompleter`)**: Búsqueda por subcadenas (`MatchContains`) insensible a mayúsculas. Poblado inicial con la Pokédex de Uranium y carga asíncrona de 1300+ especies oficiales.
- **Selección en 1 Clic**: Elegir una sugerencia en el menú desplegable dispara la búsqueda automáticamente sin necesidad de presionar `Enter` dos veces.
- **Atajos de Teclado Globales**:
  - `Ctrl + F` (o `Cmd + F` en macOS): Enfoca la barra de búsqueda y resalta todo el texto para una nueva consulta inmediata.
  - `Esc`: Limpia el texto de búsqueda y deselecciona los tipos activos en la calculadora.

---

## 🏛️ Clean Architecture & Estructura del Código

El proyecto separa de forma estricta el dominio matemático de la capa de interfaz gráfica:

```text
Calculadora_Pokemon/
│
├── main.py                     # Punto de entrada de la aplicación Qt
├── run_tests.py                # Runner del conjunto de pruebas unitarias
├── requirements.txt            # Dependencias del proyecto
├── .gitignore                  # Exclusiones de Git (build/, dist/, *.spec)
├── README.md                   # Documentación técnica
│
├── src/
│   ├── core/                   # [CAPA DE DOMINIO - Sin dependencias UI]
│   │   ├── enums.py            # Enumeraciones tipadas (PokemonType, EffectivenessCategory)
│   │   ├── constants.py        # Matriz canónica 19x19 de efectividades
│   │   ├── models.py           # DTOs inmutables (TypeEffectivenessResult, OffensiveCoverageResult)
│   │   ├── calculator.py       # Motor matemático de cálculo defensivo y STAB ofensivo
│   │   └── pokeapi.py          # Cliente híbrido Local-First + PokéAPI (QThread)
│   │
│   ├── ui/                     # [CAPA DE PRESENTACIÓN - PySide6 / Qt 6]
│   │   ├── main_window.py      # Ventana principal panorámica (16:9, 2 columnas)
│   │   ├── styles.py           # Tokens de diseño y hoja de estilos global QSS
│   │   ├── components/         # Widgets y componentes visuales reutilizables
│   │   │   ├── flow_layout.py      # Layout fluido con ajuste de línea responsivo
│   │   │   ├── type_button.py      # Botón de tipo con hover animado y glow
│   │   │   ├── type_chip.py        # Chip de daño con soporte para subtítulo RichText/STAB
│   │   │   ├── type_selector.py    # Cuadrícula de 19 tipos elementales
│   │   │   ├── results_dashboard.py# QTabWidget de resultados (Defensa y Ofensiva)
│   │   │   └── search_bar.py       # Barra de búsqueda con QCompleter y atajos
│   │   └── controllers/
│   │       └── selection_controller.py # Controlador reactivo de selección (FIFO)
│   │
│   └── data/                   # [CAPA DE DATOS ESTÁTICOS]
│       └── custom_pokedex.json # Base de datos local de Pokémon Uranium (~189 entradas)
│
└── tests/                      # [SUITE DE PRUEBAS AUTOMATIZADAS]
    ├── test_calculator.py      # Pruebas del motor matemático, matriz 19x19 y STAB
    ├── test_ui.py              # Pruebas de integración de widgets, pestañas y chips
    └── test_pokeapi.py         # Pruebas del cliente híbrido y SearchBar
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Rol en el Proyecto |
|---|---|---|
| **Lenguaje** | Python 3.10+ (probado en 3.14) | Núcleo lógico y desarrollo desktop |
| **Framework GUI** | PySide6 (Qt 6.6+) | Interfaz nativa de alto rendimiento |
| **Concurrencia** | `QThread` | Consultas HTTP asíncronas no bloqueantes |
| **Testing** | `unittest` (Standard Library) | 47 pruebas automatizadas de regresión |
| **Empaquetado** | `pyinstaller` | Compilación binaria para Windows x64 |

---

## 🚀 Instalación y Ejecución Local

### Prerrequisitos
- Python 3.10 o superior instalado.

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/Calculadora_Pokemon.git
cd Calculadora_Pokemon
```

### 2. Configurar el Entorno Virtual
```powershell
# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación
```powershell
python main.py
```

---

## 🧪 Suite de Pruebas Unitarias

Ejecuta el conjunto completo de 47 pruebas automatizadas con demostraciones en consola:

```powershell
python run_tests.py
```

```text
Ran 47 tests in 0.840s
OK (100% passing)
```

---

## 📦 Distribución y Despliegue (.exe para Windows)

Para compilar el ejecutable independiente sin consola con la base de datos local inyectada:

```powershell
pyinstaller --name "PokeCalc_Uranium" --windowed --onefile --add-data "src/data/custom_pokedex.json;src/data" main.py
```

El binario compilado se genera en:
```text
dist/PokeCalc_Uranium.exe (~47.7 MB)
```
