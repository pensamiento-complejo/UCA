import urllib.request, ssl, csv, io, os, html, re, json, unicodedata

ctx = ssl._create_unverified_context()
SPREADSHEET_ID = '1FLfUeeAXg8-w2HD1B0IiQ24Qu728MX59DvLWIN-qHT4'
RED_CSV_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Red'

req = urllib.request.Request(RED_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as resp:
    reader = list(csv.reader(io.StringIO(resp.read().decode('utf-8'))))

docentes_raw = reader[1:]

docentes = []
for idx, r in enumerate(docentes_raw):
    if len(r) < 2:
        continue
    nombre = (r[1] or '').strip()
    if not nombre or nombre.lower() == 'nombre completo':
        continue

    correo = (r[0] or '').strip()
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
    clean_slug = slug_raw.replace('/', '').strip()
    if not clean_slug and nombre:
        clean_slug = re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFD', nombre.lower()).encode('ascii', 'ignore').decode('utf-8'))
    if not clean_slug:
        clean_slug = f'docente-{idx+1}'

    if not imagen or not imagen.startswith('http'):
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

def render_pre_card(doc, link_prefix):
    link_url = f"{link_prefix}{doc['slug']}.html"
    areas_list = [a.strip() for a in re.split(r'[,;\n•*]+', doc['areas']) if a.strip()]
    first_areas = areas_list[:2]
    areas_html = "".join(f'<span class="area-chip">{html.escape(a)}</span>' for a in first_areas) if first_areas else '<span class="area-chip">Pensamiento Complejo</span>'
    
    clean_search_text = f"{doc['nombre']} {doc['grado']} {doc['areas']} {doc['correo']}".lower()
    default_img = 'https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png'

    return f'''
    <article class="docente-card" data-search="{html.escape(clean_search_text)}" onclick="window.location.href='{link_url}'">
        <div class="card-header">
            <span class="card-degree">{html.escape(doc['grado'] or 'Docente')}</span>
            <div class="card-avatar-wrapper">
                <img src="{doc['imagen']}" alt="{html.escape(doc['nombre'])}" class="card-avatar" loading="lazy" onerror="this.onerror=null;this.src='{default_img}';">
            </div>
        </div>
        <div class="card-body">
            <h3 class="card-name">{html.escape(doc['nombre'])}</h3>
            <div class="card-areas-chips">
                {areas_html}
            </div>
            <p class="card-bio">{html.escape(doc['semblanza'][:120])}...</p>
        </div>
        <div class="card-footer">
            <a href="{link_url}" class="card-btn" onclick="event.stopPropagation();">
                <span>Conocer Perfil</span>
                <span class="arrow">↗</span>
            </a>
        </div>
    </article>
    '''

def build_exhibitor_html(is_subdir=False):
    rel_root = '../' if is_subdir else ''
    card_link_prefix = '' if is_subdir else 'red/'
    
    docentes_json = json.dumps(docentes, ensure_ascii=False)
    cards_html = "\n".join(render_pre_card(d, card_link_prefix) for d in docentes)

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Red Transversal de Pensamiento Complejo | Claustro Docente UNRC</title>
    
    <!-- PWA & Mobile Meta Tags -->
    <link rel="manifest" href="{rel_root}manifest.webmanifest">
    <meta name="theme-color" content="#ae0340">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Pensamiento Complejo">
    <link rel="apple-touch-icon" href="{rel_root}icons/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="{rel_root}icons/favicon-32.png">

    <!-- PapaParse para sincronización en tiempo real con la hoja Red -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>

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
            --transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
            --card-border: 1px solid rgba(0,0,0,0.08);
            --shadow-card: 0 8px 24px rgba(0,0,0,0.05);
            --shadow-hover: 0 16px 36px rgba(174, 3, 64, 0.12);
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Open Sauce One', 'Lato', sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
            background-color: var(--bg-light);
            color: var(--text-dark);
            overflow-x: hidden;
            padding-top: 60px;
            line-height: 1.5;
        }}

        /* 1. BARRA DE NAVEGACIÓN GLOBAL PLATAFORMA */
        .platform-nav {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background: rgba(255, 255, 255, 0.96);
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
            gap: 16px;
        }}
        .platform-link {{
            color: #4b5563;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 8px 14px;
            border-radius: 6px;
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

        /* BOTÓN HAMBURGUESA MÓVIL */
        .mobile-nav-toggle {{
            display: none;
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 10px;
            width: 44px;
            height: 44px;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 5px;
            z-index: 10002;
        }}
        .mobile-nav-toggle .bar {{
            width: 24px;
            height: 2.5px;
            background-color: #111111;
            border-radius: 2px;
            transition: all 0.3s ease;
        }}
        .mobile-nav-toggle.open .bar:nth-child(1) {{
            transform: translateY(7.5px) rotate(45deg);
        }}
        .mobile-nav-toggle.open .bar:nth-child(2) {{
            opacity: 0;
        }}
        .mobile-nav-toggle.open .bar:nth-child(3) {{
            transform: translateY(-7.5px) rotate(-45deg);
        }}

        @media (max-width: 820px) {{
            .mobile-nav-toggle {{ display: flex; }}
            .platform-links {{
                position: fixed;
                top: 60px;
                left: 0;
                width: 100%;
                height: calc(100vh - 60px);
                background: rgba(255, 255, 255, 0.98);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                flex-direction: column;
                align-items: stretch;
                padding: 24px 20px;
                gap: 10px;
                transform: translateY(-100%);
                opacity: 0;
                pointer-events: none;
                transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
                overflow-y: auto;
                box-shadow: 0 20px 40px rgba(0,0,0,0.12);
            }}
            .platform-links.mobile-open {{
                transform: translateY(0);
                opacity: 1;
                pointer-events: auto;
            }}
            .platform-link {{
                font-size: 1rem;
                padding: 14px 18px;
                border-radius: 8px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }}
        }}

        /* 2. HERO INSTITUCIONAL CON ESTILO GRÁFICO E IMAGEN EN MEDIO */
        .hero-container {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px 20px 40px;
            background-color: var(--bg-light);
            position: relative;
            overflow: hidden;
            border-bottom: 1px solid rgba(0,0,0,0.06);
        }}
        .hero-container::before {{
            content: '';
            position: absolute;
            top: -20%;
            left: 50%;
            transform: translateX(-50%);
            width: 700px;
            height: 350px;
            background: radial-gradient(circle, rgba(174, 3, 64, 0.08) 0%, transparent 70%);
            pointer-events: none;
        }}

        .hero-grid {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            grid-template-rows: auto auto auto;
            column-gap: 2vw;
            align-items: center;
            width: 100%;
            max-width: 1200px;
            position: relative;
            z-index: 2;
        }}

        @keyframes blurFadeIn {{
            0% {{ opacity: 0; filter: blur(10px); transform: translateY(12px); }}
            100% {{ opacity: 1; filter: blur(0); transform: translateY(0); }}
        }}

        .hero-grid > * {{ opacity: 0; animation: blurFadeIn 1s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}

        .red-text {{ color: var(--unrc-color); font-weight: 600; font-size: clamp(1rem, 1.5vw, 1.5rem); letter-spacing: -0.02em; }}
        .black-text {{ font-weight: 800; font-size: clamp(2.8rem, 5.8vw, 6.5rem); line-height: 0.85; letter-spacing: -0.04em; color: #111; }}

        .text-top {{ grid-column: 1; grid-row: 1; justify-self: end; align-self: end; margin-bottom: 5px; animation-delay: 0.1s; }}
        .text-pensamiento {{ grid-column: 1; grid-row: 2; justify-self: end; animation-delay: 0.2s; }}
        .hero-img {{ 
            grid-column: 2; 
            grid-row: 1 / span 3; 
            height: clamp(130px, 16vw, 220px); 
            object-fit: contain; 
            animation-delay: 0.3s; 
            user-select: none;
            transition: transform 0.4s ease;
        }}
        .hero-img:hover {{ transform: scale(1.04) rotate(1deg); }}
        .text-complejo {{ grid-column: 3; grid-row: 2; justify-self: start; animation-delay: 0.4s; }}
        .text-bottom {{ grid-column: 3; grid-row: 3; justify-self: start; align-self: start; margin-top: 5px; animation-delay: 0.5s; }}

        .hero-subtitle {{
            margin-top: 30px;
            font-size: clamp(0.9rem, 1.8vw, 1.1rem);
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--unrc-color);
            text-align: center;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(174, 3, 64, 0.06);
            padding: 8px 24px;
            border-radius: 30px;
            border: 1px solid rgba(174, 3, 64, 0.18);
            opacity: 0;
            animation: blurFadeIn 1s ease-out 0.6s forwards;
        }}

        .hero-description {{
            max-width: 820px;
            margin: 20px auto 0;
            font-size: 1.05rem;
            line-height: 1.7;
            color: var(--text-grey);
            text-align: center;
            font-weight: 400;
            opacity: 0;
            animation: blurFadeIn 1s ease-out 0.75s forwards;
        }}

        @media (max-width: 640px) {{
            .hero-container {{ padding: 35px 16px 25px; }}
            .hero-grid {{
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                gap: 6px;
            }}
            .text-top {{ order: 1; margin: 0; }}
            .text-pensamiento {{ order: 2; margin: 0; }}
            .hero-img {{ order: 3; height: 115px; margin: 10px 0; }}
            .text-complejo {{ order: 4; margin: 0; }}
            .text-bottom {{ order: 5; margin: 0; }}
            .black-text {{ font-size: 2.3rem; line-height: 1; }}
            .red-text {{ font-size: 0.92rem; }}
        }}

        /* 3. SECCIÓN DEL BUSCADOR */
        .search-section {{
            max-width: 800px;
            margin: 40px auto 30px;
            padding: 0 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }}

        .search-box {{
            position: relative;
            width: 100%;
            display: flex;
            align-items: center;
        }}

        .search-icon {{
            position: absolute;
            left: 20px;
            font-size: 1.1rem;
            color: var(--unrc-color);
            pointer-events: none;
        }}

        #tagSearch {{
            width: 100%;
            padding: 16px 50px 16px 52px;
            border: 2px solid var(--unrc-color);
            background: #ffffff;
            font-family: inherit;
            font-size: 16px; /* Evita zoom automático en Safari iOS */
            letter-spacing: 0.5px;
            color: var(--text-dark);
            border-radius: 40px;
            outline: none;
            transition: var(--transition);
            box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        }}

        #tagSearch:focus {{
            box-shadow: 0 0 24px rgba(174, 3, 64, 0.22);
            border-color: var(--unrc-dark);
        }}

        .clear-btn {{
            position: absolute;
            right: 18px;
            background: rgba(0,0,0,0.06);
            border: none;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 0.8rem;
            color: #555;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }}
        .clear-btn:hover {{ background: rgba(174, 3, 64, 0.15); color: var(--unrc-color); }}

        .search-counter {{
            font-size: 0.88rem;
            color: var(--text-grey);
            font-weight: 500;
        }}
        .search-counter strong {{
            color: var(--unrc-color);
            font-weight: 800;
        }}

        /* 4. GRILLA MODERNA DE DOCENTES */
        .docentes-section {{
            max-width: 1320px;
            margin: 0 auto;
            padding: 10px 5% 80px;
        }}

        .docentes-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
            gap: 28px;
            width: 100%;
        }}

        .docente-card {{
            background: #ffffff;
            border-radius: 14px;
            border: var(--card-border);
            box-shadow: var(--shadow-card);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: var(--transition);
            cursor: pointer;
            position: relative;
        }}

        .docente-card:hover {{
            transform: translateY(-6px);
            box-shadow: var(--shadow-hover);
            border-color: rgba(174, 3, 64, 0.25);
        }}

        .card-header {{
            position: relative;
            background: linear-gradient(135deg, rgba(174, 3, 64, 0.05) 0%, rgba(98, 1, 55, 0.08) 100%);
            padding: 30px 20px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            border-bottom: 1px solid rgba(0,0,0,0.04);
        }}

        .card-degree {{
            position: absolute;
            top: 14px;
            left: 16px;
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--unrc-color);
            background: rgba(255, 255, 255, 0.95);
            padding: 4px 10px;
            border-radius: 20px;
            border: 1px solid rgba(174, 3, 64, 0.2);
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }}

        .card-avatar-wrapper {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            padding: 4px;
            background: #ffffff;
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .card-avatar {{
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
            transition: transform 0.4s ease;
        }}

        .docente-card:hover .card-avatar {{
            transform: scale(1.06);
        }}

        .card-body {{
            padding: 22px 20px 16px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            text-align: center;
        }}

        .card-name {{
            font-size: 1.15rem;
            font-weight: 900;
            color: var(--text-dark);
            text-transform: uppercase;
            letter-spacing: -0.01em;
            line-height: 1.25;
            margin-bottom: 12px;
            transition: color 0.2s;
        }}

        .docente-card:hover .card-name {{
            color: var(--unrc-color);
        }}

        .card-areas-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            justify-content: center;
            margin-bottom: 14px;
        }}

        .area-chip {{
            font-size: 0.72rem;
            font-weight: 600;
            color: #555555;
            background: #f4f4f4;
            padding: 4px 10px;
            border-radius: 12px;
            letter-spacing: 0.3px;
        }}

        .card-bio {{
            font-size: 0.88rem;
            color: var(--text-grey);
            line-height: 1.55;
            margin-top: auto;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-align: center;
        }}

        .card-footer {{
            padding: 16px 20px;
            border-top: 1px solid rgba(0,0,0,0.05);
            background: #fafafa;
        }}

        .card-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            padding: 10px 16px;
            background: var(--unrc-color);
            color: #ffffff;
            text-decoration: none;
            font-weight: 800;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-radius: 25px;
            transition: all 0.25s ease;
            box-shadow: 0 4px 12px rgba(174, 3, 64, 0.2);
        }}

        .card-btn .arrow {{
            transition: transform 0.25s ease;
        }}

        .docente-card:hover .card-btn {{
            background: var(--unrc-dark);
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(98, 1, 55, 0.3);
        }}

        .docente-card:hover .card-btn .arrow {{
            transform: translateX(3px) translateY(-3px);
        }}

        /* ESTADO SIN RESULTADOS */
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            background: #ffffff;
            border-radius: 14px;
            border: 1px dashed #ddd;
            margin-top: 20px;
        }}
        .no-results-icon {{ font-size: 3rem; margin-bottom: 15px; opacity: 0.6; }}
        .no-results h3 {{ font-size: 1.3rem; font-weight: 800; color: var(--unrc-color); margin-bottom: 10px; text-transform: uppercase; }}
        .no-results p {{ font-size: 0.95rem; color: var(--text-grey); margin-bottom: 20px; }}
        .btn-reset {{
            background: var(--unrc-color);
            color: white;
            border: none;
            padding: 10px 24px;
            font-family: inherit;
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-radius: 25px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .btn-reset:hover {{ background: var(--unrc-dark); }}

        /* 5. FOOTER INSTITUCIONAL */
        footer {{ 
            background: #fafafa; 
            border-top: 1px solid #eee; 
            padding: 60px 5%; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            gap: 20px; 
        }}
        .logo-footer {{ height: 55px; max-width: 100%; object-fit: contain; }}
        .footer-tag {{ 
            color: var(--unrc-color); 
            font-size: 0.72rem; 
            font-weight: 600; 
            letter-spacing: 5px; 
            text-transform: uppercase; 
            text-align: center; 
            display: flex; 
            flex-direction: row; 
            flex-wrap: wrap; 
            justify-content: center; 
            gap: 12px;
        }}

        @media (max-width: 768px) {{
            .docentes-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            .search-section {{ margin: 30px auto 20px; }}
            .footer-tag {{ flex-direction: column; gap: 8px; letter-spacing: 3px; }}
        }}
    </style>
</head>
<body>

    <!-- PLATFORM NAV -->
    <nav class="platform-nav">
        <a href="{rel_root}index.html" class="platform-brand">
            <img src="https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png" alt="Logo UNRC">
            <span>Pensamiento Complejo</span>
        </a>
        <button class="mobile-nav-toggle" id="mobileNavToggle" aria-label="Abrir menú de navegación" onclick="toggleMobileNav()">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
        </button>
        <div class="platform-links">
            <a href="{rel_root}index.html" class="platform-link">Inicio</a>
            <a href="{rel_root}red.html" class="platform-link active">Red</a>
            <a href="{rel_root}uca.html" class="platform-link">UCA</a>
            <a href="{rel_root}complejidades-hub.html" class="platform-link">Complejidades Hub</a>
            <a href="{rel_root}newsletter.html" class="platform-link">Newsletter</a>
        </div>
    </nav>

    <!-- CABECERA INSTITUCIONAL CON ESTILO GRÁFICO E IMAGEN EN MEDIO -->
    <header class="hero-container">
        <div class="hero-grid">
            <div class="text-top red-text">RED TRANSVERSAL DE</div>
            <div class="text-pensamiento black-text">PENSAMIENTO</div>
            <img src="https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png" alt="Logo Pensamiento Complejo" class="hero-img">
            <div class="text-complejo black-text">COMPLEJO</div>
            <div class="text-bottom red-text">Y SUSTENTABILIDAD</div>
        </div>
        <div class="hero-subtitle">
            <span>🏛️</span> Claustro Docente e Investigación
        </div>
        <p class="hero-description">
            Conoce los perfiles, trayectorias y campos epistemológicos de las y los docentes adscritos a la Red Transversal de Pensamiento Complejo de la Universidad Nacional Rosario Castellanos.
        </p>
    </header>

    <!-- BUSCADOR PRINCIPAL (SIN CATEGORÍAS) -->
    <section class="search-section">
        <div class="search-box">
            <span class="search-icon">🔍</span>
            <input type="text" id="tagSearch" placeholder="BUSCAR POR DOCENTE, GRADO O ÁREA DE INVESTIGACIÓN..." oninput="filterDocentes()" autocomplete="off">
            <button id="clearSearchBtn" class="clear-btn" onclick="clearSearch()" style="display:none;" aria-label="Limpiar búsqueda">✕</button>
        </div>
        <div class="search-counter">
            Mostrando <strong id="visibleCount">{len(docentes)}</strong> de <strong id="totalDocentesCount">{len(docentes)}</strong> docentes adscritos
        </div>
    </section>

    <!-- LISTA DIRECTA DE DOCENTES -->
    <main class="docentes-section">
        <div class="docentes-grid" id="docentesGrid">
            {cards_html}
        </div>
        <div id="noResults" class="no-results" style="display:none;">
            <div class="no-results-icon">🔎</div>
            <h3>No se encontraron docentes</h3>
            <p>No hay registros que coincidan con "<strong id="searchTermText"></strong>".</p>
            <button class="btn-reset" onclick="clearSearch()">Ver todo el claustro</button>
        </div>
    </main>

    <!-- FOOTER INSTITUCIONAL -->
    <footer>
        <img src="https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png" alt="Logo UNRC" class="logo-footer">
        <div class="footer-tag">
            <span>Claustro Docente</span>
            <span>•</span>
            <span>Red Transversal de Pensamiento Complejo UNRC</span>
        </div>
    </footer>

    <script>
        const initialDocentes = {docentes_json};
        const linkPrefix = "{card_link_prefix}";
        const SPREADSHEET_ID = '{SPREADSHEET_ID}';
        const RED_CSV_URL = `https://docs.google.com/spreadsheets/d/${{SPREADSHEET_ID}}/gviz/tq?tqx=out:csv&sheet=Red`;
        const defaultLogo = 'https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png';

        function escapeHtml(text) {{
            if (!text) return '';
            return String(text)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }}

        function createDocenteCard(doc) {{
            const cleanSlug = (doc.slug || '').replace(/^\\/+/, '').trim();
            const linkUrl = cleanSlug ? `${{linkPrefix}}${{cleanSlug}}.html` : '#';
            const areasList = (doc.areas || '').split(/[,;\\n•*]+/).map(a => a.trim()).filter(Boolean);
            const firstAreas = areasList.slice(0, 2);
            const areasHtml = firstAreas.length > 0 
                ? firstAreas.map(a => `<span class="area-chip">${{escapeHtml(a)}}</span>`).join('') 
                : '<span class="area-chip">Pensamiento Complejo</span>';
            
            const cleanSearchText = `${{doc.nombre || ''}} ${{doc.grado || ''}} ${{doc.areas || ''}} ${{doc.correo || ''}}`.toLowerCase();
            const imgUrl = (doc.imagen && doc.imagen.startsWith('http')) ? doc.imagen : defaultLogo;
            const bioText = (doc.semblanza || '').length > 120 ? doc.semblanza.substring(0, 120) + '...' : (doc.semblanza || '');

            return `
            <article class="docente-card" data-search="${{escapeHtml(cleanSearchText)}}" onclick="window.location.href='${{linkUrl}}'">
                <div class="card-header">
                    <span class="card-degree">${{escapeHtml(doc.grado || 'Docente')}}</span>
                    <div class="card-avatar-wrapper">
                        <img src="${{imgUrl}}" alt="${{escapeHtml(doc.nombre)}}" class="card-avatar" loading="lazy" onerror="this.onerror=null;this.src='${{defaultLogo}}';">
                    </div>
                </div>
                <div class="card-body">
                    <h3 class="card-name">${{escapeHtml(doc.nombre)}}</h3>
                    <div class="card-areas-chips">
                        ${{areasHtml}}
                    </div>
                    <p class="card-bio">${{escapeHtml(bioText)}}</p>
                </div>
                <div class="card-footer">
                    <a href="${{linkUrl}}" class="card-btn" onclick="event.stopPropagation();">
                        <span>Conocer Perfil</span>
                        <span class="arrow">↗</span>
                    </a>
                </div>
            </article>
            `;
        }}

        function toggleMobileNav() {{
            const toggle = document.getElementById('mobileNavToggle');
            const menu = document.querySelector('.platform-links');
            if (!toggle || !menu) return;
            const isOpen = toggle.classList.toggle('open');
            menu.classList.toggle('mobile-open', isOpen);
            document.body.style.overflow = isOpen ? 'hidden' : '';
        }}

        function filterDocentes() {{
            const query = (document.getElementById('tagSearch').value || '').trim().toLowerCase();
            const clearBtn = document.getElementById('clearSearchBtn');
            clearBtn.style.display = query ? 'flex' : 'none';

            const cards = document.querySelectorAll('.docente-card');
            let visible = 0;

            cards.forEach(card => {{
                const searchData = card.getAttribute('data-search') || '';
                if (!query || searchData.includes(query)) {{
                    card.style.display = 'flex';
                    visible++;
                }} else {{
                    card.style.display = 'none';
                }}
            }});

            document.getElementById('visibleCount').innerText = visible;
            const noResults = document.getElementById('noResults');
            if (visible === 0) {{
                document.getElementById('searchTermText').innerText = query;
                noResults.style.display = 'block';
            }} else {{
                noResults.style.display = 'none';
            }}
        }}

        function clearSearch() {{
            const input = document.getElementById('tagSearch');
            input.value = '';
            input.focus();
            filterDocentes();
        }}

        // Mapeo dinámico y exclusivo con la hoja "Red" (todo y solo lo que aparezca en el sheet)
        function syncWithSheet() {{
            if (typeof Papa === 'undefined') return;
            Papa.parse(RED_CSV_URL, {{
                download: true,
                header: false,
                skipEmptyLines: true,
                complete: function(results) {{
                    if (!results || !results.data || results.data.length < 2) return;
                    const rows = results.data.slice(1);
                    const validDocentes = [];

                    rows.forEach((r, idx) => {{
                        if (!r || r.length < 2) return;
                        const nombre = (r[1] || '').trim();
                        if (!nombre || nombre.toLowerCase() === 'nombre completo') return;

                        const correo = (r[0] || '').trim();
                        const grado = (r[2] || '').trim();
                        const semblanza = (r[3] || '').trim();
                        const areas = (r[4] || '').trim();
                        const rg_academia = (r[5] || '').trim();
                        const orcid = (r[6] || '').trim();
                        // OMITIR Col H (r[7]) - Foto drive
                        const publicaciones = (r[8] || '').trim();
                        const portafolio = (r[9] || '').trim();
                        const cv_drive = (r[10] || '').trim();
                        // OMITIR Col L (r[11]) - WhatsApp
                        const imagen = (r[12] || '').trim() || defaultLogo;
                        const rawSlug = (r[13] || '').trim();
                        let cleanSlug = rawSlug.replace(/^\\/+/, '').trim();
                        if (!cleanSlug && nombre) {{
                            cleanSlug = nombre.toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").replace(/[^a-z0-9]/g, "");
                        }}

                        validDocentes.push({{
                            id: idx + 1,
                            correo: correo,
                            nombre: nombre,
                            grado: grado,
                            semblanza: semblanza,
                            areas: areas,
                            rg_academia: rg_academia,
                            orcid: orcid,
                            publicaciones: publicaciones,
                            portafolio: portafolio,
                            cv_drive: cv_drive,
                            imagen: imagen,
                            slug: cleanSlug
                        }});
                    }});

                    if (validDocentes.length === 0) return;

                    const grid = document.getElementById('docentesGrid');
                    if (grid) {{
                        grid.innerHTML = validDocentes.map(d => createDocenteCard(d)).join('\\n');
                    }}
                    const totalEl = document.getElementById('totalDocentesCount');
                    if (totalEl) totalEl.innerText = validDocentes.length;
                    filterDocentes();
                }},
                error: function(err) {{
                    console.warn("Aviso: Sincronización en vivo con Google Sheets no disponible, usando contenido local.", err);
                }}
            }});
        }}
        syncWithSheet();

        // PWA Service Worker Registration
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('{rel_root}sw.js')
                    .catch(err => console.log('SW error:', err));
            }});
        }}
    </script>
</body>
</html>
'''

# 1. Generar red.html en la raíz
with open('/Users/logiciststudio/.gemini/antigravity-ide/scratch/PensamientoComplejo/red.html', 'w', encoding='utf-8') as f:
    f.write(build_exhibitor_html(is_subdir=False))
print("Generado red.html exitosamente.")

# 2. Generar red/index.html para soportar la URL limpia red
with open('/Users/logiciststudio/.gemini/antigravity-ide/scratch/PensamientoComplejo/red/index.html', 'w', encoding='utf-8') as f:
    f.write(build_exhibitor_html(is_subdir=True))
print("Generado red/index.html exitosamente.")
