import urllib.request, ssl, csv, io, os, html, re

ctx = ssl._create_unverified_context()
SPREADSHEET_ID = '1FLfUeeAXg8-w2HD1B0IiQ24Qu728MX59DvLWIN-qHT4'
RED_CSV_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Red'

req = urllib.request.Request(RED_CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as resp:
    reader = list(csv.reader(io.StringIO(resp.read().decode('utf-8'))))

header = reader[0]
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
    # OMIT Col H (r[7] - Drive photo)
    publicaciones = (r[8] or '').strip()
    portafolio = (r[9] or '').strip()
    cv_drive = (r[10] or '').strip()
    # OMIT Col L (r[11] - WhatsApp)
    imagen = (r[12] or '').strip() # CDN R2
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

print(f'Procesados {len(docentes)} docentes.')

def parse_publications_to_items(pubs_text):
    if not pubs_text:
        return []
    
    # Separar por viñetas o saltos de línea
    raw_lines = re.split(r'\n+|•|\t|\r', pubs_text)
    items = []
    
    url_regex = re.compile(r'https?://[^\s]+')
    
    current_entry = ""
    for line in raw_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        # Descartar encabezados tipo "ARTÍCULOS EN REVISTAS..."
        if line_clean.isupper() and len(line_clean) > 10 and not any(char.isdigit() for char in line_clean):
            continue
        
        # Detectar si contiene link
        found_urls = url_regex.findall(line_clean)
        link = found_urls[0] if found_urls else ""
        
        # Limpiar texto
        text_only = url_regex.sub('', line_clean).strip()
        text_only = text_only.rstrip('.,;:')
        if text_only.lower().endswith('disponible en') or text_only.lower().endswith('disponible'):
            text_only = text_only[:text_only.lower().rfind('disponible')].strip().rstrip('.,;:')
            
        if len(text_only) > 15:
            items.append({
                't': text_only,
                'l': link
            })
            
    return items

def build_microsite_html(d, rel_prefix='../'):
    pubs = parse_publications_to_items(d['publicaciones'])
    
    # Formatear semblanza en párrafos
    semblanza_paragraphs = [p.strip() for p in d['semblanza'].split('\n') if p.strip()]
    semblanza_html = "<br><br>".join(html.escape(p) for p in semblanza_paragraphs) if semblanza_paragraphs else "Perfil en actualización académica institucional."

    # Formatear líneas de investigación
    areas_list = [a.strip() for a in re.split(r'[,;\n•*]+', d['areas']) if a.strip()]
    lines_str = " • ".join(html.escape(a) for a in areas_list) if areas_list else html.escape(d['areas'])

    # Botones de acción
    action_buttons_html = ""
    if d['orcid'] and 'orcid.org' in d['orcid']:
        orcid_clean = d['orcid'] if d['orcid'].startswith('http') else 'https://orcid.org/' + d['orcid'].replace('ORCID:', '').strip()
        action_buttons_html += f'<a href="{orcid_clean}" target="_blank" class="btn-minimal btn-outline">ORCID</a>\n'
    elif d['orcid'] and len(d['orcid']) > 5:
        orcid_clean = 'https://orcid.org/' + d['orcid'].replace('ORCID:', '').strip()
        action_buttons_html += f'<a href="{orcid_clean}" target="_blank" class="btn-minimal btn-outline">ORCID</a>\n'

    if d['rg_academia'] and d['rg_academia'] != 'N/A' and d['rg_academia'].startswith('http'):
        label = "ResearchGate" if "researchgate" in d['rg_academia'].lower() else ("Google Scholar" if "scholar" in d['rg_academia'].lower() else "Academia.edu")
        action_buttons_html += f'<a href="{d["rg_academia"]}" target="_blank" class="btn-minimal btn-outline">{label}</a>\n'

    if d['portafolio'] and d['portafolio'].startswith('http'):
        action_buttons_html += f'<a href="{d["portafolio"]}" target="_blank" class="btn-minimal btn-outline">Portafolio / Web</a>\n'

    action_buttons_html += f'<div class="btn-minimal btn-solid" onclick="toggleCV(true)">Curriculum Vitae</div>\n'

    # Lista de publicaciones APA
    if pubs:
        pubs_html = ""
        for p in pubs:
            link_html = f'<a href="{html.escape(p["l"])}" target="_blank" class="btn-link">Consultar Publicación ↗</a>' if p['l'] else ''
            pubs_html += f'''
            <div class="apa-entry">
                <div class="apa-text">{html.escape(p["t"])}</div>
                {link_html}
            </div>
            '''
    else:
        pubs_html = '''
        <div style="padding: 30px; background: #fafafa; border-radius: 8px; border: 1px solid #eee; text-align: center; color: #666; margin-bottom: 40px;">
            <p style="font-size: 1rem; margin-bottom: 8px; font-weight: 700; color: #ae0340;">📋 Registro en Proceso</p>
            <p style="font-size: 0.9rem; margin: 0;">La producción intelectual y publicaciones arbitradas de este perfil se encuentran en proceso de catalogación institucional en la Red.</p>
        </div>
        '''

    cv_download_btn = ""
    if d['cv_drive'] and d['cv_drive'].startswith('http'):
        cv_download_btn = f'''
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #f0f0f0;">
            <a href="{d['cv_drive']}" target="_blank" class="btn-minimal btn-solid" style="display:inline-block; max-width:280px; text-decoration:none;">Descargar CV en PDF ↗</a>
        </div>
        '''

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(d['nombre'])} | Red Transversal de Pensamiento Complejo UNRC</title>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@100;300;400;700;900&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
    <style>
        :root {{ 
            --vino: #ae0340; 
            --vino-dark: #620137; 
            --bg: #ffffff; 
            --text: #111111; 
            --muted: #666666; 
            --border: #f0f0f0;
        }}
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Lato', sans-serif; 
            margin: 0; 
            background: var(--bg); 
            color: var(--text); 
            -webkit-font-smoothing: antialiased; 
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
            background: var(--vino);
        }}

        /* 2. SUBHEADER STICKY CON IDENTIDAD DOCENTE */
        .header-identity-bar {{ 
            background: rgba(255, 255, 255, 0.98); 
            padding: 0 5%; 
            display: flex; 
            align-items: center; 
            position: sticky; 
            top: 60px; 
            z-index: 999; 
            height: 52px;
            border-bottom: 1px solid #f0f0f0;
        }}
        .header-identity {{
            display: flex; 
            align-items: center; 
            gap: 15px; 
            opacity: 0; 
            transform: translateX(-20px); 
            transition: 0.5s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .header-identity.visible {{ opacity: 1; transform: translateX(0); }}
        .header-photo {{ width: 34px; height: 34px; border-radius: 50%; object-fit: cover; border: 1.5px solid var(--vino); }}
        .header-name {{ font-weight: 900; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 2px; color: var(--vino); }}
        .back-to-red {{
            margin-left: auto;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--vino);
            text-decoration: none;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid var(--vino);
            transition: all 0.25s;
        }}
        .back-to-red:hover {{
            background: var(--vino);
            color: #fff;
        }}

        /* 3. HERO SECTION */
        .hero {{ 
            display: grid; 
            grid-template-columns: 1fr 1.25fr; 
            min-height: 65vh; 
            align-items: center; 
            padding: 50px 5% 40px; 
            gap: 60px; 
            max-width: 1300px;
            margin: 0 auto;
        }}
        
        .photo-box {{ display: flex; justify-content: center; align-items: center; }}
        .photo-box img {{ 
            width: 100%; 
            max-width: 320px; 
            aspect-ratio: 1/1; 
            object-fit: cover; 
            border-radius: 50%; 
            filter: grayscale(100%); 
            border: 2px solid #f0f0f0; 
            transition: 0.8s ease; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.06); 
        }}
        .photo-box img:hover {{ filter: grayscale(0%); transform: scale(1.02); }}
        
        .hero-info h1 {{ 
            font-weight: 900; 
            font-size: clamp(2rem, 3.8vw, 3.2rem); 
            line-height: 1.05; 
            color: var(--vino); 
            margin: 0 0 10px; 
            text-transform: uppercase; 
            letter-spacing: -0.01em;
        }}
        
        .degree-badge {{
            display: inline-block;
            background: rgba(174, 3, 64, 0.08);
            color: var(--vino);
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            padding: 5px 14px;
            border-radius: 20px;
            margin-bottom: 12px;
            border: 1px solid rgba(174, 3, 64, 0.15);
        }}

        .lines {{ 
            font-size: 0.85rem; 
            letter-spacing: 2px; 
            text-transform: uppercase; 
            color: var(--muted); 
            margin: 12px 0 20px; 
            font-weight: 400; 
            line-height: 1.6; 
        }}
        
        .semblanza-text {{ 
            font-size: 1.05rem; 
            font-weight: 300; 
            line-height: 1.85; 
            margin: 20px 0; 
            color: #444; 
            text-align: justify; 
            max-width: 95%; 
        }}
        
        .contact-info {{ 
            font-size: 0.75rem; 
            font-weight: 600; 
            color: var(--vino-dark); 
            letter-spacing: 1px; 
            margin-top: 15px; 
            text-transform: uppercase; 
        }}

        .action-bar {{ display: flex; gap: 12px; margin-top: 25px; flex-wrap: wrap; }}
        .btn-minimal {{ 
            padding: 10px 18px; 
            text-decoration: none; 
            text-transform: uppercase; 
            font-size: 0.68rem; 
            letter-spacing: 2px; 
            font-weight: 700; 
            border: 1px solid var(--vino); 
            transition: 0.3s; 
            cursor: pointer; 
            text-align: center; 
            border-radius: 4px;
        }}
        .btn-outline {{ color: var(--vino); background: transparent; }}
        .btn-outline:hover {{ background: var(--vino); color: white; transform: translateY(-2px); }}
        .btn-solid {{ background: var(--vino); color: white; }}
        .btn-solid:hover {{ background: var(--vino-dark); border-color: var(--vino-dark); transform: translateY(-2px); }}

        /* 4. PRODUCCIÓN INTELECTUAL */
        .section-label {{ 
            font-size: 1.8rem; 
            font-weight: 900; 
            text-transform: uppercase; 
            margin: 80px 5% 30px; 
            border-bottom: 2px solid var(--text); 
            padding-bottom: 12px; 
            max-width: 1300px;
        }}
        .pub-list {{ 
            padding: 0 5% 100px; 
            max-width: 1300px;
            margin: 0 auto;
        }}
        .apa-entry {{ 
            margin-bottom: 25px; 
            font-size: 0.92rem; 
            line-height: 1.65; 
            border-bottom: 1px solid #f4f4f4; 
            padding-bottom: 20px; 
            display: flex; 
            justify-content: space-between; 
            align-items: flex-start; 
            gap: 30px; 
        }}
        .apa-text {{ color: #222; max-width: 85%; }}
        .btn-link {{ 
            font-size: 0.65rem; 
            font-weight: 900; 
            color: var(--vino); 
            text-decoration: none; 
            border: 1px solid var(--vino); 
            padding: 7px 14px; 
            transition: 0.3s; 
            white-space: nowrap; 
            text-transform: uppercase; 
            border-radius: 4px;
        }}
        .btn-link:hover {{ background: var(--vino); color: white; }}

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
            color: var(--vino); 
            font-size: 0.72rem; 
            font-weight: 600; 
            letter-spacing: 6px; 
            text-transform: uppercase; 
            text-align: center; 
            display: flex; 
            flex-direction: row; 
            flex-wrap: wrap; 
            justify-content: center; 
            gap: 15px;
        }}

        /* 6. MODAL CV */
        .modal-overlay {{ 
            position: fixed; 
            top: 0; left: 0; 
            width: 100%; height: 100%; 
            background: rgba(174, 3, 64, 0.3); 
            backdrop-filter: blur(16px); 
            -webkit-backdrop-filter: blur(16px); 
            z-index: 20000; 
            display: none; 
            justify-content: center; 
            align-items: center; 
            padding: 20px;
        }}
        .modal-box {{ 
            width: 100%;
            max-width: 800px; 
            max-height: 85vh; 
            background: white; 
            padding: 50px; 
            overflow-y: auto; 
            position: relative; 
            box-shadow: 0 40px 80px rgba(0,0,0,0.25); 
            border-radius: 12px;
            border: 1px solid #eee; 
        }}
        .close-btn {{ 
            position: absolute; 
            top: 25px; right: 30px; 
            cursor: pointer; 
            font-size: 0.75rem; 
            font-weight: 900; 
            letter-spacing: 2px; 
            color: var(--vino); 
        }}
        .cv-title {{ 
            font-weight: 900; 
            font-size: 1.8rem; 
            text-transform: uppercase; 
            color: var(--vino); 
            margin-bottom: 25px; 
            border-bottom: 4px solid var(--vino); 
            display: inline-block; 
            padding-bottom: 6px;
        }}
        .cv-section h4 {{ 
            border-bottom: 1px solid #f0f0f0; 
            text-transform: uppercase; 
            font-size: 0.8rem; 
            letter-spacing: 2px; 
            color: var(--vino); 
            margin-top: 30px; 
            padding-bottom: 8px; 
        }}
        .cv-row {{ 
            display: grid; 
            grid-template-columns: 140px 1fr; 
            gap: 20px; 
            margin: 15px 0; 
            font-size: 0.9rem; 
            font-weight: 300; 
            line-height: 1.6; 
            color: #444; 
        }}
        .cv-year {{ font-weight: 700; color: #999; }}

        @media(max-width: 900px) {{
            .hero {{ grid-template-columns: 1fr; min-height: auto; padding-bottom: 40px; gap: 30px; text-align: center; }}
            .semblanza-text {{ text-align: left; margin: 20px auto; }}
            .action-bar {{ justify-content: center; }}
            .apa-entry {{ flex-direction: column; gap: 15px; }}
            .modal-box {{ padding: 30px 20px; }}
            .cv-row {{ grid-template-columns: 1fr; gap: 6px; }}
        }}
    </style>
</head>
<body>

    <!-- PLATFORM NAV -->
    <nav class="platform-nav">
        <a href="{rel_prefix}index.html" class="platform-brand">
            <img src="https://pub-6fb96c9e88234007a84a1dee992411f5.r2.dev/display_1789606914957_Logo_pensamiento_Complejo.png" alt="Logo UNRC">
            <span>Pensamiento Complejo</span>
        </a>
        <div class="platform-links">
            <a href="{rel_prefix}index.html" class="platform-link">Inicio</a>
            <a href="{rel_prefix}red.html" class="platform-link active">Red</a>
            <a href="{rel_prefix}uca.html" class="platform-link">UCA</a>
            <a href="{rel_prefix}complejidades-hub.html" class="platform-link">Complejidades Hub</a>
            <a href="{rel_prefix}newsletter.html" class="platform-link">Newsletter</a>
        </div>
    </nav>

    <!-- STICKY IDENTITY HEADER -->
    <div class="header-identity-bar">
        <div class="header-identity" id="headerIdentity">
            <img src="{d['imagen']}" class="header-photo" alt="{html.escape(d['nombre'])}">
            <span class="header-name">{html.escape(d['nombre'])}</span>
        </div>
        <a href="{rel_prefix}red.html" class="back-to-red">‹ Volver a la Red</a>
    </div>

    <!-- HERO -->
    <div class="hero" id="heroTrigger">
        <div class="photo-box">
            <img src="{d['imagen']}" alt="{html.escape(d['nombre'])}">
        </div>
        <div class="hero-info">
            <span class="degree-badge">{html.escape(d['grado'] or 'Docente Investigador')}</span>
            <h1>{html.escape(d['nombre'])}</h1>
            <div class="lines">{lines_str}</div>
            <div class="semblanza-text">{semblanza_html}</div>
            {f'<div class="contact-info">Contacto institucional: {html.escape(d["correo"])}</div>' if d['correo'] else ''}
            <div class="action-bar">
                {action_buttons_html}
            </div>
        </div>
    </div>

    <!-- PRODUCCIÓN INTELECTUAL -->
    <h2 class="section-label">Producción Intelectual</h2>
    <div class="pub-list">
        {pubs_html}
    </div>

    <!-- MODAL CV -->
    <div id="cvModal" class="modal-overlay" onclick="toggleCV(false)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <div class="close-btn" onclick="toggleCV(false)">[ CERRAR ]</div>
            <div class="cv-title">Trayectoria Académica</div>
            
            <div class="cv-section">
                <h4>Grado y Especialidad</h4>
                <div class="cv-row">
                    <div class="cv-year">Formación</div>
                    <div><strong>{html.escape(d['grado'])}</strong><br>Universidad Nacional Rosario Castellanos</div>
                </div>
                <div class="cv-row">
                    <div class="cv-year">Líneas de Investigación</div>
                    <div>{lines_str}</div>
                </div>
            </div>

            <div class="cv-section">
                <h4>Semblanza Curricular</h4>
                <div style="font-size:0.92rem; line-height:1.7; color:#444; margin-top:10px;">
                    {semblanza_html}
                </div>
            </div>

            {cv_download_btn}
        </div>
    </div>

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
        gsap.registerPlugin(ScrollTrigger);
        ScrollTrigger.create({{
            trigger: "#heroTrigger",
            start: "top -50px",
            onEnter: () => document.getElementById('headerIdentity').classList.add('visible'),
            onLeaveBack: () => document.getElementById('headerIdentity').classList.remove('visible')
        }});

        function toggleCV(show) {{ 
            document.getElementById('cvModal').style.display = show ? 'flex' : 'none'; 
            document.body.style.overflow = show ? 'hidden' : '';
        }}
    </script>
</body>
</html>
'''

# 1. Generar los micrositios para cada docente
out_dir = '/Users/logiciststudio/.gemini/antigravity-ide/scratch/PensamientoComplejo/red'
os.makedirs(out_dir, exist_ok=True)

for d in docentes:
    slug = d['slug']
    # 1. Archivo en red/{slug}.html (rel_prefix='../')
    file_path_html = os.path.join(out_dir, f"{slug}.html")
    with open(file_path_html, 'w', encoding='utf-8') as f:
        f.write(build_microsite_html(d, rel_prefix='../'))
    print(f"Creado micrositio: red/{slug}.html")

    # 2. Archivo en red/{slug}/index.html (rel_prefix='../../') para permitir URL limpia red/{slug}
    slug_dir = os.path.join(out_dir, slug)
    os.makedirs(slug_dir, exist_ok=True)
    file_path_index = os.path.join(slug_dir, "index.html")
    with open(file_path_index, 'w', encoding='utf-8') as f:
        f.write(build_microsite_html(d, rel_prefix='../../'))
    print(f"Creado micrositio limpio: red/{slug}/index.html")

print("Todos los micrositios estáticos han sido generados exitosamente.")
