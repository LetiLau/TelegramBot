import asyncio
import os
import oci
import requests



def send_telegram_alert(message):
    token = os.getenv("USEFUL_BOT")
    chat_id = os.getenv("ADMIN_ID")
    
    """Invia un messaggio Telegram usando direttamente le API HTTP."""
    
    if not token or not chat_id:
        print("[Oracle-Debug] ❌ Impossibile inviare Telegram: Token o Admin ID mancanti.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[Oracle-Debug] Impossibile inviare notifica Telegram: {e}")



async def oracle_cloud_worker():
    """Versione Debugger: Controlla l'ambiente prima di agire."""
    
    print("\n" + "="*50)
    print("🔍 INIZIO DIAGNOSTICA AMBIENTE ORACLE CLOUD 🔍")
    print("="*50)

    # 1. CONTROLLO FILE FISICI (Secret Files di Render)
    pem_path = "/etc/secrets/oci_key.pem"
    env_path = "/etc/secrets/.env"
    
    has_pem = os.path.exists(pem_path)
    has_env = os.path.exists(env_path)
    
    print(f"File Chiave (.pem) in {pem_path}  -> {'✅ PRESENTE' if has_pem else '❌ MANCANTE'}")
    print(f"File Variabili (.env) in {env_path} -> {'✅ PRESENTE' if has_env else '❌ MANCANTE'}")
    
    if not has_pem:
        print("💡 SUGGERIMENTO: Su Render, crea un Secret File chiamato 'oci_key.pem'")
    if not has_env:
        print("💡 SUGGERIMENTO: Su Render, crea un Secret File chiamato '.env'")

    # 2. CONTROLLO VARIABILI D'AMBIENTE
    vars_to_check = [
        "OCI_USER_ID", "OCI_TENANCY_ID", "OCI_FINGERPRINT",
        "OCI_REGION", "OCI_COMPARTMENT_ID", "OCI_SUBNET_ID",
        "OCI_IMAGE_ID", "OCI_SSH_PUBLIC_KEY"
    ]

    print("\n--- Analisi Variabili ---")
    mancanti = []
    
    for var in vars_to_check:
        val = os.environ.get(var)
        if val:
            # Nascondiamo la parte centrale per non stampare chiavi intere nei log
            masked = f"{val[:6]}...{val[-4:]}" if len(val) > 15 else "***[OK]***"
            print(f"✅ {var:<22}: TROVATA ({masked})")
        else:
            print(f"❌ {var:<22}: MANCANTE O VUOTA!")
            mancanti.append(var)

    print("="*50 + "\n")

    # 3. VALUTAZIONE RISULTATO
    if not has_pem or mancanti:
        errore_totale = (
            f"❌ DIAGNOSTICA FALLITA!\n"
            f"File PEM presente: {has_pem}\n"
            f"Variabili mancanti: {', '.join(mancanti) if mancanti else 'Nessuna, ma manca il file PEM'}"
        )
        print(errore_totale)
        send_telegram_alert(errore_totale)
        return  # BLOCCA L'ESECUZIONE QUI. Inutile provare a contattare Oracle.

    send_telegram_alert("✅ Diagnostica superata! Tutte le variabili trovate. Avvio connessione a Oracle...")

    # ---------------------------------------------------------
    # SE TUTTO È OK, PROCEDIAMO CON ORACLE
    # ---------------------------------------------------------
    config = {
        "user": os.environ.get("OCI_USER_ID"),
        "key_file": pem_path,
        "fingerprint": os.environ.get("OCI_FINGERPRINT"),
        "tenancy": os.environ.get("OCI_TENANCY_ID"),
        "region": os.environ.get("OCI_REGION")
    }
    
    try:
        compute_client = oci.core.ComputeClient(config)
    except Exception as e:
        msg = f"❌ Errore critico nel setup del client Oracle: {e}"
        print(msg)
        send_telegram_alert(msg)
        return

    # Sostituisci con il tuo AD esatto (es. Uocm:EU-FRANKFURT-1-AD-1)
    AVAILABILITY_DOMAIN = "fFRg:EU-TURIN-1-AD-1"

    instance_details = oci.core.models.LaunchInstanceDetails(
        compartment_id=os.environ.get("OCI_COMPARTMENT_ID"),
        availability_domain=AVAILABILITY_DOMAIN,
        shape="VM.Standard.A1.Flex",
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(ocpus=4, memory_in_gbs=24),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=os.environ.get("OCI_SUBNET_ID"),
            assign_public_ip=True
        ),
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            source_type="image",
            image_id=os.environ.get("OCI_IMAGE_ID"),
            boot_volume_size_in_gbs=160
        ),
        metadata={"ssh_authorized_keys": os.environ.get("OCI_SSH_PUBLIC_KEY")},
        display_name="Minecraft_Server_ARM"
    )

    tentativo = 1
    while True:
        try:
            print(f"[Oracle] Tentativo {tentativo} di creazione VM...")
            await asyncio.to_thread(compute_client.launch_instance, instance_details)
            msg = "✅ SUCCESSO! La VM Oracle Cloud è stata creata. Spegni lo script!"
            print(msg)
            send_telegram_alert(msg)
            break
            
        except oci.exceptions.ServiceError as e:
            if e.status in [500, 429]:
                print(f"[Oracle] Tentativo {tentativo}: Out of capacity. Riprovo tra 60s...")
                await asyncio.sleep(120)
                tentativo += 1
            else:
                errore_msg = f"❌ Errore API Oracle (Codice {e.status}): {e.message}"
                print(errore_msg)
                send_telegram_alert(errore_msg)
                break
