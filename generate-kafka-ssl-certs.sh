#!/bin/bash

# Set the following variables as needed
VALIDITY=365
PASSWORD=password123
COUNTRY=IT
STATE=YourState
LOCALITY=YourCity
ORGANIZATION=YourOrganization
ORGANIZATIONAL_UNIT=YourUnit
SERVER_CN=kafka
CLIENT_CN=client

mkdir -p ssl
cd ssl

# Clean up the existing files
rm -f *.jks *.crt *.csr *.key *.p12 ca-cert ca-key kafka_*_creds

create_keystore() {
    name=$1
    cn=$2
    keytool -keystore $name.keystore.jks -alias $name -validity $VALIDITY -genkey -keyalg RSA \
    -storepass $PASSWORD -keypass $PASSWORD \
    -dname "CN=$cn, OU=$ORGANIZATIONAL_UNIT, O=$ORGANIZATION, L=$LOCALITY, S=$STATE, C=$COUNTRY"
}

create_truststore() {
    name=$1
    keytool -keystore $name.truststore.jks -alias CARoot -import -file ca-cert -storepass $PASSWORD -noprompt
}

# CSR = Certificate Signing Request
create_csr() {
    name=$1
    keytool -keystore $name.keystore.jks -alias $name -certreq -file $name-cert-file -storepass $PASSWORD -keypass $PASSWORD
}

sign_cert() {
    name=$1
    openssl x509 -req -CA ca-cert -CAkey ca-key -in $name-cert-file -out $name-cert-signed -days $VALIDITY -CAcreateserial -passin pass:$PASSWORD
}

# Import the CA cert into the keystore
import_cert() {
    name=$1
    keytool -keystore $name.keystore.jks -alias CARoot -import -file ca-cert -storepass $PASSWORD -keypass $PASSWORD -noprompt
    keytool -keystore $name.keystore.jks -alias $name -import -file $name-cert-signed -storepass $PASSWORD -keypass $PASSWORD -noprompt
}

# Generete CA authority
openssl req -new -x509 -keyout ca-key -out ca-cert -days $VALIDITY -passin pass:$PASSWORD -passout pass:$PASSWORD \
    -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=CA"

# Generate certificates for the brokers
for i in 1 2 3
do
    create_keystore "kafka$i" "$SERVER_CN$i"
    create_csr "kafka$i"
    sign_cert "kafka$i"
    import_cert "kafka$i"
    create_truststore "kafka$i"
done

# Generate certificates for the client
create_keystore "client" "$CLIENT_CN"
create_csr "client"
sign_cert "client"
import_cert "client"
create_truststore "client"

# Create a file with the password
echo $PASSWORD > kafka_keystore_creds
echo $PASSWORD > kafka_sslkey_creds
echo $PASSWORD > kafka_truststore_creds

# Convert the keystore and truststore to PKCS12 format
keytool -importkeystore -srckeystore client.keystore.jks -destkeystore client.p12 -deststoretype PKCS12 -srcstorepass $PASSWORD -deststorepass $PASSWORD
openssl pkcs12 -in client.p12 -out client.key -nocerts -nodes -passin pass:$PASSWORD
openssl pkcs12 -in client.p12 -out client.crt -clcerts -nokeys -passin pass:$PASSWORD
cp ca-cert client.ca

# Remove temporary files
rm -f *-cert-file *-cert-signed *.p12

echo "Certificates created in the ssl folder"