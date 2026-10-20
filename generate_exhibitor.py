import urllib.request, ssl, csv, io, os, html, re, json

ctx = ssl._create_unverified_context()
SPREADSHEET_ID = '1FLfUeeAXg8-w2HD1B0IiQ24Qu728MX59DvLWIN-qHT4'
RED_CSV_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Red'

req = urllib.request.Request(RED_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as resp:
    reader = list(csv.reader(io.StringIO(resp.read().decode('utf-8'))))

docentes_raw = reader[1:]

docentes = []
for idx, r in enumerate(docentes_raw):
    correo = (r[0] or '').strip()
    nombre = (r[1] or '').strip()
    grado = (r[2] or '').strip()
    semblanza = (r[3] or '').strip()
    areas = (r[4] or '').strip()
    rg_academia = (r[5] or '').strip()
    orcid = (r[6] or '').strip()
    # OMIT Col H (r[7])
    publicaciones = (r[8] or '').strip()
    portafolio = (r[9] or '').strip()
    cv_drive = (r[10] or '').strip()
    # OMIT Col L (r[11])
    imagen = (r[12] or '').strip()
    slug_raw = (r[13] or '').strip()
    clean_slug = slug_raw.replace('/', '').strip() or f'docente-{idx+1}'

    if not imagen:
        imagen = 'https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png'

    docentes.append({
        'id': idx + 1,
        'correo': correo,
        'nombre': nombre,
        'grado': grado,
        'semblanza': semblanza,
        'areas': areas,
        'rg_academia': rg_academia,
        'orcid': orcid,
        'publicaciones': publicaciones,
        'portafolio': portafolio,
        'cv_drive': cv_drive,
        'imagen': imagen,
        'slug': clean_slug
    })

def build_exhibitor_html(is_subdir=False):
    rel_root = '../' if is_subdir else ''
    card_link_prefix = '' if is_subdir else 'red/'
    
    docentes_json = json.dumps(docentes, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Red Transversal de Pensamiento Complejo | Claustro Docente UNRC</title>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.cdnfonts.com/css/open-sauce-one');

        :root {{
            --unrc-color: #ae0340;
            --unrc-dark: #620137;
            --unrc-light: #cf044d;
            --text-dark: #111111;
            --text-grey: #4b5563;
            --bg-light: #fcfcfc;
            --transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Open Sauce One', 'Lato', sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
            background-color: var(--bg-light);
            color: var(--text-dark);
            overflow-x: hidden;
            padding-top: 60px;
        }}

        /* 1. BARRA DE NAVEGACIÓN GLOBAL PLATAFORMA */
        .platform-nav {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 5%;
            border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        }}
        .platform-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: #111111;
            font-weight: 700;
            font-size: 0.95rem;
            letter-spacing: 0.02em;
        }}
        .platform-brand img {{
            height: 34px;
            width: auto;
            object-fit: contain;
        }}
        .platform-links {{
            display: flex;
            align-items: center;
            gap: 18px;
        }}
        .platform-link {{
            color: #4b5563;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 6px 12px;
            border-radius: 4px;
            transition: color 0.25s, background 0.25s;
        }}
        .platform-link:hover {{
            color: #000000;
            background: rgba(0, 0, 0, 0.05);
        }}
        .platform-link.active {{
            color: #ffffff;
            background: var(--unrc-color);
        }}

        /* 2. HEADER INSTITUCIONAL */
        .header-container {{
            position: relative;
            text-align: center;
            padding: 70px 20px 50px;
            margin-bottom: 30px;
            background: linear-gradient(rgba(255, 255, 255, 0.90), rgba(255, 255, 255, 0.97)), 
                        url('https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1787861087069_Mesa_de_ayuda.jpg') center/cover no-repeat;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            border-bottom: 1px solid #eee;
        }}

        .main-title {{
            font-weight: 900;
            font-size: clamp(1.8rem, 4vw, 3.2rem);
            text-transform: uppercase;
            letter-spacing: 4px;
            color: var(--unrc-dark);
            margin: 0;
            line-height: 1.15;
        }}

        .subtitle-box {{
            display: inline-block;
            margin-top: 15px;
            padding: 6px 16px;
            border-bottom: 3px solid var(--unrc-color);
        }}

        .main-subtitle {{
            font-weight: 700;
            font-size: clamp(0.95rem, 2vw, 1.25rem);
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--unrc-color);
            margin: 0;
        }}

        .description {{
            max-width: 860px;
            margin: 22px auto 0;
            font-weight: 400;
            line-height: 1.7;
            font-size: 1.05rem;
            color: var(--text-grey);
        }}

        /* 3. BARRA DE BÚSQUEDA Y FILTROS */
        .search-container {{
            text-align: center;
            margin-bottom: 25px;
            padding: 0 20px;
        }}

        #tagSearch {{
            padding: 13px 26px;
            width: 100%;
            max-width: 460px;
            border: 2px solid var(--unrc-color);
            background: #ffffff;
            font-family: inherit;
            font-size: 0.92rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-dark);
            border-radius: 30px;
            outline: none;
            transition: var(--transition);
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        #tagSearch:focus {{
            box-shadow: 0 0 20px rgba(174, 3, 64, 0.25);
            border-color: var(--unrc-dark);
        }}

        .submenu-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            max-width: 1100px;
            margin: 0 auto 40px auto;
            padding: 0 20px;
        }}

        .submenu-btn {{
            background: #ffffff;
            color: var(--unrc-color);
            border: 1.5px solid var(--unrc-color);
            padding: 8px 18px;
            font-family: inherit;
            font-weight: 700;
            font-size: 0.8rem;
            text-transform: uppercase;
            border-radius: 20px;
            cursor: pointer;
            transition: var(--transition);
        }}

        .submenu-btn:hover, .submenu-btn.active {{
            background: var(--unrc-color);
            color: #ffffff;
            box-shadow: 0 5px 15px rgba(174, 3, 64, 0.3);
            transform: translateY(-2px);
        }}

        /* 4. NETFLIX ROWS */
        .netflix-row {{
            margin-bottom: 50px;
            position: relative;
        }}

        .category-title {{
            font-weight: 900;
            font-size: 1.3rem;
            margin: 0 0 15px 4vw;
            padding-left: 15px;
            border-left: 5px solid var(--unrc-color);
            text-transform: uppercase;
            color: var(--unrc-dark);
            letter-spacing: 1px;
        }}

        .carousel-wrapper {{
            position: relative;
            display: flex;
            align-items: center;
            padding: 15px 4vw;
        }}

        .track-container {{
            overflow: visible; 
            width: 100%;
        }}

        .track {{
            display: flex;
            gap: 20px;
            transition: transform 0.4s ease-in-out;
        }}

        .nav-arrow {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.95);
            color: var(--unrc-color);
            border: 1px solid #ddd;
            border-radius: 50%;
            font-size: 2rem;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 10;
            transition: 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.12);
        }}

        .nav-arrow:hover {{
            background: var(--unrc-color);
            color: white;
            transform: translateY(-50%) scale(1.1);
        }}

        .left-arrow {{ left: 2vw; }}
        .right-arrow {{ right: 2vw; }}

        /* TARJETAS DOCENTE */
        .card {{
            position: relative;
            width: 250px;
            height: 310px;
            flex-shrink: 0;
            border-radius: 10px;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            background: #fff;
            perspective: 1000px;
            text-decoration: none;
            overflow: visible;
        }}

        .card > img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 10px;
            filter: grayscale(85%);
            transition: filter 0.4s ease, transform 0.4s ease;
        }}

        .card:hover > img {{
            filter: grayscale(0%);
        }}

        .card-name-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 30px 12px 14px;
            background: linear-gradient(transparent, rgba(17, 17, 17, 0.95));
            border-bottom-left-radius: 10px;
            border-bottom-right-radius: 10px;
            text-align: center;
            box-sizing: border-box;
            color: white;
        }}

        .card-name-overlay p {{
            margin: 0;
            font-weight: 800;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .card-degree-tag {{
            font-size: 0.72rem;
            color: rgba(255,255,255,0.8);
            margin-top: 4px;
            display: block;
            text-transform: capitalize;
        }}

        /* HOVER PREVIEW POPUP ESTILO NETFLIX */
        .hover-rect {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.85);
            width: 660px;
            height: 350px;
            background-color: #ffffff;
            border-radius: 14px;
            opacity: 0;
            visibility: hidden;
            transition: var(--transition);
            z-index: 100;
            display: flex;
            overflow: hidden;
            box-shadow: 0 30px 60px rgba(0,0,0,0.35);
            pointer-events: none; 
            border: 1px solid #eaeaea;
        }}

        .netflix-row:hover {{ z-index: 50; }} 
        .card:hover {{ z-index: 100; }}
        
        .card:hover .hover-rect {{
            opacity: 1;
            visibility: visible;
            transform: translate(-50%, -50%) scale(1);
            pointer-events: auto;
        }}

        .hover-content {{
            position: relative;
            z-index: 1;
            display: flex;
            width: 100%;
        }}

        .hover-left {{
            width: 40%;
            padding: 24px;
            background: linear-gradient(135deg, var(--unrc-dark) 0%, var(--unrc-color) 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: white;
            box-shadow: 5px 0 20px rgba(0,0,0,0.15);
        }}

        .hover-left h3 {{
            margin: 0 0 12px 0;
            font-size: 1.05rem;
            font-weight: 900;
            text-transform: uppercase;
            line-height: 1.25;
        }}

        .hover-left img {{
            width: 130px;
            height: 130px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #fff;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            margin-bottom: 10px;
        }}

        .hover-left span {{
            font-size: 0.75rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .hover-right {{
            width: 60%;
            padding: 25px;
            display: flex;
            flex-direction: column;
            background: #ffffff;
        }}

        .hover-areas-badge {{
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--unrc-color);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}

        .hover-right p {{
            font-size: 0.92rem;
            line-height: 1.6;
            font-weight: 400;
            color: var(--text-grey);
            margin-bottom: 15px;
            flex-grow: 1;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 7;
            -webkit-box-orient: vertical;
        }}

        .hover-actions {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }}

        .btn-more {{
            background: var(--unrc-color);
            color: #fff;
            padding: 10px 22px;
            text-decoration: none;
            font-weight: 800;
            text-transform: uppercase;
            font-size: 0.78rem;
            letter-spacing: 1px;
            border-radius: 25px;
            transition: 0.3s;
        }}

        .btn-more:hover {{
            background: var(--unrc-dark);
            box-shadow: 0 5px 15px rgba(174, 3, 64, 0.4);
            transform: translateY(-2px);
        }}

        .unrc-logo-small {{
            width: 44px;
            height: auto;
            object-fit: contain;
        }}

        #loading {{ 
            text-align: center; 
            font-weight: 800; 
            letter-spacing: 4px; 
            margin: 40px auto; 
            color: var(--unrc-color); 
            display: none;
        }}
        .hidden-row {{ display: none !important; }}

        /* MODO BÚSQUEDA / GRILLA ACTIVA */
        #sections-container.search-active .category-title {{ display: none; }}
        #sections-container.search-active .nav-arrow {{ display: none; }}
        #sections-container.search-active .carousel-wrapper {{ padding: 0 4vw; display: block; }}
        #sections-container.search-active .track-container {{ overflow: visible; }}
        #sections-container.search-active .track {{
            flex-wrap: wrap;
            justify-content: center;
            gap: 25px;
            transform: none !important;
            transition: none !important;
        }}
        #sections-container.search-active .netflix-row {{ margin-bottom: 25px; }}

        /* FOOTER */
        footer {{ 
            background: #fafafa; 
            border-top: 1px solid #eee; 
            padding: 60px 5%; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            gap: 20px; 
            margin-top: 60px;
        }}
        .logo-footer {{ height: 50px; max-width: 100%; object-fit: contain; }}
        .footer-tag {{ 
            color: var(--unrc-color); 
            font-size: 0.75rem; 
            font-weight: 600; 
            letter-spacing: 4px; 
            text-transform: uppercase; 
            text-align: center; 
        }}

        @media(max-width: 900px) {{
            .hover-rect {{ width: 90vw; height: auto; flex-direction: column; }}
            .hover-left {{ width: 100%; padding: 18px; }}
            .hover-right {{ width: 100%; padding: 18px; }}
            .hover-right p {{ -webkit-line-clamp: 4; }}
        }}
    </style>
