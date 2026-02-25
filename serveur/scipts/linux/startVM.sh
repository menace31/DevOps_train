# Start the virtual machine
#!/bin/bash
echo "Starting the virtual machine..."

docker run -d -p 8080:5001 --name mon_app mdevillet31/ma-capsule