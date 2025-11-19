import xml.etree.ElementTree as ET
import os
from collections import defaultdict

# --- Definició de colors per a la consola (codis ANSI) ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def formatar_color_numero(numero):
    if numero > 0:
        return f"{Colors.OKGREEN}{numero}{Colors.ENDC}"
    else:
        return f"{Colors.FAIL}{numero}{Colors.ENDC}"


def color_urgencia(text_urgencia):
    if text_urgencia.startswith("Alta"):
        return f"{Colors.FAIL}{text_urgencia}{Colors.ENDC}"
    elif text_urgencia.startswith("Mitjana"):
        return f"{Colors.WARNING}{text_urgencia}{Colors.ENDC}"
    elif text_urgencia.startswith("Baixa"):
        return f"{Colors.OKGREEN}{text_urgencia}{Colors.ENDC}"
    else:
        return text_urgencia


def get_text_or_na(element, tag_name):
    node = element.find(tag_name)
    if node is not None and node.text is not None:
        return node.text.strip()
    return "N/A"


def processar_incidencies(fitxer_xml, mostrar_detalls=True):
    try:
        arbre = ET.parse(fitxer_xml)
        arrel = arbre.getroot()
    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: No s'ha trobat el fitxer '{fitxer_xml}'.{Colors.ENDC}")
        return
    except ET.ParseError:
        print(f"{Colors.FAIL}Error: El fitxer '{fitxer_xml}' no és un XML vàlid.{Colors.ENDC}")
        return

    total_respostes = 0
    comptador_urgencia = defaultdict(int)
    comptador_tipus = defaultdict(int)
    llista_incidencies = []

    for resposta in arrel.findall('resposta'):
        total_respostes += 1
        incidencia_data = {
            'timestamp': get_text_or_na(resposta, 'Marca_de_temps'),
            'email': get_text_or_na(resposta, 'Adreça_electrònica'),
            'qui': get_text_or_na(resposta, 'field_1._Nom_i_cognom_professor_alumne_que_informa'),
            'urgencia': get_text_or_na(resposta, 'field_2._Urgència_'),
            'aula': get_text_or_na(resposta, 'field_3._Aula_on_està_l_incidència.'),
            'tipus_dispositiu': get_text_or_na(resposta, 'field_4._Tipus_de_dispositiu'),
            'codi_dispositiu': get_text_or_na(resposta, 'field_5._Dispositiu_d_incidència_Codi_dispositiu'),
            'tipus_incidencia': get_text_or_na(resposta, 'field_6._Quin_tipus_d_incidència_és_'),
            'desc': get_text_or_na(resposta, 'field_7._Explicació_de_l_incidència'),
            'error': get_text_or_na(resposta, 'field_8._Missatge_de_l_error_exactament_'),
            'profe': get_text_or_na(resposta, 'field_9._Professor_s_responsable_a_l_aula'),
            'obs': get_text_or_na(resposta, 'field_10._Altres_observacions__Perquè__com__etc...__')
        }
        llista_incidencies.append(incidencia_data)
        comptador_urgencia[incidencia_data['urgencia']] += 1
        comptador_tipus[incidencia_data['tipus_incidencia']] += 1

    os.system('cls' if os.name == 'nt' else 'clear')

    # --- RESUM ---
    print(f"{Colors.BOLD}{Colors.OKBLUE}--- RESUM D'INCIDÈNCIES REBUDES ---{Colors.ENDC}")
    print(f"Total d'incidències: {Colors.BOLD}{total_respostes}{Colors.ENDC}")
    print("-" * 35)

    print(f"{Colors.OKCYAN}Recompte per Urgència:{Colors.ENDC}")
    for urgencia, count in comptador_urgencia.items():
        percent = (count / total_respostes * 100) if total_respostes > 0 else 0
        print(f"  - {urgencia:<40} : {formatar_color_numero(count)} ({percent:.2f}%)")

    print(f"\n{Colors.OKCYAN}Recompte per Tipus d'Incidència:{Colors.ENDC}")
    for tipus, count in comptador_tipus.items():
        percent = (count / total_respostes * 100) if total_respostes > 0 else 0
        print(f"  - {tipus:<40} : {formatar_color_numero(count)} ({percent:.2f}%)")

    # --- DETALLS (solo si el usuario lo pide) ---
    if mostrar_detalls:
        print("\n" * 2)
        print(f"{Colors.BOLD}{Colors.OKBLUE}--- DETALL DE LES INCIDÈNCIES ---{Colors.ENDC}")
        if not llista_incidencies:
            print(f"{Colors.WARNING}No s'ha trobat cap incidència per llistar.{Colors.ENDC}")
            return
        for i, incidencia in enumerate(llista_incidencies):
            print(f"\n{Colors.UNDERLINE}Incidència #{i + 1}{Colors.ENDC}")
            print(f"  {Colors.OKCYAN}Data:{Colors.ENDC}         {incidencia['timestamp']}")
            print(f"  {Colors.OKCYAN}Reportat per:{Colors.ENDC} {incidencia['qui']} ({incidencia['email']})")
            print(f"  {Colors.OKCYAN}Professor/a:{Colors.ENDC}  {incidencia['profe']}")
            print(f"  {Colors.OKCYAN}Urgència:{Colors.ENDC}     {color_urgencia(incidencia['urgencia'])}")
            print(f"  {Colors.OKCYAN}Aula:{Colors.ENDC}         {incidencia['aula']}")
            print(f"  {Colors.OKCYAN}Dispositiu:{Colors.ENDC}   {incidencia['tipus_dispositiu']} (Codi: {incidencia['codi_dispositiu']})")
            print(f"  {Colors.OKCYAN}Tipus:{Colors.ENDC}        {incidencia['tipus_incidencia']}")
            print(f"  {Colors.OKCYAN}Descripció:{Colors.ENDC}   {incidencia['desc']}")
            print(f"  {Colors.OKCYAN}Missatge error:{Colors.ENDC} {incidencia['error']}")
            print(f"  {Colors.OKCYAN}Observacions:{Colors.ENDC}  {incidencia['obs']}")
            print("-" * 40)

    print(f"\n{Colors.OKCYAN}Processament finalitzat.{Colors.ENDC}")


# --- Punt d'entrada ---
if __name__ == "__main__":
    NOM_FITXER_XML = "../CSV_to_XML/XML/TA04_G3_(respostes)_Respostes_al_formulari_1.xml"

    print(f"{Colors.BOLD}{Colors.OKBLUE}--- MENÚ PRINCIPAL ---{Colors.ENDC}")
    print("1. Veure només el resum")
    print("2. Veure resum + detalls")

    opcio = None
    try:
        while True:
            opcio = input("Escull una opció (1/2): ").strip()
            if opcio in ("1", "2"):
                break
            print(f"{Colors.WARNING}Opció invàlida. Si us plau, escriu '1' o '2'.{Colors.ENDC}")
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Colors.FAIL}Operació cancel·lada per l'usuari.{Colors.ENDC}")
        exit(1)

    if opcio == "1":
        processar_incidencies(NOM_FITXER_XML, mostrar_detalls=False)
    else:  # opcio == "2"
        processar_incidencies(NOM_FITXER_XML, mostrar_detalls=True)