</head>
<body>

    <!-- BARRA DE NAVEGACIÓN GLOBAL PLATAFORMA -->
    <nav class="platform-nav">
        <a href="{rel_root}index.html" class="platform-brand">
            <img src="https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png" alt="Logo UNRC">
            <span>Pensamiento Complejo</span>
        </a>
        <div class="platform-links">
            <a href="{rel_root}index.html" class="platform-link">Inicio</a>
            <a href="{rel_root}red.html" class="platform-link active">Red</a>
            <a href="{rel_root}uca.html" class="platform-link">UCA</a>
            <a href="{rel_root}complejidades-hub.html" class="platform-link">Complejidades Hub</a>
            <a href="{rel_root}newsletter.html" class="platform-link">Newsletter</a>
        </div>
    </nav>

    <!-- HEADER DE LA RED TRANSVERSAL -->
    <header class="header-container">
        <h1 class="main-title">Red Transversal de Pensamiento Complejo</h1>
        <div class="subtitle-box">
            <h2 class="main-subtitle">Claustro Académico y Equipo Docente | UNRC</h2>
        </div>
        <p class="description">
            Explora las semblanzas, trayectorias académicas, proyectos y líneas de investigación de las y los docentes adscritos a la Red Transversal de Pensamiento Complejo para la Argumentación.
        </p>
    </header>

    <!-- BUSCADOR -->
    <div class="search-container">
        <input type="text" id="tagSearch" placeholder="BUSCAR DOCENTE, LÍNEA DE INVESTIGACIÓN O PALABRA CLAVE..." onkeyup="applyFilters()">
    </div>

    <!-- SUBMENÚ DE CATEGORÍAS -->
    <div class="submenu-container" id="submenu">
        <button class="submenu-btn active" data-filter="all" onclick="selectSubmenu(this)">Todos</button>
        <button class="submenu-btn" data-filter="sistemas, adaptativo, cibernét, complejidad" onclick="selectSubmenu(this)">Sistemas Complejos</button>
        <button class="submenu-btn" data-filter="filosof, bioét, biopolít, discurso, epistemolog, lógica" onclick="selectSubmenu(this)">Filosofía y Epistemología</button>
        <button class="submenu-btn" data-filter="social, reinserción, inclusión, política" onclick="selectSubmenu(this)">Ciencias Sociales</button>
        <button class="submenu-btn" data-filter="derecho, género, feminis, daño, criminolog" onclick="selectSubmenu(this)">Derecho y Género</button>
        <button class="submenu-btn" data-filter="pedagog, educación, multimodal, tecno, digital" onclick="selectSubmenu(this)">Pedagogía y Multimodalidad</button>
        <button class="submenu-btn" data-filter="arquitect, patrimon, restaur, inmueble" onclick="selectSubmenu(this)">Arquitectura y Patrimonio</button>
    </div>

    <div id="loading">SINCRONIZANDO CON GOOGLE SHEETS...</div>
    <div id="sections-container"></div>

    <!-- FOOTER INSTITUCIONAL -->
    <footer>
        <img src="https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png" alt="Logo UNRC" class="logo-footer">
        <div class="footer-tag">
            <span>Red Transversal de Pensamiento Complejo</span>
            <span>•</span>
            <span>Universidad Nacional Rosario Castellanos © 2026</span>
        </div>
    </footer>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
    <script>
        const initialDocentes = {docentes_json};
        const SPREADSHEET_ID = '1FLfUeeAXg8-w2HD1B0IiQ24Qu728MX59DvLWIN-qHT4';
        const SHEET_RED_URL = `https://docs.google.com/spreadsheets/d/${{SPREADSHEET_ID}}/gviz/tq?tqx=out:csv&sheet=Red`;

        let autoPlayIntervals = [];
        let allDocentes = initialDocentes;

        const isSubdir = {"true" if is_subdir else "false"};
        const linkPrefix = isSubdir ? "" : "red/";

        function init() {{
            renderExhibidor(allDocentes);
            // Sincronizar en segundo plano con Google Sheets
            Papa.parse(SHEET_RED_URL, {{
                download: true, header: false, skipEmptyLines: true,
                complete: function(results) {{
                    const rows = results.data.slice(1);
                    if (rows && rows.length > 0) {{
                        const fetched = rows.map((r, idx) => ({{
                            id: idx + 1,
                            correo: (r[0] || '').trim(),
                            nombre: (r[1] || '').trim(),
                            grado: (r[2] || '').trim(),
                            semblanza: (r[3] || '').trim(),
                            areas: (r[4] || '').trim(),
                            rg_academia: (r[5] || '').trim(),
                            orcid: (r[6] || '').trim(),
                            publicaciones: (r[8] || '').trim(),
                            portafolio: (r[9] || '').trim(),
                            cv_drive: (r[10] || '').trim(),
                            imagen: (r[12] || '').trim() || 'https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png',
                            slug: (r[13] || '').replace('/', '').trim() || `docente-${{idx+1}}`
                        }})).filter(d => d.nombre !== '');
                        
                        if (fetched.length > 0) {{
                            allDocentes = fetched;
                            renderExhibidor(allDocentes);
                        }}
                    }}
                }},
                error: function(e) {{
                    console.log("Continuando con datos locales:", e);
                }}
            }});
        }}

        function renderExhibidor(docentesList) {{
            const container = document.getElementById('sections-container');
            container.innerHTML = '';
            pauseAllCarousels();
            autoPlayIntervals = [];

            const mapCategorias = {{
                "Sistemas Complejos y Cibernética": ["sistemas", "adaptativo", "cibernét", "complejidad"],
                "Filosofía, Bioética y Epistemología": ["filosof", "bioét", "biopolít", "discurso", "epistemolog", "lógica", "nacionalismo"],
                "Derecho, Género y Cultura Digital": ["derecho", "género", "sentipensar", "daño", "criminolog", "legal", "jurídic"],
                "Ciencias Sociales y Humanidades": ["social", "reinserción", "inclusión", "política", "tutoria"],
                "Pedagogía, Comunicación y Multimodalidad": ["pedagog", "educación", "multimodal", "tecno", "digital", "comunicación"],
                "Arquitectura, Hábitat y Patrimonio": ["arquitect", "patrimon", "restaur", "inmueble"]
            }};

            const groupedData = {{}};
            Object.keys(mapCategorias).forEach(cat => groupedData[cat] = []);
            groupedData["Otras Áreas de Investigación"] = [];

            docentesList.forEach(doc => {{
                const areasRaw = (doc.areas || "").toLowerCase();
                const semblanzaRaw = (doc.semblanza || "").toLowerCase();
                let assigned = false;

                for (let [catName, keywords] of Object.entries(mapCategorias)) {{
                    if (keywords.some(kw => areasRaw.includes(kw) || semblanzaRaw.includes(kw))) {{
                        groupedData[catName].push(doc);
                        assigned = true;
                    }}
                }}

                if (!assigned) {{
                    groupedData["Otras Áreas de Investigación"].push(doc);
                }}
            }});

            let rowIndex = 0;
            Object.keys(groupedData).forEach((cat) => {{
                if (groupedData[cat].length > 0) {{
                    const rowHtml = createNetflixRow(cat, groupedData[cat], rowIndex);
                    container.appendChild(rowHtml);
                    rowIndex++;
                }}
            }});

            startCarousels();
        }}

        function createNetflixRow(title, data, index) {{
            const rowDiv = document.createElement('div');
            rowDiv.className = 'netflix-row';
            rowDiv.id = `row-${{index}}`;

            const titleEl = document.createElement('h2');
            titleEl.className = 'category-title';
            titleEl.innerText = title;
            rowDiv.appendChild(titleEl);

            const wrapper = document.createElement('div');
            wrapper.className = 'carousel-wrapper';

            const leftBtn = document.createElement('button');
            leftBtn.className = 'nav-arrow left-arrow';
            leftBtn.innerHTML = '‹';
            leftBtn.onclick = () => moveSlide(`track-${{index}}`, 'left');
            wrapper.appendChild(leftBtn);

            const trackContainer = document.createElement('div');
            trackContainer.className = 'track-container';
            
            const track = document.createElement('div');
            track.className = 'track';
            track.id = `track-${{index}}`;

            data.forEach((doc) => {{
                const card = document.createElement('div');
                card.className = 'card';
                card.setAttribute('data-tags', (doc.areas + ' ' + doc.grado).toLowerCase());
                card.setAttribute('data-name', doc.nombre.toLowerCase());

                const linkUrl = `${{linkPrefix}}${{doc.slug}}.html`;

                card.innerHTML = `
                    <img src="${{doc.imagen}}" alt="${{doc.nombre}}" loading="lazy">
                    <div class="card-name-overlay">
                        <p>${{doc.nombre}}</p>
                        <span class="card-degree-tag">${{doc.grado || 'Docente Investigador'}}</span>
                    </div>
                    
                    <div class="hover-rect">
                        <div class="hover-content">
                            <div class="hover-left">
                                <img src="${{doc.imagen}}" alt="${{doc.nombre}}">
                                <h3>${{doc.nombre}}</h3>
                                <span>${{doc.grado || 'Docente Investigador'}}</span>
                            </div>
                            <div class="hover-right">
                                <div class="hover-areas-badge">📌 ${{doc.areas ? doc.areas.slice(0, 70) + '...' : 'Pensamiento Complejo'}}</div>
                                <p>${{doc.semblanza || 'Docente adscrito a la Red Transversal de Pensamiento Complejo para la Argumentación.'}}</p>
                                <div class="hover-actions">
                                    <a href="${{linkUrl}}" class="btn-more">Conocer Perfil ↗</a>
                                    <img src="https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png" class="unrc-logo-small" alt="UNRC">
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                track.appendChild(card);
            }});

            trackContainer.appendChild(track);
            wrapper.appendChild(trackContainer);

            const rightBtn = document.createElement('button');
            rightBtn.className = 'nav-arrow right-arrow';
            rightBtn.innerHTML = '›';
            rightBtn.onclick = () => moveSlide(`track-${{index}}`, 'right');
            wrapper.appendChild(rightBtn);

            rowDiv.appendChild(wrapper);

            rowDiv.addEventListener('mouseenter', () => pauseCarousel(index));
            rowDiv.addEventListener('mouseleave', () => {{
                if (!document.getElementById('sections-container').classList.contains('search-active')) {{
                    resumeCarousel(index, `track-${{index}}`);
                }}
            }});

            return rowDiv;
        }}

        function moveSlide(trackId, direction) {{
            if (document.getElementById('sections-container').classList.contains('search-active')) return;
            
            const track = document.getElementById(trackId);
            if (!track || track.children.length === 0) return;

            const cardWidth = 270; 

            if (direction === 'right') {{
                const first = track.firstElementChild;
                track.style.transition = 'transform 0.4s ease-in-out';
                track.style.transform = `translateX(-${{cardWidth}}px)`;
                setTimeout(() => {{
                    track.style.transition = 'none';
                    track.appendChild(first); 
                    track.style.transform = 'translateX(0)';
                }}, 400);
            }} else {{
                const last = track.lastElementChild;
                track.style.transition = 'none';
                track.insertBefore(last, track.firstElementChild); 
                track.style.transform = `translateX(-${{cardWidth}}px)`;
                
                void track.offsetWidth; 
                
                track.style.transition = 'transform 0.4s ease-in-out';
                track.style.transform = 'translateX(0)';
            }}
        }}

        function startCarousels() {{
            const tracks = document.querySelectorAll('.track');
            tracks.forEach((track, index) => {{
                resumeCarousel(index, track.id);
            }});
        }}

        function pauseCarousel(index) {{
            clearInterval(autoPlayIntervals[index]);
        }}

        function pauseAllCarousels() {{
            autoPlayIntervals.forEach(interval => clearInterval(interval));
        }}

        function resumeCarousel(index, trackId) {{
            clearInterval(autoPlayIntervals[index]);
            autoPlayIntervals[index] = setInterval(() => {{
                moveSlide(trackId, 'right');
            }}, 4500);
        }}

        function resumeAllCarousels() {{
            const tracks = document.querySelectorAll('.track');
            tracks.forEach((track, index) => {{
                resumeCarousel(index, track.id);
            }});
        }}

        function selectSubmenu(btnElement) {{
            document.querySelectorAll('.submenu-btn').forEach(btn => btn.classList.remove('active'));
            btnElement.classList.add('active');
            applyFilters();
        }}

        function applyFilters() {{
            const searchVal = document.getElementById('tagSearch').value.toLowerCase().trim();
            const activeBtn = document.querySelector('.submenu-btn.active');
            const submenuVal = activeBtn ? activeBtn.getAttribute('data-filter') : 'all';
            
            const container = document.getElementById('sections-container');
            const isFiltering = searchVal !== "" || submenuVal !== "all";

            if (isFiltering) {{
                container.classList.add('search-active');
                pauseAllCarousels();
            }} else {{
                container.classList.remove('search-active');
                resumeAllCarousels();
            }}

            const keyArray = submenuVal !== 'all' ? submenuVal.split(',').map(k => k.trim()) : [];
            const nombresImpresos = new Set();

            document.querySelectorAll('.card').forEach(card => {{
                if (!isFiltering) {{
                    card.style.display = 'block';
                    return;
                }}

                const tags = card.getAttribute('data-tags');
                const name = card.getAttribute('data-name');

                const matchesSearch = searchVal === "" || name.includes(searchVal) || tags.includes(searchVal);
                const matchesSubmenu = submenuVal === 'all' || keyArray.some(k => tags.includes(k));

                if (matchesSearch && matchesSubmenu) {{
                    if (!nombresImpresos.has(name)) {{
                        card.style.display = 'block';
                        nombresImpresos.add(name);
                    }} else {{
                        card.style.display = 'none';
                    }}
                }} else {{
                    card.style.display = 'none';
                }}
            }});

            hideEmptyRows();
        }}

        function hideEmptyRows() {{
            document.querySelectorAll('.netflix-row').forEach(row => {{
                const visibleCards = Array.from(row.querySelectorAll('.card')).filter(c => c.style.display !== 'none');
                if (visibleCards.length === 0) {{
                    row.classList.add('hidden-row');
                }} else {{
                    row.classList.remove('hidden-row');
                }}
            }});
        }}

        init();
    </script>
</body>
</html>
'''

# Generar red.html en la raíz
with open('/Users/logiciststudio/.gemini/antigravity-ide/scratch/PensamientoComplejo/red.html', 'w', encoding='utf-8') as f:
    f.write(build_exhibitor_html(is_subdir=False))
print("Generado red.html en la raíz.")

# Generar red/index.html dentro de red/
with open('/Users/logiciststudio/.gemini/antigravity-ide/scratch/PensamientoComplejo/red/index.html', 'w', encoding='utf-8') as f:
    f.write(build_exhibitor_html(is_subdir=True))
print("Generado red/index.html dentro de red/.")
