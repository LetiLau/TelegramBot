import asyncio
import os
import oci

async def oracle_cloud_worker(app_bot):
    """
    Tenta di creare la VM in loop.
    Prende in input l'istanza del bot per inviare le notifiche push all'admin.
    """
    admin_id = os.getenv("ADMIN_ID")
    if not admin_id:
        print("[Oracle] ERRORE: ADMIN_ID mancante nelle variabili d'ambiente.")
        return

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
        print(f"[Oracle] Errore di inizializzazione client: {e}")
        return

    # Inserisci il tuo Availability Domain esatto (es. Uocm:EU-FRANKFURT-1-AD-1)
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
            
            # Chiamata API bloccante delegata a un thread separato
            await asyncio.to_thread(compute_client.launch_instance, instance_details)
            
            msg = "✅ Successo! La VM Oracle Cloud è stata creata. Puoi disattivare lo script su Render."
            print(msg)
            # Notifica tramite il bot passato dal main
            await app_bot.bot.send_message(chat_id=admin_id, text=msg)
            break
            
        except oci.exceptions.ServiceError as e:
            if e.status in [500, 429]:
                print(f"[Oracle] Out of capacity (Errore {e.status}). Riprovo tra 60s...")
                await asyncio.sleep(60)
                tentativo += 1
            else:
                errore_msg = f"❌ Errore critico Oracle: {e.message}"
                print(errore_msg)
                await app_bot.bot.send_message(chat_id=admin_id, text=errore_msg)
                break
