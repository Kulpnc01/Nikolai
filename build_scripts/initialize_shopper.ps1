You are initializing the Shopper Assistant Node (SAN) development environment.

Your tasks:

1. Prepare the DevDrive on E:\ for module development.
   - Create E:\Nikolai\Modules\ShopperModule\
   - Create subdirectories:
       /spec
       /contracts
       /integration
       /build_output
       /android_app
       /logs
       /pipeline

2. Create the Shopper Module integration contract.
   - Define expected inputs from GCLI (build spec, file tree, code artifacts).
   - Define expected outputs to GCLI (status, validation, runtime constraints).
   - Define the runtime interface between SAN and Nikolai:
       - Data ingestion API
       - Overlay instruction API
       - UI automation instruction schema
       - BLE interaction schema
       - Navigation/media streaming schema

3. Prepare the module manifest.
   - Module name: Shopper Assistant Node
   - Module type: Android Accessibility + Device Hub
   - Module responsibilities:
       - Detect Shipt order acceptance
       - Extract shopping lists and delivery metadata
       - Communicate with Nikolai via Termux/Tailscale
       - Display overlays and automation instructions
       - Host BLE devices
       - Stream navigation/media to head units

4. Prepare the pipeline interface.
   - Create E:\Nikolai\Modules\ShopperModule\pipeline\incoming\
   - Create E:\Nikolai\Modules\ShopperModule\pipeline\outgoing\
   - GCLI will place build artifacts in /incoming
   - Nikolai will place validation reports in /outgoing

5. Wait for GCLI to deliver:
   - san_build_spec.txt
   - san_final_spec.txt
   - android_app_source.zip
   - module_contract.json

When the files arrive, validate them and prepare the module for compilation and deployment.