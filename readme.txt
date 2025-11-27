TactoAR
Software per la segmentazione di immagini mediche e la creazione di modelli 3D.

Prerequisiti: Python 3.10
Python 3.10 o versioni successive sono necessarie per far girare il progetto.
Puoi scaricare l'ultima versione dal sito ufficiale di Python: https://www.python.org/downloads/

Installazione:

1) Crea una directory e clona la repository

md Tac2Ar
git clone https://github.com/Tonyciuffo/Tac2AR.git

2) Entra nella directory e crea un ambiente virtuale con venv:

cd Tac2Ar

Windows: python -m venv venv
Linux/MacOs: python3 -m venv venv

3) Attiva l'ambiente virtuale:

Windows: venv\Scripts\activate
Linux/macOS: source venv/bin/activate

4) installa i requirements

pip install -r requirements.txt

5) Per abilitare l'accelerazione GPU installa PyTorch con CUDA (scegli la versione adatta alla tua scheda video):

RTX serie 30/40:
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

RTX serie 50 e superiori:
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

6) Scarica Blender 4.5 LTS ed estrai/copia la cartella estratta nella directory base del progetto con il nome "Blender":

Windows: https://download.blender.org/release/Blender4.5/blender-4.5.0-windows-x64.zip
Linux: https://download.blender.org/release/Blender4.5/blender-4.5.0-linux-x64.tar.xz
MacOs (x64 - Intel): https://download.blender.org/release/Blender4.5/blender-4.5.0-macos-x64.dmg
MacOs (arm64 -AMD): https://download.blender.org/release/Blender4.5/blender-4.5.0-macos-arm64.dmg

7) Metti uno stack di DICOM o un NIfTI nella directory Input
Ricorda di preparare una cartella per il cliente ed una sottocartella per la sessione
(es. Ospedale_A\Caso_N\scan.nii)
(es. Ospedale_A\Caso_N\DICOM\Images*.dcm)

8) In config.py, nelle impostazioni generali del progetto, imposta cliente e sessione con le directory di Input in modo che coincidano
Es.
# ID del cliente corrente. Usato per la strutturazione delle directory e i nomi dei file.
CLIENT_ID = "Ospedale_A"

# ID della sessione del progetto corrente (es. ID scansione paziente). Usato per la strutturazione delle directory e i nomi dei file.
PROJECT_SESSION_ID = "Caso_N"

8) Esegui con:
python Main.py
Pipeline di segmentazione renale? [y/N] -> Se "y" avvia pipeline di segmentazione renale eseguendo run_all.sh (Aggiornare paths kidney_segmentation_folder)
E' possibile lanciare i processi di segmentazione e di fix delle geometrie indipendentemente con:
python execute_segmentator_pipeline.py
python execute_blender_pipeline-py

9) Nella directory di Output verranno generati:
- Un file glb in standard PRB
- Un file fbx in standard UPR
- Una direcotry Textures con tutte le texture nei due standard (la metalness nel formato URP viene chiamata "_MetallicSmoothness")
- 1 scena blender con history (materiali procedurali, proiettori, modificatori)
- 2 scene blender a valle del bake (uno PBR ed uno URP per debug)
- 2 manifest in formato json con l'associazione segmenti-materiali prima e dopo l'interrogazione del database snomed (al momento viene interrogato il csv fornito con totalsegmentator)
- 1 file log nella root del progetto. Verboso ma completo.

BUG NOTI:
Triangoli neri sulle mesh:
Da indagare. corrispondono a facce su parti di uv non coperte da texture. Spostati da un apply deformer, transform, uv... da indagare


ACKNOWLEDGMENTS / RINGRAZIAMENIT:

Total Segmentator:
https://pubs.rsna.org/doi/10.1148/ryai.230024

Blender:
https://www.blender.org/about/credits/

Python:
https://www.python.org/doc/copyright/

