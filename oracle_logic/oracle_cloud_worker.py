import asyncio
import os
import oci
import requests

def send_telegram_alert(message):
    """Invia un messaggio Telegram usando direttamente le API HTTP."""
    token = os.getenv("USEFUL_BOT")
    chat_id = os.getenv("ADMIN_ID")
    
    if not token or not chat_id:
        print("[Oracle] Token o Admin ID mancanti per la notifica Telegram.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[Oracle] Impossibile inviare notifica Telegram: {e}")

async def oracle_cloud_worker(): # Nessun parametro in ingresso!
    """Tenta di creare la VM in loop."""
    
    # Messaggio di avvio
    send_telegram_alert("🚀 Script Oracle avviato in background. Inizio polling...")

    config = {
        "user": os.environ.get("OCI_USER_ID"),
        "key_file": "/etc/secrets/oci_key.pem",
        "fingerprint": os.environ.get("OCI_FINGERPRINT"),
        "tenancy": os.environ.get("OCI_TENANCY_ID"),
        "region": os.environ.get("OCI_REGION")
    }
    
    try:
        compute_client = oci.core.ComputeClient(config)
    except Exception as e:
        msg = f"❌ Errore di inizializzazione client Oracle: {e}"
        print(msg)
        send_telegram_alert(msg)
        return

    # RICORDATI DI INSERIRE IL TUO AD ESATTO QUI
    AVAILABILITY_DOMAIN = "INSERISCI_IL_TUO_AD_QUI" 

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
                await asyncio.sleep(60)
                tentativo += 1
            else:
                errore_msg = f"❌ Errore critico API Oracle: {e.message}"
                print(errore_msg)
                send_telegram_alert(errore_msg)
                break
