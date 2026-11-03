# ⚡ PokeCalc Uranium • Calculadora de Tipos Pokémon (Gen VI+)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/PySide6-Qt_6.6%2B-41CD52.svg?logo=qt&logoColor=white)](https://wiki.qt.io/Qt_for_Python)
[![Network](https://img.shields.io/badge/API-PokéAPI_v2-EF5350.svg)](https://pokeapi.co/)
[![Tests](https://img.shields.io/badge/Tests-45%2F45_Passing-success.svg)](#suite-de-pruebas-unitarias)
[![Platform](https://img.shields.io/badge/Platform-Windows_x64-0078D6.svg?logo=windows&logoColor=white)](#distribución-y-empaquetado)

Aplicación nativa de escritorio de alto rendimiento para el análisis matemático y defensivo de tipos elementales de Pokémon basada en las mecánicas oficiales de la **Generación VI en adelante** y expandida con soporte completo para el fan-game de culto **Pokémon Uranium** (incorporando el **Tipo Nuclear**).

Diseñada bajo principios estrictos de **Clean Architecture**, **Domain-Driven Design (DDD)** y desacoplamiento **MVC**, ofreciendo una interfaz de usuario moderna (*Dark Mode*, monitores 16:9 panorámicos) y un motor de búsqueda híbrido **Local-First** con resolución en 0 ms.

---

## 📸 Vista General y Capturas de Pantalla

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ⚡ CALCULADORA DE TIPOS POKÉMON • GEN VI+                          [FASE 6 • RELEASE] │
├──────────────────────────────────────────┬─────────────────────────────────────────────┤
│ [🔍 Buscar Pokémon (Ctrl+F)...] [Buscar] │ PERFIL DEFENSIVO: NORMAL / NUCLEAR          │
│ ---------------------------------------- │ ------------------------------------------- │
│  [Normal]  [Fuego]    [Agua]    [Planta] │ ⚠️ VULNERABILIDAD EXTREMA (x4)             │
│  [Electr]  [Hielo]    [Lucha]   [Veneno] │  • Lucha                                    │
│  [Tierra]  [Volador]  [Psíquic] [Bicho]  │ ------------------------------------------- │
│  [Roca]    [Fantasma] [Dragón]  [Siniest]│ ⚔️ DEBILIDADES (x2)                         │
│  [Acero]   [Hada]     [☢ NUCLEAR]       │  • Fuego  • Agua  • Planta  • Eléctrico ... │
│                                          │ ------------------------------------------- │
│ [ Restablecer Selección (Esc) ]          │ 🛡️ RESISTENCIAS (x0.5)                      │
│                                          │  • Nuclear                                  │
│                                          │ ------------------------------------------- │
│                                          │ ⛔ INMUNIDADES (x0)                          │
│                                          │  • Fantasma                                 │
└──────────────────────────────────────────┴─────────────────────────────────────────────┘
```

---

## ✨ Características Principales

### 1. 🧮 Motor Matemático de Tipos (Gen VI+)
- **19 Tipos Elementales**: Los 18 canónicos (Normal, Fuego, Agua, Planta, Eléctrico, Hielo, Lucha, Veneno, Tierra, Volador, Psíquico, Bicho, Roca, Fantasma, Dragón, Siniestro, Acero, Hada) + el **Tipo Nuclear** de Pokémon Uranium.
- **Matriz de Interacción 19x19 (361 cruces)**: Implementación de la fórmula defensiva multiplicativa:
  $$\text{Multiplicador Defensor}(T_{\text{ataque}}, [T_1, T_2]) = \text{Matriz}[T_{\text{ataque}}, T_1] \times \text{Matriz}[T_{\text{ataque}}, T_2]$$
- **Clasificación Automática de Daño**: Segmentación dinámica en categorías de impacto:
  - **x4.0**: Vulnerabilidad Extrema (Doble debilidad)
  - **x2.0**: Debilidad
  - **x1.0**: Daño Neutro
  - **x0.5**: Resistencia
  - **x0.25**: Súper Resistencia
  - **x0.0**: Inmunidad absoluta
- **Propiedad Conmutativa Estricta**: $f(A, B) = f(B, A)$ garantizada y testeada al 100%.

### 2. ☢️ Soporte Oficial para Pokémon Uranium (Tipo Nuclear)
- **Reglas Ofensivas de Nuclear**: Asesta daño supereficaz (**x2.0**) a todos los tipos elementales existentes, excepto contra **Acero (x0.5)** y **Nuclear (x0.5)**.
- **Reglas Defensivas de Nuclear**: Recibe daño crítico (**x2.0**) de todos los tipos elementales del juego, excepto de ataques de tipo **Nuclear (x0.5)**.
- **Paleta Atómica**: Integrado en la interfaz con colores radioactivos dedicados (`#39FF14`).

### 3. ⚡ Buscador Híbrido Local-First (0 ms) & PokéAPI v2
- **Arquitectura de Doble Fuente**:
  1. **Capa Local (0 ms)**: Archivo JSON con ~189 especies exclusivas y variantes atómicas de Pokémon Uranium (ej. *Nucleon, Urayne, Baariette, Corsoreef-Nuclear*). Si el Pokémon coincide, se procesa en memoria instantáneamente sin emitir tráfico de red.
  2. **Capa Remota Asíncrona (PokéAPI)**: Si no se encuentra localmente, un hilo en segundo plano (`QThread`) consulta la API oficial sin bloquear el hilo principal de la interfaz (UI Thread).
- **Caché en Memoria**: Consultas repetidas resueltas sin solicitudes HTTP redundantes.

### 4. 🎯 Autocompletado Reactivo & Atajos de Teclado
- **Sugerencias Predictivas (`QCompleter`)**:
  - Poblado inicial inmediato con la Pokédex de Uranium.
  - Carga en segundo plano de más de 1300 nombres oficiales desde PokéAPI.
  - Búsqueda por subcadena insensible a mayúsculas/minúsculas (`MatchContains`).
  - **Activación en 1 Clic/Enter**: Seleccionar una sugerencia rellena el texto y ejecuta la búsqueda automáticamente.
- **Atajos de Teclado Nativos**:
  - `Ctrl + F` (o `Cmd + F` en macOS): Enfoca la barra de búsqueda y selecciona todo el texto para una nueva consulta rápida.
  - `Esc`: Limpia el texto de búsqueda y deselecciona los tipos activos en la calculadora.

### 5. 🖥️ Diseño UI/UX Desktop Premium
- **Tema Oscuro Profesional**: Fondos de alto contraste (`#0F1117`, `#181B26`), bordes sutiles y tipografía legible.
- **Layout Panorámico 16:9**: División optimizada en 2 columnas (Panel de Entrada a la izquierda con ancho fijo y Dashboard de Resultados expandible a la derecha).
- **Componentes Reactivos**: Chips de daño (`TypeChip`) con tooltips dinámicos, botones de tipos (`TypeButton`) con efecto de brillo (*glow*) y animaciones de desvanecimiento suave (`QGraphicsOpacityEffect`).

---

## 🏛️ Arquitectura del Software (Clean Architecture / MVC)

El proyecto está diseñado bajo un estricto desacoplamiento entre el núcleo matemático de dominio y la capa visual:

```text
Calculadora_Pokemon/
│
├── main.py                     # Punto de entrada de la aplicación Qt
├── run_tests.py                # Runner del conjunto de pruebas unitarias
├── requirements.txt            # Dependencias del proyecto
├── .gitignore                  # Reglas de exclusión para Git
├── README.md                   # Documentación técnica
│
├── src/
│   ├── core/                   # [CAPA DE DOMINIO - Sin dependencias UI]
│   │   ├── __init__.py
│   │   ├── enums.py            # Enumeraciones fuertemente tipadas (PokemonType)
│   │   ├── constants.py        # Matriz canónica 19x19 de efectividades
│   │   ├── models.py           # Modelos inmutables de resultado (TypeDefenseProfile)
│   │   ├── calculator.py       # Motor matemático de cálculo defensivo
│   │   └── pokeapi.py          # Cliente híbrido (Local-First + PokéAPI QThread)
│   │
│   ├── ui/                     # [CAPA DE PRESENTACIÓN - PySide6 / Qt 6]
│   │   ├── __init__.py
│   │   ├── main_window.py      # Ventana principal panorámica (16:9, 2 columnas)
│   │   ├── styles.py           # Tokens de diseño y hoja de estilos global (QSS)
│   │   ├── components/         # Widgets y componentes visuales reutilizables
│   │   │   ├── __init__.py
│   │   │   ├── flow_layout.py      # Layout fluido con ajuste de línea responsivo
│   │   │   ├── type_button.py      # Botón de tipo con hover animado y glow
│   │   │   ├── type_chip.py        # Chip de daño con badge coloreado
│   │   │   ├── type_selector.py    # Cuadrícula 3x6 de selección de tipos
│   │   │   ├── results_dashboard.py# Dashboard con desglose de efectividades
│   │   │   └── search_bar.py       # Barra de búsqueda con QCompleter y atajos
│   │   └── controllers/
│   │       ├── __init__.py
│   │       └── selection_controller.py # Controlador reactivo (Estado, FIFO)
│   │
│   └── data/                   # [CAPA DE DATOS ESTÁTICOS]
│       └── custom_pokedex.json # Base de datos local de Pokémon Uranium
│
└── tests/                      # [SUITE DE PRUEBAS AUTOMATIZADAS]
    ├── __init__.py
    ├── test_calculator.py      # Pruebas del motor matemático y matriz 19x19
    ├── test_ui.py              # Pruebas de integración de componentes UI
    └── test_pokeapi.py         # Pruebas del cliente híbrido y SearchBar
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Propósito |
|---|---|---|
| **Lenguaje** | Python 3.10+ (probado en 3.14) | Núcleo lógico y desarrollo backend/desktop |
| **GUI Framework** | PySide6 (Qt 6) | Framework nativo multiplataforma de escritorio |
| **Networking** | `requests` + `QThread` | Cliente HTTP con concurrencia no bloqueante |
| **Testing** | `unittest` (Standard Library) | Batería de pruebas automatizadas con mocks |
| **Packaging** | `pyinstaller` | Generación de ejecutables nativos independientes (.exe) |

---

## 🚀 Instalación y Ejecución Local

### Prerrequisitos
- Python 3.10 o superior instalado en el sistema.
- Gestor de paquetes `pip`.

### 1. Clonar el Repositorio
```bash
git clone https://github.com/AnthonyDHerreraE/Calculadora_Pokemon.git
cd Calculadora_Pokemon
```

### 2. Configurar el Entorno Virtual (Recomendado)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Iniciar la Aplicación
```bash
python main.py
```

---

## 🧪 Suite de Pruebas Unitarias

El proyecto cuenta con una cobertura completa de pruebas que validan desde la precisión de las tablas de tipos hasta la integración de hilos y la sincronización de interfaces:

```bash
python run_tests.py
```

O usando el módulo nativo `unittest`:
```bash
python -m unittest discover -s tests -v
```

### Resultados de la Suite:
- **45 pruebas ejecutadas exitosamente (100% passing)**:
  - 17 pruebas de integridad de la matriz, nerfs de Gen VI, tipo Hada y tipo Nuclear.
  - 12 pruebas de normalización, cliente híbrido, caché en memoria y PokéAPI.
  - 16 pruebas de widgets UI, controlador FIFO, animaciones, `QCompleter` y atajos de teclado.

---

## 📦 Distribución y Empaquetado (.exe para Windows)

Para distribuir la aplicación a usuarios finales sin requerir que tengan Python instalado, se utiliza **PyInstaller** en modo de archivo único (*One-File*), ventana limpia (*Windowed*) e inyección de la base de datos de Uranium:

```powershell
pyinstaller --name "PokeCalc_Uranium" --windowed --onefile --add-data "src/data/custom_pokedex.json;src/data" main.py
```

El binario resultante se genera en el directorio:
```text
dist/PokeCalc_Uranium.exe
```

---

## 📄 Licencia y Créditos

- **Licencia**: Este proyecto se distribuye con fines educativos y de demostración técnica bajo la licencia MIT.
- **Datos Oficiales de Pokémon**: Todos los derechos de marcas, nombres y sprites de Pokémon pertenecen a © Nintendo, Creatures Inc. y GAME FREAK Inc. Datos provistos por [PokéAPI](https://pokeapi.co/).
- **Pokémon Uranium**: Todos los derechos de los Fakemon del fan-game pertenecen al equipo de desarrollo de Pokémon Uranium.
